import os
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from app.common.database.mysql.school.zn_school_department_project_mapper import ZnSchoolDepartmentProject


class CheckSchool(BaseModel):
    """
       CheckSchool 是一个数据验证和解析类，用于确定是否需要查询数据库以获取关于指定学校和专业的详细信息。

       属性:
       - country_name (str): 国家名称，用于指定查询的国家。
       - school_name (str): 学校名称，用于指定查询的学校。
       - major_name (str): 专业名称，用于指定查询的专业。
       - gpa_req (int): GPA 要求，用于确定特定专业的入学 GPA 要求。
       - academic_degree (str): 学位类型，用于指定查询的学位（如本科、硕士、博士）。

       功能:
       - 该类通过验证用户的输入来帮助系统判断是否需要进行数据库查询。
       - 如果用户提供的输入信息足够完整和具体，可以直接使用这些信息而无需额外的数据库查询。
       - 如果用户的输入信息不完整或需要进一步验证，该类的实例化对象可以指示系统从数据库中检索所需的详细信息。
       """
    country_name: Optional[str] = Field(description="国家名称")
    school_name: Optional[str] = Field(description="学校名称")
    major_name: Optional[str] = Field(description="专业名称")
    gpa_req: Optional[int] = Field(description="GPA要求")
    degree_type: Optional[str] = Field(description="学位")


def search_school(check_school: CheckSchool):
    zn_school_department_project_dict = ZnSchoolDepartmentProject.select_by_check_school(check_school)
    # 遍历赋值的方式转换为CheckSchool对象列表
    check_school_list = []
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


async def details(text: str):
    print(text)


async def information_consultant(text: str):
    print(text)


def generate_prompt(text: str) -> PromptTemplate:
    """生成包含参考数据的完整 prompt."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../../prompt/' + text)
    template = PromptTemplate.from_file(file_path)
    return template
