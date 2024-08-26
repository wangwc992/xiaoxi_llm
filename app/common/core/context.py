import contextvars

from app.common.utils.logging import get_logger

# 用于创建线程本地的上下文变量，这些变量在不同的线程或异步任务之间是独立的
request_context = contextvars.ContextVar("request_context")

logger = get_logger(__name__)

# 用于记录chat接口的请求次数
chat_visits_number = 0
# chat接口的请求次数上限
chat_visits_number_max = 30


# 用于记录chat接口的请求次数，防止请求次数超过上限
# /root/miniconda3/envs/agiclass/lib/python3.10/site-packages/vllm/engine/llm_engine.py
#  1094：context.chat_visits_number = num_running_sys
def get_chat_visits_number() -> bool:
    global chat_visits_number
    global chat_visits_number_max
    if chat_visits_number >= chat_visits_number_max:
        logger.error(f"请求次数超过上限{chat_visits_number_max}次，请稍后再试。")
        return True
    logger.info(f"chat_visits_number : {chat_visits_number}")
    return False
