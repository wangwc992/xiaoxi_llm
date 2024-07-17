from app.database.weaviate.knowledge_base import KnowledgeBaseWeaviate
from app.database.weaviate.weaviate_client import WeaviateClient

knowledgeBase = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

# print(knowledgeBase.get_collection_config())
#
#
# knowledgeBase.weaviate_client.delete_collection_name(knowledgeBase.collections_name)
#
# knowledgeBase.create_collection()
#
# WeaviateClient.collections_list_all()
#
# knowledgeBase.weaviate_client.get_collection_config()


print(knowledgeBase.search_id('7b8721e4-cfd0-49e4-97e5-eb4696dabb10'))
