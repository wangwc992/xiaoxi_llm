from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List

from app.common.core.config import settings

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.usage.usage_lib import UsageContext


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
    # model = "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4"
    model = "/root/autodl-tmp/llm/Qwen2-72B-Instruct"
    tensor_parallel_size = 8
    # quantization = "gptq"

    engine_args = {
        "model": model,
        "tensor_parallel_size": tensor_parallel_size,
        "max_model_len": 26000
        # "quantization": "gptq"
    }

    engine_args = AsyncEngineArgs(**engine_args)
    engine = AsyncLLMEngine.from_engine_args(
        engine_args, usage_context=UsageContext.API_SERVER)
