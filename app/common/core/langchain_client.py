from typing import List

from langchain_core.runnables.utils import Input
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.common.core.config import settings


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

    def __init__(self, tools: list = None, model="gpt-4o"):
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
