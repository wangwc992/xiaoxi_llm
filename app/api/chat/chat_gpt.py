import asyncio

from fastapi import Request, APIRouter, Response
from langchain_core.messages import SystemMessage, FunctionMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate

from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool, details_tool, information_consultant_tool, Action, exec_action
import app.common.database.redis.redis_client as redis_client

tools = [check_school_tool, details_tool, information_consultant_tool]
llm_with_tools = LangChain(tools=tools)

router = APIRouter(prefix="/chat")


@router.post("/v1")
async def stream(request: Request) -> Response:
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    member_id = request_dict.pop("member_id")
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
        return text
    # {'args': {'check_school': {'country_name': '澳大利亚', 'school_name': '悉尼大学'}}, 'type': 'searchSchool'}
    functions_tool = result.get("functions")[0]
    function_message = FunctionMessage(content="你是小希留学顾问助手")
    chat_message_history.add_message(function_message)
    # 转成Action对象
    functions_tool = Action(**functions_tool)
    calling_str = await exec_action(tools, functions_tool)
    tool_message = ToolMessage(content=calling_str)



def chat_gpt():
    chat_history = ChatMessageHistory()
    chat_history.add_user_message("想去悉尼大学留学")
    chat_history.add_user_message("gpa3.5,留学的学位是本科")
    chat_history.add_user_message('''根据上下文用户的输入，想去悉尼大学留学，gpa3.5，留学的学位是本科，从以下专业中选择合适的推荐专业：
    悉尼大学	The University of Sydney	教学硕士（中等）	Master of Teaching (Secondary)  学位博士  gpa要求4.5    
    悉尼大学	The University of Sydney	护理学士（高级研究）	Bachelor of Nursing (Advanced Studies)  学位本科  gpa要求3.5    
    悉尼大学	The University of Sydney	教育硕士（TESOL）	Master of Education (TESOL) 学位本科 gpa要求3.5    
    悉尼大学	The University of Sydney	经济学学士	Bachelor of Economics   学位硕士   gpa要求3.5    
    悉尼大学	The University of Sydney	商业学士	Bachelor of Commerce    学位博士    gpa要求4.5    
    悉尼大学	The University of Sydney	计算机科学硕士（高级入学）	Master of Computer Science (advanced entry) 学位本科 gpa要求3.5    
    悉尼大学	The University of Sydney	战略公共关系硕士	Master of Strategic Public Relations    学位本科    gpa要求2.5    
    悉尼大学	The University of Sydney	数字传播与文化硕士	Master of Digital Communication and Culture 学位硕士 gpa要求5.5    
    悉尼大学	The University of Sydney	媒体实践硕士	Master of Media Practice    学位本科    gpa要求4.5    
    悉尼大学	The University of Sydney	商法硕士	Master of Business Law 学位博士  gpa要求3.0    ''')

    # result = asyncio.run(llm_with_tools.invoke_tools(chat_history.messages))
    # print(result)
    # print(llm_with_tools.invoke("悉尼大学	The University of Sydney	商法硕士	Master of Business Law的详情信息"))
    # print(llm_with_tools.invoke("悉尼大学的奖学金"))
    # print(llm_with_tools.invoke("悉尼大学的免申请费动态"))
    # print(llm_with_tools.invoke("悉尼大学热门的专业"))
    # print(llm_with_tools.invoke("周杰伦的个人资料"))

    # prompt = "小王"
    # member_id = 123
    # chat_message_history_key = redis_client.CHAT_MESSAGE_HISTORY = f"chat:message:history:{member_id}"
    # # redis_client.set_object(chat_message_history_key, chat_history)
    # chat_message_history = redis_client.get_object(chat_message_history_key, ChatMessageHistory)
    # if chat_message_history is None:
    #     chat_message_history = ChatMessageHistory()
    #
    # chat_message_history.add_user_message(prompt)
    # redis_client.set_object(chat_message_history_key, chat_message_history)

    chat_message_history = ChatMessageHistory()
    system = SystemMessage(content="你是AGIClass的课程助理。"),
    chat_message_history.add_message(system)
    chat_message_history.add_user_message("你好")
    print(chat_message_history.messages)


if __name__ == "__main__":
    chat_gpt()
