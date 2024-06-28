from langchain_core.tools import StructuredTool, BaseTool
from pydantic import ValidationError

from typing import Optional, Dict, Any
from langchain_core.pydantic_v1 import BaseModel, Field

from app.tools.school.check_school import search_school


class Action(BaseModel):
    name: str = Field(description="Tool name")
    args: Optional[Dict[str, Any]] = Field(description="Tool input arguments, containing arguments names and values")


def __find_tool(tools: list, tool_name: str) -> Optional[BaseTool]:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    return None


def exec_action(tools, action: Action) -> str:
    # 查找工具
    tool = __find_tool(tools, action.name)
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
    description="判断是否想留学，根据学生提供的信息，查询学校信息",
)
