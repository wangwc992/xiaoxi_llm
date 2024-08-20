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
# 在源码/root/miniconda3/envs/agiclass/lib/python3.10/site-packages/vllm/engine/async_llm_engine.py
# 143：process_request_output 、184：abort_request
# 用到了这个函数
def get_chat_visits_number(is_completions: bool = False) -> bool:
    global chat_visits_number
    global chat_visits_number_max
    if is_completions:
        if chat_visits_number >= chat_visits_number_max:
            logger.error(f"请求次数超过上限{chat_visits_number_max}次，请稍后再试。")
            return True
        chat_visits_number += 1
    else:
        chat_visits_number -= 1
    logger.info(f"chat_visits_number {is_completions}: {chat_visits_number}")
    return False
