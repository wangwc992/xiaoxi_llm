from fastapi import Request, APIRouter
from vllm.entrypoints.openai.protocol import ChatCompletionRequest
from app.api.openai.api_server import create_chat_completion

router = APIRouter(prefix="/chat")

@router.post("/v1/chat/completions", response_model=None)
async def generate(request: ChatCompletionRequest, raw_request: Request):
    """生成文本或流式返回生成的文本."""
    return await create_chat_completion(request, raw_request)
