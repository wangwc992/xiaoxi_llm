import json
import os
from datetime import datetime
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel

from app.api.knowledge_base.knowledge_base import get_chat_visits_number
from app.api.openai.api_server import create_chat_completion
from app.common.core.langchain_client import get_openai_serving_chat
from app.common.utils.logging import get_logger
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from langchain_community.chat_message_histories import ChatMessageHistory

from app.database.weaviate.knowledge_base import knowledge_base_weaviate

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    """
    Pydantic model for chat completion request data.

    Attributes:
        query (str): The user's query to generate a response for.
        stream (bool): Flag indicating if the response should be streamed.
        model (str): The model to use for generating the response.
    """
    query: str
    stream: bool
    model: str


async def engine_abort(request_id: str):
    """
    Abort the request with the given ID.

    Args:
        request_id (str): The ID of the request to abort.
    """
    openai_serving_chat = get_openai_serving_chat()
    await openai_serving_chat.engine.abort(request_id)


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request):
    """
    Generate text or stream the generated text as a response.

    Args:
        request (MyChatCompletionRequestModel): The request model containing the query, stream flag, and model.
        raw_request (Request): The original HTTP request.
        background_tasks (BackgroundTasks): Background tasks for FastAPI.

    Returns:
        StreamingResponse or JSONResponse: The generated response, either streamed or as a complete response.
    """
    # Record start time
    start_time = datetime.now()
    # Extract Authorization header as member ID
    member_id = raw_request.headers.get("Authorization")

    # Retrieve or initialize chat message history for the user
    chat_message_history_key = f"chat:message:history:{member_id}"
    chat_message_history = get_object(chat_message_history_key, ChatMessageHistory) or ChatMessageHistory()

    # Add a system message if the chat history is empty
    if not chat_message_history.messages:
        chat_message_history.add_message(SystemMessage(content="你是小希留学顾问助手"))

    # Add the user's query to the chat history
    chat_message_history.add_user_message(request.query)
    # Convert messages to the required format
    message_list = [{"role": message.type, "content": message.content} for message in chat_message_history.messages]
    logger.info(f"message_list: {message_list}")

    # Load reference data
    reference_data, knowledge_link = await load_reference_data(request.query, 10)
    # 加载prompt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../prompt/knowledge_prompt.txt')
    template = PromptTemplate.from_file(file_path)
    prompt = template.format(input=request.query, reference_data=reference_data)
    message_list[-1]['content'] = prompt

    # Set stream options if the request is for streaming
    stream_options = StreamOptions(include_usage=True) if request.stream else None

    # Create a ChatCompletionRequest object
    chat_request = ChatCompletionRequest(messages=message_list, stream=request.stream, model=request.model,
                                         stream_options=stream_options)

    # Call create_chat_completion and get the result
    result = await create_chat_completion(chat_request, raw_request)

    # Return a streaming response if requested
    if isinstance(result, StreamingResponse):
        return StreamingResponse(
            stream_response(result, chat_message_history, chat_message_history_key, member_id, message_list,
                            start_time, knowledge_link),
            media_type="text/event-stream")
    else:
        message_dict = await extract_message(result)
        await process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id,
                                     message_list,
                                     start_time)
        # 将 JSONResponse 的内容提取并转换为字典
        response_dict = json.loads(result.body.decode('utf-8'))

        # 添加 reference_data 字段
        response_dict["reference_data"] = reference_data
        response_dict["knowledge_link"] = knowledge_link

        # 重新生成 JSONResponse 对象
        result = JSONResponse(content=response_dict)

        # 记录日志
        logger.info(f"message_dict: {response_dict}: {type(result)}")
        # chat visits number increment after minus one
        await get_chat_visits_number(is_completions=False)
        # 返回修改后的 JSONResponse 对象
        return result


async def stream_response(result, chat_message_history, chat_message_history_key, member_id, message_list, start_time,
                          knowledge_link):
    """
    Handle streaming response.

    Args:
        result (StreamingResponse): The streaming response from the chat completion request.
        chat_message_history (ChatMessageHistory): The user's chat message history.
        chat_message_history_key (str): Redis key for the user's chat message history.
        member_id (str): The user's member ID.
        message_list (list): List of messages in the chat.
        start_time (datetime): The start time of the request.

    Yields:
        str: Chunks of the streaming response.
    """
    output = ''
    usage = None
    first_chunk = True
    async for chunk in result.body_iterator:
        logger.info(f"chunk: {chunk}")
        if first_chunk:
            chunk = chunk.replace('"role":"assistant"', f'"role":"assistant","content":{json.dumps(knowledge_link)}')
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
                # chat visits number increment after minus one
                await get_chat_visits_number(is_completions=False)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

    message_dict = {"output": output, "usage": usage}
    await process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id, message_list,
                                 start_time)


async def extract_message(result):
    """
    Extract message from non-streaming output.

    Args:
        result (JSONResponse): The response from the chat completion request.

    Returns:
        dict: A dictionary containing the output text and usage information.
    """
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
    """
    Process actions after receiving the response.

    Args:
        message_dict (dict): A dictionary containing the output text and usage information.
        chat_message_history (ChatMessageHistory): The user's chat message history.
        chat_message_history_key (str): Redis key for the user's chat message history.
        member_id (str): The user's member ID.
        message_list (list): List of messages in the chat.
        start_time (datetime): The start time of the request.
    """
    logger.info(f"message_dict: {message_dict}")
    end_time = datetime.now()
    # Save the message to chat history in Redis
    # TODO
    # await save_redis(chat_message_history, chat_message_history_key, message_dict)

    # Save the message to chat history in Langfuse
    # TODO
    # await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time,
    #                     end_time)



async def load_reference_data(query, limit):
    """ Load reference data from the knowledge base. """
    response_list = knowledge_base_weaviate.search_hybrid(query, limit)
    reference_data = "\n\n".join([f"Reference data {n + 1}: {response_list[n].instruction}: {response_list[n].output}————{response_list[n].database}: {response_list[n].db_id}"
                                  for n in range(len(response_list))])
    knowledge_link = [response.link for response in response_list if
                      response.database == "t_knowledge_info" and response.link]
    return reference_data, knowledge_link


async def save_redis(chat_message_history, chat_message_history_key, message_dict):
    """
    Save the message to chat history in Redis.

    Args:
        chat_message_history (ChatMessageHistory): The user's chat message history.
        chat_message_history_key (str): Redis key for the user's chat message history.
        message_dict (dict): A dictionary containing the output text.
    """
    chat_message_history.add_ai_message(message_dict.get('output'))
    set_object(chat_message_history_key, chat_message_history)


@observe()
async def save_langfuse(member_id, message_list, output, usage, start_time, end_time):
    """
    Save the message to chat history in Langfuse.

    Args:
        member_id (str): The user's member ID.
        message_list (list): List of messages in the chat.
        output (str): The generated response text.
        usage (ModelUsage): Usage information of the model.
        start_time (datetime): The start time of the request.
        end_time (datetime): The end time of the request.
    """
    langfuse_context.update_current_observation(user_id=member_id, metadata={"test": "test value"},
                                                input=message_list, output=output)
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)
