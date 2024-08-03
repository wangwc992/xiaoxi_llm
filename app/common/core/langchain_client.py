import subprocess

from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

from sentence_transformers import SentenceTransformer

from app.common.core.config import settings


class Embedding:
    embedding_arg = settings["embedding"]
    model_kwargs = {'device': embedding_arg["device"]}
    encode_kwargs = {'normalize_embeddings': False}
    print(f"Embedding: {embedding_arg['embedding_path']}，device: {embedding_arg['device']}，normalize_embeddings: {False}")
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


def get_gpu_count():
    result = subprocess.run(['nvidia-smi', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        # 按行分割输出并计算行数，行数即为 GPU 的数量
        gpu_lines = result.stdout.strip().split('\n')
        return len(gpu_lines)
    else:
        print(f"Error executing nvidia-smi: {result.stderr}")
        return 0
