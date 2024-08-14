from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

from app.common.core.config import settings


class Embedding:
    embedding_arg = settings["embedding"]
    device_number = settings.get('gpu_count', 0) - 1
    # "cuda:4"
    device = f"cuda:{device_number}" if device_number >= 0 else "cpu"
    model_kwargs = {'device': device}
    encode_kwargs = {'normalize_embeddings': False}
    embedding = HuggingFaceEmbeddings(
        model_name=embedding_arg['embedding_path'],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # model = SentenceTransformer(embedding_arg['embedding_path'])

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        return cls.embedding.embed_query(text)
        # return cls.model.encode(text)[0].tolist()

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        return cls.embedding.embed_documents(texts)
        # return cls.model.encode(text).tolist()
