from app.common.database.mysql.xxlxdb.school.zn_school_department_project_mapper import ZnSchoolDepartmentProject, \
    CheckSchool
from app.common.database.weaviate.Knowledge_ik_index_mapper import KnowledgeIkIndexMapper
from app.prompt.prompt_load import generate_prompt


def search_school(check_school: CheckSchool):
    zn_school_department_project_dict = ZnSchoolDepartmentProject.select_by_check_school(check_school)
    # 遍历赋值的方式转换为CheckSchool对象列表
    check_school_list = []
    if zn_school_department_project_dict is None:
        return "没有找到符合条件的学校和专业信息"
    for zn_school_department_project in zn_school_department_project_dict:
        check_school = CheckSchool(
            country_name=zn_school_department_project['country_name'],
            school_name=zn_school_department_project['school_chinese_name'] + "/" + zn_school_department_project[
                'school_english_name'],
            major_name=zn_school_department_project['major_chinese_name'] + "/" + zn_school_department_project[
                'major_english_name'],
            degree_type=zn_school_department_project['degree_type']
        )
        check_school_list.append(check_school)
    template = generate_prompt("search_school.txt")
    prompt = template.format(check_school_info=check_school, check_school_list=check_school_list)
    return prompt


def details(text: str):
    prompt = KnowledgeIkIndexMapper.generate_prompt(text)
    return prompt


def student_matriculate_case(text: str):
    prompt = KnowledgeIkIndexMapper.generate_prompt(text)
    return prompt


async def information_consultant(text: str):
    print(text)
