import asyncio
import json
import os
from typing import Optional

from datetime import datetime, timezone, timedelta
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field
from weaviate.classes.query import Filter

from app.api.openai.api_server import create_chat_completion
from app.common.core.langchain_client import Embedding
from app.common.utils.logging import get_logger
from app.common.utils.object_utils import ObjectFormatter
from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.mysql.xxlxdb.service_confirm.service_confirm_school import select_service_school, \
    select_service_history
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from vllm.utils import random_uuid

from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate, AiChatLogModel
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
from app.prompt import classification_query, xiao_xi_chat, matching_summary, matching_information

router = APIRouter(prefix="/chat")
logger = get_logger(__name__)


class MyChatCompletionRequestModel(BaseModel):
    query: str = Field(..., description="用户输入的问题")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    model: Optional[str] = Field("/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4", description="模型名称")
    conversation_id: Optional[str] = Field(None, description="会话id，用于标识一个会话")
    member_id: Optional[str] = Field("1001", description="用户ID")


# {"queryType":"C","task":"3","studentName":"xuyunyi","schoolName":"oeinstein","majorName":"digitalhumanities"}
class ClassificationModel(BaseModel):
    query_type: Optional[str] = Field(None, description="问题类型")
    task: Optional[str] = Field(None, description="任务编号")
    student_name: Optional[str] = Field(None, description="学生姓名")
    school_name: Optional[str] = Field(None, description="学校名称")
    major_name: Optional[str] = Field(None, description="专业名称")


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request,
                                  background_tasks: BackgroundTasks):
    # 接口开始时间
    start_time = datetime.now()
    # 知识库链接
    knowledge_link = {}
    # 参考数据
    reference_data = {}
    # 参考数据数量
    reference_data_count = 0

    # 获取请求参数
    member_id = request.member_id
    conversation_id = request.conversation_id
    query = request.query
    model = request.model
    stream = request.stream

    # 判断是否为流式输出
    stream_options = StreamOptions(include_usage=True) if request.stream else None

    # 初始化历史消息列表
    conversation_id, history_message_list = await get_history_message_list(conversation_id, query)

    # 加载classificationQuery模板，进行任务分类
    classification_model = await classification(model, query, raw_request)
    if classification_model:
        classification_result = f'''data: {{"choices": [ {{ "index": 0, "delta": {{ "role": "1", "content": {classification_model} }}}} ]}}'''
        yield classification_result
    # 获取任务类型
    query_type = classification_model.query_type
    # ------------------------------------------------------------------------------------------------------------------
    if query_type == "A" or query_type == "B":
        # 留学相关的海外院校/专业/申请相关的知识
        if query_type == "A":
            # 获取海外院校/专业/申请相关的知识
            filters = Filter.by_property("db_name").not_equal("platform_introduction")
        else:
            # 小希平台相关功能知识
            filters = Filter.by_property("db_name").equal("platform_introduction")
        # 获取参考数据
        reference_data_dict = await load_reference_data(query=query, filters=filters, limit=10)
        reference_data = reference_data_dict.get("reference_data")
        knowledge_link = reference_data_dict.get("knowledge_link")
        reference_data_count = reference_data_dict.get("reference_data_count")

        # 加载prompt模板
        template = PromptTemplate.from_template(xiao_xi_chat)
        prompt = template.format(input=query, reference_data=reference_data)
    elif query_type == "C":
        # 小希平台进行留学申请相关操作
        student_name = classification_model.student_name
        result = '''data: {"choices": [ { "index": 0, "delta": { "role": "1", "content": "学生姓名不存在，直接返回" }} ]}'''
        if not student_name:
            yield result
        else:
            task = classification_model.task
            # 使用classification_model已知的学生信息，查询数据库，获取学生信息
            student_info_dict_list = "假设这儿是查询数据库的返回的学生信息"
            if not student_info_dict_list:
                result = '''data: {"choices": [ { "index": 0, "delta": { "role": "1", "content": "学生申请信息不存在，直接返回" }} ]}'''
                yield result
            if task == "11":
                application_progress_data_list = await get_application_progress_data_list(student_name)
                # 加载prompt模板
                template = PromptTemplate.from_template(matching_summary)
                prompt = template.format(input=query, student_info=classification_model,
                                         application_progress_data_list=application_progress_data_list)
            else:
                # 加载prompt模板
                template = PromptTemplate.from_template(matching_information)
                prompt = template.format(input=query, student_info=classification_model,
                                         application_information_list="学生申请信息")
    else:
        # 闲聊
        system = {"role": "system", "content": "你是ai闲聊助手"}
        prompt = request.query
        history_message_list.append(system)

    human = {"role": "human", "content": prompt}
    history_message_list.append(human)
    chat_request = ChatCompletionRequest(
        messages=history_message_list,
        stream=stream,
        model=model,
        stream_options=stream_options
    )
    # 获取返回结果
    result = await create_chat_completion(chat_request, raw_request)

    # ------------------------------------------------------------------------------------------------------------------
    # 将用户输入添加到消息列表，便于后续保存
    history_message_list[-1]["content"] = query
    # 判断是否为流式输出
    if isinstance(result, StreamingResponse):
        yield  StreamingResponse(
            stream_response(result, member_id, history_message_list, start_time, knowledge_link, conversation_id,
                            reference_data_count),
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
        yield result


async def get_application_progress_data_list(student_name):
    """ 获取学生的申请进度数据列表
    :param student_name: 学生姓名
    :return: 学生的申请进度数据列表
    """
    service_school_dict_list = select_service_school(student_name)
    service_school_id_list = [service_school_dict.get("id") for service_school_dict in
                              service_school_dict_list]
    service_history_dict_list = select_service_history(service_school_id_list)
    # Create a dictionary with school id as the key
    school_dict = {school['id']: school for school in service_school_dict_list}
    # Initialize the service_history field for each school
    for school in school_dict.values():
        school['service_history'] = []
    # Append each history item to the corresponding school dictionary
    for history in service_history_dict_list:
        confirm_schl_id = history['confirm_schl_id']
        if confirm_schl_id in school_dict:
            school_dict[confirm_schl_id]['service_history'].append(history)
    # Convert the dictionary back to a list
    application_progress_data_list = list(school_dict.values())
    return application_progress_data_list


async def classification(model: str, query: str, raw_request: Request):
    """ 任务分类
    :param model: 模型名称
    :param query: 用户输入
    :param raw_request: 请求
    :return: 任务分类结果 ClassificationModel
    """
    template = PromptTemplate.from_template(classification_query)
    classification_query_prompt = template.format(input=query)
    print(classification_query_prompt)
    system = {"role": "system", "content": "你是问题分类助手"}
    human = {"role": "human", "content": classification_query_prompt}
    chat_request = ChatCompletionRequest(
        messages=[system, human],
        model=model,
    )
    # 创建chat_completion请求
    result = await create_chat_completion(chat_request, raw_request)
    # 提取消息
    result_dict = await extract_message(result)
    output = result_dict.get('output')
    # 获取任务分类,转换为ClassificationModel
    classification_model = ObjectFormatter.dict_to_object(json.loads(output), ClassificationModel)
    logger.info(f"classification_model: {classification_model.__dict__}")
    return classification_model


async def get_history_message_list(conversation_id: str, query: str):
    """ 获取历史消息列表
    :param conversation_id: 会话ID
    :param query: 用户输入
    :return: 会话ID, 历史消息列表
    """
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
    return conversation_id, history_message_list


async def stream_response(result: StreamingResponse, member_id: str, message_list: list, start_time: datetime,
                          knowledge_link: dict,
                          conversation_id: str, reference_data_count: int):
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
            delta['reference_data_count'] = reference_data_count
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
    # await save_langfuse(member_id=member_id, chat_message_history=chat_message_history, output=output, usage=usage,
    #                     start_time=start_time, end_time=end_time)


async def load_reference_data(query, filters, limit):
    """ 加载参考数据
    :param query: 用户输入
    :param filters: 过滤条件
    :param limit: 限制数量
    :return: 参考数据
    """
    # 从weaviate获取参考数据
    response_list = await knowledge_base_weaviate.search_hybrid(query, limit, filters)
    reference_data = "\n\n".join(
        [f"{response_list[n].instruction}: {response_list[n].output}" for n in range(len(response_list))])
    # 获取知识库链接, 仅获取t_knowledge_info的链接,并且将字符串转换为字典
    knowledge_link = []
    for response in response_list:
        if response.db_name == "t_knowledge_info" and response.link:
            try:
                knowledge_link.append(eval(response.link.replace("\n", "")))
            except:
                logger.error(f"knowledge_link error: {response.link},type: {type(response.link)}")

    return {
        "reference_data": reference_data,
        "knowledge_link": knowledge_link,
        "reference_data_count": len(response_list),
    }


async def get_weaviste_history(conversation_id, query):
    """ 从向量数据库获取历史消息列表
    :param conversation_id: 会话ID
    :param query: 用户输入
    :return: 消息列表
    """
    # 从weaviate获取历史记录
    filters = Filter.by_property("conversation_id").equal(conversation_id)
    ai_chat_log_list = await ai_chat_log_weaviate.search_hybrid(query=query, limit=10, filters=filters)

    # 将历史记录转换为消息列表
    message_list = []
    system = {"role": "system", "content": "你是小希留学顾问助手"}
    message_list.append(system)
    for ai_chat_log in ai_chat_log_list:
        human = {"role": "human", "content": ai_chat_log.instruction}
        ai = {"role": "ai", "content": ai_chat_log.output}
        message_list.append(human)
        message_list.append(ai)
    return message_list


async def save_weaviste(conversation_id, member_id, input, output):
    """ 保存聊天记录到向量数据库
    :param conversation_id: 会话ID
    :param member_id: 用户ID
    :param input: 用户输入
    :param output: 输出
    """
    ai_chat_log_model = AiChatLogModel(
        conversation_id=conversation_id,
        message_id=member_id,
        user_id="123",
        instruction=input,
        output=output,
        created_time=datetime.now(timezone(timedelta(hours=8))),
        reference_data_uuids=["123"]
    )
    vector = Embedding.embed_query(ai_chat_log_model.output)
    uuid = ai_chat_log_weaviate.insert_data(ai_chat_log_model.dict(), vector)


async def save_redis(chat_message_history, chat_message_history_key, result_dict):
    """ 保存聊天记录到redis
    :param chat_message_history: 聊天记录
    :param chat_message_history_key: 聊天记录key
    :param result_dict: 模型返回结果
    """
    chat_message_history.add_ai_message(result_dict.get('output'))
    await set_object(chat_message_history_key, chat_message_history)


@observe()
async def save_langfuse(member_id: str, chat_message_history: list, output: str, usage: ModelUsage,
                        start_time: datetime, end_time: datetime):
    """ 保存聊天记录到langfuse
    :param member_id: 用户ID
    :param chat_message_history: 聊天记录
    :param output: 输出
    :param usage: 使用情况
    :param start_time: 请求开始时间
    :param end_time: 请求结束时间
    """
    langfuse_context.update_current_observation(user_id=member_id, metadata={"test": "test value"},
                                                input=chat_message_history, output=output)
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)
