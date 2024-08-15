from langchain_core.prompts import PromptTemplate

template = "你好，我是{user_name}，我是{user_age}岁。"
template = PromptTemplate.from_template(template)
x = template.format(user_name="张三", user_age=18)
print( x)