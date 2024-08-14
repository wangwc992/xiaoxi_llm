import asyncio
import json
import os
from typing import Optional

import torch
from datetime import datetime, timezone, timedelta
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field
from weaviate.classes.query import Filter

from app.api.openai.api_server import create_chat_completion
from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from vllm.utils import random_uuid
from langchain_community.chat_message_histories import ChatMessageHistory

from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate, AiChatLogModel
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    query: str = Field(..., description="用户输入的问题")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    model: Optional[str] = Field("/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4", description="模型名称")
    conversation_id: Optional[str] = Field(None, description="会话id，用于标识一个会话")
    member_id: Optional[str] = Field("1001", description="用户ID")


async def get_reference_data(query: str, alpha: float, limit: int = 10):
    return await knowledge_base_weaviate.search_hybrid_or(query=query, alpha=alpha, limit=limit)


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request,
                                  background_tasks: BackgroundTasks):
    # 请求开始时间
    start_time = datetime.now()
    member_id = request.member_id
    # 获取会话id
    conversation_id = request.conversation_id
    query = request.query
    # 初始化历史消息列表
    history_message_list = []
    if not conversation_id:
        # 会话id不存在，表示为第一次请求，生成会话id
        conversation_id = f"conversation-{random_uuid()}"
        system = {"role": "system", "content": "你是小希留学顾问助手"}
        human = {"role": "human", "content": query}
        history_message_list.append(system)
        history_message_list.append(human)
    else:
        # 会话id存在，获取历史记录
        history_message_list = await get_weaviste_history(conversation_id, query)
    logger.info(f"history_message_list: {history_message_list}")

    # 获取参考数据
    reference_data_dict = await load_reference_data(query, 10)
    reference_data = reference_data_dict.get("reference_data")
    knowledge_link = reference_data_dict.get("knowledge_link")

    # 加载prompt模板
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../prompt/knowledge_prompt.txt')
    template = PromptTemplate.from_file(file_path)
    prompt = template.format(input=query, reference_data=reference_data)
    # 拼接prompt将用户输入添加到消息列表
    history_message_list.append({"role": "human", "content": prompt})
    # 判断是否为流式输出
    stream_options = StreamOptions(include_usage=True) if request.stream else None
    # 创建chat_completion请求
    chat_request = ChatCompletionRequest(
        messages=history_message_list,
        stream=request.stream,
        model=request.model,
        stream_options=stream_options
    )
    # 将用户输入添加到消息列表，便于后续保存
    history_message_list[-1]["content"] = query

    # 获取返回结果
    result = await create_chat_completion(chat_request, raw_request)

    # 判断是否为流式输出
    if isinstance(result, StreamingResponse):
        return StreamingResponse(
            stream_response(result, member_id, history_message_list, start_time, knowledge_link, conversation_id),
            media_type="text/event-stream"
        )
    else:
        result_dict = await extract_message(result)
        background_tasks.add_task(process_after_response, result_dict,
                                  member_id, history_message_list, start_time, conversation_id)

        # 转码为json格式
        response_dict = json.loads(result.body.decode('utf-8'))
        response_dict["reference_data"] = reference_data
        response_dict["knowledge_link"] = knowledge_link
        result = JSONResponse(content=response_dict)
        return result


async def stream_response(result, member_id, message_list, start_time, knowledge_link, conversation_id):
    '''
    流式输出
    :param result:  返回结果
    :param member_id:  用户ID
    :param message_list:  消息列表
    :param start_time:  请求开始时间
    :param knowledge_link:  知识库链接
    :param conversation_id:     会话ID
    :return:    流式输出
    '''
    # 初始化输出
    output = ''
    # 初始化使用情况
    usage = None
    # 判断是否为第一个chunk
    first_chunk = True
    async for chunk in result.body_iterator:
        if first_chunk:
            # 第一个chunk，添加知识库链接,并将会话id添加到chunk中,并转码为json格式返回
            chunk = chunk[len("data: "):]
            chunk_data = json.loads(chunk)
            delta = chunk_data.get('choices')[0]['delta']
            delta['role'] = "1"
            delta['content'] = knowledge_link
            chunk_data['conversation_id'] = conversation_id
            chunk = f"data: {json.dumps(chunk_data)}\n\n"
        yield chunk
        # 判断是否为最后一个或者第一个chunk，如果是则跳过，不处理
        if chunk.strip() == "data: [DONE]" or not chunk.strip() or first_chunk:
            first_chunk = False
            continue
        # 去除chunk中的data:前缀
        if chunk.startswith("data: "):
            chunk = chunk[len("data: "):]
        try:
            chunk_data = json.loads(chunk)
            choices = chunk_data.get('choices')
            # 判断choices是否为空或者finish_reason是否为stop，finish_reason=stop表示生成完成
            if choices and choices[0].get('finish_reason') != 'stop':
                delta_content = choices[0]['delta'].get('content')
                if delta_content:
                    output += delta_content
            else:
                # 生成完成，获取使用情况
                usage = chunk_data.get('usage')
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

    result_dict = {"output": output, "usage": usage}
    await process_after_response(result_dict, member_id, message_list, start_time, conversation_id)


async def extract_message(result):
    '''
    非流式输出 提取消息
    :param result:  返回结果
    :return:  消息
    '''
    # 初始化输出
    output = ''
    # 初始化使用情况
    usage = None
    if isinstance(result, JSONResponse):
        result_body = result.body.decode('utf-8')
        result_content = json.loads(result_body)
        if result_content.get('object') == 'error':
            output = result_body
        else:
            # 获取输出
            output += result_content['choices'][0]['message']['content']
            # 获取使用情况
            usage = result_content.get('usage')
    return {"output": output, "usage": usage}


async def process_after_response(result_dict, member_id, chat_message_history, start_time, conversation_id):
    # 请求结束时间
    end_time = datetime.now()
    # 获取用户输入
    input = chat_message_history[-1]['content']
    # 获取输出
    output = result_dict.get('output')
    # 获取使用情况
    usage = result_dict.get('usage')
    if usage:
        # 将使用情况转换为ModelUsage
        usage = ModelUsage(input=usage['prompt_tokens'], output=usage['completion_tokens'],
                           total=usage['total_tokens'], unit='TOKENS')

    await save_weaviste(conversation_id, member_id, input, output)
    # TODO
    # await save_redis(chat_message_history, chat_message_history_key, result_dict)
    # await save_langfuse(member_id, chat_message_history, output, usage, start_time, end_time)


async def load_reference_data(query, limit):
    # 匹配关键字使用特定知识库
    filters = None
    for key, values in ai_knowledge_base_keyword_dict.items():
        if any(v in query for v in values):
            filters = Filter.by_property("database").equal(key)
            break

    # 从weaviate获取参考数据
    response_list = await knowledge_base_weaviate.search_hybrid(query, limit, filters)
    reference_data = "\n\n".join(
        [f"{response_list[n].instruction}: {response_list[n].output}" for n in range(len(response_list))])
    # 获取知识库链接, 仅获取t_knowledge_info的链接,并且将字符串转换为字典
    knowledge_link = []
    for response in response_list:
        if response.database == "t_knowledge_info" and response.link:
            try:
                knowledge_link.append(eval(response.link.replace("\n", "")))
                logger.info(f"knowledge_link: {response.link},type: {type(response.link)}")
            except:
                logger.error(f"knowledge_link error: {response.link},type: {type(response.link)}")
    return {
        "reference_data": reference_data,
            "knowledge_link": knowledge_link,
    }


async def get_weaviste_history(conversation_id, query):
    # 从weaviate获取历史记录
    filters = Filter.by_property("conversation_id").equal(conversation_id)
    ai_chat_log_list = await ai_chat_log_weaviate.search_hybrid(query=query, limit=10, filters=filters)

    # 将历史记录转换为消息列表
    message_list = []
    for ai_chat_log in ai_chat_log_list:
        human = {"role": "human", "content": ai_chat_log.input}
        ai = {"role": "ai", "content": ai_chat_log.output}
        message_list.append(human)
        message_list.append(ai)
    return message_list


async def save_weaviste(conversation_id, member_id, input, output):
    '''
    保存聊天记录到weaviate
    :param conversation_id:     会话ID
    :param member_id:       用户ID
    :param input:    用户输入
    :param output:  输出
    :return:    None
    '''
    ai_chat_log_model = AiChatLogModel(
        conversation_id=conversation_id,
        message_id=member_id,
        user_id="123",
        input=input,
        output=output,
        created_time=datetime.now(timezone(timedelta(hours=8))),
        reference_data_uuids=["123"]
    )
    vector = Embedding.embed_query(ai_chat_log_model.output)
    uuid = ai_chat_log_weaviate.insert_data(ai_chat_log_model.dict(), vector)


async def save_redis(chat_message_history, chat_message_history_key, result_dict):
    '''
    保存聊天记录到redis
    :param chat_message_history:    聊天记录
    :param chat_message_history_key:    聊天记录key
    :param result_dict:     返回结果
    :return:    None
    '''
    chat_message_history.add_ai_message(result_dict.get('output'))
    await set_object(chat_message_history_key, chat_message_history)


@observe()
async def save_langfuse(member_id, chat_message_history, output, usage, start_time, end_time):
    '''
    保存聊天记录到langfuse
    :param member_id:   用户ID
    :param chat_message_history:        聊天记录
    :param output:  输出
    :param usage:   使用情况
    :param start_time:  请求开始时间
    :param end_time:    请求结束时间
    :return:    None
    '''
    langfuse_context.update_current_observation(user_id=member_id, metadata={"test": "test value"},
                                                input=chat_message_history, output=output)
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)
