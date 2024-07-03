from app.common.core.langchain_client import LangChain
from app.tools.tools import check_school_tool, details_tool, information_consultant_tool

tools = [check_school_tool, details_tool, information_consultant_tool]
llm_with_tools = LangChain(tools=tools)
query = [
    # 原始问题
    "悉尼大学的计算机专业怎么样？",
    "悉尼大学金融专业？",
    "悉尼大学免申请费详情？",
    "清华毕业 GPA 3.5 想去悉尼大学金融专业有什么推荐？",
    "GPA 3.5 可以申请悉尼大学金融专业吗？",
    "新南威尔士雅思机考可以吗",
    "悉尼大学本科计算机专业？",
    "墨尔本大学新生选课？",
    "我本科学历",
    "悉尼大学的计算机专业有哪些？",
    "悉尼大学的计算机专业详情",
    "悉尼大学医学专业怎么样",
    "悉尼排名前十的计算机专业",
    "悉尼大学配额",
    "上海海洋大学，文化产业管理，绩点2.0，申请澳大利亚硕士",
    "悉尼大学本科计算机专业？",
    "悉尼大学的计算机专业有那些？",
    "悉尼大学的学费是多少？",
    "GPA 3.0 可以申请悉尼大学的计算机科学专业吗？",
    "我有两年的工作经验，想申请悉尼大学的计算机硕士，有什么建议吗？",
    "悉尼大学有哪些热门专业？",
    "悉尼大学和墨尔本大学的计算机专业哪个好？",
    "悉尼大学本科国际学生的入学要求是什么？",
    "如何申请悉尼大学的奖学金？",
    "阿德对澳门的分数要求？",
    "我想了解悉尼大学的宿舍情况",
    "悉尼大学的计算机专业就业前景怎么样？",
    "悉尼大学的计算机科学硕士项目如何？",
    "澳洲50分申什么硕士？",
    "悉尼大学本科计算机专业有哪些课程？"
]

for q in query:
    result = llm_with_tools.invoke_tools(q)
    invoked_tools = [tool.get("name") for tool in result.tool_calls]
    print(q, invoked_tools)
