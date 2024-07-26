import json
import sys

from app.common.core.langchain_client import Embedding
from app.common.utils.html_util import HtmlUtils
from app.common.utils.logging import get_logger
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
                                                                     search_zn_school_recruit_art)
from app.common.utils.object_utils import ObjectFormatter
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
from app.common.utils.FileToText import FileToText

logger = get_logger(__name__)
file_to_text = FileToText()

# 查询起始id
start_id = 0

# 每次查询条数
limit = 2


def get_string(*string_list):
    text = " ".join([str(s) for s in string_list if s])
    return text


# 拿出富文本中A标签和img标签的链接，我会传入一个字符串的富文本
def get_file_info(file_url):
    file_info = file_to_text.urlToText(file_url)
    return file_info


def insert_t_knowledge_info_data():
    '''知识库
    1、问答/文件相关知识库内容洗入向量库时注意事项：
    a、标题洗入要求： {国家}{院校}{问题类型}{问题是否常见}的以下问题：{标题内容}：

    b、答案洗入要求： {回复顾问}于{日期}回复内容如下：{问题答案}

    如果有文件，则在{问题答案}后方增加：该回答引用了以下文件，文件名：{文件名}，文件内容：{文件内容（pdf、excel、word提取信息，图片ocr信息）}
    eg：

    标题为： 澳洲伍伦贡大学入学要求常见问题：老师，卧龙岗新开的护理硕士学费出来了吗？
    内容为： 李薇于2024-06-07 16:26回复内容如下：两年总学费是74664'''
    global start_id
    while True:
        knowledge_info_dict_list = search_knowledge_info_data(id=start_id, limit=limit)
        if not knowledge_info_dict_list:
            break
        start_id = knowledge_info_dict_list[-1].get("id")
        knowledge_base_model = [{
            "database": "t_knowledge_info",
            "db_id": str(knowledge_info.get("id", '') or ''),
            "instruction": get_string(knowledge_info.get("country", '') or '',
                                      knowledge_info.get("school", '') or '',
                                      knowledge_info.get("class", '') or '',
                                      "的以下问题",
                                      knowledge_info.get("name", '') or ''),
            "input": "",
            "output": ((knowledge_info.get("founder", '') or '') + "于" +
                       ((knowledge_info.get("replyerTime").strftime("%Y-%m-%d %H:%M:%S"))
                        if knowledge_info.get("replyerTime") else '') + "回复内容如下：" +
                       HtmlUtils.replace_link_with_url(knowledge_info.get("content", '') or '')),
            "keyword": get_string(knowledge_info.get("country", '') or '',
                                  knowledge_info.get("school", '') or '',
                                  knowledge_info.get("class", '') or ''),
            "file_info": file_to_text.urlToText(knowledge_info.get("fileurl", '') or '') if knowledge_info.get(
                "fileurl") else "",
        } for knowledge_info in knowledge_info_dict_list]

        insert_weaviate_data_all(knowledge_base_model)


def insert_institution_information_data():
    '''小希平台院校资讯
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}于{时间}的{资讯类型}的{标题}资讯。

    b、资讯内容：
    以下为资讯正文：{资讯内容}
    以下为资讯附件：{附件标题}{附件内容}
    以下为资料正文中附件{附件内容}。
    '''
    notice_massage_dict_list = search_notice_message_data(id=start_id, limit=limit)
    knowledge_base_model = [{
        "database": "notice_message",
        "db_id": str(notice_massage.get('notice_id', '')),
        "instruction": (notice_massage.get('school_name', '') + " " +
                        notice_massage.get('school_english_name', '') + "于" +
                        (notice_massage.get('notice_create_time').strftime("%Y-%m-%d %H:%M:%S")
                         if notice_massage.get('notice_create_time') else '') + " " +
                        notice_massage.get('notice_category', '') + " " +
                        notice_massage.get('notice_title', '')),
        "input": "",
        "output": ("以下是咨询正文：" + (notice_massage.get('notice_summary', '') or '') +
                   "以下是咨询附件：" + (notice_massage.get('attachment_name', '') or '') + " " +
                   (file_info if (file_info := (file_to_text.urlToText(notice_massage["attachment_url"])
                                                if notice_massage.get("attachment_url") else '')) else '') +
                   "以下是正文中的附件：" + (notice_massage.get('notice_title', '') or '')),
        "keyword": get_string(notice_massage.get("school_name", '') or '',
                              notice_massage.get("school_english_name", '') or '',
                              notice_massage.get("class", '') or ''),
        "file_info": file_info if (file_info := (file_to_text.urlToText(notice_massage["attachment_url"])
                                                 if notice_massage.get("attachment_url") else '')) else '',
    } for notice_massage in notice_massage_dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_platform_introduction_data():
    '''插入小希平台介绍的全部数据
    这部分内容由产品经理团队整理出文字版本的word或者pdf文档给到技术，技术洗入向量数据库。
    产品经理给出的文档格式如下：

    a、问题： 小希平台/小希系统的{模块}{功能}介绍说明如下/问题解答如下：

    b、答案： {答案}'''
    pass


def insert_college_library01_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{基本信息}如下：
    b、内容信息：
    （*仅洗入字段内容不为空的字段，字段为（*我这里仅列出标题））：【*院校中文名：】【*院校英文名：】【*所属国家：】【所属地区：】【*官网地址：】【申请费支付维度：】【申请周期-算法统计：】【申请周期-人工配置：】
        '''
    school_info_basic = search_school_info_basic_data(id=start_id, limit=limit)
    knowledge_base_model = [{
        "database": "zn_school_info",
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的基本信息").strip()
        ),
        "input": "",
        "output": (
                (f"院校中文名：{school_info.get('chinese_name', '')} " if school_info.get('chinese_name') else '') +
                (f"院校英文名：{school_info.get('english_name', '')} " if school_info.get('english_name') else '') +
                (f"所属国家：{school_info.get('country_name', '')} " if school_info.get('country_name') else '') +
                (f"所属地区：{school_info.get('city_path', '')} " if school_info.get('city_path') else '') +
                (f"官网地址：{school_info.get('website', '')} " if school_info.get('website') else '') +
                (f"申请费支付维度：{school_info.get('fee_dimension', '')} " if school_info.get(
                    'fee_dimension') else '') +
                (f"申请周期-算法统计：{school_info.get('apply_cycle_algorithm', '')} " if school_info.get(
                    'apply_cycle_algorithm') else '') +
                (f"申请周期-人工配置：{school_info.get('apply_cycle_manual', '')} " if school_info.get(
                    'apply_cycle_manual') else '')
        ).strip(),
        "keyword": get_string(
            school_info.get("chinese_name", '') or '',
            school_info.get("english_name", '') or '',
            school_info.get("school_abbreviations", '') or ''
        ),
        "file_info": "",
    } for school_info in school_info_basic]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library02_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校排名}如下：
    b、内容信息：
    【世界USNEWS排名：】【世界泰晤士排名：】【世界QS排名：】【地区USNEWS排名：】【地区泰晤士排名：】【地区QS排名：】
    '''
    school_info_ranking_list = search_school_info_ranking_data(id=start_id, limit=limit)
    knowledge_base_model = [{
        "database": "zn_school_info",
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的院校排名").strip()
        ),
        "input": "",
        "output": (
                (f"世界USNEWS排名：{school_info.get('world_rank_usnews', '')} " if school_info.get(
                    'world_rank_usnews') else '') +
                (f"世界泰晤士排名：：{school_info.get('world_rank_the', '')} " if school_info.get(
                    'world_rank_the') else '') +
                (f"世界QS排名：{school_info.get('world_rank_qs', '')} " if school_info.get('world_rank_qs') else '') +
                (f"地区USNEWS排名：{school_info.get('local_rank_usnews', '')} " if school_info.get(
                    'local_rank_usnews') else '') +
                (f"地区泰晤士排名：{school_info.get('local_rank_the', '')} " if school_info.get(
                    'local_rank_the') else '') +
                (f"地区QS排名：{school_info.get('local_rank_qs', '')} " if school_info.get('local_rank_qs') else '')
        ).strip(),
        "keyword": get_string(
            school_info.get("chinese_name", '') or '',
            school_info.get("english_name", '') or '',
            school_info.get("school_abbreviations", '') or ''
        ),
        "file_info": "",
    } for school_info in school_info_ranking_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library03_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校更多信息}如下：
    b、内容信息：
    【就业率：】【毕业薪资：】【学生总数量：】【本科生数量：】【研究生数量：】【国际学生比例：】【师生比例：】【男女比例：】【院校简介：】【院校历史：】【地理位置：】【校园环境：】【学校宿舍：】【图书馆：】【学校设施：】【招生办信息：】【防疫信息：】
    '''
    school_info_more_list = search_school_info_more_data(id=start_id, limit=limit)
    knowledge_base_model = [{
        "database": "zn_school_info",
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的院校更多信息").strip()
        ),
        "input": "",
        "output": (
                (f"就业率：{school_info.get('employment_rate', '')} " if school_info.get('employment_rate') else '') +
                (f"毕业薪资：{school_info.get('employment_salary', '')} " if school_info.get(
                    'employment_salary') else '') +
                (f"学生总数量：{school_info.get('student_amount', '')} " if school_info.get('student_amount') else '') +
                (f"本科生数量：{school_info.get('undergraduate_amount', '')} " if school_info.get(
                    'undergraduate_amount') else '') +
                (f"研究生数量：{school_info.get('graduate_amount', '')} " if school_info.get(
                    'graduate_amount') else '') +
                (f"国际学生比例：{school_info.get('international_ratio', '')} " if school_info.get(
                    'international_ratio') else '') +
                (f"师生比例：{school_info.get('faculty_ratio', '')} " if school_info.get('faculty_ratio') else '') +
                (f"男女比例：{school_info.get('boy_girl_ratio', '')} " if school_info.get('boy_girl_ratio') else '') +
                (f"院校简介：{school_info.get('introduction', '')} " if school_info.get('introduction') else '') +
                (f"院校历史：{school_info.get('history', '')} " if school_info.get('history') else '') +
                (f"地理位置：{school_info.get('location', '')} " if school_info.get("location") else '') +
                (f"校园环境：{school_info.get('campus', '')} " if school_info.get('campus') else '') +
                (f"学校宿舍：{school_info.get('accommodation', '')} " if school_info.get('accommodation') else '') +
                (f"图书馆：{school_info.get('library', '')} " if school_info.get('library') else '') +
                (f"学校设施：{school_info.get('installation', '')} " if school_info.get('installation') else '') +
                (f"招生办信息：{school_info.get('admissions_office', '')} " if school_info.get(
                    'admissions_office') else '') +
                (f"防疫信息：{school_info.get('covid_rule', '')} " if school_info.get('covid_rule') else '')

        ),
        "keyword": get_string(
            school_info.get("chinese_name", '') or '',
            school_info.get("english_name", '') or '',
            school_info.get("school_abbreviations", '') or ''
        ),
        "file_info": "",
    } for school_info in school_info_more_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library04_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校择校理由}如下：
    b、内容信息：
    【择校理由：】【学校特色：】【强势专业：】【热门专业：】【院系设置：】【好评项：】【差评项：】
    '''
    database = "zn_school_selection_reason"
    zn_school_selection_reason_list = search_zn_school_selection_reason(limit=10)
    knowledge_base_model = [{
        "database": database,
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的院校择校理由").strip()
        ),
        "input": "",
        "output": (
                (f"择校理由：{school_info.get('selection_reason', '')} " if school_info.get(
                    'selection_reason') else '') +
                (f"学校特色：{school_info.get('feature', '')} " if school_info.get('feature') else '') +
                (f"强势专业：{school_info.get('strong_majors', '')} " if school_info.get('strong_majors') else '') +
                (f"热门专业：{school_info.get('hot_majors', '')} " if school_info.get('hot_majors') else '') +
                (f"院系设置：{school_info.get('department_major', '')} " if school_info.get(
                    'department_major') else '') +
                (f"好评项：{school_info.get('evaluation_good', '')} " if school_info.get('evaluation_good') else '') +
                (f"差评项：{school_info.get('evaluation_bad', '')} " if school_info.get('evaluation_bad') else '')
        ),
        "keyword": get_string(
            school_info.get("chinese_name", '') or '',
            school_info.get("english_name", '') or '',
            school_info.get("school_abbreviations", '') or ''
        ),
        "file_info": "",
    } for school_info in zn_school_selection_reason_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library05_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{本科生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【申请简介：】【录取率：】【申请人数：】【申请学期：】【申请截止时间：】【Offer发放时间：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【GPA成绩：】【ACT成绩：】【SAT成绩：】【SAT2成绩：】【GRE成绩：】【GMAT成绩：】【雅思成绩：】【托福成绩：】【native成绩：】【其他成绩：】【奖学金：】【申请材料：】【申请流程】
    '''
    database = "zn_school_recruit_graduate_1"
    search_zn_school_recruit_graduate_1_list = search_zn_school_recruit_graduate_1(limit=10)
    knowledge_base_model = [{
        "database": database,
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的本科生院校招生信息").strip()
        ),
        "input": "",
        "output": (
                (f"录取信息如下："
                 f"【申请简介：{school_info.get('introduction', '')}】" if school_info.get('introduction') else '') +
                (f"【录取率：{school_info.get('admission_rate', '')}】" if school_info.get('admission_rate') else '') +
                (f"【申请人数：{school_info.get('apply_amount', '')}】" if school_info.get('apply_amount') else '') +
                (f"【申请学期：{school_info.get('semester', '')}】" if school_info.get('semester') else '') +
                (f"【申请截止时间：{school_info.get('time_apply_deadline', '')}】" if school_info.get(
                    'time_apply_deadline') else '') +
                (f"【Offer发放时间：{school_info.get('time_offer', '')}】" if school_info.get('time_offer') else '') +

                (f"\n留学费用如下："
                 f"【申请费用：{school_info.get('fee_apply', '')}】" if school_info.get('fee_apply') else '') +
                (f"【学费：{school_info.get('fee_tuition', '')}】" if school_info.get('fee_tuition') else '') +
                (f"【书本费：{school_info.get('fee_book', '')}】" if school_info.get('fee_book') else '') +
                (f"【生活费：{school_info.get('fee_life', '')}】" if school_info.get('fee_life') else '') +
                (f"【交通费：{school_info.get('fee_traffic', '')}】" if school_info.get('fee_traffic') else '') +
                (f"【住宿费用：{school_info.get('fee_accommodation', '')}】" if school_info.get(
                    'fee_accommodation') else '') +
                (f"【其他费用：{school_info.get('fee_others', '')}】" if school_info.get('fee_others') else '') +
                (f"【总花费：{school_info.get('fee_total', '')}】" if school_info.get('fee_total') else '') +

                (f"\n考试要求如下："
                 f"【GPA成绩：{school_info.get('score_gpa', '')}】" if school_info.get('score_gpa') else '') +
                (f"【ACT成绩：{school_info.get('score_act', '')}】" if school_info.get('score_act') else '') +
                (f"【SAT成绩：{school_info.get('score_sat', '')}】" if school_info.get('score_sat') else '') +
                (f"【SAT2成绩：{school_info.get('score_sat2', '')}】" if school_info.get('score_sat2') else '') +
                (f"【GRE成绩：{school_info.get('score_gre', '')}】" if school_info.get('score_gre') else '') +
                (f"【GMAT成绩：{school_info.get('score_gmat', '')}】" if school_info.get('score_gmat') else '') +
                (f"【雅思成绩：{school_info.get('score_ielts', '')}】" if school_info.get('score_ielts') else '') +
                (f"【托福成绩：{school_info.get('score_toefl', '')}】" if school_info.get('score_toefl') else '') +
                (f"【native成绩：{school_info.get('score_native', '')}】" if school_info.get('score_native') else '') +
                (f"【其他成绩：{school_info.get('score_others', '')}】" if school_info.get('score_others') else '') +

                (f"【奖学金：{school_info.get('scholarship', '')}】" if school_info.get('scholarship') else '') +
                (f"【申请材料：{school_info.get('material', '')}】" if school_info.get('material') else '') +
                (f"【申请流程：{school_info.get('recruit_flow', '')}】" if school_info.get('recruit_flow') else '')
        )

    } for school_info in search_zn_school_recruit_graduate_1_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library06_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{研究生生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【申请简介：】【录取率：】【申请人数：】【申请学期：】【申请截止时间：】【Offer发放时间：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【GPA成绩：】【ACT成绩：】【SAT成绩：】【SAT2成绩：】【GRE成绩：】【GMAT成绩：】【雅思成绩：】【托福成绩：】【native成绩：】【其他成绩：】【奖学金：】【申请材料：】【申请流程】
    '''
    database = "zn_school_recruit_graduate_2"
    search_zn_school_recruit_graduate_2_list = search_zn_school_recruit_graduate_2(limit=10)
    knowledge_base_model = [{
        "database": database,
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的本科生院校招生信息").strip()
        ),
        "input": "",
        "output": (
                (f"录取信息如下："
                 f"【申请简介：{school_info.get('introduction', '')}】" if school_info.get('introduction') else '') +
                (f"【录取率：{school_info.get('admission_rate', '')}】" if school_info.get('admission_rate') else '') +
                (f"【申请人数：{school_info.get('apply_amount', '')}】" if school_info.get('apply_amount') else '') +
                (f"【申请学期：{school_info.get('semester', '')}】" if school_info.get('semester') else '') +
                (f"【申请截止时间：{school_info.get('time_apply_deadline', '')}】" if school_info.get(
                    'time_apply_deadline') else '') +
                (f"【Offer发放时间：{school_info.get('time_offer', '')}】" if school_info.get('time_offer') else '') +

                (f"\n留学费用如下："
                 f"【申请费用：{school_info.get('fee_apply', '')}】" if school_info.get('fee_apply') else '') +
                (f"【学费：{school_info.get('fee_tuition', '')}】" if school_info.get('fee_tuition') else '') +
                (f"【书本费：{school_info.get('fee_book', '')}】" if school_info.get('fee_book') else '') +
                (f"【生活费：{school_info.get('fee_life', '')}】" if school_info.get('fee_life') else '') +
                (f"【交通费：{school_info.get('fee_traffic', '')}】" if school_info.get('fee_traffic') else '') +
                (f"【住宿费用：{school_info.get('fee_accommodation', '')}】" if school_info.get(
                    'fee_accommodation') else '') +
                (f"【其他费用：{school_info.get('fee_others', '')}】" if school_info.get('fee_others') else '') +
                (f"【总花费：{school_info.get('fee_total', '')}】" if school_info.get('fee_total') else '') +

                (f"\n考试要求如下："
                 f"【GPA成绩：{school_info.get('score_gpa', '')}】" if school_info.get('score_gpa') else '') +
                (f"【ACT成绩：{school_info.get('score_act', '')}】" if school_info.get('score_act') else '') +
                (f"【SAT成绩：{school_info.get('score_sat', '')}】" if school_info.get('score_sat') else '') +
                (f"【SAT2成绩：{school_info.get('score_sat2', '')}】" if school_info.get('score_sat2') else '') +
                (f"【GRE成绩：{school_info.get('score_gre', '')}】" if school_info.get('score_gre') else '') +
                (f"【GMAT成绩：{school_info.get('score_gmat', '')}】" if school_info.get('score_gmat') else '') +
                (f"【雅思成绩：{school_info.get('score_ielts', '')}】" if school_info.get('score_ielts') else '') +
                (f"【托福成绩：{school_info.get('score_toefl', '')}】" if school_info.get('score_toefl') else '') +
                (f"【native成绩：{school_info.get('score_native', '')}】" if school_info.get('score_native') else '') +
                (f"【其他成绩：{school_info.get('score_others', '')}】" if school_info.get('score_others') else '') +

                (f"【奖学金：{school_info.get('scholarship', '')}】" if school_info.get('scholarship') else '') +
                (f"【申请材料：{school_info.get('material', '')}】" if school_info.get('material') else '') +
                (f"【申请流程：{school_info.get('recruit_flow', '')}】" if school_info.get('recruit_flow') else '')
        )

    } for school_info in search_zn_school_recruit_graduate_2_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_college_library07_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{艺术生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【录取率：】【申请难度：】【优势专业：】【申请经验：】【明星校友：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【研究生专业：】【本科专业：】【研究生雅思成绩：】【本科雅思成绩：】【研究生托福成绩：】【本科托福成绩：】【研究生申请截止日：】【本科申请截止日期：】【研究生申请要求：】【本科申请要求：】【研究生作品集要求：】【本科作品集要求：】
    '''
    database = "zn_school_recruit_art"
    search_zn_school_recruit_graduate_2_list = search_zn_school_recruit_art(limit=10)
    knowledge_base_model = [{
        "database": database,
        "db_id": str(school_info.get('id', '')),
        "instruction": (
            (school_info.get('chinese_name', '') + " " +
             school_info.get('english_name', '') + " " +
             school_info.get('school_abbreviations', '') + "的本科生院校招生信息").strip()
        ),
        "input": "",
        "output": (
                (f"录取信息如下："
                 f"【申请简介：{school_info.get('introduction', '')}】" if school_info.get('introduction') else '') +
                (f"【录取率：{school_info.get('admission_rate', '')}】" if school_info.get('admission_rate') else '') +
                (f"【申请人数：{school_info.get('apply_amount', '')}】" if school_info.get('apply_amount') else '') +
                (f"【申请学期：{school_info.get('semester', '')}】" if school_info.get('semester') else '') +
                (f"【申请截止时间：{school_info.get('time_apply_deadline', '')}】" if school_info.get(
                    'time_apply_deadline') else '') +
                (f"【Offer发放时间：{school_info.get('time_offer', '')}】" if school_info.get('time_offer') else '') +

                (f"\n留学费用如下："
                 f"【申请费用：{school_info.get('fee_apply', '')}】" if school_info.get('fee_apply') else '') +
                (f"【学费：{school_info.get('fee_tuition', '')}】" if school_info.get('fee_tuition') else '') +
                (f"【书本费：{school_info.get('fee_book', '')}】" if school_info.get('fee_book') else '') +
                (f"【生活费：{school_info.get('fee_life', '')}】" if school_info.get('fee_life') else '') +
                (f"【交通费：{school_info.get('fee_traffic', '')}】" if school_info.get('fee_traffic') else '') +
                (f"【住宿费用：{school_info.get('fee_accommodation', '')}】" if school_info.get(
                    'fee_accommodation') else '') +
                (f"【其他费用：{school_info.get('fee_others', '')}】" if school_info.get('fee_others') else '') +
                (f"【总花费：{school_info.get('fee_total', '')}】" if school_info.get('fee_total') else '') +

                (f"\n考试要求如下："
                 f"【GPA成绩：{school_info.get('score_gpa', '')}】" if school_info.get('score_gpa') else '') +
                (f"【ACT成绩：{school_info.get('score_act', '')}】" if school_info.get('score_act') else '') +
                (f"【SAT成绩：{school_info.get('score_sat', '')}】" if school_info.get('score_sat') else '') +
                (f"【SAT2成绩：{school_info.get('score_sat2', '')}】" if school_info.get('score_sat2') else '') +
                (f"【GRE成绩：{school_info.get('score_gre', '')}】" if school_info.get('score_gre') else '') +
                (f"【GMAT成绩：{school_info.get('score_gmat', '')}】" if school_info.get('score_gmat') else '') +
                (f"【雅思成绩：{school_info.get('score_ielts', '')}】" if school_info.get('score_ielts') else '') +
                (f"【托福成绩：{school_info.get('score_toefl', '')}】" if school_info.get('score_toefl') else '') +
                (f"【native成绩：{school_info.get('score_native', '')}】" if school_info.get('score_native') else '') +
                (f"【其他成绩：{school_info.get('score_others', '')}】" if school_info.get('score_others') else '') +

                (f"【奖学金：{school_info.get('scholarship', '')}】" if school_info.get('scholarship') else '') +
                (f"【申请材料：{school_info.get('material', '')}】" if school_info.get('material') else '') +
                (f"【申请流程：{school_info.get('recruit_flow', '')}】" if school_info.get('recruit_flow') else '')
        )

    } for school_info in search_zn_school_recruit_graduate_2_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library01_data():
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
    zn_school_department_project_dict_list = search_zn_school_department_project01(limit=limit)
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
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的专业基本信息",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library02_data():
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
    2、关键时间和费用：
    【开学时间：】【申请截止时间：】【Offer发放时间：】【Offer发放截止时间：】【申请费用：】【学费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    '''
    database = "zn_school_department_project_02"
    zn_school_department_project_dict_list = search_zn_school_department_project02(limit=limit)
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
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的关键时间和费用",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library03_data():
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
    3、申请要求
    【雅思成绩：】【雅思总分：】【托福成绩：】【托福总分：】
    '''
    database = "zn_school_department_project_03"
    zn_school_department_project_dict_list = search_zn_school_department_project03(limit=limit)
    # {'id': 1, 'school_name': '麻省理工学院', 'english_name': 'Massachusetts Institute of Technology', 'school_abbreviations': '', 'chinese_name': '建筑技术-博士PhD', 'znsdp.english_name': 'PhD in Building Technology', 'school_id': 1, 'campus': None, 'ielts_score': '', 'ielts_total_score': None, 'toefl_score': '90', 'toefl_total_score': None}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"},
                     {"雅思成绩": "ielts_score"}, {"雅思总分": "ielts_total_score"},
                     {"托福成绩": "toefl_score"}, {"托福总分": "toefl_total_score"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library04_data():
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
    zn_school_department_project_dict_list = search_zn_school_department_project04(limit=limit)
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
                     {"BC要求": "bc_requirement"}, {"BC分数": "bc_score"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的本科专业申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library05_data():
    '''专业库洗入格式如下：

    a、标题信息： {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
    b、内容信息：
        5、研究生专业申请要求
        【c9均分要求：】【C9均分分数：】【211均分要求：】【211均分分数：】【985均分要求：】【985均分分数：】【非211均分要求：】【非211均分分数：】【专业背景要求：】【是否接受跨专业：】
    '''
    database = "zn_school_department_project_05"
    zn_school_department_project_dict_list = search_zn_school_department_project05(limit=limit)
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
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的研究生专业申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


def insert_major_library06_data():
    '''专业库洗入格式如下：

    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：

    b、内容信息：
    6、其它申请要求：
    【学术要求：】【申请材料：】【申请要点：】【是否减免学分：】【减免学分条件：】
    '''
    database = "zn_school_department_project_06"
    zn_school_department_project_dict_list = search_zn_school_department_project06(limit=limit)
    #     {'id': 1, 'school_name': '麻省理工学院', 'english_name': 'Massachusetts Institute of Technology', 'school_abbreviations': '', 'chinese_name': '建筑技术-博士PhD', 'znsdp.english_name': 'PhD in Building Technology', 'school_id': 1, 'campus': None, 'academic_requirement': None, 'application_materials': '1、申请表\n2、学历证明以及各科成绩单\n3、托福成绩单\n4、GRE成绩单\n5、申请费\n6、银行资金证明\n7、个人简历', 'application_elements': '', 'credit_reduction': 0, 'credit_reduction_condition': None}
    key_name_list = [{"db_id": "id"}, {"院校中文名": "school_name"}, {"院校英文名": "english_name"},
                     {"院校简称": "school_abbreviations"}, {"专业中文名": "chinese_name"},
                     {"专业英文名": "znsdp.english_name"}, {"学校id": "school_id"}, {"校区": "campus"},
                     {"学术要求": "academic_requirement"}, {"申请材料": "application_materials"},
                     {"申请要点": "application_elements"}, {"是否减免学分": "credit_reduction"},
                     {"减免学分条件": "credit_reduction_condition"}]
    dict_list = ObjectFormatter.attribute_concatenation(key_name_list, zn_school_department_project_dict_list)
    knowledge_base_model = [{
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": f"{dict.get('key_value')} 的其它申请要求",
        "input": "",
        "output": dict.get('key_value'),
        "keyword": dict.get('key_value'),
        "file_info": "",
    } for dict in dict_list]
    insert_weaviate_data_all(knowledge_base_model)


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


def manner_execution(args: list):
    if len(args) < 2:
        print("请输入参数")
        sys.exit()
    method = args[1]
    if method == "insert_college_library01_data":
        insert_college_library01_data()
    elif method == "insert_college_library02_data":
        insert_college_library02_data()
    elif method == "insert_college_library03_data":
        insert_college_library03_data()
    elif method == "insert_college_library04_data":
        insert_college_library04_data()
    elif method == "insert_college_library05_data":
        insert_college_library05_data()
    elif method == "insert_college_library06_data":
        insert_college_library06_data()
    elif method == "insert_college_library07_data":
        insert_college_library07_data()
    elif method == "insert_major_library01_data":
        insert_major_library01_data()
    elif method == "insert_major_library02_data":
        insert_major_library02_data()
    elif method == "insert_major_library03_data":
        insert_major_library03_data()
    elif method == "insert_major_library04_data":
        insert_major_library04_data()
    elif method == "insert_major_library05_data":
        insert_major_library05_data()
    elif method == "insert_major_library06_data":
        insert_major_library06_data()
    elif method == "clear_all_data":
        clear_all_data(knowledge_base_weaviate.collections_name)
    elif method == "delete_weaviate_data_by_id":
        if len(args) < 3:
            print("请输入id")
            sys.exit()
        id = args[2]
        delete_weaviate_data_by_id(id, knowledge_base_weaviate.collections_name)
    elif method == "search_weaviate_data_by_query":
        if len(args) < 3:
            print("请输入query")
            sys.exit()
        query = args[2]
        if len(args) < 4:
            limit = 10
        else:
            limit = int(args[3])
        print(search_weaviate_data_by_query(query, limit))
    elif method == "update_weaviate_data_by_id":
        if len(args) < 3:
            print("请输入id")
            sys.exit()
        id = args[2]
        if len(args) < 4:
            print("请输入properties")
            sys.exit()
        properties = json.loads(args[3])
        update_weaviate_data_by_id(id, properties)
    elif method == "delete_collection_name":
        delete_collection_name()
    elif method == "delete_by_database":
        if len(args) < 3:
            print("请输入database")
            sys.exit()
        database = args[2]
        delete_by_database(database)
    else:
        print("请输入正确的参数")
        sys.exit()


