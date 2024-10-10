from app.database.mysql.mysql_client import xxlxdb
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_model import IntentionStudyAbroad


def getDepartmentProjectList(intention_study_abroad: IntentionStudyAbroad):
    """"""
    sql = """
        SELECT t1.id, t1.chinese_name,t1.degree_type,t4.english_name,t1.length_of_schoolings,t1.length_of_full,t1.opening_month FROM zn_school_department_project t1
        INNER JOIN zn_school_department_project_category t2 ON t2.zsdp_id = t1.id
        INNER JOIN zn_school_major_category t3 ON t3.id = t2.category_id
        INNER JOIN zn_school_info t4 ON t4.id = t1.school_id
        INNER JOIN zn_school_rank t5 ON t5.school_id = t4.id
        WHERE t2.category_id = 1
        AND t4.country_name = '澳大利亚' 
        AND t5.world_rank_qs <= 50 
        AND t1.degree_type = '博士' 
        AND t4.english_name = 'UNSW Sydney' 
        AND (FIND_IN_SET('3/年', length_of_schoolings) OR length_of_full = '3.5年')
        AND opening_month LIKE '%-5,%'
    """

    return xxlxdb.execute_all2dict(sql)
