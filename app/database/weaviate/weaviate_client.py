import os

import weaviate
from dotenv import load_dotenv
from weaviate.collections.classes.config import Configure
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.embedded import EmbeddedOptions
import weaviate.classes as wvc
from app.common.core.config import settings

# Load environment variables from .env file
load_dotenv()


class WeaviateClient:
    app_env = os.getenv('APP_ENV', 'dev')
    if app_env == 'dev':
        weaviate_dict = settings["weaviate"]
        client = weaviate.connect_to_local(
            host=weaviate_dict["host"],
            port=weaviate_dict["port"],
            headers={"X-Huggingface-Api-Key": "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"}
        )
    else:
        client = weaviate.WeaviateClient(
            embedded_options=EmbeddedOptions(
                additional_env_vars={
                    # "ENABLE_MODULES": "text2vec-transformers",
                    # "TRANSFORMERS_INFERENCE_API": 'http://127.0.0.1:8090',
                    "BACKUP_FILESYSTEM_PATH": "/root/autodl-tmp/database/weaviate"
                }
            )
        )
        client.connect()

    def __init__(self, collections_name):
        self.collections_name = collections_name
        self.collection = self.client.collections.get(collections_name)

    @classmethod
    def collections_list_all(cls):
        '''列出Weaviate数据库中的所有集合'''
        collections = cls.client.collections.list_all()
        for collection in collections:
            print(collection)
        return collections

    @classmethod
    def exists(cls, collection_name):
        '''判断集合是否存在'''
        return cls.client.collections.exists(collection_name)

    def get_collection_config(self):
        '''获取集合配置'''
        articles_config = self.collection.config.get()
        print(articles_config)

    @classmethod
    def delete_collection_name(cls, collection_name):
        '''删除集合'''
        cls.client.collections.delete(collection_name)

    def create_collection(self, properties):
        '''创建集合'''
        if not self.exists(self.collections_name):
            self.client.collections.create(
                self.collections_name,
                vector_index_config=Configure.VectorIndex.hnsw(),
                properties=properties
            )

    def insert_data(self, properties, vec):
        '''插入数据'''
        # 返回uuid列表
        return self.collection.data.insert(properties=properties, vector=vec)

    def basth_insert_data(self, properties_list: list, vecs: list):
        '''批量插入数据'''
        uuid_list = []
        with self.collection.batch.dynamic() as batch:
            for properties in properties_list:
                uuid = batch.add_object(properties=properties, vector=vecs.pop(0))  # 从vecs中取出一个向量
                uuid_list.append(uuid)
        return uuid_list

    def update_data_by_uuid(self, uuid, update_data):
        self.collection.data.update(
            uuid=uuid,
            properties=update_data
        )

    def update_data(self, uuid, properties, vec):
        self.collection.data.update(
            uuid=uuid,
            properties=properties,
            vector=vec
        )

    def search_id(self, uuid):
        data_object = self.collection.query.fetch_object_by_id(uuid)
        print(data_object.properties)

    def hybrid_data(self, query, vec, limit=10):
        response = self.collection.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            target_vector="instruction",
            vector=vec,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=10,
        )

    def delete_data(self, uuid):
        '''删除数据'''
        self.collection.delete(uuid)




if __name__ == '__main__':
    WeaviateClient.collections_list_all()
    # WeaviateClient.get_collection_config()
    # WeaviateClient.delete_collection_name("jeopardy")
    # WeaviateClient.create_collection("jeopardy", properties)
    # WeaviateClient.insert_data("jeopardy", properties, vec)
    # WeaviateClient.basth_insert_data("jeopardy", properties_list, vecs)
    # WeaviateClient.update_data("uuid", "jeopardy", properties, vec)
    # WeaviateClient.search_id("uuid")
    # WeaviateClient.query_data("jeopardy", "query", vec)
    # WeaviateClient.delete_data("jeopardy", "uuid")

