import os
import json

from io import BytesIO
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


@router.post("/v1/chat/completions", response_model=None)
async def generate(request: MyChatCompletionRequestModel, raw_request: Request, background_tasks: BackgroundTasks):
    """生成文本或流式返回生成的文本."""
    usage: Optional[Union[BaseModel, ModelUsage]] = None
    # 记录开始时间
    start_time = datetime.now()
    # 获取请求头Authorization
    member_id = raw_request.headers.get("Authorization")

    # 获取用户历史消息
    chat_message_history_key = f"chat:message:history:{member_id}"
    chat_message_history = get_object(chat_message_history_key, ChatMessageHistory)
    if chat_message_history is None:
        chat_message_history = ChatMessageHistory()
        system = SystemMessage(content="你是小希留学顾问助手")
        chat_message_history.add_message(system)

    chat_message_history.add_user_message(request.query)
    message_list = [{"role": message.type, "content": message.content} for message in chat_message_history.messages]
    logger.info(f"message_list: {message_list}")
    # 加载参考数据
    # response_list = load_reference_data(request.query, 10)
    # reference_data = "\n\n".join([f"Reference data {n + 1}: {response_list[n].instruction}————{response_list[n].output}"
    #                               for n in range(len(response_list))])
    #
    # # 加载prompt
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(base_dir, '../../prompt/knowledge_prompt.txt')
    # template = PromptTemplate.from_file(file_path)
    # prompt = template.format(input=request.query, reference_data=reference_data)

    # 创建 ChatCompletionRequest 对象
    stream = request.stream
    if stream:
        stream_options = StreamOptions(include_usage=True)
    else:
        stream_options = None
    chat_request = ChatCompletionRequest(messages=message_list, stream=request.stream, model=request.model,
                                         stream_options=stream_options)

    # 调用 create_chat_completion 并获取结果
    result = await create_chat_completion(chat_request, raw_request)

    # 返回结果，不等待后续处理
    # 处理流式响应
    if isinstance(result, StreamingResponse):
        # 读取流式响应的数据
        stream_data = BytesIO()
        async for chunk in result.body_iterator:
            stream_data.write(chunk.encode('utf-8'))  # 将字符串转换为字节并写入
        stream_data.seek(0)  # 重置流的位置

        # 启动一个后台任务来处理消息提取和保存
        background_tasks.add_task(
            process_after_response, stream_data, chat_message_history, chat_message_history_key, member_id,
            message_list, start_time)

        # 返回流式响应
        return StreamingResponse(stream_data, media_type="application/json")
    else:
        await process_after_response(result, chat_message_history, chat_message_history_key, member_id,
                                     message_list, start_time)
        return result


async def process_after_response(result, chat_message_history, chat_message_history_key, member_id, message_list,
                                 start_time):
    message_dict = await extract_message(result)
    # 记录结束时间
    end_time = datetime.now()
    logger.info(f"start_time: {start_time}, end_time: {end_time}")
    logger.info(f"message_dict: {message_dict}")

    # # 添加 AI 消息到聊天历史记录
    chat_message_history.add_ai_message(message_dict.get('output'))
    # 聊天历史记录保存到 Redis
    set_object(chat_message_history_key, chat_message_history)

    # 使用  保存消息
    await save_langfuse(member_id, message_list, message_dict.get('output'), message_dict.get('usage'), start_time,
                        end_time)


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


async def extract_message(result):
    '''保存消息到聊天历史记录'''
    output = ''
    usage = None
    logger.info(f"result:{result}, type:{type(result)}")
    # 处理 JSONResponse
    if isinstance(result, JSONResponse):
        logger.info(f"非流式输出")
        result_body = result.body
        result_content = json.loads(result_body.decode('utf-8'))
        logger.info(f"result_content: {result_content}")
        output += result_content.get('choices')[0].get('message').get('content')
        usage_or = result_content.get('usage')
        if usage_or:
            # {'prompt_tokens': 31, 'total_tokens': 472, 'completion_tokens': 441}
            usage = ModelUsage(input=usage_or.get('prompt_tokens'), output=usage_or.get('completion_tokens'),
                               total=usage_or.get('total_tokens'), unit='TOKENS')
            logger.info(f"usage: {usage}")

    # 处理 StreamingResponse
    elif isinstance(result, StreamingResponse):
        logger.info(f"流式输出")
        async for chunk in result.body_iterator:
            logger.info(f"chunk: {chunk}")
            # 检查 chunk 是否为空或者是特殊标记
            if chunk.strip() == "data: [DONE]" or not chunk.strip():
                continue
            # 去除 'data: ' 前缀
            if chunk.startswith("data: "):
                chunk = chunk[len("data: "):]
            # 解析 JSON 数据
            try:
                chunk_data = json.loads(chunk)
                choices = chunk_data.get('choices')
                if choices and choices[0].get('finish_reason') != 'stop':
                    delta_content = chunk_data.get('choices')[0].get('delta').get('content')
                    if delta_content:  # 检查 content 是否为 None
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
    logger.info(f"Extracted message - output: {output}, usage: {usage}")
    return {
        "output": output,
        "usage": usage
    }
