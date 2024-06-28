from langchain_core.pydantic_v1 import BaseModel, Field


class CheckSchool(BaseModel):
    country_name: str = Field(description="国家名称")
    school_name: str = Field(description="学校名称")
    major_name: str = Field(description="专业名称")
    gpa_req: int = Field(description="GPA要求")
    academic_degree: str = Field(description="学位")


async def search_school(check_school: CheckSchool):
    print(check_school.dict())
