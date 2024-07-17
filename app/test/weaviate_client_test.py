from app.database.weaviate.knowledge_base import KnowledgeBaseWeaviate
from app.database.weaviate.weaviate_client import WeaviateClient

knowledgeBase = KnowledgeBaseWeaviate()

knowledgeBase.create_collection()

WeaviateClient.collections_list_all()
