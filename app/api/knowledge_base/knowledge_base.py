from fastapi import Request, APIRouter
from app.common.utils.logging import get_logger

from app.services.knowledge_base_service import knowledge_base_generate, MyChatCompletionRequestModel

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


@router.post("/v1/chat/completions", response_model=None)
async def generate(request: MyChatCompletionRequestModel, raw_request: Request):
    return await knowledge_base_generate(request, raw_request)
