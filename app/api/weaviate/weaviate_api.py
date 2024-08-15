from fastapi import APIRouter, HTTPException

from app.common.utils.logging import get_logger
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate

router = APIRouter(prefix="/weaviate")
logger = get_logger(__name__)


@router.post("/collection", description="Create a weaviate collection")
async def create_collection(collection_name: str):
    # 根据collection_name选择不同的knowledge_base_weaviate、ai_chat_log_weaviate
    if collection_name == "knowledge_base":
        selected_weaviate = knowledge_base_weaviate
    elif collection_name == "ai_chat_log":
        selected_weaviate = ai_chat_log_weaviate
    else:
        raise HTTPException(status_code=400, detail="Invalid collection name")

    # 创建集合
    selected_weaviate.create_collection(selected_weaviate.properties)

    return {"message": f"{collection_name} collection created successfully"}


def clear_all_data(database: str):
    '''
    将 weaviate的t_knowledge_info表的全部数据清空
    :return:
    '''
    knowledge_base_weaviate.clear_all_data(database)


def delete_weaviate_data_by_id(id: str, database: str):
    '''
    根据id删除weaviate的数据
    :param id:
    :return:
    '''
    knowledge_base_weaviate.delete_data_by_id(id, database)


def search_weaviate_data_by_query(query: str, limit: int):
    '''
    根据query查询weaviate的数据
    :param query:
    :param limit:
    :return:
    '''
    return knowledge_base_weaviate.search_hybrid(query, limit)


def update_weaviate_data_by_id(id: str, properties: dict):
    '''
    根据id更新weaviate的数据
    :param id:
    :param properties:
    :return:
    '''
    knowledge_base_weaviate.update_data_by_uuid(id, properties)


def delete_collection_name():
    knowledge_base_weaviate.delete_collection_name(knowledge_base_weaviate.collections_name)


def delete_by_database(database: str):
    knowledge_base_weaviate.delete_by_database(database)
