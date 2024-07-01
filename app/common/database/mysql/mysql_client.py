import MySQLdb
import MySQLdb.cursors
from typing import Any, Dict, List, Type
from app.common.core.config import settings
from app.common.utils.logging import get_logger

logger = get_logger(__name__)


class MySQLConnect:
    mysql_dict = settings["mysql"]
    mySQLConnectCur = None
    conn = None
    __cur = None

    @classmethod
    def connect(cls):
        """建立数据库连接"""
        if cls.conn:
            cls.conn.close()
        cls.conn = MySQLdb.connect(
            host=cls.mysql_dict["host"],
            user=cls.mysql_dict["user"],
            passwd=cls.mysql_dict["password"],
            database=cls.mysql_dict["database"],
            port=cls.mysql_dict["port"],
            cursorclass=MySQLdb.cursors.DictCursor  # 使用字典游标类
        )
        cls.__cur = cls.conn.cursor()

    @classmethod
    def check_connection(cls):
        """检查连接状态，如果断开则重新连接"""
        try:
            cls.conn.ping()
        except MySQLdb.Error as e:
            print(f"Database connection error: {e}")
            cls.connect()

    @classmethod
    def execute(cls, sql: str, params: tuple = ()):
        """执行 SQL 语句，带有自动重连功能"""
        cls.check_connection()
        # 打印 执行的sql
        logger.info("Executing query: %s", cls.__cur.mogrify(sql, params))
        try:
            cls.__cur.execute(sql, params)
        except MySQLdb.Error as e:
            logger.error("Error executing query: %s", e)
            cls.connect()  # 尝试重新连接
            cls.__cur.execute(sql, params)  # 再次尝试执行

    @classmethod
    def fetchall(cls) -> List[Dict[str, Any]]:
        """获取所有查询结果"""
        return cls.__cur.fetchall()

    @classmethod
    def fetchone(cls) -> Dict[str, Any]:
        """获取单条查询结果"""
        return cls.__cur.fetchone()

    @classmethod
    def close(cls):
        """关闭数据库连接"""
        if cls.__cur:
            cls.__cur.close()
        if cls.conn:
            cls.conn.close()

    @classmethod
    def dict2bean(cls, dict_data: Dict[str, Any], bean: Type) -> Any:
        """将字典转换为实体类"""
        bean_instance = bean()
        bean_fields = bean_instance.__fields__.keys()
        for key in dict_data.keys():
            if key in bean_fields:
                setattr(bean_instance, key, dict_data[key])
        return bean_instance

    @classmethod
    def dict_list2bean_list(cls, dict_list: List[Dict[str, Any]], bean: Type) -> List[Any]:
        """将字典列表转换为实体类列表"""
        return [cls.dict2bean(data, bean) for data in dict_list]

    @classmethod
    def execute_one(cls, sql: str, bean: Type, params: tuple = ()) -> Dict[str, Any]:
        """执行 SQL 语句并返回单条结果"""
        cls.execute(sql, params)
        return cls.fetchone()

    @classmethod
    def execute_all(cls, sql: str, bean: Type, params: tuple = (), limit=10) -> List[Any]:
        """执行 SQL 语句并返回所有结果"""
        # 如果 limit 为 None，则不限制查询数量
        if limit is not None:
            sql += f' limit {limit}'
        cls.execute(sql, params)
        result = cls.fetchall()
        if not result:
            return None
        return cls.dict_list2bean_list(result, bean)

    @classmethod
    def execute_all2dict(cls, sql: str, params: tuple = (), limit=10) -> List[Dict[str, Any]]:
        """执行 SQL 语句并返回所有结果"""
        # 如果 limit 为 None，则不限制查询数量
        if limit is not None:
            sql += f' limit {limit}'
        cls.execute(sql, params)
        result = cls.fetchall()
        if not result:
            return None
        return result

    @classmethod
    def select_by_id(cls, table_name: str, id: Any, bean: Type) -> Any:
        """根据 ID 查询表中数据"""
        sql = f'select * from {table_name} where id=%s'
        cls.execute(sql, (id,))
        result = cls.fetchone()
        if result is None:
            return None
        return cls.dict2bean(result, bean)

    @classmethod
    def select_by_dict(cls, table_name: str, dict_data: Dict[str, Any], bean: Type, limit: int = 10) -> List[Any]:
        """根据字典查询表中数据"""
        sql = f'select * from {table_name} where '
        values = []

        for key, value in dict_data.items():
            if value is not None and value != "":
                sql += f'{key}=%s and '
                values.append(value)

        if not values:
            sql = sql[:-7]  # 删除 ' where ' 的最后 7 个字符
        else:
            sql = sql[:-4]  # 删除 ' and ' 的最后 4 个字符

        if limit is not None:
            sql += f' limit {limit}'

        cls.execute(sql, tuple(values))
        result = cls.fetchall()

        if not result:
            return None

        return cls.dict_list2bean_list(result, bean)


# 初始化数据库连接
MySQLConnect.connect()
