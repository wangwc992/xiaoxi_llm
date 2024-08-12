import datetime

from pydantic import BaseModel, Field
from weaviate.classes.config import Configure, Property, DataType
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery

from app.common.core.langchain_client import Embedding
from app.common.utils.jieba_utils import jieba_tool
from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.weaviate_client import WeaviateClient


class AiChatLogModel(BaseModel):
    conversation_id: str = Field(description="会话id，用于标识一个会话")
    message_id: str = Field(description="消息id，用于标识一个消息")
    user_id: str = Field(description="用户id，用于标识一个用户")
    input: str = Field(description="用户输入的问题")
    output: str = Field(description="小希的回答")
    created_time: datetime = Field(description="消息创建时间")
    reference_data_uuids: list = Field(description="参考数据uuids")


class AiChatLogWeaviate(WeaviateClient):
    collections_name = "Ai_chat_log"
    properties = [
        Property(name='conversation_id', data_type=DataType.TEXT, description=' 会话id，用于标识一个会话'),
        Property(name='message_id', data_type=DataType.TEXT, description='消息id，用于标识一个消息'),
        Property(name='user_id', data_type=DataType.TEXT, description='用户id，用于标识一个用户'),
        Property(name='input', data_type=DataType.TEXT, description='用户输入的问题'),
        Property(name='output', data_type=DataType.TEXT, description='小希的回答'),
        Property(name='created_time', data_type=DataType.DATE, description='消息创建时间'),
        Property(name='reference_data_uuids', data_type=DataType.TEXT_ARRAY, description='参考数据uuids')
    ]

    async def search_hybrid(self, query, limit, filters=None):
        '''在Weaviate数据库中搜索数据'''
        query_keyword = ' '.join(jieba_tool.cut_for_search(query))
        response = self.collection.query.hybrid(
            query=query_keyword,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            filters=filters,
            query_properties=["output"],
            vector=Embedding.embed_query(query),
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=limit,
        )
        response_list = []
        for o in response.objects:
            properties = o.properties
            knowledge_base = ObjectFormatter.dict_to_object(properties, AiChatLogModel)
            response_list.append(knowledge_base)
        return response_list


ai_chat_log_weaviate = AiChatLogWeaviate(AiChatLogWeaviate.collections_name)

if __name__ == '__main__':
    # 创建集合
    # ai_chat_log_weaviate.create_collection(ai_chat_log_weaviate.properties)

    ai_chat_log_model = AiChatLogModel(
        conversation_id="conversation_id",
        message_id="123",
        user_id="123",
        input="你好",
        output="你好",
        created_time="2022-01-01T00:00:00Z",
        reference_data_uuids=["123"]
    )
    vector = Embedding.embed_query(ai_chat_log_model.output)
    uuid = ai_chat_log_weaviate.insert_data(ai_chat_log_model.dict(), vector)
    print(uuid)
