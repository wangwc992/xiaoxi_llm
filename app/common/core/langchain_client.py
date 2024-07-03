from typing import List

from langchain_core.runnables.utils import Input
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langfuse.decorators import observe, langfuse_context

from app.common.core.config import settings
from app.common.core.context import request_context


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
            self.llm_with_tools = self.llm.bind_tools(tools=tools, tool_choice="required")

    def invoke(self, input: Input) -> str:
        result = self.llm.invoke(input)
        return result

    @observe()
    def invoke_tools(self, input: Input) -> dict:
        member_id = request_context.get("member_id", "1")
        langfuse_context.update_current_trace(
            user_id=member_id,
        )
        langfuse_handler = langfuse_context.get_current_langchain_handler()

        x = self.llm_with_tools.invoke(input=input, config={"callbacks": [langfuse_handler]})
        x = self.llm_with_tools.invoke(input=input)
        return x
