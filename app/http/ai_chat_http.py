import http.client
import json

from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionRequest


async def create_chat_completion(chat_completion_request: ChatCompletionRequest):
    conn = http.client.HTTPSConnection("u430182-ac52-13068849.cqa1.seetacloud.com")
    payload = json.dumps(chat_completion_request.dict())
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    for line in res:
        #     return StreamingResponse(content=generator, media_type="text/event-stream")
        yield line.decode('utf-8')


def completions(chat_completion_request: ChatCompletionRequest):
    conn = http.client.HTTPSConnection("u430182-ac52-13068849.cqa1.seetacloud.com")
    payload = json.dumps(chat_completion_request.dict())
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode('utf-8')
