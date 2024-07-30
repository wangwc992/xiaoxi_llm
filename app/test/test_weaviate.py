import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.collections.classes.grpc import HybridFusion

from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger

logger = get_logger(__name__)
client = weaviate.connect_to_local(grpc_port=50060, port=8079, skip_init_checks=True)
collections_name = 'Qwen_data_base'
collection = client.collections.get(collections_name)


def delete_many():
    collection.data.delete_many(
        where=Filter.by_property("database").like("*"),
        # dry_run=True,
        # verbose=True
    )


query_bm25_database = 'platform_introduction'


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


database = 'zn_school_department_project'


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


if __name__ == "__main__":
    # delete_many()
    #
    # query_bm25(query_bm25_database)

    # clear_all_data(database)

    vec = Embedding.embed_query(hybrid_data_query)
    response = hybrid_data(hybrid_data_query, vec)

    pass
