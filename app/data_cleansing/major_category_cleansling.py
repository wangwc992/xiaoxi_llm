"""清洗专业二级分类数据"""
from app.common.core.langchain_client import Embedding
from app.database.mysql.xxlxdb.school.major_category_mapper import get_major_category_list
from app.database.weaviate.major_category_weaviate import major_category_weaviate


def all_data_cleansing() -> list:
    """清洗专业二级分类数据"""
    major_category_list = get_major_category_list()
    # 将major_category_list 里面的id字段改为db_id
    for doc in major_category_list:
        doc["db_id"] = doc.pop("id")
    texts = [doc['category_english_name'] + " " + doc['zh_category_name'] for doc in major_category_list]
    doc_vecs = Embedding.embed_documents(texts)
    uuid_list = major_category_weaviate.basth_insert_data(major_category_list, doc_vecs)
    return uuid_list
