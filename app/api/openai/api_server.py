import asyncio
import tiktoken
from typing import Set, Optional

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, Response, StreamingResponse
from vllm.entrypoints.openai.protocol import (ChatCompletionRequest,
                                              ChatCompletionResponse,
                                              CompletionRequest,
                                              EmbeddingRequest, ErrorResponse,
                                              EmbeddingResponse, EmbeddingResponseData)
from vllm.entrypoints.openai.serving_embedding import OpenAIServingEmbedding
from vllm.logger import init_logger
from vllm.version import __version__ as VLLM_VERSION

from app.common.core.langchain_client import Embedding, get_openai_serving_chat, get_openai_serving_completion

TIMEOUT_KEEP_ALIVE = 5  # seconds

openai_serving_embedding: OpenAIServingEmbedding
logger = init_logger('vllm.entrypoints.openai.api_server')
# 获取编码器
token_encoder = tiktoken.get_encoding("cl100k_base")
_running_tasks: Set[asyncio.Task] = set()

router = APIRouter()


@router.get("/health")
async def health() -> Response:
    """Health check."""
    openai_serving_chat = get_openai_serving_chat()
    await openai_serving_chat.engine.check_health()
    return Response(status_code=200)


@router.get("/v1/models")
async def show_available_models():
    openai_serving_chat = get_openai_serving_chat()
    models = await openai_serving_chat.show_available_models()
    return JSONResponse(content=models.model_dump())


@router.get("/version")
async def show_version():
    ver = {"version": VLLM_VERSION}
    return JSONResponse(content=ver)


@router.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest,
                                 raw_request:  Optional[Request] = None):
    openai_serving_chat = get_openai_serving_chat()
    generator = await openai_serving_chat.create_chat_completion(
        request, raw_request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(content=generator.model_dump(),
                            status_code=generator.code)
    if request.stream:
        return StreamingResponse(content=generator,
                                 media_type="text/event-stream")
    else:
        assert isinstance(generator, ChatCompletionResponse)
        return JSONResponse(content=generator.model_dump())


@router.post("/v1/completions")
async def create_completion(request: CompletionRequest, raw_request: Request):
    openai_serving_completion = get_openai_serving_completion()
    generator = await openai_serving_completion.create_completion(
        request, raw_request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(content=generator.model_dump(),
                            status_code=generator.code)
    if request.stream:
        return StreamingResponse(content=generator,
                                 media_type="text/event-stream")
    else:
        return JSONResponse(content=generator.model_dump())


@router.post("/v1/embeddings")
async def create_embedding(request: EmbeddingRequest, raw_request: Request):
    # generator = await openai_serving_embedding.create_embedding(
    #     request, raw_request)
    # 打印request
    print(request)
    if isinstance(request.input, list) and all(isinstance(token, int) for token in request.input):
        # 对编码结果进行解码
        decoded_text = token_encoder.decode(request.input)
        request.input = [decoded_text]

    generator = Embedding.embed_documents(request.input)

    list1 = []
    for g in generator:
        s = EmbeddingResponseData(input=request.input, embedding=g, index=0)
        list1.append(s)
    content = EmbeddingResponse(data=list1, object="list", model="HuggingFaceEmbeddings",
                                usage={"prompt_tokens": 8, "total_tokens": 8})

    return JSONResponse(content=content.dict())
