import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.collections.classes.grpc import HybridFusion

from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.knowledge_base import KnowledgeBaseModel

logger = get_logger(__name__)
client = weaviate.connect_to_local(grpc_port=50060, port=8079, skip_init_checks=True)
collections_name = 'Qwen_data_base'
collection = client.collections.get(collections_name)


def delete_many():
    result = collection.data.delete_many(
        where=Filter.by_property("database").like("*"),
        # dry_run=True,
        # verbose=True
    )
    logger.info(f"Clear all data in Weaviate database: {database}, result: {result}")

query_bm25_database = 't_knowledge_info'


def query_bm25(query_bm25: str):
    response = collection.query.bm25(
        query=query_bm25,
        query_properties=["database"],
        return_metadata=MetadataQuery(score=True),
        limit=3
    )

    for o in response.objects:
        print(o.properties)
        print(o.metadata.score)


database = 't_knowledge_info'


def clear_all_data(database: str):
    '''清空Weaviate数据库中的所有数据'''
    result = collection.data.delete_many(
        where=Filter.by_property("database").equal(database)
    )
    logger.info(f"Clear all data in Weaviate database: {database}, result: {result}")


hybrid_data_query = '瑞克大学院校排名'


def hybrid_data(query, vec, limit=10):
    '''混合查询数据'''
    logger.info(f"Hybrid querying data in collection: {collections_name}")
    response = collection.query.hybrid(
        query=query,
        fusion_type=HybridFusion.RELATIVE_SCORE,
        query_properties=["instruction"],
        vector=vec,
        return_metadata=MetadataQuery(score=True, explain_score=True),
        limit=limit,
    )
    for o in response.objects:
        print(o.properties)
        print(o.metadata.score)
        print(o.metadata.explain_score)

    return response

def search_hybrid(query, limit):
    '''在Weaviate数据库中搜索数据'''
    logger.info(f"Searching Weaviate database with query: {query}")
    response = collection.query.hybrid(
        query=query,
        fusion_type=HybridFusion.RELATIVE_SCORE,
        # target_vector="instruction",
        vector=Embedding.embed_query(query),
        return_metadata=MetadataQuery(score=True, explain_score=True),
        limit=limit,
    )
    response_list = []
    for o in response.objects:
        properties = o.properties
        knowledge_base = ObjectFormatter.dict_to_object(properties, KnowledgeBaseModel)
        response_list.append(knowledge_base)
    return response_list
if __name__ == "__main__":
    delete_many()
    #
    # query_bm25(query_bm25_database)
    #
    # clear_all_data(database)
    # query_bm25(query_bm25_database)

    # vec = Embedding.embed_query(hybrid_data_query)
    # response = hybrid_data(hybrid_data_query, vec)

    # search_hybrid("墨尔本大学怎么样", 10)

    pass
