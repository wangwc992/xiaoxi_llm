import os

import pandas as pd

from app.common.utils.object_utils import ObjectFormatter
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_school_info_basic_data, \
    search_school_info_ranking_data


def insert_college_library01_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{基本信息}如下：
    b、内容信息：
    （*仅洗入字段内容不为空的字段，字段为（*我这里仅列出标题））：【*院校中文名：】【*院校英文名：】【*所属国家：】【所属地区：】【*官网地址：】【申请费支付维度：】【申请周期-算法统计：】【申请周期-人工配置：】
        '''
    school_info_basic = search_school_info_basic_data(id=start_id, limit=limit)
    if not school_info_basic:
        # 抛出异常，终止程序
        raise Exception(f'院校库基本信息数据已全部洗入')
    key_name_list01 = [{'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{'': 'chinese_name'}, {'': 'english_name'}, {'': 'country_name'},
                       {'所属地区': "city_path"}, {'': "website"}, {'申请费支付维度': 'fee_dimension'},
                       {'申请周期-算法统计': 'apply_cycle_algorithm'}, {'申请周期-人工配置': 'apply_cycle_manual'}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, school_info_basic)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_basic)

    knowledge_base_model = [{
        "database": "zn_school_info",
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的基本信息",
        "input": "",
        "output": dict_list02[i].get("key_value"),
        "keyword": "",
        "file_info": "",
    } for i, dict in enumerate(dict_list01)]

    print(knowledge_base_model)

def insert_college_library02_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校排名}如下：
    b、内容信息：
    【世界USNEWS排名：】【世界泰晤士排名：】【世界QS排名：】【地区USNEWS排名：】【地区泰晤士排名：】【地区QS排名：】
    '''
    school_info_ranking_list = search_school_info_ranking_data(id=start_id, limit=limit)
    if not school_info_ranking_list:
        # 抛出异常，终止程序
        raise Exception(f"院校库排名信息数据已全部洗入")
    key_name_list01 = [{'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{"世界泰晤士排名": "world_rank_the"}, {"世界QS排名": "world_rank_qs"},
                       {"地区USNEWS排名": "local_rank_usnews"}, {"地区泰晤士排名": "local_rank_the"},
                       {"地区QS排名": "local_rank_qs"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, school_info_ranking_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_ranking_list)
    knowledge_base_model = [{
        "database": "zn_school_info",
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的院校排名",
        "input": "",
        "output": dict_list02[i].get("key_value"),
        "keyword": "",
        "file_info": "",
    } for i, dict in enumerate(dict_list01)]

    return school_info_ranking_list[-1].get("id")


def insert_platform_introduction_data(start_id: int = 0, limit: int = 10):
    '''插入小希平台介绍的全部数据
    这部分内容由产品经理团队整理出文字版本的word或者pdf文档给到技术，技术洗入向量数据库。
    产品经理给出的文档格式如下：

    a、问题： 小希平台/小希系统的{模块}{功能}介绍说明如下/问题解答如下：

    b、答案： {答案}'''
    datasets = 'platform_introduction'
    # 加载小希平台介绍数据的xlsx文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../data_cleansing/data/platform_introduction.xlsx')
    df = pd.read_excel(file_path)

    # Extract the necessary information
    data = df.to_dict(orient='records')
    knowledge_base_model = [{
        "database": datasets,
        "db_id": i,
        "instruction": info.get('instruction'),
        "input": "",
        "output": info.get('output'),
        "keyword": "",
        "file_info": "",
    } for i, info in enumerate(data)]

if __name__ == '__main__':
    # insert_college_library02_data()
    insert_platform_introduction_data()