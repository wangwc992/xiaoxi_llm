import weaviate
from app.common.core.config import settings


class WeaviateClient:
    weaviate_dict = settings["weaviate"]
    client = weaviate.connect_to_local(
        host=weaviate_dict["host"],
        port=weaviate_dict["port"],
        headers={"X-Huggingface-Api-Key": "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"}
    )
    # client = weaviate.WeaviateClient(
    #     embedded_options=EmbeddedOptions(
    #         additional_env_vars={
    #             # "ENABLE_MODULES": "text2vec-transformers",
    #             # "TRANSFORMERS_INFERENCE_API": 'http://127.0.0.1:8090',
    #             "BACKUP_FILESYSTEM_PATH": "/root/autodl-tmp/database/weaviate"
    #         }
    #     )
    #     # Add additional options here. For syntax, see the Python client documentation.
    # )
    # client.connect()
