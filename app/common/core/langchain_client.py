import asyncio
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List
from app.common.core.config import settings
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.usage.usage_lib import UsageContext
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
from vllm.entrypoints.openai.serving_completion import OpenAIServingCompletion

class Embedding:
    llm = settings["llm"]
    model_kwargs = {'device': llm["device"]}
    encode_kwargs = {'normalize_embeddings': False}

    embedding = HuggingFaceEmbeddings(
        model_name=llm['embedding_path'],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        return cls.embedding.embed_query(text)

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        return cls.embedding.embed_documents(texts)


class VllmClient:
    model = "/root/autodl-tmp/llm/Qwen2-7B-Instruct"
    engine_args = {
        "model": model,
    }

    engine_args = AsyncEngineArgs(**engine_args)
    engine = None
    model_config = None
    openai_serving_chat = None
    openai_serving_completion = None

    @classmethod
    async def initialize(cls):
        cls.engine = AsyncLLMEngine.from_engine_args(
            cls.engine_args, usage_context=UsageContext.API_SERVER)
        cls.model_config = await cls.engine.get_model_config()
        cls.openai_serving_chat = OpenAIServingChat(
            cls.engine, cls.model_config, cls.model, "assistant")
        cls.openai_serving_completion = OpenAIServingCompletion(
            cls.engine, cls.model_config, cls.model)

