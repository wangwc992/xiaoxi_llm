import asyncio

import aiohttp
import json

from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionRequest, ChatCompletionMessageParam


async def create_chat_completion(chat_completion_request: ChatCompletionRequest):
    url = "https://u430182-ac52-13068849.cqa1.seetacloud.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=chat_completion_request.dict(), headers=headers) as response:
            async for line in response.content:
                yield line.decode('utf-8')


chat_completion_request = ChatCompletionRequest(
    messages=[
        ChatCompletionMessageParam(role='system', content='你是一个严谨的智能问题分类助手，不会提供虚假信息'),
        ChatCompletionMessageParam(role='user',
                                   content='**角色**  \r\n你是问题任务分类助手。\r\n\r\n**任务**  \r\n你需要根据用户的提问，判断问题与以下哪一项匹配，以找到对应任务的帮助用户解决问题。\r\n\r\n**分类项**：\r\n\r\n**一、咨询问题**：\r\n- **A**：询问/提问/希望了解与留学相关的海外院校/专业/申请相关的知识。\r\n  - 若是，回复 A，格式示例：{"query_type":"A"}。\r\n\r\n- **B**：询问/提问/希望了解与澳际教育/小希平台相关功能知识，或小希的业务知识。\r\n  - 若是，回复 B，格式示例：{"query_type":"B"}。\r\n\r\n**二、闲聊**：\r\n- **D**：如果识别到用户输入的问题和留学申请，或者和小希系统，或平台的操作无关，请回复 D，格式示例：{"query_type":"D"}。\r\n\r\n**约束**：\r\n1. 请严格按照格式示例进行输出。\r\n2. 格式的 `value` 为空不添加该字段,不能使用未提及，未提供等，没有value就不返回该字段\r\n3. 返回 JSON 格式。不要用md格式输出。{开头，}结尾。\r\n\r\n用户问题： {悉尼大学}'),
    ],
    stream=False,
    model='/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4',
    stream_options=None
)

# async def x():
#     lists = await create_chat_completion(chat_completion_request)
#     for i in lists:
#         print(i)
# asyncio.run(x())

x = "\n"
if x == "\n":
    print("true")
else:
    print("false")

