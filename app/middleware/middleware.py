# middleware.py
import os

from dotenv import load_dotenv, find_dotenv
from fastapi import Request
from fastapi.responses import Response
from starlette.responses import StreamingResponse, JSONResponse

from app.common.utils.logging import get_logger
from app.data.dictionaries import sensitive_words

logger = get_logger(__name__)


async def log_request_body(request: Request, call_next):
    if request.method == "POST":
        body = await request.json()
        logger.info(f"POST Request Body: {body}")
    else:
        # get请求打印参数
        logger.info(f"GET Request Body: {request.query_params}")
    response = await call_next(request)
    return response


async def sensitive_word_filter(request: Request, call_next):
    # 获取请求的body内容
    body = await request.body()
    body_text = body.decode("utf-8")

    # 检查是否包含敏感词
    for word in sensitive_words:
        if word in body_text:
            result = f'''data: {{"choices": [ {{ "index": 0, "delta": {{ "role": "3", "content": "您的问题涉及敏感内容 {word}，小希无法回答呦，请换个话题吧。" }},  }} ]}}'''
            return StreamingResponse(content=result,
                                     media_type="text/event-stream")
    # 如果不包含敏感词，继续处理请求
    response = await call_next(request)
    return response


async def authentication(request: Request, call_next):
    _ = load_dotenv(find_dotenv())
    # 加载.env文件
    load_dotenv(".env")
    VLLM_API_KEY = os.getenv("VLLM_API_KEY")
    if VLLM_API_KEY:
        token = request.headers.get("Authorization")
        if request.method == "OPTIONS":
            return await call_next(request)
        if not request.url.path.startswith(f"{root_path}/v1"):
            return await call_next(request)
        if request.headers.get("Authorization") != "Bearer " + token:
            return JSONResponse(content={"error": "Unauthorized"},
                                status_code=401)
        return await call_next(request)