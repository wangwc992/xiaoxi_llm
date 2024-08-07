import asyncio
import contextvars

from app.common.utils.logging import get_logger

# 用于创建线程本地的上下文变量，这些变量在不同的线程或异步任务之间是独立的
request_context = contextvars.ContextVar("request_context")

logger = get_logger(__name__)


lock = asyncio.Lock()
chat_visits_number = 0
chat_visits_number_max = 30


async def get_chat_visits_number(is_completions: bool = False) -> bool:
    global chat_visits_number
    global chat_visits_number_max
    logger.info(f"当前 chat_visits_number: {chat_visits_number},{is_completions}")
    async with lock:
        if is_completions:
            if chat_visits_number >= chat_visits_number_max:
                logger.error(f"请求次数超过上限{chat_visits_number_max}次，请稍后再试。")
                return True
            chat_visits_number += 1
        else:
            chat_visits_number -= 1
    return False


