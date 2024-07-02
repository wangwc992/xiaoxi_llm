from langchain_core.messages import SystemMessage, FunctionMessage, ToolMessage, BaseMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool, details_tool, information_consultant_tool, Action, exec_action, find_tool
import app.common.database.redis.redis_client as redis_client

tools = [check_school_tool, details_tool, information_consultant_tool]
llm_with_tools = LangChain(tools=tools)

prompt = "悉尼大学的奖学金？"
member_id = "1"
chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
if chat_message_history is None:
    chat_message_history = ChatMessageHistory()
    system = SystemMessage(content="你是小希留学顾问助手")
    chat_message_history.add_message(system)
chat_message_history.add_user_message(prompt)

result = llm_with_tools.invoke_tools(chat_message_history.messages)

tool_calls = result.tool_calls[0]
content = result.content
if content:
    chat_message_history.add_ai_message(content)
    print(content)
else:
    chat_message_history.add_message(result)
    functions_tool = Action(**tool_calls)
    calling_str = exec_action(tools, functions_tool)
    tool_message = ToolMessage(content=calling_str, tool_call_id=tool_calls.get("id"))
    chat_message_history.add_message(tool_message)
    result = llm_with_tools.invoke(chat_message_history.messages)
    chat_message_history.add_user_message(result.content)
    print(result)
print('*' * 50)
print(chat_message_history.messages)
