import weaviate
from app.common.core.config import settings
from weaviate.embedded import EmbeddedOptions


class WeaviateClient:
    weaviate_dict = settings["weaviate"]
    client = weaviate.connect_to_local(
        host=weaviate_dict["host"],
        port=weaviate_dict["port"],
        headers={"X-Huggingface-Api-Key": "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"}
    )
    # client = weaviate.WeaviateClient(
    #     embedded_options=EmbeddedOptions(
    #         additional_env_vars={
    #             # "ENABLE_MODULES": "text2vec-transformers",
    #             # "TRANSFORMERS_INFERENCE_API": 'http://127.0.0.1:8090',
    #             "BACKUP_FILESYSTEM_PATH": "/root/autodl-tmp/database/weaviate"
    #         }
    #     )
    # )
    # client.connect()

    @classmethod
    def collections_list_all(cls):
        '''列出Weaviate数据库中的所有集合'''
        collections = cls.client.collections.list_all()
        for collection in collections:
            print(collection)
        return collections

    @classmethod
    def get_collection_config(cls):
        '''获取集合配置'''
        articles_config = cls.client.config.get()
        print(articles_config)

    @classmethod
    def delete_collection_name(cls, collection_name):
        '''删除集合'''
        cls.client.collections.delete(collection_name)

    @classmethod
    def create_collection(cls, collections_name, properties):
        '''创建集合'''
        cls.client.collections.create(
            collections_name,
            vector_index_config=Configure.VectorIndex.hnsw(),
            properties=properties
        )

    @classmethod
    def insert_data(cls, collections_name, properties, vec):
        '''插入数据'''
        collections = cls.client.collections.get(collections_name)
        # 返回uuid列表
        return jeopardy.data.insert(properties=properties, vector=vec)

    @classmethod
    def basth_insert_data(cls, collections_name, properties_list: list, vecs: list):
        '''批量插入数据'''
        collections = cls.client.collections.get(collections_name)
        uuid_list = []
        with collection.batch.dynamic() as batch:
            for properties in properties_list:
                uuid = batch.add_object(properties=properties, vector=vecs.pop(0))  # 从vecs中取出一个向量
                uuid_list.append(uuid)
        return uuid_list

    @classmethod
    def update_data(cls, uuid, update_data):
        collections = cls.client.collections.get(collections_name)
        collections.data.update(
            uuid=uuid,
            properties=update_data
        )

    @classmethod
    def update_data(cls, uuid, collections_name, properties, vec):
        collections = cls.client.collections.get(collections_name)
        collections.data.update(
            uuid=uuid,
            properties=properties,
            vector=vec
        )

    @classmethod
    def search_id(cls, uuid):
        collections = cls.client.collections.get(collections_name)
        data_object = collections.query.fetch_object_by_id(uuid)
        print(data_object.properties)

    @classmethod
    def query_data(cls, collections_name, query, vec):
        collections = cls.client.collections.get(collections_name)
        response = collections.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            target_vector="instruction",
            vector=vec,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=10,
        )

    @classmethod
    def delete_data(cls, collections_name, uuid):
        '''删除数据'''
        collections = cls.client.collections.get(collections_name)
        collections.delete(uuid)

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
