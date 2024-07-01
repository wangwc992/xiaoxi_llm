from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.common.core.config import settings


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

    def __init__(self, tools: list, model="gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0.7)  # 默认是gpt-3.5-turbo
        self.llm_with_tools = self.llm.bind_tools(tools=tools) | {
            "functions": JsonOutputToolsParser(),
            "text": StrOutputParser()
        }

    def invoke(self, prompt: str) -> str:
        result = self.llm.invoke(prompt)
        return result

    def invoke_tools(self, prompt: str) -> str:
        result = self.llm_with_tools.invoke(prompt)
        text = result.get("text")
        if text:
            return text

        functions =  str(result.get("functions"))
