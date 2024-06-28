from langchain_community.llms import VLLM
import asyncio
llm = VLLM(
    model="/root/autodl-tmp/llm/Qwen2-7B-Instruct",
    trust_remote_code=True,  # mandatory for hf models
    max_new_tokens=128,
    top_k=10,
    top_p=0.95,
    temperature=0.8,
)

print(llm.invoke("What is the capital of France ?"))

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

llm_chain = LLMChain(prompt=prompt, llm=llm)

question = "Who was the US president in the year the first Pokemon game was released?"

print(llm_chain.invoke(question))

async def main():
    print(llm_chain.acall(question))

if __name__ == "__main__":
    # result = llm_with_tools.invoke("我想去留学，推荐学校和专业")
    # print(result)
    for i in range(10):
        asyncio.run(main())