import weaviate
from weaviate.embedded import EmbeddedOptions
import os

client = weaviate.WeaviateClient(
    embedded_options=EmbeddedOptions(
        additional_env_vars={
            "ENABLE_MODULES": "backup-filesystem,text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai",
            "BACKUP_FILESYSTEM_PATH": "/root/autodl-tmp/database/weaviate"
        }
    )
    # Add additional options here. For syntax, see the Python client documentation.
)

# Run your client code in a context manager or call client.close()
# before exiting the client to avoid connection errors.
client.connect()  # Call `connect()` to connect to the server when you use `WeaviateClient`

# Add your client code here.