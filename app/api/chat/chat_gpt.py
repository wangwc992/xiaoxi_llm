from fastapi import Request, APIRouter, Response
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool, details_tool, information_consultant_tool, Action, exec_action
import app.common.database.redis.redis_client as redis_client

tools = [check_school_tool, details_tool, information_consultant_tool]
llm_with_tools = LangChain(tools=tools)

router = APIRouter(prefix="/chat")


@router.post("/v1")
async def stream(request: Request) -> Response:
    # 获取请求数据
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    member_id = request_dict.pop("member_id")

    # 获取用户历史消息
    chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
    chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
    if chat_message_history is None:
        chat_message_history = ChatMessageHistory()
        system = SystemMessage(content="你是小希留学顾问助手")
        chat_message_history.add_message(system)
    chat_message_history.add_user_message(prompt)

    # 执行工具获取结果
    result = llm_with_tools.invoke_tools(chat_message_history.messages)

    # 添加AI回复
    content = result.content

    # 如果有AI回复，直接返回，否则执行工具
    if content:
        chat_message_history.add_ai_message(content)
        return content

    # 添加工具调用结果
    chat_message_history.add_message(result)

    # 执行工具获取结果
    tool_calls = result.tool_calls[0]
    functions_tool = Action(**tool_calls)
    calling_str = exec_action(tools, functions_tool)

    # 添加工具调用结果
    tool_message = ToolMessage(content=calling_str, tool_call_id=tool_calls.get("id"))
    chat_message_history.add_message(tool_message)

    # 执行工具获取结果
    result = llm_with_tools.invoke(chat_message_history.messages)

    # 添加用户消息，保存历史消息
    chat_message_history.add_user_message(result.content)
    redis_client.set_object(chat_message_history_key, chat_message_history)

    return result.content
