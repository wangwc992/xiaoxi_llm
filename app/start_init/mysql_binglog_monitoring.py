import threading
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent
import pymysql

from app.data_cleansing.knowledge_base_cleansing import MannerExecution, cleansing_manner_execution

manner_execution = MannerExecution(
    method_name="",
    limit=1,
    start_id=0,
    frequency=1
)

async def t_knowledge_info(data: dict):
    apply_status = data.get('apply_status')
    if apply_status == 4:
        manner_execution.method_name = 't_knowledge_info'
        manner_execution.start_id = data.get('id')
        await cleansing_manner_execution(manner_execution)


def start_binlog_listener():
    # MySQL 连接配置
    mysql_settings = {
        'host': "121.37.172.238",
        'port': 3306,
        'user': "root",
        'password': "Yhj18835534246"
    }

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
        only_schemas=["test_db", "yshs_db"],  # 监听多个数据库
        only_tables=["ai_mysql_weaviate", "Product"],  # 监听多个表
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
                    print(type(record))
                    print(f"Insert into {binlogevent.schema}.{binlogevent.table}:", record)
            elif isinstance(binlogevent, UpdateRowsEvent):
                for row in binlogevent.rows:
                    before_values = {column_names[i]: value for i, value in enumerate(row["before_values"].values())}
                    after_values = {column_names[i]: value for i, value in enumerate(row["after_values"].values())}
                    print(type(after_values))
                    print(f"Update {binlogevent.schema}.{binlogevent.table}:", before_values, "to", after_values)

    # 关闭 stream
    stream.close()

# 在一个独立线程中启动 Binlog 监听
# binlog_thread = threading.Thread(target=start_binlog_listener)
# binlog_thread.daemon = True  # 设为守护线程，主程序退出时该线程自动结束
# binlog_thread.start()
#
# # 继续执行主线程的其他代码
# print("主程序继续启动，不会被阻塞")
start_binlog_listener()