from fastapi import Request, APIRouter, Response
from vllm.sampling_params import SamplingParams
from vllm.entrypoints.openai.protocol import ChatCompletionRequest

from app.api.openai.api_server import create_chat_completion

router = (APIRouter(prefix="/chat"))


@router.get("/v1/chat/completions")
async def generate(request: ChatCompletionRequest,
                   raw_request: Request):
    """生成文本或流式返回生成的文本."""
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    stream = request_dict.pop("stream", False)
    sampling_params = SamplingParams(**request_dict)

    return create_chat_completion(request, raw_request)
