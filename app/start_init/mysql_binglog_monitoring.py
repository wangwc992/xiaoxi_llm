import asyncio

from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent
import pymysql

from app.common.core.config import settings
from app.common.core.langchain_client import Embedding
from app.common.utils.jieba_utils import jieba_tool
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, \
    insert_t_knowledge_info_data, insert_mysql_weaviate, insert_institution_information_data
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_mysql_weaviate import select_ai_mysql_weaviate, \
    insert_ai_mysql_weaviate, update_ai_mysql_weaviate
from app.database.weaviate.knowledge_base import knowledge_base_weaviate


async def choice_method(table_name: str, data: dict):
    if table_name == 't_knowledge_info':
        apply_status = data.get('apply_status')
        if apply_status != 4:
            return

    await sync_knowledge_base(table_name, data)


async def sync_knowledge_base(table_name: str, data: dict):
    # TODO 知识库updat连续更新时，会有多次同步到weaviate的问题
    db_id = data.get('id')
    limit = 1
    db_name = table_name

    method_mapping = {
        "t_knowledge_info": lambda: insert_t_knowledge_info_data(start_id=db_id, limit=limit),
        "notice_message": lambda: insert_institution_information_data(start_id=db_id, limit=limit),
    }

    start_id, knowledge_base_model_list, file_url_list = method_mapping.get(table_name)()
    knowledge_base_model = knowledge_base_model_list[0]
    instruction = knowledge_base_model.get('instruction')
    vec = Embedding.embed_query(instruction)
    keyword = jieba_tool.cut_for_search(instruction)
    knowledge_base_model['keyword'] = ' '.join(keyword)
    # 判断之前是否已经同步过
    ai_mysql_weaviate_list = select_ai_mysql_weaviate({'db_id': db_id, 'db_name': db_name}, 1)
    if ai_mysql_weaviate_list:
        # 获取之前同步的数据的 weaviate_id，更新weaviate数据
        uuid = ai_mysql_weaviate_list[0].get("weaviate_id")
        knowledge_base_weaviate.update_data_by_uuid(uuid, knowledge_base_model, vec)

        # 更新 ai_mysql_weaviate 数据
        id = ai_mysql_weaviate_list[0].get("id")
        knowledge_base_model['id'] = id
        if file_url_list:
            knowledge_base_model['file_url'] = file_url_list[0]
        if table_name == 't_knowledge_info':
            knowledge_base_model.pop('link')
        knowledge_base_model.pop('keyword')
        update_ai_mysql_weaviate(knowledge_base_model)
    else:
        uuid = knowledge_base_weaviate.insert_data(knowledge_base_model, vec)
        knowledge_base_model['weaviate_id'] = str(uuid)
        if file_url_list:
            knowledge_base_model['file_url'] = file_url_list[0]
        insert_ai_mysql_weaviate(knowledge_base_model)


async def start_binlog_listener():
    print("Binlog 监听已启动")
    # MySQL 连接配置
    xxlxdb_config = settings["mysql"]["xxlxdb"]
    smart_counselor_config = settings["mysql"]["smart_counselor"]
    xxlxdb = xxlxdb_config.get('database')
    smart_counselor = smart_counselor_config.get('database')
    xxlxdb_config.pop('database')

    # 获取指定表的字段名
    def get_column_names(database, table_name):
        connection = pymysql.connect(database=database, **xxlxdb_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                return [column[0] for column in columns]
        finally:
            connection.close()

    # 监听 Binlog 日志
    stream = BinLogStreamReader(
        connection_settings=xxlxdb_config,
        server_id=1,  # 随便设置一个唯一的 server_id
        blocking=True,
        only_schemas=[xxlxdb, smart_counselor],  # 监听多个数据库
        only_tables=["t_knowledge_info", "notice_message"],  # 监听多个表
        resume_stream=True,
    )

    # 存储不同数据库的表字段名
    table_columns = {}

    for binlogevent in stream:
        # 检查事件类型
        if isinstance(binlogevent, (WriteRowsEvent, UpdateRowsEvent)):
            schema_table = (binlogevent.schema, binlogevent.table)
            if schema_table not in table_columns:
                # 第一次遇到某个表时，获取其字段名
                table_columns[schema_table] = get_column_names(binlogevent.schema, binlogevent.table)

            column_names = table_columns[schema_table]

            if isinstance(binlogevent, WriteRowsEvent):
                for row in binlogevent.rows:
                    # 将 UNKNOWN_COLX 转换为实际的列名
                    record = {column_names[i]: value for i, value in enumerate(row["values"].values())}
                    print(f"Insert into {binlogevent.schema}.{binlogevent.table}:", record)
                    await choice_method(binlogevent.table, record)
            elif isinstance(binlogevent, UpdateRowsEvent):
                for row in binlogevent.rows:
                    before_values = {column_names[i]: value for i, value in enumerate(row["before_values"].values())}
                    after_values = {column_names[i]: value for i, value in enumerate(row["after_values"].values())}
                    print(f"Update {binlogevent.schema}.{binlogevent.table}:", before_values, "to", after_values)
                    await choice_method(binlogevent.table, after_values)

    # 关闭 stream
    stream.close()

# asyncio.run(start_binlog_listener())
