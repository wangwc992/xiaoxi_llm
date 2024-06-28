from langchain_core.pydantic_v1 import BaseModel, Field


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
    country_name: str = Field(description="国家名称")
    school_name: str = Field(description="学校名称")
    major_name: str = Field(description="专业名称")
    gpa_req: int = Field(description="GPA要求")
    academic_degree: str = Field(description="学位")


async def search_school(check_school: CheckSchool):
    print(check_school.dict())
async def details(text:str):
    print(text)
async def information_consultant(text:str):
    print(text)
