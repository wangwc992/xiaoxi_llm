import asyncio
import datetime
from typing import Optional, Union

from weaviate.classes.query import Filter
from weaviate.collections.classes.config import DataType, Configure
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.classes.config import Property
from langchain_core.pydantic_v1 import BaseModel, Field

from app.common.utils.jieba_utils import jieba_tool
from app.common.utils.logging import get_logger
from app.common.utils.object_utils import ObjectFormatter
from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_mysql_weaviate import select_ai_mysql_weaviate, \
    insert_ai_mysql_weaviate
from app.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding

logger = get_logger(__name__)


class KnowledgeBaseModel(BaseModel):
    db_id: Optional[str] = Field(None, description="数据库的id")
    db_name: str = Field(None, description="数据库")
    instruction: str = Field(None, description="描述")
    input: str = Field(None, description="输入")
    output: str = Field(None, description="输出")
    keyword: str = Field(None, description="关键词")
    file_content: str = Field(None, description="文件信息")
    link: str = Field(None, description="参考数据的link")


class KnowledgeBaseWeaviate(WeaviateClient):
    collections_name = "Qwen_data_base"
    properties = [
        Property(name='db_id', data_type=DataType.TEXT, description='数据库的id'),
        Property(name='db_name', data_type=DataType.TEXT, description='数据库'),
        Property(name='instruction', data_type=DataType.TEXT, description='描述'),
        Property(name='input', data_type=DataType.TEXT, description='输入'),
        Property(name='output', data_type=DataType.TEXT, description='输出'),
        Property(name='keyword', data_type=DataType.TEXT, description='关键词'),
        Property(name='file_content', data_type=DataType.TEXT, description='文件信息'),
        Property(name='link', data_type=DataType.TEXT, description='参考数据的link')
    ]

    def basth_insert_data(self, properties_list: list, vecs: list):
        '''批量插入数据'''
        logger.info(f"Batch inserting data into collection: {self.collections_name}")
        uuid_list = []
        with self.collection.batch.dynamic() as batch:
            for properties in properties_list:
                keyword = jieba_tool.cut_for_search(properties["instruction"])
                properties["keyword"] = ' '.join(keyword)
                uuid = batch.add_object(properties=properties, vector=vecs.pop(0))  # 从vecs中取出一个向量
                uuid_list.append(uuid)
        return uuid_list

    def search_id_or_database(self, db_id: Optional[str], database: Optional[str], limit: int = 10):
        '''根据id搜索Weaviate数据库中的数据'''
        if db_id:
            filters = (
                    Filter.by_property("db_id").equal(db_id)
                    & Filter.by_property("db_name").equal(database)
            )
        else:
            filters = Filter.by_property("db_name").equal(database)
        response = self.collection.query.fetch_objects(
            filters=filters,
            limit=limit,
        )
        response_list = []
        for o in response.objects:
            properties = o.properties
            knowledge_base = ObjectFormatter.dict_to_object(properties, KnowledgeBaseModel)
            response_list.append(knowledge_base)

        return response_list

    async def search_hybrid(self, query, limit, filters=None):
        '''在Weaviate数据库中搜索数据'''
        query_keyword = ' '.join(jieba_tool.cut_for_search(query))
        time_now = datetime.datetime.now().strftime('%Y-%m-%d')
        query_keyword = f"现在时间{time_now} {query_keyword} "
        response = self.collection.query.hybrid(
            query=query_keyword,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            filters=filters,
            query_properties=["output", "keyword^2"],
            vector=Embedding.embed_query(query),
            return_metadata=MetadataQuery(score=True, explain_score=True),
            alpha=0.5,
            limit=limit,
        )
        response_list = []
        max_explain_score = float('-inf')  # 设置为负无穷大，以便比较

        # 遍历 response.objects 以找到最大 explain_score 的对象
        for o in response.objects:
            if o.metadata.score > max_explain_score:
                max_explain_score = o.metadata.score
        # 判断max_explain_score是大于0.8的还是大于0.5的
        distance = 0.8 if max_explain_score >= 0.8 else 0.5 if max_explain_score >= 0.5 else 0

        for o in response.objects:
            properties = o.properties
            if distance > o.metadata.score and o.properties.get('db_name') == "t_knowledge_info":
                continue
            knowledge_base = ObjectFormatter.dict_to_object(properties, KnowledgeBaseModel)
            response_list.append(knowledge_base)

        return response_list

    async def search_hybrid_or(self, query, limit, alpha=0.5):
        '''在Weaviate数据库中搜索数据'''
        filters = None
        for key, values in ai_knowledge_base_keyword_dict.items():
            if any(v in query for v in values):
                filters = Filter.by_property("db_name").equal(key)
                break
        query_keyword = ' '.join(jieba_tool.cut_for_search(query))
        response = self.collection.query.hybrid(
            query=query_keyword,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            filters=filters,
            query_properties=["output", "keyword^2"],
            vector=Embedding.embed_query(query),
            return_metadata=MetadataQuery(score=True, explain_score=True),
            alpha=alpha,
            limit=limit,
        )
        response_list = []
        for o in response.objects:
            properties = o.properties
            response_list.append({"explain_score": o.metadata.explain_score,
                                  "content": properties['instruction'] + "\n" + properties['keyword'],
                                  "score": o.metadata.score})
            print(f"score: {o.metadata.score},db_name: {properties['db_name']}")
        return response_list

    def delete_data_by_id(self, db_id: str, db_name: str):
        '''根据id删除Weaviate数据库中的数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("db_id").equal(db_id) & Filter.by_property("db_name").equal(db_name)
        )
        return {"message": f"{db_id} data deleted successfully in Weaviate db_name: {db_name}"}

    def delete_by_database(self, db_name: str):
        logger.info(f"Deleting data in Weaviate db_name: {db_name}")
        '''根据database删除Weaviate数据库中的数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("db_name").equal(db_name)
        )


knowledge_base_weaviate = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

if __name__ == '__main__':
    # knowledgeBase = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)
    # WeaviateClient.delete_collection_name(knowledgeBase.collections_name)
    # knowledgeBase.create_collection(knowledgeBase.properties)
    # while 循环获取输入
    # while True:
    #     input_str = input("请输入：")
    #     if input_str == "exit":
    #         break
    #     else:
    #         asyncio.run(knowledge_base_weaviate.search_hybrid(input_str, 10))
    # knowledge_base_weaviate.clear_all_data("db_name", "notice_message")
    # query = "现在时间2024-08-22,悉尼大学最近有减免申请费的活动吗？"
    # vector = Embedding.embed_query(query)
    # response = knowledge_base_weaviate.hybrid_data(query, vector, 20)
    # for o in response.objects:
    #     properties = o.properties
    #     print( o.metadata.score, properties['instruction'])
    pass
