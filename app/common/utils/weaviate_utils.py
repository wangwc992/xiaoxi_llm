import weaviate.classes as wvc
from tqdm import tqdm

from weaviate.client import WeaviateClient


def migrate_data(client_src: WeaviateClient, client_tgt: WeaviateClient, collection_name: str, include_vector=True):
    '''
    将数据从源迁移到目标编织实例
    :param client_src: 原始weaviate实例
    :param client_tgt:  目标weaviate实例
    :param collection_name:     集合名称
    :param include_vector:    是否包含向量
    :return:
    '''
    # 创建集合
    client_tgt.collections.create(
        name=collection_name,
        multi_tenancy_config=wvc.config.Configure.multi_tenancy(enabled=False),
    )

    # 批量迁移数据
    collection_src = client_src.collections.get(collection_name)
    collection_tgt = client_tgt.collections.get(collection_name)
    # 批量添加数据
    with collection_tgt.batch.fixed_size(batch_size=100) as batch:
        for q in tqdm(collection_src.iterator(include_vector=include_vector)):
            batch.add_object(
                properties=q.properties,
                vector=q.vector["default"],
                uuid=q.uuid
            )
    return True
