import subprocess

import torch
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

from app.common.core.config import settings
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.usage.usage_lib import UsageContext
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
from vllm.entrypoints.openai.serving_completion import OpenAIServingCompletion


class Embedding:
    embedding_arg = settings["embedding"]
    model_kwargs = {'device': embedding_arg["device"]}
    encode_kwargs = {'normalize_embeddings': False}

    embedding = HuggingFaceEmbeddings(
        model_name=embedding_arg['embedding_path'],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        return cls.embedding.embed_query(text)

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        return cls.embedding.embed_documents(texts)

def get_gpu_count():
    result = subprocess.run(['nvidia-smi', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        # 按行分割输出并计算行数，行数即为 GPU 的数量
        gpu_lines = result.stdout.strip().split('\n')
        return len(gpu_lines)
    else:
        print(f"Error executing nvidia-smi: {result.stderr}")
        return 0

class VllmClient:
    # 通过 nvidia-smi -L 指令获取 GPU 个数
    # 执行 nvidia-smi -L 命令并捕获输出
    vllm = settings.get('vllm')
    gpu_count = get_gpu_count()
    if gpu_count >= 4:
        engine_args = vllm.get('qwen2_72B_instruct_gptq_int4')
    else:
        engine_args = vllm.get('qwen2_7B_instruct')

    async_engineArgs = AsyncEngineArgs(**engine_args)
    engine = AsyncLLMEngine.from_engine_args(async_engineArgs, usage_context=UsageContext.API_SERVER)
    model = engine_args.get('model')
    model_config = None
    openai_serving_chat = None
    openai_serving_completion = None

    @classmethod
    async def initialize(cls):
        cls.model_config = await cls.engine.get_model_config()
        cls.openai_serving_chat = OpenAIServingChat(cls.engine, cls.model_config, cls.model, "assistant")
        cls.openai_serving_completion = OpenAIServingCompletion(cls.engine, cls.model_config, cls.model, None)

    @classmethod
    def get_openai_serving_chat(cls):
        return cls.openai_serving_chat

    @classmethod
    def get_openai_serving_completion(cls):
        return cls.openai_serving_completion


# Ensure async initialization is called properly in the main application
async def initialize_vllm_client():
    await VllmClient.initialize()


# These need to be awaited in an async context
def get_openai_serving_chat():
    before = torch.cuda.memory_allocated()
    # Model inference or other operations
    v = VllmClient.get_openai_serving_chat()
    after = torch.cuda.memory_allocated()
    print(f'get_openai_serving_chat Memory usage increased by: {after - before}')

    return v


def get_openai_serving_completion():
    return VllmClient.get_openai_serving_completion()

