from fastapi import Request, APIRouter

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution

from app.services.knowledge_base_service import knowledge_base_generate, MyChatCompletionRequestModel, engine_abort

router = APIRouter(prefix="/knowledge_base")
logger = get_logger(__name__)

chat_visits_number = 0
chat_visits_number_max = 30


async def get_chat_visits_number(is_completions: bool = False) -> bool:
    global chat_visits_number
    global chat_visits_number_max

    if is_completions:
        if chat_visits_number >= chat_visits_number_max:
            logger.error(f"请求次数超过上限{chat_visits_number_max}次，请稍后再试。")
            return True
        chat_visits_number += 1
    else:
        chat_visits_number -= 1
    return False


@router.post("/chat/completions", description="Create a chat completion.")
async def generate(request: MyChatCompletionRequestModel, raw_request: Request):
    return await knowledge_base_generate(request, raw_request)


@router.get("/chat/abort", description="Abort the request with the given ID.")
async def abort(request_id: str):
    return await engine_abort(request_id)


@router.post("/cleansing", description="Cleansing the knowledge base.")
async def cleansing(manner_execution: MannerExecution):
    logger.info("Received cleansing request with args: %s", manner_execution)
    return await cleansing_manner_execution(manner_execution)
