import os
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from app.common.database.mysql.school.zn_school_department_project_mapper import ZnSchoolDepartmentProject
from app.common.database.weaviate.Knowledge_ik_index_mapper import KnowledgeIkIndexMapper
from app.prompt.prompt_load import generate_prompt


class CheckSchool(BaseModel):

    country_name: Optional[str] = Field(description="意向国家(中文)")
    school_name: Optional[str] = Field(description="意向学校名称(中文)")
    major_name: Optional[str] = Field(description="意向专业名称")
    gpa_req: Optional[int] = Field(description="最低 GPA 要求")
    degree_type: Optional[str] = Field(description="查询的学位类型（如本科、硕士、博士）")
    #     背景学历，背景国家，背景毕业院校
    background_degree: Optional[str] = Field(description="背景学历")
    background_country: Optional[str] = Field(description="背景国家")
    background_school: Optional[str] = Field(description="背景毕业院校")



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


