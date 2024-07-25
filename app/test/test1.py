from app.common.utils.object_utils import ObjectFormatter
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_zn_school_department_project02, \
    search_zn_school_department_project03, search_zn_school_department_project04, search_zn_school_department_project05, \
    search_zn_school_department_project06

database = "zn_school_department_project_03"
zn_school_department_project_dict_list = search_zn_school_department_project06(limit=300)
print(zn_school_department_project_dict_list)
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
print(knowledge_base_model)