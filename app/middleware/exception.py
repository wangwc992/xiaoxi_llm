import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse


# 自定义全局异常处理器
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器遇到一个错误，请稍后重试。"}
    )


# After
class ChatSuspendException(Exception):
    def __init__(self, message: str = "chat generation is suspended"):
        self.message = message
        super().__init__(self.message)

    # 自定义的 chat_suspend 异常处理器


def chat_suspend_exception_handler(request: Request, exc: ChatSuspendException):
    # result = f'data: {{"choices": [{{"index": 0, "delta": {{"role": "4", "content": "{exc.message}"}}}}]}}'
    result = '''data: { "code": "500", "content": "服务器异常"}'''
    return StreamingResponse(content=result, media_type="text/event-stream")
