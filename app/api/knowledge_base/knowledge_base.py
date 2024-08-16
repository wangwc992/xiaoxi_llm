import traceback
from fastapi import Request, APIRouter, BackgroundTasks
from starlette.responses import StreamingResponse

from app.common.core.context import get_chat_visits_number
from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution
from app.middleware.exception import ChatSuspendException

from app.services.knowledge_base_service import (knowledge_base_generate, MyChatCompletionRequestModel)

router = APIRouter(prefix="/knowledge_base")
logger = get_logger(__name__)


@router.post("/chat/completions", description="Create a chat completion.")
async def generate(request: MyChatCompletionRequestModel, raw_request: Request, background_tasks: BackgroundTasks):
    '''方法描述
    生成对话完成

    参数:
    request: MyChatCompletionRequestModel   请求体
    raw_request: Request    请求
    background_tasks: BackgroundTasks   后台任务
    返回:
    StreamingResponse    流响应

    例子:
    {
      "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
      "query": "你好",
      "stream": true
    }
    role: 1 为用户，2 chat并发数过多，3 敏感词
    '''
    # 判断是否超过最大并发数
    if get_chat_visits_number(is_completions=True):
        result = '''data: {"choices": [ { "index": 0, "delta": { "role": "2", "content": "当前提问人数过多，请您在10s后再提问~\n当前提问人数过多，请您在10s后再提问~ 来试试知识库？常见问题、文件资料、精选案例这儿都有👋" }} ]}'''
        return StreamingResponse(content=result, media_type="text/event-stream")

    try:
        return await knowledge_base_generate(request, raw_request, background_tasks)
    except Exception as e:
        # 捕获异常并处理
        error_message = ''.join(traceback.format_exception(None, e, e.__traceback__))
        logger.error(f"Error in /chat/completions: {error_message}")
        raise ChatSuspendException("当前对话已暂停，请稍后再试。")
