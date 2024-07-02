from typing import List

from langchain_core.runnables.utils import Input
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.common.core.config import settings
from app.tools.tools import exec_action, Action


# from vllm.engine.arg_utils import AsyncEngineArgs
# from vllm.engine.async_llm_engine import AsyncLLMEngine
# from vllm.usage.usage_lib import UsageContext

# class VllmClient:
#     model = "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4"
#     # model = "/root/autodl-tmp/llm/Qwen2-7B-Instruct"
#     tensor_parallel_size = 4
#     quantization = "gptq"
#
#     engine_args = {
#         "model": model,
#         "tensor_parallel_size": tensor_parallel_size,
#         "quantization": "gptq"
#     }
#
#     engine_args = AsyncEngineArgs(**engine_args)
#     engine = AsyncLLMEngine.from_engine_args(
#         engine_args, usage_context=UsageContext.API_SERVER)

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


class LangChain:

    def __init__(self, tools: list = None, model="gpt-3.5-turbo"):
        self.tools = tools
        self.llm = ChatOpenAI(model=model, temperature=0.7)  # 默认是gpt-3.5-turbo
        if tools:
            self.llm_with_tools = self.llm.bind_tools(tools=tools)

    def invoke(self, input: Input) -> str:
        result = self.llm.invoke(input)
        return result

    def invoke_tools(self, input: Input) -> dict:
        x = self.llm_with_tools.invoke(input)
        return x

