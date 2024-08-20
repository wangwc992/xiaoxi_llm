import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.collections.classes.grpc import HybridFusion

from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger

logger = get_logger(__name__)
client = weaviate.connect_to_local(grpc_port=50060, port=8079, skip_init_checks=True)
collections_name = 'Qwen_data_base'
ai_chat_log = 'Ai_chat_log'
collection = client.collections.get(collections_name)


def delete_many():
    while True:
        result = collection.data.delete_many(
            where=Filter.by_property("instruction").like("*"),
            # dry_run=True,
            # verbose=True
        )
        logger.info(f" result: {result}")

        if result.matches < 10000:
            break


query_bm25_database = 'platform_introduction'


def query_bm25(query_bm25: str):
    response = collection.query.bm25(
        query=query_bm25,
        query_properties=["db_name"],
        return_metadata=MetadataQuery(score=True),
        limit=40
    )

    for o in response.objects:
        print(o.properties)
        print(o.metadata.score)


database = 'notice_message'


def clear_all_data(database: str):
    '''清空Weaviate数据库中的所有数据'''
    while True:
        filters = (
            Filter.by_property("db_name").equal(database)
        )
        result = collection.data.delete_many(
            where=filters,
            # dry_run=True,
            # verbose=True
        )
        logger.info(f"Clear all data in Weaviate database: {database}, result: {result}")
        if result.matches < 10000:
            break


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
        query_properties=["instruction"],
        filters=Filter.by_property("database").equal("notice_message"),
        vector=Embedding.embed_query(query),
        return_metadata=MetadataQuery(score=True, explain_score=True),
        limit=limit,
    )
    response_list = []
    for o in response.objects:
        print(o.properties)
        print(o.metadata.score, o.metadata.explain_score)
    return response_list


def fetch_objects():
    response = collection.query.fetch_objects(
        filters=(
                Filter.by_property("db_id").equal("26487")
                & Filter.by_property("database").equal("t_knowledge_info")
        ),
        limit=5,
    )
    for o in response.objects:
        print(o.properties)


if __name__ == "__main__":
    delete_many()
    # delete_collection_name()
    # create_collection_name()
    #
    # query_bm25(query_bm25_database)
    # query_bm25("notice_message")

    # clear_all_data(database)
    # clear_all_data("platform_introduction")
    # query_bm25(query_bm25_database)

    # vec = Embedding.embed_query(hybrid_data_query)
    # response = hybrid_data(hybrid_data_query, vec)

    # search_hybrid("墨尔本大学 怎么样", 10)
    # fetch_objects()
    pass
