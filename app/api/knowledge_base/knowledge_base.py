from fastapi import Request, APIRouter
from langchain_core.messages import SystemMessage
from vllm.entrypoints.openai.protocol import ChatCompletionRequest
from app.api.openai.api_server import create_chat_completion
from app.database.redis.redis_client import redis_client

from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter(prefix="/chat")

@router.post("/v1/chat/completions", response_model=None)
async def generate(request: ChatCompletionRequest, raw_request: Request):
    """生成文本或流式返回生成的文本."""
    # 获取请求头Authorization
    member_id = raw_request.headers.get("Authorization")

    # 获取用户历史消息
    chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
    chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
    if chat_message_history is None:
        chat_message_history = ChatMessageHistory()
        system = SystemMessage(content="你是小希留学顾问助手")
        chat_message_history.add_message(system)

    chat_message_history.add_user_message("悉尼大学的计算机专业")
    request.messages = chat_message_history.messages
    return await create_chat_completion(request, raw_request)
