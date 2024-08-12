from pydantic import BaseModel, Field
from weaviate.classes.config import Configure, Property, DataType
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery

from app.database.weaviate.weaviate_client import WeaviateClient


class AiChatLogModel(BaseModel):
    conversation_id: str = Field(description="会话id，用于标识一个会话")
    message_id: str = Field(description="消息id，用于标识一个消息")
    user_id: str = Field(description="用户id，用于标识一个用户")
    query: str = Field(description="用户输入的问题")
    response: str = Field(description="小希的回答")
    created_time: str = Field(description="消息创建时间")
    reference_data_uuids: list = Field(description="参考数据uuids")


class AiChatLogWeaviate(WeaviateClient):
    collections_name = "Ai_chat_log"
    properties = [
        Property(name='conversation_id', data_type=DataType.TEXT, description=' 会话id，用于标识一个会话'),
        Property(name='message_id', data_type=DataType.TEXT, description='消息id，用于标识一个消息'),
        Property(name='user_id', data_type=DataType.TEXT, description='用户id，用于标识一个用户'),
        Property(name='query', data_type=DataType.TEXT, description='用户输入的问题'),
        Property(name='response', data_type=DataType.TEXT, description='小希的回答'),
        Property(name='created_time', data_type=DataType.DATE, description='消息创建时间'),
        Property(name='reference_data_uuids', data_type=DataType.TEXT_ARRAY, description='参考数据uuids')
    ]
    vectorizer_config = [
        # Set a named vector
        Configure.NamedVectors.text2vec_transformers(  # Use the "text2vec-cohere" vectorizer
            name="response", source_properties=["response"]  # Set the source property(ies)
        ),
        # Set another named vector
        Configure.NamedVectors.text2vec_transformers(  # Use the "text2vec-openai" vectorizer
            name="query", source_properties=["query"]  # Set the source property(ies)
        ),
    ]

    def create_collection1(self, properties, vectorizer_config):
        '''创建集合'''
        self.client.collections.create(
            self.collections_name,
            # vector_index_config=Configure.VectorIndex.hnsw(),
            properties=properties,
            vectorizer_config=vectorizer_config

        )

    def insert_data1(self, properties):
        '''插入数据'''
        # 返回uuid列表
        return self.collection.data.insert(properties=properties)


    def hybrid_data1(self, query, vec, limit=10):
        '''混合查询数据'''
        response = self.collection.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            query_properties=["query"],
            # vector=vec,
            target_vector="query",
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=limit,
        )

        return response

ai_chat_log_weaviate = AiChatLogWeaviate(AiChatLogWeaviate.collections_name)

if __name__ == '__main__':
    # ai_chat_log_weaviate.create_collection1(ai_chat_log_weaviate.properties, ai_chat_log_weaviate.vectorizer_config)
    # uuid = ai_chat_log_weaviate.insert_data1({
    #     "conversation_id": "1",
    #     "message_id": "1",
    #     "user_id": "1",
    #     "query": "query:海贼王",
    #     "response": "query:火影忍者",
    #     "created_time": "2022-01-01T00:00:00Z",
    #     "reference_data_uuids": ["1", "2"]
    # })
    # print(uuid)
    # ai_chat_log_weaviate.search_id(uuid)

    response = ai_chat_log_weaviate.hybrid_data1("海贼王", None)
    print(response)
