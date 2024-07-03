from langchain_core.tools import StructuredTool, BaseTool
from pydantic import ValidationError

from typing import Optional, Dict, Any
from langchain_core.pydantic_v1 import BaseModel, Field

from app.tools.school.check_school import search_school, details, information_consultant, student_matriculate_case


class Action(BaseModel):
    name: str = Field(description="Tool name")
    args: Optional[Dict[str, Any]] = Field(description="Tool input arguments, containing arguments names and values")


def find_tool(tools: list, tool_name: str) -> Optional[BaseTool]:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    return None


def exec_action(tools, action: Action) -> str:
    # 查找工具
    tool = find_tool(tools, action.name)
    if tool is None:
        observation = (
            f"Error: 找不到工具或指令 '{action.name}'. "
            f"请从提供的工具/指令列表中选择，请确保按对顶格式输出。"
        )
    else:
        try:
            # 执行工具
            observation = tool.run(action.args)
        except ValidationError as e:
            # 工具的入参异常
            observation = (
                f"Validation Error in args: {str(e)}, args: {action.args}"
            )
        except Exception as e:
            # 工具执行异常
            observation = f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"

    return observation


check_school_tool = StructuredTool.from_function(
    func=search_school,
    name="searchSchool",
    description='''
    This tool is used to gather detailed information about various educational institutions and their academic programs. It helps users search for schools, explore available majors and courses, understand specific program details, and check admission requirements. Use this tool to:

Find out what academic programs (e.g., majors, minors, specializations) are offered by different schools.
Get detailed descriptions of particular programs, including information about the curriculum and course offerings.
Evaluate the suitability of certain institutions for your academic and career goals.
Compare admission criteria for specific programs at various schools.This tool is used to gather detailed information about various educational institutions and their academic programs. It helps users search for schools, explore available majors and courses, understand specific program details, and check admission requirements. Use this tool to:

Find out what academic programs (e.g., majors, minors, specializations) are offered by different schools.
Get detailed descriptions of particular programs, including information about the curriculum and course offerings.
Evaluate the suitability of certain institutions for your academic and career goals.
Compare admission criteria for specific programs at various schools.
    '''
)

details_tool = StructuredTool.from_function(
    func=details,
    name="details",
    description='''
    This tool provides comprehensive details about specific aspects of educational institutions. It covers topics like tuition fees, application processes, campus facilities, scholarships, and more. It is particularly useful for users seeking in-depth information on specific queries related to the logistics and details of studying at particular institutions
    '''
)

student_matriculate_case_tool = StructuredTool.from_function(
    func=student_matriculate_case,
    name="studentMatriculateCase",
    description="()"
)

information_consultant_tool = StructuredTool.from_function(
    func=information_consultant,
    name="informationConsultant",
    description="没有命中其他的function calling时，调用这个function",
)
