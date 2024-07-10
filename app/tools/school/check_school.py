from app.common.database.mysql.xxlxdb.school.zn_school_department_project_mapper import ZnSchoolDepartmentProject, \
    CheckSchool
from app.common.database.weaviate.Knowledge_ik_index_mapper import KnowledgeIkIndexMapper
from app.prompt.prompt_load import generate_prompt
from app.services.xxlxdb.school.zn_school_department_project_service import get_school_Project_data


def search_school(check_school: CheckSchool):
    school_Project_data = get_school_Project_data(check_school)
    # 遍历赋值的方式转换为CheckSchool对象列表

    template = generate_prompt("search_school.txt")
    prompt = template.format(check_school_info=check_school, check_school_list=school_Project_data)
    return prompt


def details(text: str):
    prompt = KnowledgeIkIndexMapper.generate_prompt(text)
    return prompt


def student_matriculate_case(text: str):
    prompt = KnowledgeIkIndexMapper.generate_prompt(text)
    return prompt


async def information_consultant(text: str):
    print(text)
