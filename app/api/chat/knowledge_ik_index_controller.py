import os

from fastapi import Request
from fastapi.responses import Response
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

from fastapi import APIRouter
from langchain_core.prompts import PromptTemplate

from app.common.core.langchain_client import VllmClient
from app.common.database.weaviate.Knowledge_ik_index_mapper import KnowledgeIkIndexMapper

router = APIRouter(prefix="/chat")

knowledgeIkIndexService = KnowledgeIkIndexMapper()
engine = VllmClient.llm


@router.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


async def chat(text: str):
    response_list = knowledgeIkIndexService.search_hybrid(text, 10)
    reference_data = "\n\n".join([f"reference data{n + 1}: {response_list[n].output}"
                                  for n in range(len(response_list))])
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../../prompt/knowledge_prompt.txt')
    template = PromptTemplate.from_file(file_path)
    prompt = template.format(input=text, reference_data=reference_data)
    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.8,
        repetition_penalty=1.05,
        max_tokens=2048
    )
    request_id = random_uuid()
    prompt_text = text

    # 生成文本的过程
    results_generator = engine.generate(prompt_text, sampling_params, request_id)

    final_output = None
    async for request_output in results_generator:
        # 在实际应用中，你需要检查客户端是否断开连接
        # 这里简化了，假设客户端始终连接
        final_output = request_output

    assert final_output is not None
    text_outputs = [output.text for output in final_output.outputs]
    ret = {"reference_data": reference_data, "text": text_outputs}
    print(ret)  # 输出结果，可以根据需要保存或处理


@router.post("/generate")
async def generate(request: Request) -> Response:
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    count = request_dict.pop("count")

    for text in prompt:
        await chat(text)
        # tasks = [chat() for _ in range(int(count))]
        # await asyncio.gather(*tasks)
