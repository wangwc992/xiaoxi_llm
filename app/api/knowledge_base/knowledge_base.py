import asyncio
import traceback
from fastapi import Request, APIRouter, BackgroundTasks
from starlette.responses import StreamingResponse

from app.api.openai.api_server import scheduler
from app.common.core.context import get_chat_visits_number
from app.common.utils.logging import get_logger
from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate
from app.middleware.exception import ChatSuspendException

from app.services.knowledge_base_service import (knowledge_base_generate, MyChatCompletionRequestModel,
                                                 knowledge_base_networked_generate)
from app.test.google import reference_networked_rag

router = APIRouter(prefix="/knowledge_base/chat")
logger = get_logger(__name__)


@router.post("/completions", description="Create a chat completion.")
async def generate(request: MyChatCompletionRequestModel, raw_request: Request, background_tasks: BackgroundTasks):
    '''方法描述
    生成对话完成

    参数:
    request: MyChatCompletionRequestModel   请求体
    raw_request: Request    请求，用于获取请求头，请求体等信息，这用于监听请求是否中断
    background_tasks: BackgroundTasks   后台任务，用于异步处理
    返回:
    StreamingResponse    流响应，返回统一格式的数据

    例子:
    {
      "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
      "query": "你好",
      "stream": true
    }
    role: 1 为用户，2 chat并发数过多，3 敏感词、4 为程序异常
    '''
    await scheduler()
    # 判断是否超过最大并发数
    if get_chat_visits_number():
        result = '''data: {"choices": [ { "index": 0, "delta": { "role": "2", "content": "chat线程数量超了" }} ]}'''
        return StreamingResponse(content=result, media_type="text/event-stream")

    try:
        return await knowledge_base_generate(request, raw_request, background_tasks)
    except Exception as e:
        # 捕获异常并处理
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        logger.error(f"Error in /chat/completions: {error_message}")
        raise ChatSuspendException("当前对话已暂停，请稍后再试。")


@router.get("/weaviateSearch1")
async def reference_data1(query: str):
    return await knowledge_base_networked_generate(query)


# 清空聊天记录
@router.delete("/clear", description="Clear all chat data.")
async def clear_chat_data():
    ai_chat_log_weaviate.clear_all_data("instruction", "*")
