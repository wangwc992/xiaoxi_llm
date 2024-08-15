import os
from dotenv import load_dotenv, find_dotenv
from fastapi import Request
from fastapi.responses import Response
from starlette.responses import StreamingResponse, JSONResponse
from app.common.utils.logging import get_logger
from app.data.dictionaries import sensitive_words

logger = get_logger(__name__)

# 只在模块加载时加载一次环境变量
load_dotenv(find_dotenv())


async def log_request_body(request: Request, call_next):
    # 读取请求体
    body = await request.body()
    if request.method == "POST":
        logger.info(f"POST Request Body: {body.decode('utf-8')}")
    else:
        # GET请求打印参数
        logger.info(f"GET Request Params: {request.query_params}")
    # 将请求体重新放入request中以供后续中间件使用
    request._body = body
    response = await call_next(request)
    return response


async def sensitive_word_filter(request: Request, call_next):
    # 获取请求体内容
    body = request._body if hasattr(request, '_body') else await request.body()
    body_text = body.decode("utf-8")

    # 检查是否包含敏感词
    for word in sensitive_words:
        if word in body_text:
            result = f'''data: {{"choices": [ {{"index": 0, "delta": {{"role": "3", "content": "您的问题涉及敏感内容 {word}，小希无法回答呦，请换个话题吧。" }}}}]}}'''
            return StreamingResponse(content=result, media_type="text/event-stream")

    # 继续处理请求
    response = await call_next(request)
    return response


async def authentication(request: Request, call_next):
    VLLM_API_KEY = os.getenv("VLLM_API_KEY")
    if VLLM_API_KEY:
        token = request.headers.get("Authorization")
        if request.method == "OPTIONS":
            return await call_next(request)
        # 检查 Authorization 头部是否与预期的 token 一致
        if token != f"Bearer {VLLM_API_KEY}":
            return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    response = await call_next(request)
    return response
