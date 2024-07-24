from app.common.core.langchain_client import Embedding
from app.common.utils.html_util import HtmlUtils
from app.common.utils.logging import get_logger
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_knowledge_info_data, \
    search_notice_message_data,search_school_info_basic_data
from app.database.weaviate.knowledge_base import KnowledgeBaseWeaviate
from app.common.utils.FileToText import FileToText

knowledge_base_weaviate = KnowledgeBaseWeaviate(KnowledgeBaseWeaviate.collections_name)

logger = get_logger(__name__)
file_to_text = FileToText()
# 查询起始id
start_id = 0

# 每次查询条数
limit = 1

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
            "file_info": file_to_text.urlToText(knowledge_info.get("fileurl", '') or '') if knowledge_info.get("fileurl") else "",
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
        "instruction": (school_info.get('chinese_name', '') + " " +
                        school_info.get('english_name', '') + " " +
                        school_info.get('school_abbreviations', '') + "的基本信息"),

        "input": "",
        "output": ("院校中文名：" + (school_info.get('chinese_name', '') or '') + " " +
                   "院校英文名：" + (school_info.get('english_name', '') or '') + " " +
                   "所属国家：" + (school_info.get('country_name', '') or '') + " " +
                   "所属地区：" + (school_info.get('city_path', '') or '') + " " +
                   "官网地址：" + (school_info.get('website', '') or '') + " " +
                   "申请费支付维度：" + (school_info.get("fee_dimension")) + " " +
                   "申请周期-算法统计：" + (school_info.get("apply_cycle_algorithm")) + " " +
                   "申请周期-人工配置：" + (school_info.get("apply_cycle_manual")) + " "
                   ),
        "keyword": get_string(school_info.get("chinese_name", '') or '',
                              school_info.get("english_name", '') or '',
                              school_info.get("school_abbreviations", '') or ''),
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
    pass


def insert_college_library03_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校更多信息}如下：
    b、内容信息：
    【就业率：】【毕业薪资：】【学生总数量：】【本科生数量：】【研究生数量：】【国际学生比例：】【师生比例：】【男女比例：】【院校简介：】【院校历史：】【地理位置：】【校园环境：】【学校宿舍：】【图书馆：】【学校设施：】【招生办信息：】【防疫信息：】
    '''
    pass


def insert_college_library04_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{院校择校理由}如下：
    b、内容信息：
    【择校理由：】【学校特色：】【强势专业：】【热门专业：】【院系设置：】【好评项：】【差评项：】
    '''
    pass


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
    pass


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
    pass


def insert_college_library07_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{本科生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【申请简介：】【录取率：】【申请人数：】【申请学期：】【申请截止时间：】【Offer发放时间：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【GPA成绩：】【ACT成绩：】【SAT成绩：】【SAT2成绩：】【GRE成绩：】【GMAT成绩：】【雅思成绩：】【托福成绩：】【native成绩：】【其他成绩：】【奖学金：】【申请材料：】【申请流程】
    '''
    pass


def insert_college_library08_data():
    '''院校库洗入格式如下
    a、标题信息：
    {院校中文名}{院校英文名}{院校简称}的{艺术生院校招生信息}如下：
    b、内容信息：
    1、录取信息如下：【录取率：】【申请难度：】【优势专业：】【申请经验：】【明星校友：】
    2、留学费用如下：【申请费用：】【学费：】【书本费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】
    3、考试要求如下：
    【研究生专业：】【本科专业：】【研究生雅思成绩：】【本科雅思成绩：】【研究生托福成绩：】【本科托福成绩：】【研究生申请截止日：】【本科申请截止日期：】【研究生申请要求：】【本科申请要求：】【研究生作品集要求：】【本科作品集要求：】
    '''
    pass


def insert_major_library01_data():
    '''专业库洗入格式如下：

   a、标题信息：
   {院校中文名}{院校英文名}{院校简称}的{{专业英文}{专业中文}信息资料如下：
   b、内容信息：

   1、专业基本信息：
   【所属院系：】【所属校区：】【*专业中文名：】【*专业英文名：】【课程编码：】【*专业链接：】【*全日制学制：】【专业小方向：】【非全日制：】【*学位名称：】【*学位类型：】【*学位等级：】【专业简称 】【开学时间：】【所在城市：】【专业介绍：】【专业分类】

   2、关键时间和费用：
   【开学时间：】【申请截止时间：】【Offer发放时间：】【Offer发放截止时间：】【申请费用：】【学费：】【生活费：】【交通费：】【住宿费用：】【其他费用：】【总花费：】

   3、申请要求
   【雅思成绩：】【雅思总分：】【托福成绩：】【托福总分：】

   4、本科专业申请要求
   【ATAR要求：】【ATAR分数：】【SAT要求：】【SAT分数：】【UKAlevel三科要求：】【UKAlevel三科分数：】【ACT要求：】【ACT分数：】【分数一:
   】【分数二:  】【分数三:  】【UKAlevel四科要求：】【UKAlevel四科分数：】【AP要求：】【AP分数：】【IB要求：】【IB分数：】【高考要求：】
   【高考分数：】【OSSD要求：】【OSSD分数：】【BC要求：】【BC分数：】

   5、研究生专业申请要求
   【c9均分要求：】【C9均分分数：】【211均分要求：】【211均分分数：】【985均分要求：】【985均分分数：】【非211均分要求：】【非211均分分数：】【专业背景要求：】【是否接受跨专业：】

   6、其它申请要求：
   【学术要求：】【申请材料：】【申请要点：】【是否减免学分：】【减免学分条件：】'''

    pass


def insert_weaviate_data_all(knowledge_base_model: list):
    '''
    将t_knowledge_info表的全部数据插入weaviate数据
    :return:
    '''
    texts = [doc['instruction'] for doc in knowledge_base_model]

    doc_vecs = Embedding.embed_documents(texts)

    uuid_list = knowledge_base_weaviate.basth_insert_data(properties_list=knowledge_base_model, vecs=doc_vecs)
    logger.info(
        "插入大于id:%s的%s条的数据%s" % (knowledge_base_model[0].get('db_id'), len(knowledge_base_model), uuid_list))


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


if __name__ == '__main__':
    #database = "t_knowledge_info"
    #insert_t_knowledge_info_data()

    # clear_all_data(database)
    # delete_weaviate_data_by_id("155")
    # search_weaviate_data_by_query("英国", 10)
    # update_weaviate_data_by_id("7e08b804-8b7c-47f8-a92b-29256d274266", {
    #     "database": "t_knowledge_info",
    #     "db_id": "156",
    #     "input": "",
    #     "instruction": "英国 约克大学（英国） 院校介绍 请问英国约克大学申请UNSW商科硕士需要达到多少分呢？",
    #     "output": "郝丽君12 2023-03-22 10:22:41 英国本科学历达到58分，是符合USNW要求65%的硕士录取要求的。如分数达不到，可考虑申请GC项目进行过渡。",
    #     "state": 1
    # })
    #insert_institution_information_data()
    insert_college_library01_data()
