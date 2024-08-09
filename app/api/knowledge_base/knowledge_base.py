import asyncio

from fastapi import Request, APIRouter, BackgroundTasks
from starlette.responses import StreamingResponse

from app.common.core.context import get_chat_visits_number
from app.common.utils.logging import get_logger
from app.data_cleansing1.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution

from app.services.knowledge_base_service import knowledge_base_generate, MyChatCompletionRequestModel, \
     get_reference_data

router = APIRouter(prefix="/knowledge_base")
logger = get_logger(__name__)


@router.post("/chat/completions", description="Create a chat completion.")
async def generate(request: MyChatCompletionRequestModel, raw_request: Request,background_tasks: BackgroundTasks):
    if get_chat_visits_number(is_completions=True):
        result = '''data: {"choices": [
            {
                "index": 0,
                "delta": {
                    "role": "2",
                    "content": "chatOutnumber"
                },
            }
        ]}'''
        return StreamingResponse(content=result,
                                 media_type="text/event-stream")
    return await knowledge_base_generate(request, raw_request, background_tasks)


@router.post("/cleansing", description="Cleansing the knowledge base.")
async def cleansing(manner_execution: MannerExecution):
    logger.info("Received cleansing request with args: %s", manner_execution)
    return await cleansing_manner_execution(manner_execution)


@router.get("/weaviateSearch")
def reference_data(text: str):
    return get_reference_data(text)
