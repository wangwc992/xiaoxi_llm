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
    description=(
        "The `searchSchool` tool is designed to identify whether the user has provided specific information "
        "about their target study abroad institutions or programs. It evaluates the user's input to determine "
        "if there is a clear mention of the country, school, or major they are interested in. "
        "If the user specifies detailed and concrete information (e.g., country name, school name, major), "
        "the tool can directly proceed to check these details. "
        "Examples: 'Bachelor's in Computer Science at the University of Sydney', 'I have an undergraduate degree'."
    )
)

details_tool = StructuredTool.from_function(
    func=details,
    name="details",
    description=(
        "The `details` tool provides detailed explanations and information based on specific queries about "
        "universities, programs, and application requirements. It offers in-depth responses to user inquiries "
        "regarding course structures, program characteristics, application requirements, fee waivers, and GPA thresholds. "
        "Examples: 'How is the Computer Science program at the University of Sydney?', 'Details on the Financial program at the University of Sydney', "
        "'Does the University of Sydney waive application fees?', 'Advice for a Tsinghua graduate with a GPA of 3.5 applying to the University of Sydney's Financial program', "
        "'Can a GPA of 3.5 qualify for the University of Sydney's Financial program?'."
    )
)

student_matriculate_case_tool = StructuredTool.from_function(
    func=student_matriculate_case,
    name="studentMatriculateCase",
    description=(
        "The `details` tool provides detailed explanations and information based on specific queries about "
        "universities, programs, and application requirements. It offers in-depth responses to user inquiries "
        "regarding course structures, program characteristics, application requirements, fee waivers, and GPA thresholds. "
        "Examples: 'How is the Computer Science program at the University of Sydney?', 'Details on the Financial program at the University of Sydney', "
        "'Does the University of Sydney waive application fees?', 'Advice for a Tsinghua graduate with a GPA of 3.5 applying to the University of Sydney's Financial program', "
        "'Can a GPA of 3.5 qualify for the University of Sydney's Financial program?'."
    )
)

information_consultant_tool = StructuredTool.from_function(
    func=information_consultant,
    name="informationConsultant",
    description="没有命中其他的function calling时，调用这个function",
)
