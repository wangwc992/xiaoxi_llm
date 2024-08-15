from typing import Optional

from fastapi import APIRouter, HTTPException

from app.common.utils.logging import get_logger
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate

router = APIRouter(prefix="/weaviate")
logger = get_logger(__name__)


@router.post("/collection", description="Create a weaviate collection")
async def create_collection():
    result = knowledge_base_weaviate.create_collection(knowledge_base_weaviate.properties)
    return result


@router.delete("/collection", description="delete a weaviate collection")
async def create_collection():
    result = knowledge_base_weaviate.delete_collection_name(knowledge_base_weaviate.properties)
    return result


@router.delete("/clearDatabaseData", description="Clear all data in weaviate")
async def clear_all_data(database: str, ):
    result = knowledge_base_weaviate.clear_all_data(database)
    return result


@router.delete("/deleteData", description="Clear all data in weaviate")
def delete_weaviate_data_by_id(uuid: Optional[str], id: Optional[str], database: Optional[str]):
    if uuid:
        result = knowledge_base_weaviate.delete_data_by_uuid(uuid)
    elif id and database:
        result = knowledge_base_weaviate.delete_data_by_id(id, database)
    else:
        raise HTTPException(status_code=400, detail="uuid or id and database must be provided")
    return result

@router.get("/query", description="Query data in weaviate")
def search_weaviate_data_by_query(query: str, limit: int):
    '''
    根据query查询weaviate的数据
    :param query:
    :param limit:
    :return:
    '''
    return knowledge_base_weaviate.search_hybrid(query, limit)


@router.put("/update_weaviate_data", description="Update data in weaviate")
def update_weaviate_data_by_id(id: str, properties: dict):
    '''
    根据id更新weaviate的数据
    :param id:
    :param properties:
    :return:
    '''
    knowledge_base_weaviate.update_data_by_uuid(id, properties)
