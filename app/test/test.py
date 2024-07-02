from langchain_core.messages import SystemMessage, FunctionMessage, ToolMessage
from langchain_community.chat_message_histories import ChatMessageHistory

from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool, details_tool, information_consultant_tool, Action, exec_action, find_tool
import app.common.database.redis.redis_client as redis_client

tools = [check_school_tool, details_tool, information_consultant_tool]
llm_with_tools = LangChain(tools=tools)

prompt = "想去澳大利亚的悉尼大学留学，gpa3.5，留学的学位是本科"
member_id = "321"
chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
if chat_message_history is None:
    chat_message_history = ChatMessageHistory()
    system = SystemMessage(content="你是小希留学顾问助手")
    chat_message_history.add_message(system)
chat_message_history.add_user_message(prompt)

result = llm_with_tools.invoke_tools(chat_message_history.messages)

text = result.get("text")
if text:
    chat_message_history.add_ai_message(text)
    print(text)
else:
    # {'args': {'check_school': {'country_name': '澳大利亚', 'school_name': '悉尼大学'}}, 'type': 'searchSchool'}
    functions_calling = result.get("functions")[0]
    tool_type = functions_calling.get("type")
    tool = find_tool(tools, tool_type)
    # 创建 `FunctionMessage` 实例
    function_message = FunctionMessage(
        name=tool_type,
        content=(
            f"描述: {tool.description}\n"
            f"参数: {functions_calling.get('args')}"
        )
    )

    chat_message_history.add_message(function_message)
    # 转成Action对象
    functions_tool = Action(**functions_calling)
    calling_str = exec_action(tools, functions_tool)

    chat_message_history.add_message(result)

    tool_message = ToolMessage(content=calling_str, tool_call_id=functions_calling.get("id"))
    chat_message_history.add_message(tool_message)
    result = llm_with_tools.invoke_tools(chat_message_history.messages)
    print(result)
