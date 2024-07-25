import os
from io import BytesIO
import json
from typing import Optional, Union
from datetime import datetime
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel
from app.api.openai.api_server import create_chat_completion
from app.common.utils.logging import get_logger
from app.database.redis.redis_client import redis_client, get_object, set_object
from vllm.entrypoints.openai.protocol import (ChatCompletionRequest, StreamOptions)

from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    # 根据 ChatCompletionRequest 定义模型字段
    query: str
    stream: bool
    model: str

@observe()
async def save_langfuse(member_id, message_list, output, usage, start_time, end_time):
    '''保存消息到聊天历史记录'''
    langfuse_context.update_current_observation(
        user_id=member_id,
        metadata={"test": "test value"},
        input=message_list,
        output=output,
    )
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)

# 定义 process_chunk 和 process_after_response 函数
async def process_chunk(chunk, chat_message_history_key, member_id, message_list, start_time):
    stream_data = BytesIO(chunk.encode('utf-8'))
    result = StreamingResponse(stream_data, media_type="application/json")
    message_dict = await extract_message(result)
    chat_message_history = get_object(chat_message_history_key, ChatMessageHistory)
    if not chat_message_history:
        chat_message_history = ChatMessageHistory()

    chat_message_history.add_ai_message(message_dict.get('output'))
    set_object(chat_message_history_key, chat_message_history)
    end_time = datetime.now()
    await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time, end_time)

async def process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id, message_list, start_time):
    end_time = datetime.now()
    logger.info(f"start_time: {start_time}, end_time: {end_time}")
    logger.info(f"message_dict: {message_dict}")

    chat_message_history.add_ai_message(message_dict.get('output'))
    set_object(chat_message_history_key, chat_message_history)
    await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time, end_time)

async def extract_message(result):
    output = ''
    usage = None
    if isinstance(result, JSONResponse):
        result_body = result.body
        result_content = json.loads(result_body.decode('utf-8'))
        logger.info(f"result_content: {result_content}")
        output += result_content.get('choices')[0].get('message').get('content')
        usage_or = result_content.get('usage')
        if usage_or:
            usage = ModelUsage(input=usage_or.get('prompt_tokens'), output=usage_or.get('completion_tokens'),
                               total=usage_or.get('total_tokens'), unit='TOKENS')
            logger.info(f"usage: {usage}")

    elif isinstance(result, StreamingResponse):
        logger.info(f"流式输出")
        async for chunk in result.body_iterator:
            logger.info(f"chunk: {chunk}")
            chunk = chunk.decode('utf-8')  # 将字节转换为字符串
            if chunk.strip() == "data: [DONE]" or not chunk.strip():
                continue
            if chunk.startswith("data: "):
                chunk = chunk[len("data: "):]
            try:
                chunk_data = json.loads(chunk)
                choices = chunk_data.get('choices')
                if choices and choices[0].get('finish_reason') != 'stop':
                    delta_content = chunk_data.get('choices')[0].get('delta').get('content')
                    if delta_content:
                        output += delta_content
                else:
                    usage_or = chunk_data.get('usage')
                    if usage_or:
                        usage = ModelUsage(input=usage_or.get('prompt_tokens'),
                                           output=usage_or.get('completion_tokens'),
                                           total=usage_or.get('total_tokens'), unit='TOKENS')
                        logger.info(f"usage: {usage}")
            except json.JSONDecodeError as e:
                logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")
    return {
        "output": output,
        "usage": usage
    }

# 定义 generate 函数
@router.post("/v1/chat/completions", response_model=None)
async def generate(request: MyChatCompletionRequestModel, raw_request: Request, background_tasks: BackgroundTasks):
    usage: Optional[Union[BaseModel, ModelUsage]] = None
    start_time = datetime.now()
    member_id = raw_request.headers.get("Authorization")

    chat_message_history_key = f"chat:message:history:{member_id}"
    chat_message_history = get_object(chat_message_history_key, ChatMessageHistory)
    if chat_message_history is None:
        chat_message_history = ChatMessageHistory()
        system = SystemMessage(content="你是小希留学顾问助手")
        chat_message_history.add_message(system)

    chat_message_history.add_user_message(request.query)
    message_list = [{"role": message.type, "content": message.content} for message in chat_message_history.messages]
    logger.info(f"message_list: {message_list}")

    stream = request.stream
    if stream:
        stream_options = StreamOptions(include_usage=True)
    else:
        stream_options = None
    chat_request = ChatCompletionRequest(messages=message_list, stream=request.stream, model=request.model,
                                         stream_options=stream_options)

    result = await create_chat_completion(chat_request, raw_request)

    if isinstance(result, StreamingResponse):
        async def stream_response():
            async for chunk in result.body_iterator:
                if chunk.strip() == "data: [DONE]" or not chunk.strip():
                    continue
                if chunk.startswith("data: "):
                    chunk = chunk[len("data: "):]
                try:
                    chunk_data = json.loads(chunk)
                    choices = chunk_data.get('choices')
                    if choices and choices[0].get('finish_reason') != 'stop':
                        delta_content = chunk_data.get('choices')[0].get('delta').get('content')
                        if delta_content:
                            yield f"data: {json.dumps(chunk_data)}\n\n"
                            background_tasks.add_task(
                                process_chunk, chunk, chat_message_history_key, member_id, message_list, start_time)
                    else:
                        usage_or = chunk_data.get('usage')
                        if usage_or:
                            usage = ModelUsage(input=usage_or.get('prompt_tokens'),
                                               output=usage_or.get('completion_tokens'),
                                               total=usage_or.get('total_tokens'), unit='TOKENS')
                            logger.info(f"usage: {usage}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

        return StreamingResponse(stream_response(), media_type="text/event-stream")
    else:
        message_dict = await extract_message(result)
        logger.info(f"message_dict1: {message_dict}")
        await process_after_response(message_dict, chat_message_history, chat_message_history_key, member_id, message_list, start_time)
        return result
