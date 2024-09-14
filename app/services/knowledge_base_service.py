import json
from typing import Optional

from datetime import datetime, timezone, timedelta
from fastapi import Request, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.prompts import PromptTemplate
from langfuse.client import Langfuse, ModelUsage
from langfuse.decorators import observe, langfuse_context
from pydantic import BaseModel, Field
from weaviate.classes.query import Filter

from app.api.openai.api_server import create_chat_completion, get_tokens, get_detokenize
from app.common.core.langchain_client import Embedding
from app.common.utils.google_utils import invoke, get_link_title, get_link_text
from app.common.utils.html_util import cleat_text, get_text_from_html, text2soup
from app.common.utils.logging import get_logger
from app.common.utils.object_utils import ObjectFormatter
from app.common.utils.text_utils import is_all_chinese, chinese_to_pinyin
from app.data.dictionaries import school_abbreviations
from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_knowledge_base import insert_ai_chat_log
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_model import AiChatLogModel, ReferenceDataDto, \
    MyChatCompletionRequestModel, ClassificationModel
from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionStreamResponse, Message, \
    datat_to_chat_completion_stream_response
from app.database.mysql.xxlxdb.service_confirm.service_confirm_school import select_service_school, \
    select_service_history, select_member_id_by_company_id, select_student_by_member_id, select_student_by_name
from app.database.redis.redis_client import get_object, set_object
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, StreamOptions
from vllm.utils import random_uuid

from app.database.weaviate.ai_chat_log import ai_chat_log_weaviate, AiChatWeaviateModel
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
from app.http.google_search import google_search
from app.prompt import classification_query, xiao_xi_chat, matching_summary, matching_information, \
    reanswer_classification_query

logger = get_logger(__name__)

TASK_A, TASK_B, TASK_C, TASK_D = "A", "B", "C", "D"


async def knowledge_base_generate(request: MyChatCompletionRequestModel, raw_request: Request,
                                  background_tasks: BackgroundTasks):
    reference_data_dto = ReferenceDataDto()

    # 获取请求参数
    conversation_id = request.conversation_id
    # query改写,将学校简称替换为全称
    query = query_rewrite(request.query)
    model = request.model
    stream = request.stream
    user_type = request.user_type
    user_id = request.user_id
    reanswer = request.reanswer

    # 初始化AiChatLog,用于保存聊天记录
    ai_chat_log_model = AiChatLogModel()
    ai_chat_log_model.start_time = datetime.now()
    ai_chat_log_model.query = query
    ai_chat_log_model.model_name = model
    ai_chat_log_model.user_id = user_id

    # 判断是否为流式输出
    stream_options = StreamOptions(include_usage=True) if request.stream else None

    # 初始化历史消息列表
    conversation_id, history_message_list = await get_history_message_list(conversation_id, query)
    ai_chat_log_model.conversation_id = conversation_id

    # 加载classificationQuery模板，进行任务分类
    classification_model = await classification(ai_chat_log_model=ai_chat_log_model, reanswer=reanswer,
                                                raw_request=raw_request)
    # 获取任务类型
    query_type = classification_model.query_type
    message_type = query_type
    # 返回对象
    chat_completion_stream_response = ChatCompletionStreamResponse()

    # ------------------------------------------------------------------------------------------------------------------
    if query_type == TASK_A or query_type == TASK_B:
        # 留学相关的海外院校/专业/申请相关的知识
        if query_type == TASK_A:
            # 获取海外院校/专业/申请相关的知识
            filters = Filter.by_property("db_name").not_equal("platform_introduction")
        else:
            # 小希平台相关功能知识
            filters = Filter.by_property("db_name").equal("platform_introduction")
        # 获取参考数据
        reference_data_dto = await load_reference_data(query=query, filters=filters, limit=10)

        # 加载prompt模板
        template = PromptTemplate.from_template(xiao_xi_chat)
        prompt = template.format(input=query, reference_data=reference_data_dto.reference_data)
    elif query_type == TASK_C:
        # 小希平台进行留学申请相关操作
        student_name = classification_model.student_name
        if not student_name:
            await chat_result_msg05(chat_completion_stream_response, "学生姓名为空")
            return JSONResponse(content=chat_completion_stream_response.dict())

        # 判断此次请求是否有权限查看学生信息
        service_master_list = await get_service_master(user_type, user_id, student_name)
        if not service_master_list:
            await chat_result_msg05(chat_completion_stream_response, f"名下没有 {student_name} 的学生")
            return JSONResponse(content=chat_completion_stream_response.dict())

        else:
            # 将学生姓名添加到classification_model中
            classification_model.student_name = service_master_list[0].get("student_name")
            task = classification_model.task
            message_type = query_type + "-" + task
            if task == "14":
                application_progress_data_list = await get_application_progress_data_list(
                    service_master_list[0].get("id"))
                if not application_progress_data_list:
                    await chat_result_msg05(chat_completion_stream_response, f"学生{student_name}没有可总结的申请进度")
                    return JSONResponse(content=chat_completion_stream_response.dict())
                # 加载prompt模板
                template = PromptTemplate.from_template(matching_summary)

                prompt = template.format(input=query, student_info=classification_model,
                                         application_progress_data_list=application_progress_data_list)
            else:
                # 加载prompt模板
                service_school_dict_list = select_service_school(service_master_list[0].get("id"))
                if not service_school_dict_list:
                    await chat_result_msg05(chat_completion_stream_response, f"{student_name}没有可操作的学校")
                    return JSONResponse(content=chat_completion_stream_response.dict())

                choice = chat_completion_stream_response.choices[0].delta
                choice.role = "platform_operation"

                template = PromptTemplate.from_template(matching_information)
                prompt = template.format(input=query, student_info=classification_model,
                                         application_information_list=service_school_dict_list)

                system = Message(role="system", content="你是数据分析提取助手")
                human = Message(role="user", content=prompt)
                chat_request = ChatCompletionRequest(
                    messages=[system, human],
                    model=model,
                )
                # 创建chat_completion请求
                chat_result = await create_chat_completion(chat_request, raw_request)
                # 提取消息
                chat_completion_stream_response = await extract_message(chat_result)

                chat_completion_stream_response.classification_model = classification_model
                # 将用户输入添加到消息列表，便于后续保存
                await chat_responsr_to_chat_log(ai_chat_log_model, chat_completion_stream_response)
                # 获取返回结果
                output_dict = await json_formatting(ai_chat_log_model.output)
                # 将学校id添加到classification_model中
                classification_model.service_school_id = output_dict.get("ids")
                return JSONResponse(content=chat_completion_stream_response.dict())
    else:
        # 闲聊
        system = Message(role="system", content="你是ai闲聊助手")
        prompt = request.query
        history_message_list.append(system)

    human = Message(role="human", content=prompt)
    history_message_list.append(human)
    chat_request = ChatCompletionRequest(
        messages=history_message_list,
        stream=stream,
        model=model,
        stream_options=stream_options
    )
    # 获取返回结果
    result = await create_chat_completion(chat_request, raw_request)

    ai_chat_log_model.prompt = prompt
    ai_chat_log_model.message_type = message_type
    # ------------------------------------------------------------------------------------------------------------------
    # 将用户输入添加到消息列表，便于后续保存
    history_message_list[-1]["content"] = query
    # 判断是否为流式输出
    if isinstance(result, StreamingResponse):
        return StreamingResponse(
            stream_response(result, ai_chat_log_model, reference_data_dto, classification_model),
            media_type="text/event-stream"
        )
    else:
        # 非流式输出,提取消息
        chat_completion_stream_response = await extract_message(result)
        # 将chat_completion_stream_response转换为AiChatLogModel
        await chat_responsr_to_chat_log(ai_chat_log_model, chat_completion_stream_response)
        # 请求结束，后续处理
        background_tasks.add_task(process_after_response, ai_chat_log_model)
        # 将参考数据添加到消息结果中
        chat_completion_stream_response.reference_data_dto = reference_data_dto
        # 返回结果
        result = JSONResponse(content=chat_completion_stream_response.dict())
        return result


async def classification(ai_chat_log_model: AiChatLogModel, reanswer: bool,
                         raw_request: Request) -> ClassificationModel:
    """ 任务分类
    :param ai_chat_log_model: AiChatLogModel
    :param reanswer: 是否再次回答
    :param raw_request: 请求
    :return: 任务分类结果 ClassificationModel
    """
    if reanswer:
        template = PromptTemplate.from_template(reanswer_classification_query)
    else:
        template = PromptTemplate.from_template(classification_query)
    classification_query_prompt = template.format(input=ai_chat_log_model.query)
    system = Message(role="system", content="你是一个严谨的智能问题分类助手，不会提供虚假信息")
    human = Message(role="user", content=classification_query_prompt)
    chat_request = ChatCompletionRequest(
        messages=[system, human],
        model=ai_chat_log_model.model_name,
    )
    # 创建chat_completion请求
    result = await create_chat_completion(chat_request, raw_request)
    # 提取消息
    chat_completion_stream_response = await extract_message(result)
    # 将chat_completion_stream_response转换为AiChatLogModel
    await chat_responsr_to_chat_log(ai_chat_log_model, chat_completion_stream_response)
    output = ai_chat_log_model.output
    logger.info(f"reanswer_classification_query" + "*" * 50 + output)
    # 获取任务分类,转换为ClassificationModel
    classification_model = ObjectFormatter.dict_to_object(json.loads(output), ClassificationModel)
    return classification_model


async def stream_response(result: StreamingResponse,
                          ai_chat_log_model: AiChatLogModel,
                          reference_data_dto: ReferenceDataDto,
                          classification_model: ClassificationModel):
    """
    流式输出
    :param result:  返回结果
    :param ai_chat_log_model: AiChatLogModel
    :param reference_data_dto: 参考数据
    :param classification_model: 任务分类
    :return:    流式输出
    """
    logger.info("*" * 50 + "流式输出")
    # 初始化输出
    output = ''
    # 初始化使用情况
    done = 'data: [DONE]'
    # 判断是否为第一个chunk
    first_chunk = True
    async for chunk in result.body_iterator:
        # 判断是否为最后一个或者第一个chunk，如果是则跳过，不处理
        if chunk.strip() == done:
            yield chunk
            continue

        chat_completion_stream_response = datat_to_chat_completion_stream_response(chunk)
        if first_chunk:
            # 第一个chunk，添加知识库链接,并将会话id添加到chunk中,并转码为json格式返回
            chat_completion_stream_response.conversation_id = ai_chat_log_model.conversation_id
            chat_completion_stream_response.reference_data_dto = reference_data_dto
            delta = chat_completion_stream_response.choices[0].delta
            if classification_model.query_type == "C":
                delta.role = "platform_operation"
                delta.classification = classification_model.dict()
            first_chunk = False
        yield "data: " + chat_completion_stream_response.json() + "\n\n"

        # 去除chunk中的data:前缀
        if first_chunk:
            continue
        try:
            choices = chat_completion_stream_response.choices
            # 判断choices是否为空或者finish_reason是否为stop，finish_reason=stop表示生成完成
            if choices:
                delta_content = choices[0].delta.content
                if delta_content:
                    output += delta_content
            elif chat_completion_stream_response.usage:
                print("*" * 10, chat_completion_stream_response.usage, type(chat_completion_stream_response.usage))
                usage = chat_completion_stream_response.usage
                ai_chat_log_model.prompt_tokens, ai_chat_log_model.completion_tokens, ai_chat_log_model.total_tokens = (
                    usage.prompt_tokens, usage.completion_tokens, usage.total_tokens
                )
                ai_chat_log_model.chat_id = chat_completion_stream_response.id
                ai_chat_log_model.output = output
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e} - Skipping chunk: {chunk}")

    await process_after_response(ai_chat_log_model)


async def extract_message(result: JSONResponse) -> ChatCompletionStreamResponse:
    '''
    非流式输出 提取消息
    :param result:  返回结果
    :return:  消息
    '''
    logger.info("*" * 50 + "非流输出")
    result_body = result.body.decode('utf-8')
    # result_content = json.loads(result_body)
    chat_completion_stream_response = datat_to_chat_completion_stream_response(result_body)
    return chat_completion_stream_response


async def process_after_response(ai_chat_log_model: AiChatLogModel):
    """ 请求结束后的处理
    :param ai_chat_log_model: AiChatLogModel
    """
    # 请求结束时间
    end_time = datetime.now()
    total_duration = (end_time - ai_chat_log_model.start_time).seconds
    ai_chat_log_model.total_duration = total_duration

    await save_mysql(ai_chat_log_model)
    await save_weaviste(ai_chat_log_model)
    # TODO
    # await save_redis(chat_message_history, chat_message_history_key, result_dict)
    # await save_langfuse(user_id=user_id, chat_message_history=chat_message_history, output=output, usage=usage,
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
    reference_data_dto = ReferenceDataDto(reference_data=reference_data, knowledge_link=knowledge_link,
                                          reference_data_count=len(response_list))
    return reference_data_dto


async def get_history_message_list(conversation_id: str, query: str):
    """ 获取历史消息列表
    :param conversation_id: 会话ID
    :param query: 用户输入
    :return: 会话ID, 历史消息列表
    """
    history_message_list = []
    system = Message(role="system", content="你是小希留学顾问助手")
    history_message_list.append(system)
    if not conversation_id:
        # 会话id不存在，表示为第一次请求，生成会话id
        conversation_id = f"conversation-{random_uuid()}"
        human = Message(role="human", content=query)
        history_message_list.append(human)
    else:
        # 会话id存在，获取历史记录
        history_message_list = await get_weaviste_history(conversation_id, query)
    logger.info(f"history_message_list: {history_message_list}")
    return conversation_id, history_message_list


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
    for ai_chat_log in ai_chat_log_list:
        human = Message(role="human", content=ai_chat_log.instruction)
        assistant = Message(role="assistant", content=ai_chat_log.output)
        message_list.append(human)
        message_list.append(assistant)
    return message_list


def query_rewrite(query):
    """ 将学校简称替换为全称
    :param query: 用户输入
    :return: 替换后的用户输入
    """
    # 遍历school_abbreviation
    for index, school_abbreviation in enumerate(school_abbreviations):
        # 从第二个元素开始，遍历school_abbreviation
        for school in school_abbreviation[1:]:
            if school in query:
                query = query.replace(school, f'''{school}({school_abbreviation[0]})''')
                return query
    return query


async def save_weaviste(ai_chat_log_model: AiChatLogModel):
    """ 保存聊天记录到向量数据库"""
    ai_chat_weaviate_model = AiChatWeaviateModel(
        conversation_id=ai_chat_log_model.conversation_id,
        message_id=ai_chat_log_model.chat_id,
        user_id=ai_chat_log_model.user_id,
        instruction=ai_chat_log_model.query,
        output=ai_chat_log_model.output,
        created_time=ai_chat_log_model.start_time.replace(tzinfo=timezone(timedelta(hours=8))),
    )
    vector = Embedding.embed_query(ai_chat_log_model.output)
    uuid = ai_chat_log_weaviate.insert_data(ai_chat_weaviate_model.dict(), vector)


async def chat_responsr_to_chat_log(ai_chat_log_model, chat_completion_stream_response):
    """ 将chat_completion_stream_response转换为AiChatLogModel"""

    logger.info(f"********chat_responsr_to_chat_log: {ai_chat_log_model.dict()}"
                f"********chat_responsr_to_chat_log: {chat_completion_stream_response.dict()}")

    usage = chat_completion_stream_response.usage
    ai_chat_log_model.prompt_tokens, ai_chat_log_model.completion_tokens, ai_chat_log_model.total_tokens = (
        usage.prompt_tokens, usage.completion_tokens, usage.total_tokens
    )
    ai_chat_log_model.chat_id = chat_completion_stream_response.id
    content = chat_completion_stream_response.choices[0].delta.content
    if not content:
        content = chat_completion_stream_response.choices[0].message.content
    ai_chat_log_model.output = content


async def get_service_master(user_type, user_id, student_name):
    member_id_list = []
    if user_type == "3":
        member_id_list = select_member_id_by_company_id(user_id)
    else:
        member_id_list.append(user_id)

    student_list = select_student_by_member_id(member_id_list, student_name)
    if not student_list:
        # 判断是否纯中文，纯中文在变成拼音检索一次
        if is_all_chinese(student_name):
            pi_yin_list = chinese_to_pinyin(student_name)
            fast_name = pi_yin_list[0]
            # 第二个往后取出来拼接
            last_name = ''.join(pi_yin_list[1:])
            student_list = select_student_by_name(member_id_list, fast_name, last_name)
    return student_list


async def get_application_progress_data_list(service_master_id: str):
    """ 获取学生的申请进度数据列表
    :param student_name: 学生姓名
    :return: 学生的申请进度数据列表
    """
    service_school_dict_list = select_service_school(service_master_id)
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
        if history['status'] == "130":
            history['status_name'] = "申请资料已提交给⼩希平台"
        elif history['status'] == "140":
            history['status_name'] = "已为学⽣递交院校申请"
        history.pop('status')
        if confirm_schl_id in school_dict:
            school_dict[confirm_schl_id]['service_history'].append(history)
    # Convert the dictionary back to a list
    application_progress_data_list = list(school_dict.values())
    return application_progress_data_list


async def save_redis(chat_message_history, chat_message_history_key, result_dict):
    """ 保存聊天记录到redis
    :param chat_message_history: 聊天记录
    :param chat_message_history_key: 聊天记录key
    :param result_dict: 模型返回结果
    """
    chat_message_history.add_ai_message(result_dict.get('output'))
    await set_object(chat_message_history_key, chat_message_history)


@observe()
async def save_langfuse(user_id: str, chat_message_history: list, output: str, usage: ModelUsage,
                        start_time: datetime, end_time: datetime):
    """ 保存聊天记录到langfuse
    :param user_id: 用户ID
    :param chat_message_history: 聊天记录
    :param output: 输出
    :param usage: 使用情况
    :param start_time: 请求开始时间
    :param end_time: 请求结束时间
    """
    langfuse_context.update_current_observation(user_id=user_id, metadata={"test": "test value"},
                                                input=chat_message_history, output=output)
    trace_id = langfuse_context.get_current_trace_id()
    Langfuse().generation(usage=usage, trace_id=trace_id, start_time=start_time, end_time=end_time)


async def save_mysql(ai_chat_log_model: AiChatLogModel):
    """ 保存聊天记录到langfuse
    :param ai_chat_log_model: AiChatLogModel
    """
    insert_ai_chat_log(ai_chat_log_model)


async def knowledge_base_networked_generate(query: str):
    sorted_items = await reference_networked_rag(query)
    reference_networked_data = "\n".join([f"{index + 1}. {item[1]}" for index, item in enumerate(sorted_items)])
    return sorted_items


async def reference_networked_rag(query: str):
    await now_time("1")
    response = await google_search(query)
    items = response.get('items')
    title_list = get_link_title(items)
    await now_time("2")
    similarity_list = Embedding.similarity(query, title_list)

    # Sort items by similarity and take top 2 links
    sorted_items = sorted(zip(similarity_list, items), key=lambda x: x[0], reverse=True)[:2]
    networked_links = [item[1].get('link') for item in sorted_items]
    await now_time("3")
    text_list = [cleat_text(get_text_from_html(text2soup(get_link_text(link)))) for link in networked_links]
    await now_time("4")
    networked_reference_datas = []
    for text in text_list:
        generator = await get_tokens(text)
        logger.info(f"*****************generator: {generator},type: {type(generator)}")
        tokens = generator.tokens
        count = generator.count
        if count > 400:
            token_sublists = [tokens[i:i + 300] for i in range(0, len(tokens) - 200, 200)]
            networked_reference_datas.extend(token_sublists)
        else:
            networked_reference_datas.append(tokens)
    await now_time("5")
    networked_reference_prompt = []
    for item in networked_reference_datas:
        detokenize = await get_detokenize(item)
        networked_reference_prompt.append(detokenize.prompt)
    await now_time("6")
    networked_reference_similarity_list = Embedding.similarity(query, networked_reference_prompt)
    sorted_items = sorted(zip(networked_reference_similarity_list, networked_reference_prompt), key=lambda x: x[0],
                          reverse=True)
    return sorted_items


async def now_time(bj: str):
    now = datetime.now()
    print(bj, now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")


async def json_formatting(json_str: str) -> dict:
    start = json_str.find("{")
    end = json_str.rfind("}")
    json_str = json_str[start:end + 1]
    return eval(json_str)


async def chat_result_msg05(chat_completion_stream_response: ChatCompletionStreamResponse, content: str):
    choice = chat_completion_stream_response.choices[0].delta
    choice.content = content
    choice.role = "platform_operation"
    chat_completion_stream_response.classification_model.task = "-1"
