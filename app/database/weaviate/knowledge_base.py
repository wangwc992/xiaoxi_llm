import asyncio
from typing import Optional

from weaviate.classes.query import Filter
from weaviate.collections.classes.config import DataType, Configure
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.classes.config import Property
from langchain_core.pydantic_v1 import BaseModel, Field

from app.common.utils.jieba_utils import jieba_tool
from app.common.utils.logging import get_logger
from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding

logger = get_logger(__name__)


class KnowledgeBaseModel(BaseModel):
    db_id: Optional[str] = Field(None, description="数据库的id")
    database: Optional[str] = Field(None, description="数据库")
    instruction: Optional[str] = Field(None, description="描述")
    input: Optional[str] = Field(None, description="输入")
    output: Optional[str] = Field(None, description="关键词")
    keyword: Optional[str] = Field(None, description="状态")
    file_info: Optional[str] = Field(None, description="文件信息")
    link: Optional[dict] = Field(None, description="参考数据的link")


class KnowledgeBaseWeaviate(WeaviateClient):
    collections_name = "Qwen_data_base"
    properties = [
        Property(name='database', data_type=DataType.TEXT, description='数据库'),
        Property(name='db_id', data_type=DataType.TEXT, description='数据库的id'),
        Property(name='instruction', data_type=DataType.TEXT, description='描述'),
        Property(name='input', data_type=DataType.TEXT, description='输入'),
        Property(name='output', data_type=DataType.TEXT, description='输出'),
        Property(name='keyword', data_type=DataType.TEXT, description='关键词'),
        Property(name='file_info', data_type=DataType.TEXT, description='文件信息'),
        Property(name='link', data_type=DataType.TEXT, description='参考数据的link')
    ]

    def clear_all_data(self, database: str):
        while True:
            filters = (
                Filter.by_property("database").like(f"{database}")
            )
            result = self.collection.data.delete_many(
                where=filters,
                # dry_run=True,
                # verbose=True
            )
            logger.info(f"Clear all data in Weaviate database: {database}, result: {result}")
            if result.matches < 10000:
                break
        return {"message": f"Clear all data in Weaviate database: {database}"}  # 返回清空数据的信息

    async def search_hybrid(self, query, limit, filters=None):
        '''在Weaviate数据库中搜索数据'''
        query_keyword = ' '.join(jieba_tool.cut_for_search(query))
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
        for o in response.objects:
            properties = o.properties
            knowledge_base = ObjectFormatter.dict_to_object(properties, KnowledgeBaseModel)
            response_list.append(knowledge_base)

        return response_list

    async def search_hybrid_or(self, query, limit, alpha=0.5):
        '''在Weaviate数据库中搜索数据'''
        query_keyword = ' '.join(jieba_tool.cut_for_search(query))
        response = self.collection.query.hybrid(
            query=query_keyword,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            query_properties=["output", "keyword^2"],
            vector=Embedding.embed_query(query),
            return_metadata=MetadataQuery(score=True, explain_score=True),
            alpha=alpha,
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
            if distance > o.metadata.score and o.properties.get('database') == 't_knowledge_info':
                continue
            response_list.append({"explain_score": o.metadata.explain_score,
                                  "content": properties['instruction'] + "\n" + properties['keyword'],
                                  "score": o.metadata.score})
            print(f"score: {o.metadata.score},database: {properties['database']}")
        return response_list

    def delete_data_by_id(self, id: str, database: str):
        '''根据id删除Weaviate数据库中的数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("db_id").equal(id) & Filter.by_property("database").equal(database)
        )
        return {"message": f"{id} data deleted successfully in Weaviate database: {database}"}

    def delete_by_database(self, database: str):
        logger.info(f"Deleting data in Weaviate database: {database}")
        '''根据database删除Weaviate数据库中的数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("database").equal(database)
        )


knowledge_base_weaviate = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

if __name__ == '__main__':
    # knowledgeBase = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)
    # WeaviateClient.delete_collection_name(knowledgeBase.collections_name)
    # knowledgeBase.create_collection(knowledgeBase.properties)
    # while 循环获取输入
    while True:
        input_str = input("请输入：")
        if input_str == "exit":
            break
        else:
            asyncio.run(knowledge_base_weaviate.search_hybrid(input_str, 10))
