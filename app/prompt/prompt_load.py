import os

from langchain_core.prompts import PromptTemplate


def generate_prompt(text: str) -> PromptTemplate:
    """生成包含参考数据的完整 prompt."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir,  text)
    template = PromptTemplate.from_file(file_path)
    return template
