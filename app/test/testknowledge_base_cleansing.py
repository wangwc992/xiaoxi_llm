import os

import pandas as pd

from app.common.core.langchain_client import Embedding
from app.common.utils.object_utils import ObjectFormatter
from app.data_cleansing.knowledge_base_cleansing import file_to_text
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_school_info_basic_data, \
    search_school_info_ranking_data, search_zn_school_recruit_art, search_knowledge_info_data, \
    search_notice_message_data
from app.database.weaviate.knowledge_base import knowledge_base_weaviate


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

    texts = [doc['instruction'] for doc in knowledge_base_model]

    doc_vecs = Embedding.embed_documents(texts)

    uuid_list = knowledge_base_weaviate.basth_insert_data(properties_list=knowledge_base_model, vecs=doc_vecs)
    print(uuid_list)


def insert_college_library07_data(start_id: int = 0, limit: int = 10):
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{艺术生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【录取率：】【申请难度：】【优势专业：】【申请经验：】【明星校友：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【研究生专业：】【本科专业：】【研究生雅思成绩：】【本科雅思成绩：】【研究生托福成绩：】【本科托福成绩：】【研究生申请截止日：】【本科申请截止日期：】【研究生申请要求：】【本科申请要求：】【研究生作品集要求：】【本科作品集要求：】

# `id` int(11) NOT NULL AUTO_INCREMENT,
# `school_id` int(11) DEFAULT NULL COMMENT '院校表ID',
# `strong_majors` varchar(500) DEFAULT NULL COMMENT '优势专业',
# `admission_rate` varchar(200) DEFAULT NULL COMMENT '录取率',
# `fee_apply` varchar(200) DEFAULT NULL COMMENT '申请费用',
# `fee_tuition` varchar(200) DEFAULT NULL COMMENT '学费',
# `fee_book` varchar(200) DEFAULT NULL COMMENT '书本费',
# `fee_life` varchar(200) DEFAULT NULL COMMENT '生活费',
# `fee_traffic` varchar(200) DEFAULT NULL COMMENT '交通费',
# `fee_accommodation` varchar(200) DEFAULT NULL COMMENT '住宿费用',
# `fee_others` varchar(200) DEFAULT NULL COMMENT '其他费用',
# `fee_total` varchar(200) DEFAULT NULL COMMENT '总花费',
# `graduate_majors` text COMMENT '研究生专业',
# `graduate_score_ielts` varchar(200) DEFAULT NULL COMMENT '研究生雅思成绩',
# `graduate_score_toefl` varchar(200) DEFAULT NULL COMMENT '研究生托福成绩',
# `graduate_requirements` text COMMENT '研究生申请要求',
# `graduate_works_requirement` text COMMENT '研究生作品集要求',
# `graduate_apply_deadline` varchar(200) DEFAULT NULL COMMENT '研究生申请截止日期',
# `undergraduate_majors` text COMMENT '本科专业',
# `undergraduate_score_ielts` varchar(200) DEFAULT NULL COMMENT '本科雅思成绩',
# `undergraduate_score_toefl` varchar(200) DEFAULT NULL COMMENT '本科托福成绩',
# `undergraduate_requirements` text COMMENT '本科申请要求',
# `undergraduate_works_requirement` text COMMENT '本科作品集要求',
# `undergraduate_apply_deadline` varchar(200) DEFAULT NULL COMMENT '本科申请截止日期',
# `difficulty_name` varchar(20) DEFAULT NULL COMMENT '申请难度',
# `apply_experience` text COMMENT '申请经验',
# `alumni` text COMMENT '明星校友',
# `delete_status` int(1) DEFAULT '0' COMMENT '是否删除  0-未删除,1-已删除',
# `create_by` int(11) NOT NULL COMMENT '创建人',
# `update_by` int(11) NOT NULL COMMENT '更新人',
# `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
# `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
# `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
# `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
# `application_fee_value` decimal(8,2) DEFAULT NULL COMMENT '申请费值',
# `currency_id` int(11) DEFAULT NULL COMMENT '币种id',
# PRIMARY KEY (`id`),
# UNIQUE KEY `uk_school` (`school_id`) USING BTREE
# ) ENGINE=InnoDB AUTO_INCREMENT=837 DEFAULT CHARSET=utf8mb4 COMMENT='院校艺术生招生表';
    '''
    database = "zn_school_recruit_art"
    search_zn_school_recruit_graduate_2_list = search_zn_school_recruit_art(id=start_id, limit=limit)
    if not search_zn_school_recruit_graduate_2_list:
        # 抛出异常，终止程序
        raise Exception(f"院校库艺术生院校招生信息数据已全部洗入")
    title01 = "标题信息"
    key_name_list01 = [{'院校中文名': 'chinese_name'}, {'院校英文名': 'english_name'},
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
        "database": database,
        "db_id": dict.get('db_id'),
        "instruction": dict.get("value") + "的艺术生院校招生信息",
        "input": "",
        "output": f"""{title01}: {dict_list01[i].get("key_value")}\n{title02}: {dict_list02[i].get("key_value")}\n{title03}: {dict_list03[i].get("key_value")}\n{title04}: {dict_list04[i].get("key_value")}""",
        "keyword": "",
        "file_info": "",
    } for i, dict in enumerate(dict_list01)]

    print(knowledge_base_model)


def insert_t_knowledge_info_data(start_id: int = 0, limit: int = 100):
    '''知识库
    1、问答/文件相关知识库内容洗入向量库时注意事项：
    a、标题洗入要求： {国家}{院校}{问题类型}{问题是否常见}的以下问题：{标题内容}：

    b、答案洗入要求： {回复顾问}于{日期}回复内容如下：{问题答案}

    如果有文件，则在{问题答案}后方增加：该回答引用了以下文件，文件名：{文件名}，文件内容：{文件内容（pdf、excel、word提取信息，图片ocr信息）}
    eg：

    标题为： 澳洲伍伦贡大学入学要求常见问题：老师，卧龙岗新开的护理硕士学费出来了吗？
    内容为： 李薇于2024-06-07 16:26回复内容如下：两年总学费是74664'''
    database = "t_knowledge_info"
    knowledge_info_dict_list = search_knowledge_info_data(id=50, limit=limit)
    if not knowledge_info_dict_list:
        # logger.info(f"{database}知识库数据已全部洗入")
        # 抛出异常，终止程序
        raise Exception(f"{database}知识库数据已全部洗入")
    knowledge_base_model = []
    for knowledge_info in knowledge_info_dict_list:
        content = knowledge_info.get("content", "")
        if knowledge_info.get("fileurl"):
            print(knowledge_info["fileurl"])
            content += file_to_text.urlToText(knowledge_info["fileurl"])
        if knowledge_info.get("type") == 1:
            name = knowledge_info.get("name")
        else:
            name = knowledge_info.get("filename")
        db_id = str(knowledge_info["id"])
        instruction = f'{knowledge_info["country"]}{knowledge_info["school"]}{knowledge_info["class"]}的以下问题: {name}'
        output = f'{knowledge_info["founder"]}于{knowledge_info["replyerTime"].strftime("%Y-%m-%d %H:%H:%M")}回复内容如下：{content}'
        link = {"url": f'https://knowledge.xiaoxiedu.com/details/filedetails?id={db_id}',
                "title": name}

        knowledge_base_model.append({
            "database": database,
            "db_id": db_id,
            "instruction": instruction,
            "input": "",
            "output": output,
            "keyword": f'{knowledge_info["country"]}{knowledge_info["school"]}{knowledge_info["class"]}',
            "file_info": "",
            "url": link
        })
    print(knowledge_base_model)


def insert_institution_information_data(start_id: int = 0, limit: int = 100):
    '''小希平台院校资讯
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}于{时间}的{资讯类型}的{标题}资讯。

    b、资讯内容：
    以下为资讯正文：{资讯内容}
    以下为资讯附件：{附件标题}{附件内容}
    以下为资料正文中附件{附件内容}。
    '''
    notice_massage_dict_list = search_notice_message_data(id=start_id, limit=limit)
    if not notice_massage_dict_list:
        # 抛出异常，终止程序
        raise Exception(f"小希平台院校资讯数据已全部洗入")
    knowledge_base_model = []

    for notice_massage in notice_massage_dict_list:
        notice_create_time = notice_massage.get('notice_create_time').strftime("%Y-%m-%d %H:%M:%S")
        db_id = str(notice_massage.get('notice_id'))
        instruction_list = [notice_massage.get('school_name', ''), notice_massage.get('school_english_name', ''),
                            notice_create_time, notice_massage.get('notice_category', ''),
                            notice_massage.get('notice_title', '')]
        instruction = " ".join(instruction_list)
        file_info = ""
        if notice_massage.get('attachment_url'):
            # file_info = get_file_info(notice_massage.get('attachment_url'))
            file_info = "************************"
        output = f"""以下是资讯正文：{notice_massage.get('notice_summary', '')}\n 
        以下是资讯附件：{notice_massage.get('attachment_name', '')}\n  {file_info}\n
        以下是资料正文中附件{notice_massage.get('notice_title', '')}。"""

        knowledge_base_model.append({
            "database": "notice_message",
            "db_id": db_id,
            "instruction": instruction,
            "input": "",
            "output": output,
            "keyword": '',
            "file_info": file_info,
        })

        print(knowledge_base_model)
if __name__ == '__main__':
    # insert_college_library02_data()
    insert_t_knowledge_info_data(start_id=50,limit=10)
