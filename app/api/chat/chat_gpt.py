from fastapi import Request, APIRouter, Response
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate

from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool

llm = LangChain.llm

if __name__ == "__main__":
    tools = [check_school_tool]
    llm_with_tools = llm.bind_tools(tools) | {
        "functions": JsonOutputToolsParser(),
        "text": StrOutputParser()
    }
    result = llm_with_tools.invoke("想去悉尼大学留学")
    print(result)

    chat_history = ChatMessageHistory()
    chat_history.add_user_message("想去悉尼大学留学")
    chat_history.add_ai_message(str(result.get("functions")))
    chat_history.add_user_message("gpa3.5,留学的学位是本科")
    result = llm_with_tools.invoke(chat_history.messages)
    print(result)

    chat_history.add_ai_message(str(result.get("functions")))
    chat_history.add_user_message('''
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
    chat_history.add_user_message("有什么推荐的专业吗？")
    result = llm_with_tools.invoke(chat_history.messages)
    print(result)
