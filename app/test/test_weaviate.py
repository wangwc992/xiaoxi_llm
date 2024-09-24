import os
import warnings

import openpyxl
from openpyxl.workbook import Workbook

warnings.filterwarnings("ignore", category=DeprecationWarning)

import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.collections.classes.grpc import HybridFusion

from app.common.core.config import settings
from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate

weaviate_client = settings.get("weaviate")

logger = get_logger(__name__)
client = weaviate.connect_to_local(grpc_port=weaviate_client.get('grpc_port'), port=weaviate_client.get('port'),host=weaviate_client.get('host'), skip_init_checks=True)
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
        filters=Filter.by_property("db_name").equal("notice_message"),
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
        # filters=(
        #         Filter.by_property("db_id").equal("26487")
        #         & Filter.by_property("database").equal("t_knowledge_info")
        # ),
        limit=5,
        offset=2
    )
    for o in response.objects:
        # {'file_content': None, 'link': '{"object":"json","type": 1,"title":"本科雅思要求多少分？","id":6589,"attachment_url":""}', 'db_id': '6589', 'db_name': 't_knowledge_info', 'instruction': '英国其他其他的以下问题: 本科雅思要求多少分？', 'input': None, 'output': '平台顾问于2023-07-21 15:15:41回复内容如下：一般是总分6.0，小分5.5', 'keyword': '英国 本科 雅思'}
        # 将instruction和output的数据添加到excel文件中中
        print(o.properties)




if __name__ == "__main__":
    # delete_many()
    # delete_collection_name()
    # ai_chat_log_weaviate.delete_collection_name(ai_chat_log_weaviate.collections_name)
    # ai_chat_log_weaviate.create_collection(ai_chat_log_weaviate.properties)
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
    # 创建或加载工作簿
    def clean_string(value: str) -> str:
        """清理字符串中的非法字符。"""
        return ''.join(c for c in value if c.isprintable())


    # 创建或加载工作簿
    file_path = "C:\\Users\\wishfyc\\Desktop\\rag.xlsx"
    if not os.path.exists(file_path):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Instruction", "Output"])  # 添加标题
    else:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

    for i in range(1, 10):
        response = collection.query.fetch_objects(
            limit=100,
            offset=i
        )
        for o in response.objects:
            properties = o.properties
            instruction = clean_string(properties.get('instruction', ''))
            output = clean_string(properties.get('output', ''))
            sheet.append([instruction, output])  # 添加行

        # 保存工作簿
        workbook.save(file_path)
        print(f"第{i}页数据已保存。")
