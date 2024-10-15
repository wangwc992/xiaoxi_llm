import aiohttp
import requests

from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionRequest

url = "https://u430182-ac52-13068849.cqa1.seetacloud.com/v1/chat/completions"
headers = {'Content-Type': 'application/json'}


async def create_chat_completion(chat_completion_request: ChatCompletionRequest):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=chat_completion_request.dict(), headers=headers) as response:
            async for line in response.content:
                yield line.decode('utf-8')


def completions(chat_completion_request: ChatCompletionRequest):
    response = requests.post(url, json=chat_completion_request.dict(), headers=headers)
    return response.text
