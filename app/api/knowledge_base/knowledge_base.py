import os
import json

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from app.api.openai.api_server import create_chat_completion
from app.common.utils.logging import get_logger
from app.database.redis.redis_client import redis_client
from vllm.entrypoints.openai.protocol import ChatCompletionRequest

from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter(prefix="/chat")
loger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    # 根据 ChatCompletionRequest 定义模型字段
    query: str
    stream: bool
    model: str


@router.post("/v1/chat/completions", response_model=None)
async def generate(request: MyChatCompletionRequestModel, raw_request: Request):
    """生成文本或流式返回生成的文本."""
    # 获取请求头Authorization
    member_id = raw_request.headers.get("Authorization")

    # 获取用户历史消息
    chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
    chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
    # if chat_message_history is None:
    chat_message_history = ChatMessageHistory()
    system = SystemMessage(content="你是小希留学顾问助手")
    chat_message_history.add_message(system)

    chat_message_history.add_user_message(request.query)
    message_list = [{"role": message.type, "content": message.content} for message in
                    chat_message_history.messages]

    # 加载参考数据
    # response_list = load_reference_data(text, 10)
    # reference_data = "\n\n".join([f"Reference data {n + 1}: {response_list[n].instruction}————{response_list[n].output}"
    #                               for n in range(len(response_list))])

    # 加载prompt
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(base_dir, '../../prompt/knowledge_prompt.txt')
    # template = PromptTemplate.from_file(file_path)
    # prompt = template.format(input=query, reference_data=reference_data)

    # 创建 ChatCompletionRequest 对象
    request = ChatCompletionRequest(messages=message_list, stream=request.stream, model=request.model)
    request.messages = message_list

    # 调用 create_chat_completion 并获取结果
    result = await create_chat_completion(request, raw_request)
    # 保存消息到聊天历史记录
    await save_message(chat_message_history, chat_message_history_key, result)
    # 返回结果
    return result


async def save_message(chat_message_history, chat_message_history_key, result):
    '''保存消息到聊天历史记录'''
    content = ''
    # 处理 JSONResponse
    if isinstance(result, JSONResponse):
        result_body = result.body
        result_content = json.loads(result_body.decode('utf-8'))
        loger.info(f"result_content: {result_content}")
        content += result_content.get('choices')[0].get('message').get('content')

    # 处理 StreamingResponse
    # 处理 StreamingResponse
    elif isinstance(result, StreamingResponse):
        async for chunk in result.body_iterator:
            # 检查 chunk 是否为空或者是特殊标记
            if chunk.strip() == "data: [DONE]" or not chunk.strip():
                continue
            # 去除 'data: ' 前缀
            if chunk.startswith("data: "):
                chunk = chunk[len("data: "):]
            # 解析 JSON 数据
            try:
                chunk_data = json.loads(chunk)
                if chunk_data.get('choices')[0].get('finish_reason') != 'stop':
                    delta_content = chunk_data.get('choices')[0].get('delta').get('content')
                    if delta_content:  # 检查 content 是否为 None
                        content += delta_content
            except json.JSONDecodeError as e:
                loger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

        # 添加 AI 消息到聊天历史记录
    chat_message_history.add_ai_message(content)
    # 聊天历史记录保存到 Redis
    redis_client.set_object(chat_message_history_key, chat_message_history)
