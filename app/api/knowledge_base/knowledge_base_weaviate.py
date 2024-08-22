import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

router = APIRouter(prefix="/knowledge_base/weaviate")
logger = logging.getLogger(__name__)


@router.post("/cleansing", description="Cleansing the knowledge base.")
async def cleansing(manner_execution: MannerExecution):
    """知识库数据清洗
    manner_execution: MannerExecution   清洗方式
        {
          "method_name": "t_knowledge_info",
          "limit": 5,
          "start_id": 0,
          "frequency": 1
        }
        method_name: 选择清洗的方法
        limit: 限制的数量
        start_id: 数据的起始id
        frequency: 频率，-1为全部清洗，0为不清洗，1为清洗一次

    """
    logger.info("Received cleansing request with args: %s", manner_execution)

    return await cleansing_manner_execution(manner_execution)


@router.get("/weaviateSearch")
async def reference_data(query: str, alpha: float = 0.5, limit: int = 10):
    '''RAG结果引用数据查询
    query: str   查询字符串
    alpha: float   阈值，alpha 为 1 是纯向量搜索，alpha 为 0 是纯文本搜索
    limit: int   限制数量
    '''
    return await knowledge_base_weaviate.search_hybrid(query=query, limit=limit)


@router.post("/collection", description="Create a weaviate collection")
async def create_or_del(create_or_del: bool):
    """ 创建或删除weaviate的collection
    :param create_or_del: true为创建，false为删除
    """
    if create_or_del:
        result = knowledge_base_weaviate.create_collection(knowledge_base_weaviate.properties)
    else:
        result = knowledge_base_weaviate.delete_collection_name(knowledge_base_weaviate.collections_name)
    return result


@router.delete("/clearDatabaseData", description="Clear all data in weaviate")
async def clear_all_data(like_str: str, ):
    """ 清空weaviate的数据,根据db_name,
    :param like_str:    like_str为db_name的前缀的全部数据，like_str为空则清空全部数据
    :return:
    """
    result = knowledge_base_weaviate.clear_all_data(property="db_name", like_str=like_str)
    return result


@router.delete("/deleteData", description="Clear all data in weaviate")
def delete_weaviate_data_by_id(uuid: Optional[str], id: Optional[str], database: Optional[str]):
    """ 删除weaviate的数据,根据uuid或为数据库的id和database
    :param uuid:    weaviate的数据的uuid
    :param id:    数据的id
    :param database:    数据库的名称
    """
    if uuid:
        result = knowledge_base_weaviate.delete_data_by_uuid(uuid)
    elif id and database:
        result = knowledge_base_weaviate.delete_data_by_id(id, database)
    else:
        raise HTTPException(status_code=400, detail="uuid or id and database must be provided")
    return result


@router.get("/query", description="Query data in weaviate")
def search_weaviate_data(uuid: Optional[str] = None, db_id: Optional[str] = None, database: Optional[str] = None):
    """ 查询weaviate的数据,根据uuid或为数据库的id和database
    :param uuid:    weaviate的数据的uuid
    :param db_id:    数据的id
    :param database:    数据库的名称
    """
    if uuid:
        result = knowledge_base_weaviate.search_id(uuid)
    else:
        result = knowledge_base_weaviate.search_id_or_database(db_id, database)
    return result


@router.get("/searchHybrid", description="Query data in weaviate")
async def search_weaviate_data_by_query(query: str, limit: int, alpha: float = 0.5):
    """ 查询weaviate的数据,根据query
    :param query:    查询的字符串
    :param limit:    限制的数量
    """
    return await knowledge_base_weaviate.search_hybrid_or(query=query, alpha=alpha, limit=limit)
