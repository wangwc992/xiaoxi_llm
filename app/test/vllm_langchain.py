import asyncio
from langchain_community.llms import VLLM
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool

# 配置 VLLM 模型
llm = VLLM(
    model="/root/autodl-tmp/llm/Qwen2-7B-Instruct",
    trust_remote_code=True,  # 使用 Hugging Face 远程代码
    max_new_tokens=128,
    top_k=10,
    top_p=0.95,
    temperature=0.8,
)
# 创建 PromptTemplate 和 LLMChain
template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)
llm_chain = LLMChain(prompt=prompt, llm=llm)


# 异步函数来处理请求
async def async_invoke_llm_chain(question):
    response = await llm_chain.acall(question)  # 使用 acall() 异步调用
    return response


# 主函数，创建多个并发请求
async def main():
    questions = [
        "Who was the US president in the year the first Pokemon game was released?" for _ in range(20)
    ]

    tasks = [async_invoke_llm_chain(question) for question in questions]
    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses):
        print(f"Response {i + 1}: {response}")

def intelligent_calibration(text:str):
    print(text)

intelligent_calibration = StructuredTool.from_function(
    func=intelligent_calibration,
    name="intelligentCalibration",
    description="学生想去留学，推荐学校和专业",
)
tools = [
    intelligent_calibration
]

# llm_with_tools = llm_chain.bind_tools(tools) | {
#     "functions": JsonOutputToolsParser(),
#     "text": StrOutputParser()
# }
# 运行异步主函数

if __name__ == "__main__":
    # result = llm_with_tools.invoke("我想去留学，推荐学校和专业")
    # print(result)
    for i in range(10):
        asyncio.run(main())
