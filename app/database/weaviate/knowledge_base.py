from typing import Optional

from weaviate.collections.classes.config import DataType
# from pydantic import BaseModel, Field
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.classes.config import Property
from langchain_core.pydantic_v1 import BaseModel, Field
from app.database.weaviate.weaviate_client import WeaviateClient
from app.common.core.langchain_client import Embedding

collections_name = "Knowledge_base"

collections = WeaviateClient.client.collections.get(collections_name)


class KnowledgeBaseModel(BaseModel):
    uuid: Optional[str] = Field(None, description="weaviate数据库中的uuid")
    database: Optional[str] = Field(None, description="数据库")
    instruction: Optional[str] = Field(None, description="指令")
    input: Optional[str] = Field(None, description="输入")
    output: Optional[str] = Field(None, description="输出")
    state: Optional[int] = Field(None, description="状态")


class KnowledgeBaseWeaviate:
    weaviate_client = WeaviateClient(collections_name)
    properties = [
        Property(name='uuid', data_type=DataType.TEXT, description='weaviate数据库中的uuid'),
        Property(name='database', data_type=DataType.TEXT, description='数据库'),
        Property(name='instruction', data_type=DataType.TEXT, description='输入'),
        Property(name='input', data_type=DataType.TEXT, description='输出'),
        Property(name='state', data_type=DataType.INT, description='状态')
    ]

    def create_collection(self):
        self.weaviate_client.create_collection(self.properties)

    def search_hybrid(self, query, limit):
        response = self.weaviate_client.collections.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            target_vector="instruction",
            vector=Embedding.embed_query(query),
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=limit,
        )
        response_list = []
        for o in response.objects:
            knowledge_base = KnowledgeBaseModel(uuid=str(o.uuid), instruction=o.properties['instruction'],
                                           input=o.properties['input'], output=o.properties['output'],
                                           state=o.properties['state'])
            response_list.append(knowledge_base)
        return response_list
