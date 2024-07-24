from typing import Optional

from weaviate.classes.query import Filter
from weaviate.collections.classes.config import DataType, Configure
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.classes.config import Property
from langchain_core.pydantic_v1 import BaseModel, Field

from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding


class KnowledgeBaseModel(BaseModel):
    db_id: Optional[str] = Field(None, description="数据库的id")
    database: Optional[str] = Field(None, description="数据库")
    instruction: Optional[str] = Field(None, description="描述")
    input: Optional[str] = Field(None, description="输入")
    output: Optional[str] = Field(None, description="关键词")
    keyword: Optional[str] = Field(None, description="状态")
    file_info: Optional[str] = Field(None, description="文件信息")


class KnowledgeBaseWeaviate(WeaviateClient):
    collections_name = "qwen_data_base"
    properties = [
        Property(name='database', data_type=DataType.TEXT, description='数据库'),
        Property(name='db_id', data_type=DataType.TEXT, description='数据库的id'),
        Property(name='instruction', data_type=DataType.TEXT, description='描述'),
        Property(name='input', data_type=DataType.TEXT, description='输入'),
        Property(name='output', data_type=DataType.TEXT, description='输出'),
        Property(name='keyword', data_type=DataType.TEXT, description='关键词'),
        Property(name='file_info', data_type=DataType.TEXT, description='文件信息')
    ]

    def create_collection(self):
        self.client.collections.create(
            self.collections_name,
            vector_index_config=Configure.VectorIndex.hnsw(),
            properties=self.properties
        )

    def clear_all_data(self, database: str):
        '''清空Weaviate数据库中的所有数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("database").equal(database)
        )

    def search_hybrid(self, query, limit):
        response = self.collection.query.hybrid(
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

    def delete_data_by_id(self, id: str, database: str):
        '''根据id删除Weaviate数据库中的数据'''
        self.collection.data.delete_many(
            where=Filter.by_property("db_id").equal(id) & Filter.by_property("database").equal(database)
        )
