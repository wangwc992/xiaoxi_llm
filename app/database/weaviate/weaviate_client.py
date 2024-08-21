import os

import weaviate
from dotenv import load_dotenv
from weaviate.collections.classes.config import Configure
from weaviate.classes.query import Filter
from weaviate.collections.classes.grpc import HybridFusion, MetadataQuery
from weaviate.embedded import EmbeddedOptions
from app.common.core.config import settings
from app.common.utils.jieba_utils import jieba_tool
from app.common.utils.logging import get_logger

# Load environment variables from .env file
load_dotenv()
logger = get_logger(__name__)


class WeaviateClient:
    app_env = os.getenv('APP_ENV', 'dev')
    if app_env == 'dev':
        weaviate_dict = settings["weaviate"]
        client = weaviate.connect_to_local(
            host=weaviate_dict["host"],
            port=weaviate_dict["port"],
            grpc_port=weaviate_dict["grpc_port"],
            headers={"X-Huggingface-Api-Key": "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"}
        )
    else:
        # 先连接到本地的Weaviate数据库，本地不存在在weaviate.WeaviateClient
        try:
            client = weaviate.connect_to_local(port=8079, grpc_port=50060)
            if not client.is_ready():
                raise weaviate.exceptions.WeaviateConnectionError("Local Weaviate instance is not ready.")
        except weaviate.exceptions.WeaviateConnectionError as e:
            print(f"Error connecting to local Weaviate: {e}")
            # 启动嵌入式 Weaviate
            try:
                client = weaviate.WeaviateClient(
                    embedded_options=EmbeddedOptions(
                        binary_path="/root/autodl-tmp/database/w2",
                        additional_env_vars={
                            "BACKUP_FILESYSTEM_PATH": "/root/autodl-tmp/database/w2"
                        }
                    )
                )
                client.connect()
            except Exception as e:
                print(f"Error starting embedded Weaviate: {e}")
                raise

    def __init__(self, collections_name):
        self.collections_name = collections_name
        self.collection = self.client.collections.get(collections_name)

    @classmethod
    def collections_list_all(cls):
        '''列出Weaviate数据库中的所有集合'''
        logger.info("Listing all collections in Weaviate database")
        collections = cls.client.collections.list_all()
        for collection in collections:
            print(collection)
        return collections

    @classmethod
    def exists(cls, collection_name):
        '''判断集合是否存在'''
        is_exists = cls.client.collections.exists(collection_name)
        if is_exists:
            logger.info(f"Collection exists: {collection_name}")
        else:
            logger.info(f"Collection not exists: {collection_name}")
        return is_exists

    def get_collection_config(self):
        '''获取集合配置'''
        logger.info(f"Getting collection config: {self.collections_name}")
        articles_config = self.collection.config.get()
        print(articles_config)

    @classmethod
    def delete_collection_name(cls, collection_name):
        '''删除集合'''
        logger.info(f"Deleting collection: {collection_name}")
        result = cls.client.collections.delete(collection_name)
        return {"message": f"{collection_name} collection deleted successfully"}

    def create_collection(self, properties):
        '''创建集合'''
        if not self.exists(self.collections_name):
            result = self.client.collections.create(
                self.collections_name,
                vector_index_config=Configure.VectorIndex.hnsw(),
                properties=properties
            )
            return {"message": f"{self.collections_name} collection created successfully"}
        else:
            return {"message": f"{self.collections_name} collection already exists"}

    def insert_data(self, properties, vec):
        '''插入数据'''
        # 返回uuid列表
        logger.info(f"Inserting data into collection: {self.collections_name}")
        return self.collection.data.insert(properties=properties, vector=vec)

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

    def update_data_by_uuid(self, uuid, update_data, vec=None):
        logger.info(f"Updating data in collection: {self.collections_name}")
        if vec:
            self.collection.data.update(
                uuid=uuid,
                properties=update_data,
                vector=vec
            )
        else:
            self.collection.data.update(
                uuid=uuid,
                properties=update_data
            )
        return {"message": f"{uuid} data updated successfully"}

    def search_id(self, uuid):
        logger.info(f"Searching data by id: {uuid}")
        data_object = self.collection.query.fetch_object_by_id(uuid)
        print(data_object.properties)

    def hybrid_data(self, query, vec, limit=10):
        '''混合查询数据'''
        logger.info(f"Hybrid querying data in collection: {self.collections_name}")
        response = self.collection.query.hybrid(
            query=query,
            fusion_type=HybridFusion.RELATIVE_SCORE,
            query_properties=["instruction"],
            vector=vec,
            return_metadata=MetadataQuery(score=True, explain_score=True),
            limit=limit,
        )

        return response

    def delete_data_by_uuid(self, uuid):
        '''删除数据'''
        self.collection.delete(uuid)
        return {"message": f"{uuid} data deleted successfully"}

    def clear_all_data(self, property: str, like_str: str):
        while True:
            filters = (
                Filter.by_property(property).like(f"{like_str}")
            )
            result = self.collection.data.delete_many(
                where=filters,
                # dry_run=True,
                # verbose=True
            )
            logger.info(f"Clear all data in Weaviate database: {like_str}, result: {result}")
            if result.matches < 10000:
                break
        return {"message": f"Clear all data in Weaviate database: {like_str}"}  # 返回清空数据的信息


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
