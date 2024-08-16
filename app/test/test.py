from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.row_event import WriteRowsEvent, UpdateRowsEvent
from pymysqlreplication.event import QueryEvent
import pymysql

# MySQL 连接配置
mysql_settings = {
    'host': "121.37.172.238",
    'port': 3306,
    'user': "root",
    'password': "Yhj18835534246",
    'database': "test_db"
}
# 获取 ai_chat 表的字段名
def get_column_names(table_name):
    connection = pymysql.connect(**mysql_settings)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            return [column[0] for column in columns]
    finally:
        connection.close()

# 获取字段名
column_names = get_column_names("ai_mysql_weaviate")

# 监听 Binlog 日志
stream = BinLogStreamReader(
    connection_settings=mysql_settings,
    server_id=1,  # 随便设置一个唯一的 server_id
    blocking=True,
    # only_schemas=["test_db"],  # 只监听 `xxlx` 数据库
    only_tables=["ai_mysql_weaviate"],  # 只监听 `ai_mysql_weaviate` 表
    resume_stream=True,
)

for binlogevent in stream:
    if isinstance(binlogevent, WriteRowsEvent):
        for row in binlogevent.rows:
            # 将 UNKNOWN_COLX 转换为实际的列名
            record = {column_names[i]: value for i, value in enumerate(row["values"].values())}
            print("Insert into ai_mysql_weaviate:", record)
    elif isinstance(binlogevent, UpdateRowsEvent):
        for row in binlogevent.rows:
            before_values = {column_names[i]: value for i, value in enumerate(row["before_values"].values())}
            after_values = {column_names[i]: value for i, value in enumerate(row["after_values"].values())}
            print("Update ai_mysql_weaviate:", before_values, "to", after_values)

# 关闭 stream
stream.close()