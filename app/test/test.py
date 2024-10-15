import asyncio

import aiohttp
import json

from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionRequest, ChatCompletionMessageParam
from app.http.ai_chat_http import create_chat_completion, completions


async def create_chat_completion1(chat_completion_request: ChatCompletionRequest):
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
        ChatCompletionMessageParam(role='system', content='你是一个人工智能助手'),
        ChatCompletionMessageParam(role='user', content='请问一下，什么是人工智能？'), ],
    stream=False,
    model='/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4',
    stream_options=None
)


async def x():
    # async for line in create_chat_completion1(chat_completion_request):
    async for line in create_chat_completion(chat_completion_request):
        print(line)


# asyncio.run(x())

x = completions(chat_completion_request)
print(x, type(x))