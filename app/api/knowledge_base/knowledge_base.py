import os

from fastapi import Request, APIRouter
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from vllm.entrypoints.openai.protocol import ChatCompletionRequest
from app.api.openai.api_server import create_chat_completion
from app.database.redis.redis_client import redis_client

from langchain_community.chat_message_histories import ChatMessageHistory

router = APIRouter(prefix="/chat")


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
    # chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
    # chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
    # if chat_message_history is None:
    chat_message_history = ChatMessageHistory()
    system = SystemMessage(content="你是小希留学顾问助手")
    chat_message_history.add_message(system)

    chat_message_history.add_user_message("悉尼大学的计算机专业")
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

    request = ChatCompletionRequest(messages=message_list, stream=request.stream,
                                    model=request.model)
    request.messages = message_list

    # 添加用户消息，保存历史消息
    # chat_message_history.add_ai_message(result.content)
    # redis_client.set_object(chat_message_history_key, chat_message_history)
    result = await create_chat_completion(request, raw_request)
    return result
