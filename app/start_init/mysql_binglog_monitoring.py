import asyncio
import threading
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent
import pymysql

from app.common.core.config import settings
from app.common.core.langchain_client import Embedding
from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution, \
    insert_t_knowledge_info_data, insert_mysql_weaviate
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_mysql_weaviate import select_ai_mysql_weaviate, \
    insert_ai_mysql_weaviate, update_ai_mysql_weaviate
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

manner_execution = MannerExecution(
    method_name="",
    limit=1,
    start_id=0,
    frequency=1
)


async def choice_method(table_name: str, data: dict, type: int):
    if table_name == 't_knowledge_info':
        await sync_t_knowledge_info(data)


async def sync_t_knowledge_info(data: dict):
    db_name = "t_knowledge_info"
    apply_status = data.get('apply_status')
    if apply_status == 4:
        manner_execution.method_name = db_name
        db_id = data.get('id')
        start_id, knowledge_base_model_list, file_url_list = insert_t_knowledge_info_data(start_id=db_id, limit=1)
        knowledge_base_model = knowledge_base_model_list[0]
        vec = Embedding.embed_query(knowledge_base_model.get('instruction'))

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
            knowledge_base_model.pop('link')
            update_ai_mysql_weaviate(knowledge_base_model)
        else:
            uuid = knowledge_base_weaviate.insert_data(knowledge_base_model, vec)
            knowledge_base_model['weaviate_id'] = str(uuid)
            if file_url_list:
                knowledge_base_model['file_url'] = file_url_list[0]
            insert_ai_mysql_weaviate(knowledge_base_model)


async def start_binlog_listener():
    # MySQL 连接配置
    mysql_settings = settings["mysql"]["xxlxdb"]
    mysql_settings.pop('database')

    # 获取指定表的字段名
    def get_column_names(database, table_name):
        connection = pymysql.connect(database=database, **mysql_settings)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                return [column[0] for column in columns]
        finally:
            connection.close()

    # 监听 Binlog 日志
    stream = BinLogStreamReader(
        connection_settings=mysql_settings,
        server_id=1,  # 随便设置一个唯一的 server_id
        blocking=True,
        only_schemas=["test_xxlxdb"],  # 监听多个数据库
        only_tables=["t_knowledge_info"],  # 监听多个表
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
            if binlogevent.table == 't_knowledge_info':
                manner_execution.method_name = 't_knowledge_info'

            if isinstance(binlogevent, WriteRowsEvent):
                for row in binlogevent.rows:
                    # 将 UNKNOWN_COLX 转换为实际的列名
                    record = {column_names[i]: value for i, value in enumerate(row["values"].values())}
                    # print(f"Insert into {binlogevent.schema}.{binlogevent.table}:", record)
                    await choice_method(binlogevent.table, record, 1)
            elif isinstance(binlogevent, UpdateRowsEvent):
                for row in binlogevent.rows:
                    # before_values = {column_names[i]: value for i, value in enumerate(row["before_values"].values())}
                    after_values = {column_names[i]: value for i, value in enumerate(row["after_values"].values())}
                    # print(f"Update {binlogevent.schema}.{binlogevent.table}:", before_values, "to", after_values)
                    await choice_method(binlogevent.table, after_values, 2)

    # 关闭 stream
    stream.close()


# 在一个独立线程中启动 Binlog 监听
binlog_thread = threading.Thread(target=start_binlog_listener)
binlog_thread.daemon = True  # 设为守护线程，主程序退出时该线程自动结束
binlog_thread.start()

# 继续执行主线程的其他代码
print("主程序继续启动，不会被阻塞")
start_binlog_listener()
# asyncio.run(start_binlog_listener())
