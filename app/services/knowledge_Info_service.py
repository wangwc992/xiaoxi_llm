from app.common.core.langchain_client import Embedding
from app.common.utils.html_util import HtmlUtils
from app.common.utils.logging import get_logger
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_weaviate_data, t_knowledge_info
from app.database.weaviate.knowledge_base import KnowledgeBaseWeaviate

knowledge_base_weaviate = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

logger = get_logger(__name__)


def insert_weaviate_data_all():
    '''
    将t_knowledge_info表的全部数据插入weaviate数据
    :return:
    '''
    limit = 5
    id = 0
    while True:
        knowledge_info_dict_list = search_weaviate_data(id, limit=limit)
        if not knowledge_info_dict_list:
            break
        id = knowledge_info_dict_list[-1].get("id")
        knowledge_base_model = [{
            "database": t_knowledge_info,
            "db_id": str(knowledge_info.get("id")),
            "instruction": knowledge_info.get("country") + " " + knowledge_info.get(
                "school") + " " + knowledge_info.get(
                "class") + " " + knowledge_info.get("name"),
            "input": "",
            "output": knowledge_info.get("founder") + " " + knowledge_info.get("replyerTime").strftime(
                "%Y-%m-%d %H:%M:%S") + " " + HtmlUtils.replace_link_with_url(knowledge_info.get("content")),
            "state": knowledge_info["startup_status"]
        } for knowledge_info in knowledge_info_dict_list]

        texts = [doc['instruction'] for doc in knowledge_base_model]

        doc_vecs = Embedding.embed_documents(texts)

        uuid_list = knowledge_base_weaviate.basth_insert_data(properties_list=knowledge_base_model, vecs=doc_vecs)
        logger.info("插入大于%s的%s条的数据%s" % (id, limit, uuid_list))
        break


def clear_weaviate_data():
    '''
    将 weaviate的t_knowledge_info表的全部数据清空
    :return:
    '''
    knowledge_base_weaviate.clear_all_data("t_knowledge_info")


def delete_weaviate_data_by_id(id: str):
    '''
    根据id删除weaviate的数据
    :param id:
    :return:
    '''
    knowledge_base_weaviate.delete_data_by_id("t_knowledge_info", id)


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

if __name__ == '__main__':
    # insert_weaviate_data_all()
    # clear_weaviate_data()
    # delete_weaviate_data_by_id("155")
    # search_weaviate_data_by_query("英国", 10)
    update_weaviate_data_by_id("7e08b804-8b7c-47f8-a92b-29256d274266", {
                "database": "t_knowledge_info",
                "db_id": "156",
                "input": "",
                "instruction": "英国 约克大学（英国） 院校介绍 请问英国约克大学申请UNSW商科硕士需要达到多少分呢？",
                "output": "郝丽君12 2023-03-22 10:22:41 英国本科学历达到58分，是符合USNW要求65%的硕士录取要求的。如分数达不到，可考虑申请GC项目进行过渡。",
                "state": 1
            })
    pass
