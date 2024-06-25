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
    reference_data = "\n\n".join([f"Reference data {n + 1}: {response_list[n].output}"
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

    results_generator = engine.generate(prompt_text, sampling_params, request_id)

    final_output = None
    async for request_output in results_generator:
        final_output = request_output

    assert final_output is not None
    text_outputs = [output.text for output in final_output.outputs]
    ret = {"prompt": prompt_text, "text": text_outputs}
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

    first_chunk_time = None
    start_time = time.time()  # 记录开始时间

    async for request_output in results_generator:
        if first_chunk_time is None:
            first_chunk_time = time.time()  # 记录第一个流式输出的时间

        # 从 request_output 中提取所需的信息
        metrics = request_output.metrics

        text_outputs = [output.text for output in request_output.outputs]
        ret = {"text": text_outputs}
        yield (json.dumps(ret) + "\0").encode("utf-8")

    end_time = time.time()  # 记录结束时间

    # 格式化时间
    start_time_formatted = datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
    first_chunk_time_formatted = datetime.fromtimestamp(first_chunk_time).strftime(
        '%H:%M:%S') if first_chunk_time else 'N/A'
    end_time_formatted = datetime.fromtimestamp(end_time).strftime('%H:%M:%S')

    # 记录时间信息，可以是日志、文件或其他存储形式
    print(f"Request started at {start_time_formatted}")
    print(f"First chunk sent at {first_chunk_time_formatted}")
    print(f"Request ended at {end_time_formatted}")

    print(metrics)
    print(type(metrics))

    # 格式化各个时间点
    arrival_time = datetime.fromtimestamp(metrics.arrival_time).strftime('%H:%M:%S')
    first_scheduled_time = datetime.fromtimestamp(metrics.first_scheduled_time).strftime('%H:%M:%S')
    first_token_time = datetime.fromtimestamp(metrics.first_token_time).strftime('%H:%M:%S')
    last_token_time = datetime.fromtimestamp(metrics.last_token_time).strftime('%H:%M:%S')
    finished_time = datetime.fromtimestamp(metrics.finished_time).strftime('%H:%M:%S')

    # 计算时间间隔
    time_in_queue = metrics.time_in_queue
    time_to_first_token = metrics.first_token_time - metrics.first_scheduled_time
    generation_duration = metrics.last_token_time - metrics.first_token_time
    total_duration = metrics.finished_time - metrics.arrival_time

    # 一行输出所有信息
    print(
        f"到达时间: {arrival_time}, "
        f"首次调度时间: {first_scheduled_time}, "
        f"在队列中的时间: {time_in_queue:.3f} 秒, "
        f"首次生成令牌时间: {first_token_time}, "
        f"从调度到生成第一个令牌的时间: {time_to_first_token:.3f} 秒, "
        f"最后一个令牌生成时间: {last_token_time}, "
        f"生成所有令牌的时间: {generation_duration:.3f} 秒, "
        f"请求完成时间: {finished_time}, "
        f"从请求到达到处理完成的总时间: {total_duration:.3f} 秒"
    )


@router.post("/generate")
async def generate(request: Request) -> Response:
    """生成文本或流式返回生成的文本."""
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")

    # 调用 chat2 来流式返回结果
    return StreamingResponse(stream_text(prompt))

    # 如果需要直接返回结果而不是流式返回，则取消注释下面的代码
    # result = await generate_text(prompt)
    # return Response(content=json.dumps(result), media_type="application/json")
