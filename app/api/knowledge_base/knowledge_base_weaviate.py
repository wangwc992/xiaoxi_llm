from typing import Optional

import weaviate
from fastapi import APIRouter, HTTPException
from tqdm import tqdm
from weaviate.classes.query import Filter

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution
from app.database.weaviate.knowledge_base import knowledge_base_weaviate, KnowledgeBaseModel

router = APIRouter(prefix="/knowledge_base/weaviate")
logger = get_logger(__name__)


@router.post("/cleansing", description="Cleansing the knowledge base.")
async def cleansing(manner_execution: MannerExecution):
    '''清洗知识库'''
    logger.info("Received cleansing request with args: %s", manner_execution)

    return await cleansing_manner_execution(manner_execution)


@router.get("/weaviateSearch")
async def reference_data(query: str, alpha: float = 0.5, limit: int = 10):
    '''Weaviate搜索
    alpha 为 1 是纯向量搜索
    alpha 为 0 是纯关键字搜索'''

    return await knowledge_base_weaviate.search_hybrid_or(query=query, alpha=alpha, limit=limit)


@router.post("/collection", description="Create a weaviate collection")
async def create_collection():
    result = knowledge_base_weaviate.create_collection(knowledge_base_weaviate.properties)
    return result


@router.delete("/collection", description="delete a weaviate collection")
async def delete_collection():
    result = knowledge_base_weaviate.delete_collection_name(knowledge_base_weaviate.collections_name)
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
def search_weaviate_data(uuid: Optional[str] = None, id: Optional[str] = None, database: Optional[str] = None):
    # function body
    if uuid:
        result = knowledge_base_weaviate.search_id(uuid)
    else:
        result = knowledge_base_weaviate.search_id_or_database(id, database)
    return result


@router.get("/searchHybrid", description="Query data in weaviate")
def search_weaviate_data_by_query(query: str, limit: int):
    '''
    根据query查询weaviate的数据
    :param query:
    :param limit:
    :return:
    '''
    return knowledge_base_weaviate.search_hybrid(query, limit)


@router.put("/update_weaviate_data", description="Update data in weaviate")
def update_data(KnowledgeBaseModel: KnowledgeBaseModel):
    '''
    根据id更新weaviate的数据
    :param id:
    :param properties:
    :return:
    '''
    knowledge_base_weaviate.update_data(KnowledgeBaseModel)
