import asyncio
import json
import os
from typing import Optional

import torch
from datetime import datetime
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field
from weaviate.classes.query import Filter

from app.api.openai.api_server import create_chat_completion
from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from vllm.utils import random_uuid
from langchain_community.chat_message_histories import ChatMessageHistory

from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate, AiChatLogModel
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    query: str
    stream: bool
    model: str
    conversation_id: Optional[str] = Field(None, description="会话id，用于标识一个会话")


def get_reference_data(text: str):
    return knowledge_base_weaviate.search_hybrid_or(text, 10)


async def get_weaviste_history(conversation_id, query):
    filters = Filter.by_property("conversation_id").equal(conversation_id)
    ai_chat_log_list = await ai_chat_log_weaviate.search_hybrid(query=query, limit=10, filters=filters)

    message_list = []

    for ai_chat_log in ai_chat_log_list:
        human = {"role": "human", "content": ai_chat_log.input}
        ai = {"role": "ai", "content": ai_chat_log.output}
        message_list.append(human)
        message_list.append(ai)
    return message_list


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request,
                                  background_tasks: BackgroundTasks):
    start_time = datetime.now()
    member_id = raw_request.headers.get("Authorization")
    #
    # chat_message_history_key = f"chat:message:history:{member_id}"
    # chat_message_history = await get_object(chat_message_history_key, ChatMessageHistory) or ChatMessageHistory()
    #
    # if not chat_message_history.messages:
    #     chat_message_history.add_message(SystemMessage(content="你是小希留学顾问助手"))
    #
    # chat_message_history.add_user_message(request.query)
    # message_list = [{"role": message.type, "content": message.content} for message in chat_message_history.messages]

    conversation_id = request.conversation_id
    query = request.query
    message_list = []
    if not conversation_id:
        conversation_id = f"conversation-{random_uuid()}"
        system = {"role": "system", "content": "你是小希留学顾问助手"}
        human = {"role": "human", "content": query}
        message_list.append(system)
        message_list.append(human)
    else:
        message_list = await get_weaviste_history(conversation_id, query)

    logger.info(f"message_list: {message_list}")
    message_list.append({"role": "human", "content": query})
    reference_data_dict = await load_reference_data(request.query, 10)
    #
    reference_data = reference_data_dict.get("reference_data")
    knowledge_link = reference_data_dict.get("knowledge_link")
    #
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
            stream_response(result, member_id, message_list, start_time, knowledge_link, conversation_id),
            media_type="text/event-stream"
        )
    else:
        message_dict = await extract_message(result)
        background_tasks.add_task(process_after_response, message_dict,
                                  member_id, message_list, start_time, conversation_id)

        response_dict = json.loads(result.body.decode('utf-8'))
        response_dict["reference_data"] = reference_data
        response_dict["knowledge_link"] = knowledge_link
        result = JSONResponse(content=response_dict)

        logger.info(f"message_dict: {response_dict}: {type(result)}")
        return result


async def stream_response(result, member_id, message_list, start_time, knowledge_link, conversation_id):
    output = ''
    usage = None
    first_chunk = True
    message_id = ''
    async for chunk in result.body_iterator:
        # logger.info(f"chunk: {chunk}")
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
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

    message_dict = {"output": output, "usage": usage}
    logger.info(f"message_dict: {message_dict}")
    await process_after_response(message_dict, member_id, message_list, start_time, conversation_id)


async def extract_message(result):
    output = ''
    usage = None
    logger.info(f"result:{result}，type:{type(result)}")
    if isinstance(result, JSONResponse):
        logger.info("非流式输出")
        result_body = result.body.decode('utf-8')
        result_content = json.loads(result_body)
        if result_content.get('object') == 'error':
            output = result_body
        else:
            output += result_content['choices'][0]['message']['content']
            usage_or = result_content.get('usage')
            if usage_or:
                usage = ModelUsage(input=usage_or['prompt_tokens'], output=usage_or['completion_tokens'],
                                   total=usage_or['total_tokens'], unit='TOKENS')
    return {"output": output, "usage": usage}


async def save_weaviste(conversation_id,member_id,input,output):
    ai_chat_log_model = AiChatLogModel(
        conversation_id=conversation_id,
        message_id=member_id,
        user_id="123",
        input=input,
        output=output,
        created_time=datetime.now(),
        reference_data_uuids=["123"]
    )
    vector = Embedding.embed_query(ai_chat_log_model.output)
    uuid = ai_chat_log_weaviate.insert_data(ai_chat_log_model.dict(), vector)
    print(uuid)
    pass


async def process_after_response(message_dict, member_id, message_list, start_time, conversation_id):
    end_time = datetime.now()
    output = message_dict.get('output')
    input = message_list[-1]['content'] = output
    await save_weaviste(conversation_id,member_id,input,output)
    # TODO
    # await save_redis(chat_message_history, chat_message_history_key, message_dict)
    # await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time,
    #                     end_time)


async def load_reference_data(query, limit):
    # 匹配关键字使用特定知识库
    filters = None
    for key, values in ai_knowledge_base_keyword_dict.items():
        if any(v in query for v in values):
            filters = Filter.by_property("database").equal(key)
            break

    response_list = await knowledge_base_weaviate.search_hybrid(query, limit, filters)
    logger.info(f"weaviate 查询结果 response_list: {response_list}")
    reference_data = "\n\n".join([
        f"Reference data {n + 1}: {response_list[n].instruction}: {response_list[n].output}————{response_list[n].database}: {response_list[n].db_id}"
        for n in range(len(response_list))])
    knowledge_link = [response.link for response in response_list if
                      response.database == "t_knowledge_info" and response.link]
    return {"reference_data": reference_data,
            "knowledge_link": knowledge_link,
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
