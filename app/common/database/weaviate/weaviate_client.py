import weaviate
from app.common.core.config import settings


class WeaviateClient:
    weaviate_dict = settings["weaviate"]
    client = weaviate.connect_to_local(
        host=weaviate_dict["host"],
        port=weaviate_dict["port"],
        headers={"X-Huggingface-Api-Key": "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"}
    )
