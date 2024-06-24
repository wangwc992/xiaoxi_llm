import weaviate
from app.common.core.config import settings


class WeaviateClient:
    weaviate_dict = settings["weaviate"]
    client = weaviate.connect_to_local(
        host=weaviate_dict["host"],
        headers={"X-Huggingface-Api-Key": "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"}
    )
