import asyncio
import os
import re
from typing import Optional, Dict

import pandas as pd
from pydantic import BaseModel

from app.common.core.langchain_client import Embedding
from app.common.utils.html_util import HtmlUtils
from app.common.utils.logging import get_logger
from app.common.utils.ocr_utlis import urlToText
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_mysql_weaviate import insert_ai_mysql_weaviate_bath
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import (search_knowledge_info_data,
                                                                     search_notice_message_data,
                                                                     search_school_info_basic_data,
                                                                     search_school_info_ranking_data,
                                                                     search_zn_school_department_project01,
                                                                     search_zn_school_department_project02,
                                                                     search_zn_school_department_project03,
                                                                     search_zn_school_department_project04,
                                                                     search_zn_school_department_project05,
                                                                     search_zn_school_department_project06,
                                                                     search_school_info_more_data,
                                                                     search_zn_school_selection_reason,
                                                                     search_zn_school_recruit_graduate_1,
                                                                     search_zn_school_recruit_graduate_2,
                                                                     search_zn_school_recruit_art,
                                                                     search_zn_school_department_project,
                                                                     search_missing_knowledge_info_data,
                                                                     check_missing_knowledge_data)
from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

logger = get_logger(__name__)

t_knowledge_info = "t_knowledge_info"
notice_message = "notice_message"
platform_introduction = "platform_introduction"
zn_school_info = "zn_school_info"
zn_school_info_rank = "zn_school_info_rank"
zn_school_info_more = "zn_school_info_more"
zn_school_selection_reason = "zn_school_selection_reason"
zn_school_admission_undergraduate = "zn_school_admission_undergraduate"
zn_school_admission_graduate_student = "zn_school_admission_graduate_student"
zn_school_admission_art = "zn_school_admission_art"
zn_school_department_project = "zn_school_department_project"


def check_missing_data_in_weaviate(start_id: int = 0, limit: int = 100):
    '''查询缺失数据'''
    class_list = ["换代理表", "授权表/接受offer缴费指导表", "申请材料模板", "院校申请表"]
    global t_knowledge_info
    database = t_knowledge_info
    db_id_list = check_missing_knowledge_data(limit=limit)
    knowledge_info_dict_list = search_missing_knowledge_info_data(db_id_list)
    if not knowledge_info_dict_list:
        logger.info(f"{database}知识库数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    knowledge_base_model = []
    file_url_list = []
    for knowledge_info in knowledge_info_dict_list:
        file_url = knowledge_info.get("fileurl")
        file_url_list.append(file_url)
        output = knowledge_info.get("output")
        if not output:
            output = knowledge_info.get("content", "")
            if file_url:
                file_content = urlToText(knowledge_info["fileurl"])
                if file_content:
                    filename = knowledge_info.get("filename", "")
                    output += f"\n该回答引用了以下文件:文件名：{filename}，文件内容:{file_content}"

                    class_ = knowledge_info.get("class_")
                    for item in class_list:
                        if item in class_:
                            output += f"，文件链接：{file_url}"
                output = HtmlUtils.replace_link_with_url(output)
                update_time = knowledge_info.get("updateTime", "")
                if update_time:
                    update_time = update_time.strftime("%Y-%m-%d %H:%H:%M")
                output = f'平台顾问于{update_time}回复内容如下：{output}'

        db_id = str(knowledge_info["id"])

        type = "1" if knowledge_info.get("type") == 1 else "2"
        name = knowledge_info.get("name" if type == "1" else "filename")
        instruction = f'{knowledge_info["country"]}{knowledge_info["school"]}{knowledge_info["class"]}的以下问题: {name}'
        link = f'{{"object":"json","type": {type},"title":"{name}","id":{db_id},"attachment_url":"{file_url}"}}'

        knowledge_base_model.append({
            "db_name": database,
            "db_id": db_id,
            "instruction": instruction,
            "output": output,
            "link": link,
        })

    return knowledge_info_dict_list[-1].get("id"), knowledge_base_model, file_url_list


def insert_t_knowledge_info_data(start_id: int = 0, limit: int = 10):
    '''知识库
    1、问答/文件相关知识库内容洗入向量库时注意事项：
    a、标题洗入要求： {国家}{院校}{问题类型}{问题是否常见}的以下问题：{标题内容}：

    b、答案洗入要求： {回复顾问}于{日期}回复内容如下：{问题答案}

    如果有文件，则在{问题答案}后方增加：该回答引用了以下文件:文件名：{文件名}，文件内容：{文件内容（pdf、excel、word提取信息，图片ocr信息）}
    eg：

    标题为： 澳洲伍伦贡大学入学要求常见问题：老师，卧龙岗新开的护理硕士学费出来了吗？
    内容为： 李薇于2024-06-07 16:26回复内容如下：两年总学费是74664'''
    class_list = ["换代理表", "授权表/接受offer缴费指导表", "申请材料模板", "院校申请表"]
    global t_knowledge_info
    database = t_knowledge_info
    knowledge_info_dict_list = search_knowledge_info_data(id=start_id, limit=limit)
    if not knowledge_info_dict_list:
        logger.info(f"{database}知识库数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    knowledge_base_model = []
    file_url_list = []
    for knowledge_info in knowledge_info_dict_list:
        file_url = knowledge_info.get("fileurl")
        file_url_list.append(file_url)
        # output = knowledge_info.get("output")
        output = ""
        if output:
            # 补丁，修复之前的数据，由于文件解析太麻烦加入的补丁
            update_time = knowledge_info.get("updateTime", "").strftime("%Y-%m-%d %H:%H:%M")
            output = re.sub(r'平台顾问于.*?回复内容如下', f'平台顾问于{update_time}回复内容如下', output)
        else:
            output = knowledge_info.get("content")
            if not output:
                output = ''
            if file_url:
                file_content = urlToText(knowledge_info["fileurl"])
                if file_content:
                    filename = knowledge_info.get("filename", "")
                    output += f"\n该回答引用了以下文件:文件名：{filename}，文件内容:{file_content}"
                    class_ = knowledge_info.get("class_")
                    for item in class_list:
                        if item in class_:
                            output += f"，文件链接：{file_url}"
                update_time = knowledge_info.get("updateTime", "")
                if update_time:
                    update_time = update_time.strftime("%Y-%m-%d %H:%H:%M")
                output = f'平台顾问于{update_time}回复内容如下：{output}'
        output = HtmlUtils.replace_link_with_url(output)
        db_id = str(knowledge_info["id"])

        type = "1" if knowledge_info.get("type") == 1 else "2"
        name = knowledge_info.get("name" if type == "1" else "filename")
        instruction = f'{knowledge_info["country"]}{knowledge_info["school"]}{knowledge_info["class"]}的以下问题: {name}'
        link = f'{{"object":"json","type": {type},"title":"{name}","id":{db_id},"attachment_url":"{file_url}"}}'

        knowledge_base_model.append({
            "db_name": database,
            "db_id": db_id,
            "instruction": instruction,
            "output": output,
            "link": link,
            # "keyword": "",
            # "file_info": file_content,
            # "input": "",
        })

    return knowledge_info_dict_list[-1].get("id"), knowledge_base_model, file_url_list


def insert_institution_information_data(start_id: int = 0, limit: int = 10):
    '''小希平台院校资讯
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}于{时间}的{资讯类型}的{标题}资讯。

    b、资讯内容：
    以下为资讯正文：{资讯内容}
    以下为资讯附件：{附件标题}{附件内容}
    以下为资料正文中附件{附件内容}。
    '''
    global notice_message
    database = notice_message
    notice_massage_dict_list = search_notice_message_data(id=start_id, limit=limit)
    if not notice_massage_dict_list:
        logger.info(f"小希平台院校资讯数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    knowledge_base_model = []

    for notice_massage in notice_massage_dict_list:
        notice_create_time = notice_massage.get('notice_create_time').strftime("%Y-%m-%d %H:%M:%S")
        db_id = str(notice_massage.get('notice_id'))
        instruction_list = [notice_massage.get('school_name', ''), notice_massage.get('school_english_name', ''),
                            notice_create_time, notice_massage.get('notice_category', ''),
                            notice_massage.get('notice_title', '')]
        instruction_list = [item for item in instruction_list if item is not None]
        instruction = " ".join(instruction_list)
        file_info = ''
        # if notice_massage.get('attachment_url'):
        #     file_info = FileToText.urlToText(notice_massage.get('attachment_url'))
        #     pass
        content = HtmlUtils.replace_link_with_url(notice_massage.get('notice_summary', ''))
        output = f"""以下是资讯正文：{content}\n 
        以下是资讯附件：{notice_massage.get('attachment_name', '')}\n  {file_info}\n
        以下是资料正文中附件{notice_massage.get('notice_title', '')}。"""

        knowledge_base_model.append({
            "db_name": database,
            "db_id": db_id,
            "instruction": instruction,
            "output": output,
        })

    return notice_massage_dict_list[-1].get("notice_id"), knowledge_base_model, None


def insert_platform_introduction_data(start_id: int = 0, limit: int = 10):
    '''插入小希平台介绍的全部数据
    这部分内容由产品经理团队整理出文字版本的word或者pdf文档给到技术，技术洗入向量数据库。
    产品经理给出的文档格式如下：

    a、问题： 小希平台/小希系统的{模块}{功能}介绍说明如下/问题解答如下：

    b、答案： {答案}'''
    global platform_introduction
    database = platform_introduction
    # 加载小希平台介绍数据的xlsx文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'data/platform_introduction.xlsx')
    df = pd.read_excel(file_path)

    # Extract the necessary information
    data = df.to_dict(orient='records')
    knowledge_base_model = [{
        "db_name": database,
        "db_id": str(i),
        "instruction": info.get('instruction'),
        "output": info.get('output'),
    } for i, info in enumerate(data)]

    insert_weaviate_data_all(knowledge_base_model)
    logger.info(f"小希平台介绍数据已全部洗入")
    # 抛出异常，终止程序
    raise Exception(f'小希平台介绍数据已全部洗入')


def insert_college_library01_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{基本信息}如下：
    b、内容信息：
    （*仅洗入字段内容不为空的字段，字段为（*我这里仅列出标题））：【*院校中文名：】【*院校英文名：】【*所属国家：】【所属地区：】【*官网地址：】【申请费支付维度：】【申请周期-算法统计：】【申请周期-人工配置：】
        '''
    global zn_school_info
    database = zn_school_info
    school_info_basic = search_school_info_basic_data(id=start_id, limit=limit)
    if not school_info_basic:
        logger.info(f"院校库基本信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{'': 'chinese_name'}, {'': 'english_name'}, {'': 'country_name'},
                       {'所属地区': "city_path"}, {'': "website"}, {'申请费支付维度': 'fee_dimension'},
                       {'申请周期-算法统计': 'apply_cycle_algorithm'}, {'申请周期-人工配置': 'apply_cycle_manual'}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, school_info_basic)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_basic)

    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的基本信息",
        "output": dict_list02[i].get("key_value"),
    } for i, dict in enumerate(dict_list01)]

    return school_info_basic[-1].get("id"), knowledge_base_model, None


def insert_college_library02_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校排名}如下：
    b、内容信息：
    【世界USNEWS排名：】【世界泰晤士排名：】【世界QS排名：】【地区USNEWS排名：】【地区泰晤士排名：】【地区QS排名：】
    '''
    global zn_school_info_rank
    database = zn_school_info_rank
    school_info_ranking_list = search_school_info_ranking_data(id=start_id, limit=limit)
    if not school_info_ranking_list:
        logger.info(f"院校库排名信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{"世界泰晤士排名": "world_rank_the"}, {"世界QS排名": "world_rank_qs"},
                       {"地区USNEWS排名": "local_rank_usnews"}, {"地区泰晤士排名": "local_rank_the"},
                       {"地区QS排名": "local_rank_qs"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, school_info_ranking_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_ranking_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的院校排名",
        "output": dict_list02[i].get("key_value"),
    } for i, dict in enumerate(dict_list01)]

    return school_info_ranking_list[-1].get("id"), knowledge_base_model, None


def insert_college_library03_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校更多信息}如下：
    b、内容信息：
    【就业率：】【毕业薪资：】【学生总数量：】【本科生数量：】【研究生数量：】【国际学生比例：】【师生比例：】【男女比例：】【院校简介：】【院校历史：】【地理位置：】【校园环境：】【学校宿舍：】【图书馆：】【学校设施：】【招生办信息：】【防疫信息：】
    '''
    global zn_school_info_more
    database = zn_school_info_more
    school_info_more_list = search_school_info_more_data(id=start_id, limit=limit)
    if not school_info_more_list:
        logger.info(f"院校库更多信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{"就业率": "employment_rate"}, {"毕业薪资": "employment_salary"},
                       {"学生总数量": "student_amount"}, {"本科生数量": "undergraduate_amount"},
                       {"研究生数量": "graduate_amount"}, {"国际学生比例": "international_ratio"},
                       {"师生比例": "faculty_ratio"}, {"男女比例": "boy_girl_ratio"},
                       {"院校简介": "introduction"}, {"院校历史": "history"}, {"地理位置": "location"},
                       {"校园环境": "campus"}, {"学校宿舍": "accommodation"}, {"图书馆": "library"},
                       {"学校设施": "installation"}, {"招生办信息": "admissions_office"}, {"防疫信息": "covid_rule"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, school_info_more_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_more_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的院校更多信息",
        "output": dict_list02[i].get("key_value"),
    } for i, dict in enumerate(dict_list01)]

    return school_info_more_list[-1].get("id"), knowledge_base_model, None


def insert_college_library04_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校择校理由}如下：
    b、内容信息：
    【择校理由：】【学校特色：】【强势专业：】【热门专业：】【院系设置：】【好评项：】【差评项：】
    '''
    database = "zn_school_selection_reason"
    zn_school_selection_reason_list = search_zn_school_selection_reason(id=start_id, limit=limit)
    if not zn_school_selection_reason_list:
        logger.info(f"院校库择校理由数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    key_name_list02 = [{"择校理由": "selection_reason"}, {"学校特色": "feature"},
                       {"强势专业": "strong_majors"}, {"热门专业": "hot_majors"},
                       {"院系设置": "department_major"}, {"好评项": "evaluation_good"},
                       {"差评项": "evaluation_bad"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, zn_school_selection_reason_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, zn_school_selection_reason_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的院校择校理由",
        "output": dict_list02[i].get("key_value"),
    } for i, dict in enumerate(dict_list01)]

    return zn_school_selection_reason_list[-1].get("id"), knowledge_base_model, None


def insert_college_library05_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{本科生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【申请简介：】【录取率：】【申请人数：】【申请学期：】【申请截止时间：】【Offer发放时间：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【GPA成绩：】【ACT成绩：】【SAT成绩：】【SAT2成绩：】【GRE成绩：】【GMAT成绩：】【雅思成绩：】【托福成绩：】【native成绩：】【其他成绩：】【奖学金：】【申请材料：】【申请流程】
    '''
    global zn_school_admission_undergraduate
    database = zn_school_admission_undergraduate
    search_zn_school_recruit_graduate_1_list = search_zn_school_recruit_graduate_1(id=start_id, limit=limit)
    if not search_zn_school_recruit_graduate_1_list:
        logger.info(f"院校库本科生院校招生信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    title01 = "标题信息"
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    title02 = "录取信息如下"
    key_name_list02 = [{"申请简介": "introduction"}, {"录取率": "admission_rate"},
                       {"申请人数": "apply_amount"}, {"申请学期": "semester"},
                       {"申请截止时间": "time_apply_deadline"}, {"Offer发放时间": "time_offer"}]
    title03 = "留学费用如下"
    key_name_list03 = [{"申请费用": "fee_apply"}, {"学费": "fee_tuition"}, {"书本费": "fee_book"},
                       {"生活费": "fee_life"}, {"交通费": "fee_traffic"}, {"住宿费用": "fee_accommodation"},
                       {"其他费用": "fee_others"}, {"总花费": "fee_total"}]
    title04 = "考试要求如下"
    key_name_list04 = [{"GPA成绩": "score_gpa"},
                       {"ACT成绩": "score_act"}, {"SAT成绩": "score_sat"}, {"SAT2成绩": "score_sat2"},
                       {"GRE成绩": "score_gre"}, {"GMAT成绩": "score_gmat"}, {"雅思成绩": "score_ielts"},
                       {"托福成绩": "score_toefl"}, {"native成绩": "score_native"}, {"其他成绩": "score_others"},
                       {"奖学金": "scholarship"}, {"申请材料": "material"}, {"申请流程": "recruit_flow"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, search_zn_school_recruit_graduate_1_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, search_zn_school_recruit_graduate_1_list)
    dict_list03 = ObjectFormatter.attribute_concatenation(key_name_list03, search_zn_school_recruit_graduate_1_list)
    dict_list04 = ObjectFormatter.attribute_concatenation(key_name_list04, search_zn_school_recruit_graduate_1_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的本科生院校招生信息",
        "output": f"""{title02}：{dict_list02[i].get("key_value")}\n{title03}：{dict_list03[i].get("key_value")}\n{title04}：{dict_list04[i].get("key_value")}""",
    } for i, dict in enumerate(dict_list01)]

    return search_zn_school_recruit_graduate_1_list[-1].get("id"), knowledge_base_model, None


def insert_college_library06_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{研究生生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【申请简介：】【录取率：】【申请人数：】【申请学期：】【申请截止时间：】【Offer发放时间：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【GPA成绩：】【ACT成绩：】【SAT成绩：】【SAT2成绩：】【GRE成绩：】【GMAT成绩：】【雅思成绩：】【托福成绩：】【native成绩：】【其他成绩：】【奖学金：】【申请材料：】【申请流程】
    '''
    global zn_school_admission_graduate_student
    database = zn_school_admission_graduate_student
    search_zn_school_recruit_graduate_2_list = search_zn_school_recruit_graduate_2(id=start_id, limit=limit)
    if not search_zn_school_recruit_graduate_2_list:
        logger.info(f"院校库研究生生院校招生信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None

    title01 = "标题信息"
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    title02 = "录取信息如下"
    key_name_list02 = [{"申请简介": "introduction"}, {"录取率": "admission_rate"},
                       {"申请人数": "apply_amount"}, {"申请学期": "semester"},
                       {"申请截止时间": "time_apply_deadline"}, {"Offer发放时间": "time_offer"}]
    title03 = "留学费用如下"
    key_name_list03 = [{"申请费用": "fee_apply"}, {"学费": "fee_tuition"}, {"书本费": "fee_book"},
                       {"生活费": "fee_life"}, {"交通费": "fee_traffic"}, {"住宿费用": "fee_accommodation"},
                       {"其他费用": "fee_others"}, {"总花费": "fee_total"}]
    title04 = "考试要求如下"
    key_name_list04 = [{"GPA成绩": "score_gpa"},
                       {"ACT成绩": "score_act"}, {"SAT成绩": "score_sat"}, {"SAT2成绩": "score_sat2"},
                       {"GRE成绩": "score_gre"}, {"GMAT成绩": "score_gmat"}, {"雅思成绩": "score_ielts"},
                       {"托福成绩": "score_toefl"}, {"native成绩": "score_native"}, {"其他成绩": "score_others"},
                       {"奖学金": "scholarship"}, {"申请材料": "material"}, {"申请流程": "recruit_flow"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, search_zn_school_recruit_graduate_2_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, search_zn_school_recruit_graduate_2_list)
    dict_list03 = ObjectFormatter.attribute_concatenation(key_name_list03, search_zn_school_recruit_graduate_2_list)
    dict_list04 = ObjectFormatter.attribute_concatenation(key_name_list04, search_zn_school_recruit_graduate_2_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的研究生生院校招生信息",
        "output": f"""{title02}：{dict_list02[i].get("key_value")}\n{title03}：{dict_list03[i].get("key_value")}\n{title04}：{dict_list04[i].get("key_value")}""",
    } for i, dict in enumerate(dict_list01)]

    return search_zn_school_recruit_graduate_2_list[-1].get("id"), knowledge_base_model, None


def insert_college_library07_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{艺术生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【录取率：】【申请难度：】【优势专业：】【申请经验：】【明星校友：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【研究生专业：】【本科专业：】【研究生雅思成绩：】【本科雅思成绩：】【研究生托福成绩：】【本科托福成绩：】【研究生申请截止日：】【本科申请截止日期：】【研究生申请要求：】【本科申请要求：】【研究生作品集要求：】【本科作品集要求：】
    '''
    global zn_school_admission_art
    database = zn_school_admission_art
    search_zn_school_recruit_graduate_2_list = search_zn_school_recruit_art(id=start_id, limit=limit)
    if not search_zn_school_recruit_graduate_2_list:
        logger.info(f"院校库艺术生院校招生信息数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None
    title01 = "标题信息"
    key_name_list01 = [{"db_id": "id"}, {'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
                       {"院校简称": "school_abbreviations"}]
    title02 = "录取信息如下"
    key_name_list02 = [{"录取率": "admission_rate"}, {"申请难度": "difficulty_name"},
                       {"优势专业": "strong_majors"}, {"申请经验": "apply_experience"},
                       {"明星校友": "alumni"}]

    title03 = "留学费用如下"
    key_name_list03 = [{"申请费用": "fee_apply"}, {"学费": "fee_tuition"}, {"书本费": "fee_book"},
                       {"生活费": "fee_life"}, {"交通费": "fee_traffic"}, {"住宿费用": "fee_accommodation"},
                       {"其他费用": "fee_others"}, {"总花费": "fee_total"}]

    title04 = "考试要求如下"
    key_name_list04 = [{"研究生专业": "graduate_majors"}, {"本科专业": "undergraduate_majors"},
                       {"研究生雅思成绩": "graduate_score_ielts"}, {"本科雅思成绩": "undergraduate_score_ielts"},
                       {"研究生托福成绩": "graduate_score_toefl"}, {"本科托福成绩": "undergraduate_score_toefl"},
                       {"研究生申请截止日": "graduate_apply_deadline"},
                       {"本科申请截止日期": "undergraduate_apply_deadline"},
                       {"研究生申请要求": "graduate_requirements"}, {"本科申请要求": "undergraduate_requirements"},
                       {"研究生作品集要求": "graduate_works_requirement"},
                       {"本科作品集要求": "undergraduate_works_requirement"}]
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, search_zn_school_recruit_graduate_2_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, search_zn_school_recruit_graduate_2_list)
    dict_list03 = ObjectFormatter.attribute_concatenation(key_name_list03, search_zn_school_recruit_graduate_2_list)
    dict_list04 = ObjectFormatter.attribute_concatenation(key_name_list04, search_zn_school_recruit_graduate_2_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的艺术生院校招生信息",
        "output": f"""{title01}: {dict_list01[i].get("key_value")}\n{title02}: {dict_list02[i].get("key_value")}\n{title03}: {dict_list03[i].get("key_value")}\n{title04}: {dict_list04[i].get("key_value")}""",
    } for i, dict in enumerate(dict_list01)]

    return search_zn_school_recruit_graduate_2_list[-1].get("id"), knowledge_base_model, None


def insert_major_library_data(start_id: int = 0, limit: int = 10):
    global zn_school_department_project
    database = zn_school_department_project
    zn_school_department_project_list = search_zn_school_department_project(id=start_id, limit=limit)
    if not zn_school_department_project_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        return None, None, None

    title00 = "标题信息"
    key_name_list00 = [{"db_id": "id"}, {"院校中文名": "zsi_school_name"}, {"院校英文名": "zsi_english_name"},
                       {"院校简称": "school_abbreviations"}, {"专业中文名": "znsdp_chinese_name"},
                       {"专业英文名": "znsdp_english_name"}]

    title01 = "专业基本信息"
    key_name_list01 = [{"所属院系": "department"}, {"所属校区": "campus"}, {"专业中文名": "znsdp_chinese_name"},
                       {"专业英文名": "znsdp_english_name"}, {"课程编码": "course_code"}, {"专业链接": "major_link"},
                       {"全日制学制": "full_time_duration"}, {"专业小方向": "specialization"},
                       {"非全日制": "part_time_duration"}, {"学位名称": "degree_name"}, {"学位类型": "degree_type"},
                       {"学位等级": "degree_level"}, {"专业简称": "abbreviation"}, {"开学时间": "start_semester"},
                       {"所在城市": "city_path"}, {"专业介绍": "introduction"}, {"专业分类": "career_opportunities"}]

    title02 = "关键时间和费用"
    key_name_list02 = [{"开学时间": "start_semester"}, {"申请截止时间": "application_deadline"},
                       {"Offer发放时间": "offer_release_time"}, {"Offer截止时间": "offer_deadline"},
                       {"申请费用": "application_fee"}, {"学费": "tuition_fee"}, {"生活费": "living_expenses"},
                       {"交通费": "traffic_fee"}, {"住宿费用": "accommodation_fee"}, {"其他费用": "other_fees"},
                       {"总花费": "total_cost"}]

    title03 = "申请要求"
    key_name_list03 = [{"雅思成绩": "ielts_score"}, {"雅思总分": "ielts_total_score"},
                       {"托福成绩": "toefl_score"}, {"托福总分": "toefl_total_score"}]

    title04 = "本科专业申请要求"
    key_name_list04 = [{"ATAR要求": "atar_requirement"}, {"ATAR分数": "atar_score"},
                       {"SAT要求": "sat_requirement"}, {"SAT分数": "sat_score"},
                       {"UKAlevel三科要求": "ukalevel3_requirement"}, {"UKAlevel三科分数": "ukalevel3_score"},
                       {"ACT要求": "act_requirement"}, {"ACT分数": "act_score"},
                       {"分数一": "ukalevel3_score1"}, {"分数二": "ukalevel3_score2"},
                       {"分数三": "ukalevel3_score3"}, {"UKAlevel四科要求": "ukalevel4_requirement"},
                       {"UKAlevel四科分数": "ukalevel4_score"}, {"AP要求": "ap_requirement"}, {"AP分数": "ap_score"},
                       {"IB要求": "ib_requirement"}, {"IB分数": "ib_score"}, {"高考要求": "gaokao_requirement"},
                       {"高考分数": "gaokao_score"}, {"OSSD要求": "ossd_requirement"}, {"OSSD分数": "ossd_score"},
                       {"BC要求": "bc_requirement"}, {"BC分数": "bc_score"}]

    title05 = "研究生专业申请要求"
    key_name_list05 = [{"c9均分要求": "c9_requirement"}, {"C9均分分数": "c9_score"},
                       {"211均分要求": "s211_requirement"}, {"211均分分数": "s211_score"},
                       {"985均分要求": "s985_requirement"}, {"985均分分数": "s985_score"},
                       {"非211均分要求": "sn211_requirement"}, {"非211均分分数": "sn211_score"},
                       {"专业背景要求": "professional_background_requirement"},
                       {"是否接受跨专业": "accept_cross_major"}]

    title06 = "其它申请要求"
    key_name_list06 = [{"学术要求": "academic_requirement"}, {"申请材料": "application_materials"},
                       {"申请要点": "application_elements"}, {"是否减免学分": "credit_reduction"},
                       {"减免学分条件": "credit_reduction_condition"}]

    dict_list00 = ObjectFormatter.attribute_concatenation(key_name_list00, zn_school_department_project_list)
    dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list01, zn_school_department_project_list)
    dict_list02 = ObjectFormatter.attribute_concatenation(key_name_list02, zn_school_department_project_list)
    dict_list03 = ObjectFormatter.attribute_concatenation(key_name_list03, zn_school_department_project_list)
    dict_list04 = ObjectFormatter.attribute_concatenation(key_name_list04, zn_school_department_project_list)
    dict_list05 = ObjectFormatter.attribute_concatenation(key_name_list05, zn_school_department_project_list)
    dict_list06 = ObjectFormatter.attribute_concatenation(key_name_list06, zn_school_department_project_list)

    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": dict_list00[i].get('key_value') + "信息资料如下",
        "output": f"""{title01}: {dict_list01[i].get('key_value')}\n{title02}: {dict_list02[i].get('key_value')}\n{title03}: {dict_list03[i].get('key_value')}\n{title04}: {dict_list04[i].get('key_value')}\n{title05}: {dict_list05[i].get('key_value')}\n{title06}: {dict_list06[i].get('key_value')}""",
    } for i, dict in enumerate(dict_list00)]

    return zn_school_department_project_list[-1].get("id"), knowledge_base_model, None


def insert_major_library01_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

   a、标题信息：
   {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
   b、内容信息：
                    zsi.chinese_name AS 'school_name',
                    zsi.english_name AS 'english_name',
                    zsi.school_abbreviations AS 'school_abbreviations',
   1、专业基本信息：
   【所属院系：】【所属校区：】【*专业中文名：】【*专业英文名：】【课程编码：】【*专业链接：】【*全日制学制：】【专业小方向：】【非全日制：】【*学位名称：】【*学位类型：】【*学位等级：】【专业简称 】【开学时间：】【所在城市：】【专业介绍：】【专业分类】
    '''
    database = "zn_school_department_project_01"
    # {'department': None, 'campus': None, 'chinese_name': '语言学与哲学-博士PhD', 'english_name': 'PhD in Linguistics and Philosophy', 'course_code': None, 'major_link': None, 'full_time_duration': '5年', 'specialization': None, 'part_time_duration': None, 'degree_name': None, 'degree_type': '博士', 'degree_level': None, 'abbreviation': '', 'start_semester': '秋季', 'city_path': '美国-马萨诸塞-波士顿', 'introduction': '', 'career_opportunities': None}
    zn_school_department_project_dict_list = search_zn_school_department_project01(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"所属院系": "department"}, {"所属校区": "campus"},
                     {"专业中文名": "chinese_name"},
                     {"专业英文名": "english_name"}, {"课程编码": "course_code"}, {"专业链接": "major_link"},
                     {"全日制学制": "full_time_duration"}, {"专业小方向": "specialization"},
                     {"非全日制": "part_time_duration"}, {"学位名称": "degree_name"}, {"学位类型": "degree_type"},
                     {"学位等级": "degree_level"}, {"专业简称": "abbreviation"}, {"开学时间": "start_semester"},
                     {"所在城市": "city_path"}, {"专业介绍": "introduction"}, {"专业分类": "career_opportunities"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的专业基本信息",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_major_library02_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
    2、关键时间和费用：
    【开学时间：】【申请截止时间：】【Offer发放时间：】【Offer发放截止时间：】【申请费用：】【学费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    '''
    database = "zn_school_department_project_02"
    zn_school_department_project_dict_list = search_zn_school_department_project02(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    # # {'id': 1, 'school_name': '麻省理工学院', 'english_name': 'Massachusetts Institute of Technology', 'school_abbreviations': '', 'chinese_name': '建筑技术-博士PhD', 'znsdp.english_name': 'PhD in Building Technology', 'school_id': 1, 'campus': None, 'start_semester': '9月', 'application_deadline': '', 'offer_release_time': '', 'offer_deadline': '', 'application_fee': '75美元', 'tuition_fee': '41770美元/学年', 'living_expenses': '', 'traffic_fee': None, 'accommodation_fee': '', 'other_fees': '', 'total_cost': ''}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"}, {"学校id": "school_id"}, {"校区": "campus"},
                     {"开学时间": "start_semester"}, {"申请截止时间": "application_deadline"},
                     {"Offer发放时间": "offer_release_time"}, {"Offer截止时间": "offer_deadline"},
                     {"申请费用": "application_fee"}, {"学费": "tuition_fee"}, {"生活费": "living_expenses"},
                     {"交通费": "traffic_fee"}, {"住宿费用": "accommodation_fee"}, {"其他费用": "other_fees"},
                     {"总花费": "total_cost"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的关键时间和费用",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_major_library03_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
    3、申请要求
    【雅思成绩：】【雅思总分：】【托福成绩：】【托福总分：】
    '''
    database = "zn_school_department_project_03"
    zn_school_department_project_dict_list = search_zn_school_department_project03(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    # {'id': 1, 'school_name': '麻省理工学院', 'english_name': 'Massachusetts Institute of Technology', 'school_abbreviations': '', 'chinese_name': '建筑技术-博士PhD', 'znsdp.english_name': 'PhD in Building Technology', 'school_id': 1, 'campus': None, 'ielts_score': '', 'ielts_total_score': None, 'toefl_score': '90', 'toefl_total_score': None}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"},
                     {"雅思成绩": "ielts_score"}, {"雅思总分": "ielts_total_score"},
                     {"托福成绩": "toefl_score"}, {"托福总分": "toefl_total_score"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_major_library04_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
    4、本科专业申请要求
    【ATAR要求：】【ATAR分数：】【SAT要求：】【SAT分数：】【UKAlevel三科要求：】【UKAlevel三科分数：】【ACT要求：】【ACT分数：】【分数一:
    】【分数二:  】【分数三:  】【UKAlevel四科要求：】【UKAlevel四科分数：】【AP要求：】【AP分数：】【IB要求：】【IB分数：】【高考要求：】
    【高考分数：】【OSSD要求：】【OSSD分数：】【BC要求：】【BC分数：】
    '''
    database = "zn_school_department_project_04"
    zn_school_department_project_dict_list = search_zn_school_department_project04(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    #     {'id': 162865, 'school_name': '蒙纳士大学', 'english_name': 'Monash University', 'school_abbreviations': '', 'chinese_name': '全球商业硕士与管理硕士', 'znsdp.english_name': 'Master of Global Business and Master of Management', 'school_id': 56, 'campus': 'Caulfield campus', 'atar_requirement': '', 'atar_score': None, 'sat_requirement': '', 'sat_score': None, 'ukalevel3_requirement': '', 'ukalevel3_score': None, 'act_requirement': '', 'act_score': None, 'ukalevel3_score1': None, 'ukalevel3_score2': None, 'ukalevel3_score3': None, 'ukalevel4_requirement': '', 'ukalevel4_score': None, 'ap_requirement': '', 'ap_score': None, 'ib_requirement': '', 'ib_score': None, 'gaokao_requirement': '', 'gaokao_score': '', 'ossd_requirement': '', 'ossd_score': None, 'bc_requirement': '', 'bc_score': None}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"}, {"学校id": "school_id"}, {"校区": "campus"},
                     {"ATAR要求": "atar_requirement"}, {"ATAR分数": "atar_score"}, {"SAT要求": "sat_requirement"},
                     {"SAT分数": "sat_score"}, {"UKAlevel三科要求": "ukalevel3_requirement"},
                     {"UKAlevel三科分数": "ukalevel3_score"}, {"ACT要求": "act_requirement"},
                     {"ACT分数": "act_score"}, {"分数一": "ukalevel3_score1"}, {"分数二": "ukalevel3_score2"},
                     {"分数三": "ukalevel3_score3"}, {"UKAlevel四科要求": "ukalevel4_requirement"},
                     {"UKAlevel四科分数": "ukalevel4_score"}, {"AP要求": "ap_requirement"}, {"AP分数": "ap_score"},
                     {"IB要求": "ib_requirement"}, {"IB分数": "ib_score"}, {"高考要求": "gaokao_requirement"},
                     {"高考分数": "gaokao_score"}, {"OSSD要求": "ossd_requirement"}, {"OSSD分数": "ossd_score"},
                     {"BC要求": "bc_requirement"}, {"BC分数": "bc_score"},
                     {"c9均分要求": "c9_requirement"}, {"C9均分分数": "c9_score"}, {"211均分要求": "s211_requirement"},
                     {"211均分分数": "s211_score"}, {"985均分要求": "s985_requirement"}, {"985均分分数": "s985_score"},
                     {"非211均分要求": "sn211_requirement"}, {"非211均分分数": "sn211_score"},
                     {"专业背景要求": "professional_background_requirement"}, {"是否接受跨专业": "accept_cross_major"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的本科专业申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_major_library05_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

    a、标题信息： {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
        5、研究生专业申请要求
        【c9均分要求：】【C9均分分数：】【211均分要求：】【211均分分数：】【985均分要求：】【985均分分数：】【非211均分要求：】【非211均分分数：】【专业背景要求：】【是否接受跨专业：】
    '''
    database = "zn_school_department_project_05"
    zn_school_department_project_dict_list = search_zn_school_department_project05(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    # {'id': 156097, 'school_name': '蒙纳士大学', 'english_name': 'Monash University', 'school_abbreviations': '', 'chinese_name': '信息技术文凭课程', 'znsdp.english_name': 'Diploma of Information Technology', 'school_id': 56, 'campus': None, 'c9_requirement': '', 'c9_score': None, 's211_requirement': '', 's211_score': None, 's985_requirement': '', 's985_score': None, 'sn211_requirement': '', 'sn211_score': None, 'professional_background_requirement': '', 'accept_cross_major': 1}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"}, {"学校id": "school_id"}, {"校区": "campus"},
                     {"c9均分要求": "c9_requirement"}, {"C9均分分数": "c9_score"}, {"211均分要求": "s211_requirement"},
                     {"211均分分数": "s211_score"}, {"985均分要求": "s985_requirement"}, {"985均分分数": "s985_score"},
                     {"非211均分要求": "sn211_requirement"}, {"非211均分分数": "sn211_score"},
                     {"专业背景要求": "professional_background_requirement"}, {"是否接受跨专业": "accept_cross_major"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的研究生专业申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_major_library06_data(start_id: int = 0, limit: int = 10):
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：

    b、内容信息：
    6、其它申请要求：
    【学术要求：】【申请材料：】【申请要点：】【是否减免学分：】【减免学分条件：】
    '''
    database = "zn_school_department_project_06"
    zn_school_department_project_dict_list = search_zn_school_department_project06(id=start_id, limit=limit)
    if not zn_school_department_project_dict_list:
        logger.info(f"专业库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"专业库数据已全部洗入")
    #     {'id': 1, 'school_name': '麻省理工学院', 'english_name': 'Massachusetts Institute of Technology', 'school_abbreviations': '', 'chinese_name': '建筑技术-博士PhD', 'znsdp.english_name': 'PhD in Building Technology', 'school_id': 1, 'campus': None, 'academic_requirement': None, 'application_materials': '1、申请表\n2、学历证明以及各科成绩单\n3、托福成绩单\n4、GRE成绩单\n5、申请费\n6、银行资金证明\n7、个人简历', 'application_elements': '', 'credit_reduction': 0, 'credit_reduction_condition': None}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"}, {"学校id": "school_id"}, {"校区": "campus"},
                     {"学术要求": "academic_requirement"}, {"申请材料": "application_materials"},
                     {"申请要点": "application_elements"}, {"是否减免学分": "credit_reduction"},
                     {"减免学分条件": "credit_reduction_condition"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "db_name": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的其它申请要求",
        "output": dict.get('key_value'),
    } for dict in dict_list]

    insert_weaviate_data_all(knowledge_base_model)
    return zn_school_department_project_dict_list[-1].get("id")


def insert_weaviate_data_all(knowledge_base_model: list):
    '''
    将t_knowledge_info表的全部数据插入weaviate数据
    :return:
    '''
    texts = [doc['instruction'] for doc in knowledge_base_model]

    doc_vecs = Embedding.embed_documents(texts)

    uuid_list = knowledge_base_weaviate.basth_insert_data(properties_list=knowledge_base_model, vecs=doc_vecs)
    logger.info(
        "%s 插入大于id:%s的%s条的数据%s" % (
            knowledge_base_weaviate.collections_name, knowledge_base_model[0].get('db_id'), len(knowledge_base_model),
            uuid_list))
    return uuid_list


class MannerExecution(BaseModel):
    method_name: Optional[str] = "0"
    limit: Optional[int] = 10
    start_id: Optional[int] = 0
    frequency: Optional[int] = 1
    is_all: Optional[bool] = False
    insert_to_ai_mysql_weaviate: Optional[bool] = False


async def cleansing_manner_execution(manner_execution: MannerExecution):
    limit = manner_execution.limit
    start_id = manner_execution.start_id
    method = manner_execution.method_name
    is_all = manner_execution.is_all
    insert_to_ai_mysql_weaviate = manner_execution.insert_to_ai_mysql_weaviate

    method_mapping = {
        "check_missing_data_in_weaviate": lambda: check_missing_data_in_weaviate(start_id=start_id, limit=limit),
        "t_knowledge_info": lambda: insert_t_knowledge_info_data(start_id=start_id, limit=limit),
        "notice_message": lambda: insert_institution_information_data(start_id=start_id, limit=limit),
        "platform_introduction": lambda: insert_platform_introduction_data(start_id=start_id, limit=limit),
        "zn_school_info": lambda: insert_college_library01_data(start_id=start_id, limit=limit),
        "zn_school_info_rank": lambda: insert_college_library02_data(start_id=start_id, limit=limit),
        "zn_school_info_more": lambda: insert_college_library03_data(start_id=start_id, limit=limit),
        "zn_school_selection_reason": lambda: insert_college_library04_data(start_id=start_id, limit=limit),
        "zn_school_admission_undergraduate": lambda: insert_college_library05_data(start_id=start_id, limit=limit),
        "zn_school_admission_graduate_student": lambda: insert_college_library06_data(start_id=start_id, limit=limit),
        "zn_school_admission_art": lambda: insert_college_library07_data(start_id=start_id, limit=limit),
        "zn_school_department_project": lambda: insert_major_library_data(start_id=start_id, limit=limit),
    }

    if is_all:
        # 清空数据库
        knowledge_base_weaviate.clear_all_data(property="db_name", like_str="*")
        # 排除使用的方法
        method_mapping.pop("check_missing_data_in_weaviate")

        for method_name, method_func in method_mapping.items():
            frequency = manner_execution.frequency
            start_id = manner_execution.start_id
            if method_name == "t_knowledge_info":
                limit = 100
            try:
                while frequency != 0:
                    start_id, knowledge_base_model, file_url_list = method_func()
                    if not knowledge_base_model or frequency == 0:
                        logger.info(f"{method_name} 数据清洗完成")
                        break
                    uuid_list = insert_weaviate_data_all(knowledge_base_model)
                    if method_name == "t_knowledge_info" or method_name == "notice_message":
                        insert_mysql_weaviate(knowledge_base_model, uuid_list, file_url_list)
                    frequency -= 1
            except Exception as e:
                logger.error(e)
    else:
        frequency = manner_execution.frequency
        while frequency != 0:
            if method in method_mapping:
                start_id, knowledge_base_model, file_url_list = method_mapping[method]()
                if not knowledge_base_model or frequency == 0:
                    logger.info(f"{method} 数据清洗完成")
                    break
                uuid_list = insert_weaviate_data_all(knowledge_base_model)
                if method == "t_knowledge_info" or method == "notice_message":
                    insert_mysql_weaviate(knowledge_base_model, uuid_list, file_url_list)
                frequency -= 1
            else:
                print("请输入正确的参数")
                break


def insert_mysql_weaviate(knowledge_base_model_list, uuid_list, file_url_list):
    ai_mysql_weaviate_list = []
    db_name = knowledge_base_model_list[0].get('db_name')
    for i, knowledge_base_model in enumerate(knowledge_base_model_list):
        file_url = file_url_list[i] if file_url_list else None
        output = knowledge_base_model.get('output')
        file_content = None
        if file_url and t_knowledge_info == db_name:
            split = output.split("该回答引用了以下文件:")
            if len(split) > 1:
                output, file_content = split[0], "该回答引用了以下文件" + split[1]

        ai_mysql_weaviate = {
            "db_name": db_name,
            "db_id": knowledge_base_model.get('db_id'),
            "instruction": knowledge_base_model.get('instruction'),
            "input": knowledge_base_model.get('input'),
            "output": output,
            "keyword": knowledge_base_model.get('keyword'),
            "file_url": file_url,
            "file_content": file_content,
            "weaviate_id": uuid_list[i].hex
        }
        ai_mysql_weaviate_list.append(ai_mysql_weaviate)
    insert_ai_mysql_weaviate_bath(ai_mysql_weaviate_list)


if __name__ == '__main__':
    manner_execution = {
        "method_name": "t_knowledge_info",
        "limit": 2,
        "start_id": 0,
        "frequency": 1
    }
    manner_execution = MannerExecution(**manner_execution)
    asyncio.run(cleansing_manner_execution(manner_execution))
