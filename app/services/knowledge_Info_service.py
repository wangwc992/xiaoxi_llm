from app.common.core.langchain_client import Embedding
from app.common.utils.html_util import HtmlUtils
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_weaviate_data, t_knowledge_info
from app.database.weaviate.knowledge_base import KnowledgeBaseWeaviate


knowledge_base_weaviate = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

def insert_weaviate_data_all():
    '''
    插入weaviate数据
    :param knowledge_weaviate_model_list:
    :return:
    '''
    knowledge_info_dict_list = search_weaviate_data(limit=1)

    knowledge_base_model = [{
        "database": t_knowledge_info,
        "db_id": knowledge_info.get("id"),
        "instruction": knowledge_info.get("country") + " " + knowledge_info.get("school") + " " + knowledge_info.get(
            "class") + " " + knowledge_info.get("name"),
        "input": "",
        "output": knowledge_info.get("founder") + " " + knowledge_info.get("replyerTime").strftime(
            "%Y-%m-%d %H:%M:%S") + " " + HtmlUtils.replace_link_with_url(knowledge_info.get("content")),
        "state": knowledge_info["startup_status"]
    } for knowledge_info in knowledge_info_dict_list]

    texts = [doc['instruction'] for doc in knowledge_base_model]

    doc_vecs = Embedding.embed_documents(texts)

    uuid_list = knowledge_base_weaviate.basth_insert_data(properties_list=knowledge_base_model, vecs=doc_vecs)

    print(uuid_list)


if __name__ == '__main__':
    insert_weaviate_data_all()
