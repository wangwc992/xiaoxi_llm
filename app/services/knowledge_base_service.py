import asyncio
import json
import os
import torch
from datetime import datetime
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel

from app.api.openai.api_server import create_chat_completion
from app.common.utils.logging import get_logger
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from langchain_community.chat_message_histories import ChatMessageHistory

from app.database.weaviate.knowledge_base import knowledge_base_weaviate

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    query: str
    stream: bool
    model: str


def get_reference_data(text: str):
    return knowledge_base_weaviate.search_hybrid_or(text, 10)


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request,
                                  background_tasks: BackgroundTasks):
    start_time = datetime.now()
    member_id = raw_request.headers.get("Authorization")

    chat_message_history_key = f"chat:message:history:{member_id}"
    chat_message_history = await get_object(chat_message_history_key, ChatMessageHistory) or ChatMessageHistory()

    if not chat_message_history.messages:
        chat_message_history.add_message(SystemMessage(content="你是小希留学顾问助手"))

    chat_message_history.add_user_message(request.query)
    message_list = [{"role": message.type, "content": message.content} for message in chat_message_history.messages]
    logger.info(f"message_list: {message_list}")

    reference_data_dict = await load_reference_data(request.query, 10)

    reference_data = reference_data_dict.get("reference_data")
    knowledge_link = reference_data_dict.get("knowledge_link")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../prompt/knowledge_prompt.txt')
    template = PromptTemplate.from_file(file_path)
    prompt = template.format(input=request.query, reference_data=reference_data)
    message_list[-1]['content'] = prompt

    stream_options = StreamOptions(include_usage=True) if request.stream else None

    chat_request = ChatCompletionRequest(
        messages=message_list,
        stream=request.stream,
        model=request.model,
        stream_options=stream_options
    )

    result = await create_chat_completion(chat_request, raw_request)

    if isinstance(result, StreamingResponse):
        return StreamingResponse(
            stream_response(result, chat_message_history, chat_message_history_key, member_id, message_list,
                            start_time, knowledge_link),
            media_type="text/event-stream"
        )
    else:
        message_dict = await extract_message(result)
        background_tasks.add_task(process_after_response, message_dict, chat_message_history, chat_message_history_key,
                                  member_id, message_list, start_time)

        response_dict = json.loads(result.body.decode('utf-8'))
        response_dict["reference_data"] = reference_data
        response_dict["knowledge_link"] = knowledge_link
        result = JSONResponse(content=response_dict)

        logger.info(f"message_dict: {response_dict}: {type(result)}")
        await get_chat_visits_number(is_completions=False)
        return result


async def stream_response(result, chat_message_history, chat_message_history_key, member_id, message_list, start_time,
                          knowledge_link):
    output = ''
    usage = None
    first_chunk = True
    async for chunk in result.body_iterator:
        logger.info(f"chunk: {chunk}")
        if first_chunk:
            chunk = chunk.replace('"role":"1"', f'"role":"1","content":{json.dumps(knowledge_link)}')
        yield chunk
        if chunk.strip() == "data: [DONE]" or not chunk.strip() or first_chunk:
            first_chunk = False
            continue
        if chunk.startswith("data: "):
            chunk = chunk[len("data: "):]
        try:
            chunk_data = json.loads(chunk)
            choices = chunk_data.get('choices')
            if choices and choices[0].get('finish_reason') != 'stop':
                delta_content = choices[0]['delta'].get('content')
                if delta_content:
                    output += delta_content
            else:
                usage_or = chunk_data.get('usage')
                if usage_or:
                    usage = ModelUsage(input=usage_or['prompt_tokens'], output=usage_or['completion_tokens'],
                                       total=usage_or['total_tokens'], unit='TOKENS')
                    logger.info(f"usage: {usage}")
                await get_chat_visits_number(is_completions=False)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

    message_dict = {"output": output, "usage": usage}
    await process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id, message_list,
                                 start_time)


async def extract_message(result):
    output = ''
    usage = None
    logger.info(f"result:{result}，type:{type(result)}")
    if isinstance(result, JSONResponse):
        logger.info("非流式输出")
        result_body = result.body
        result_content = json.loads(result_body.decode('utf-8'))
        logger.info(f"result_content: {result_content}")
        output += result_content['choices'][0]['message']['content']
        usage_or = result_content.get('usage')
        if usage_or:
            usage = ModelUsage(input=usage_or['prompt_tokens'], output=usage_or['completion_tokens'],
                               total=usage_or['total_tokens'], unit='TOKENS')
            logger.info(f"usage: {usage}")
    return {"output": output, "usage": usage}


async def process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id, message_list,
                                 start_time):
    logger.info(f"message_dict: {message_dict}")
    end_time = datetime.now()
    torch.cuda.empty_cache()
    # TODO
    # await save_redis(chat_message_history, chat_message_history_key, message_dict)
    # await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time,
    #                     end_time)


async def load_reference_data(query, limit):
    response_list = await knowledge_base_weaviate.search_hybrid(query, limit)
    logger.info(f"weaviate 查询结果 response_list: {response_list}")
    reference_data = "\n\n".join([
        f"Reference data {n + 1}: {response_list[n].instruction}: {response_list[n].output}————{response_list[n].database}: {response_list[n].db_id}"
        for n in range(len(response_list))])
    knowledge_link = [response.link for response in response_list if
                      response.database == "t_knowledge_info" and response.link]
    knowledge_link.append(len(response_list))
    return {"reference_data": reference_data,
            "knowledge_link": knowledge_link,
            "reference_number": len(response_list),
            }


async def save_redis(chat_message_history, chat_message_history_key, message_dict):
    chat_message_history.add_ai_message(message_dict.get('output'))
    await set_object(chat_message_history_key, chat_message_history)


@observe()
async def save_langfuse(member_id, message_list, output, usage, start_time, end_time):
    langfuse_context.update_current_observation(user_id=member_id, metadata={"test": "test value"},
                                                input=message_list, output=output)
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)


lock = asyncio.Lock()
chat_visits_number = 0
chat_visits_number_max = 30


async def get_chat_visits_number(is_completions: bool = False) -> bool:
    global chat_visits_number
    global chat_visits_number_max
    logger.info(f"当前 chat_visits_number: {chat_visits_number},{is_completions}")
    async with lock:
        if is_completions:
            if chat_visits_number >= chat_visits_number_max:
                logger.error(f"请求次数超过上限{chat_visits_number_max}次，请稍后再试。")
                return True
            chat_visits_number += 1
        else:
            chat_visits_number -= 1
    return False
