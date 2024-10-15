from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from sentence_transformers.util import cos_sim
from app.common.core.config import settings


class Embedding:
    """ HuggingFace Embedding,文本向量化  """
    embedding_arg = settings["embedding"]
    # 获取GPU数量,使用最后一个GPU，加载模型，防止内存溢出
    device_number = '4'
    device = f"cuda:{device_number}" if device_number >= 0 else "cpu"
    model_kwargs = {'device': device}
    encode_kwargs = {'normalize_embeddings': False}
    embedding = HuggingFaceEmbeddings(
        model_name=embedding_arg['embedding_path'],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        """ Embed a single query text """
        return cls.embedding.embed_query(text)

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        """ Embed a list of document texts """
        return cls.embedding.embed_documents(texts)

    @staticmethod
    def similarity(query: str, sentence_list: list):
        query_vec = Embedding.embed_query(query)
        doc_vecs = Embedding.embed_documents(sentence_list)
        similarity = cos_sim(query_vec, doc_vecs)
        similarity_list = similarity.tolist()[0]
        return similarity_list
