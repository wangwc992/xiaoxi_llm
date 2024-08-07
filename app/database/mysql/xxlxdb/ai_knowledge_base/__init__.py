# 初始化 加载 get_keyword_by_database的数据
#
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_knowledge_base import get_keyword_by_database


def get_keyword_dict_list():
    keyword_dict_list = get_keyword_by_database()
    # [{'id': 1, 'database': 't_knowledge_info', 'keyword': '知识库', 'state': 1}]
    # database当做key，keyword当做list的value
    # {'t_knowledge_info': ['知识库'], 'notice_message': ['知识库']}
    ai_knowledge_base_keyword_dict = {}
    for keyword_dict in keyword_dict_list:
        database = keyword_dict['database']
        keyword = keyword_dict['keyword']
        if database in ai_knowledge_base_keyword_dict.keys():
            ai_knowledge_base_keyword_dict[database].append(keyword)
        else:
            ai_knowledge_base_keyword_dict[database] = [keyword]

    return ai_knowledge_base_keyword_dict

ai_knowledge_base_keyword_dict = get_keyword_dict_list()
