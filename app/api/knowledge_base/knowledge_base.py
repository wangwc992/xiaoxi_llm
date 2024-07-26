from fastapi import Request, APIRouter

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import manner_execution

from app.services.knowledge_base_service import knowledge_base_generate, MyChatCompletionRequestModel, engine_abort

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


@router.post("/v1/chat/completions", description="Create a chat completion.")
async def generate(request: MyChatCompletionRequestModel, raw_request: Request):
    return await knowledge_base_generate(request, raw_request)


@router.post("/v1/chat/abort", description="Abort the request with the given ID.")
async def abort(request_id: str):
    return await engine_abort(request_id)


@router.post("/v1/chat/cleansing", description="Cleansing the knowledge base.")
def abort(args: list):
    return manner_execution(args)
