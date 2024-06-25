import os
import json
import time
from datetime import datetime

from fastapi import Request, APIRouter, Response
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid
from langchain_core.prompts import PromptTemplate

from app.common.core.langchain_client import VllmClient
from app.common.database.weaviate.Knowledge_ik_index_mapper import KnowledgeIkIndexMapper

router = APIRouter(prefix="/chat")

# 初始化全局服务实例
knowledgeIkIndexService = KnowledgeIkIndexMapper()
engine = VllmClient.engine


@router.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


async def generate_prompt(text: str) -> str:
    """生成包含参考数据的完整 prompt."""
    response_list = knowledgeIkIndexService.search_hybrid(text, 10)
    reference_data = "\n\n".join([f"Reference data {n + 1}: {response_list[n].instruction}————{response_list[n].output}"
                                  for n in range(len(response_list))])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../../prompt/knowledge_prompt.txt')
    template = PromptTemplate.from_file(file_path)
    prompt = template.format(input=text, reference_data=reference_data)

    return prompt


async def generate_text(prompt_text: str) -> dict:
    """生成文本."""
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.8,
        repetition_penalty=1.05,
        max_tokens=2048
    )
    request_id = random_uuid()
    reference_data = await generate_prompt(prompt_text)
    results_generator = engine.generate(reference_data, sampling_params, request_id)

    final_output = None
    async for request_output in results_generator:
        final_output = request_output

    assert final_output is not None
    text_outputs = [output.text for output in final_output.outputs]
    ret = {"reference_data": reference_data, "text": text_outputs[0]}
    return ret


async def stream_text(prompt_text: str) -> AsyncGenerator[bytes, None]:
    """流式生成文本."""
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.8,
        repetition_penalty=1.05,
        max_tokens=2048
    )
    request_id = random_uuid()
    # 使用generate_prompt生成完整的prompt
    prompt_text = await generate_prompt(prompt_text)
    results_generator = engine.generate(prompt_text, sampling_params, request_id)


    async for request_output in results_generator:
        # 从 request_output 中提取所需的信息
        text_outputs = [output.text for output in request_output.outputs]
        ret = {"text": text_outputs}
        yield (json.dumps(ret) + "\0").encode("utf-8")


@router.post("/generate")
async def generate(request: Request) -> Response:
    """生成文本或流式返回生成的文本."""
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")

    # 调用 chat2 来流式返回结果
    # return StreamingResponse(stream_text(prompt))

    # 如果需要直接返回结果而不是流式返回，则取消注释下面的代码
    result = await generate_text(prompt)
    return Response(content=json.dumps(result), media_type="application/json")

@router.post("/stream")
async def stream(request: Request) -> Response:
    """生成文本或流式返回生成的文本."""
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")

    # 调用 chat2 来流式返回结果
    return StreamingResponse(stream_text(prompt))
