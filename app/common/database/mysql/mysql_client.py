import MySQLdb
import MySQLdb.cursors
from typing import Any, Dict, List, Type
from app.common.core.config import settings
from app.common.utils.logging import get_logger

logger = get_logger(__name__)


class MySQLConnect:

    def __init__(self, database: str):
        self.mysql_dict = settings["mysql"][database]
        """建立数据库连接"""
        self.conn = MySQLdb.connect(
            host=self.mysql_dict["host"],
            user=self.mysql_dict["user"],
            passwd=self.mysql_dict["password"],
            database=self.mysql_dict["database"],
            port=self.mysql_dict["port"],
            cursorclass=MySQLdb.cursors.DictCursor  # 使用字典游标类
        )
        self.__cur = self.conn.cursor()

    def check_connection(self):
        """检查连接状态，如果断开则重新连接"""
        try:
            self.conn.ping()
        except MySQLdb.Error as e:
            print(f"Database connection error: {e}")
            self.connect()

    def execute(self, sql: str, params: tuple = ()):
        """执行 SQL 语句，带有自动重连功能"""
        self.check_connection()
        # 打印 执行的sql
        logger.info("Executing query: %s", self.__cur.mogrify(sql, params))
        try:
            self.__cur.execute(sql, params)
        except MySQLdb.Error as e:
            logger.error("Error executing query: %s", e)
            self.connect()  # 尝试重新连接
            self.__cur.execute(sql, params)  # 再次尝试执行

    def fetchall(self) -> List[Dict[str, Any]]:
        """获取所有查询结果"""
        return self.__cur.fetchall()

    def fetchone(self) -> Dict[str, Any]:
        """获取单条查询结果"""
        return self.__cur.fetchone()

    def close(self):
        """关闭数据库连接"""
        if self.__cur:
            self.__cur.close()
        if self.conn:
            self.conn.close()

    def dict2bean(self, dict_data: Dict[str, Any], bean: Type) -> Any:
        """将字典转换为实体类"""
        bean_instance = bean()
        bean_fields = bean_instance.__fields__.keys()
        for key in dict_data.keys():
            if key in bean_fields:
                setattr(bean_instance, key, dict_data[key])
        return bean_instance

    def dict_list2bean_list(self, dict_list: List[Dict[str, Any]], bean: Type) -> List[Any]:
        """将字典列表转换为实体类列表"""
        return [self.dict2bean(data, bean) for data in dict_list]

    def execute_one(self, sql: str, bean: Type, params: tuple = ()) -> Dict[str, Any]:
        """执行 SQL 语句并返回单条结果"""
        self.execute(sql, params)
        return self.fetchone()

    def execute_all2object(self, sql: str, bean: Type, params: tuple = (), limit=10) -> List[Any]:
        """执行 SQL 语句并返回所有结果"""
        # 如果 limit 为 None，则不限制查询数量
        if limit is not None:
            sql += f' limit {limit}'
        self.execute(sql, params)
        result = self.fetchall()
        if not result:
            return None
        return self.dict_list2bean_list(result, bean)

    def execute_all2dict(self, sql: str, params: tuple = (), limit=10) -> List[Dict[str, Any]]:
        """执行 SQL 语句并返回所有结果"""
        # 如果 limit 为 None，则不限制查询数量
        if limit is not None:
            sql += f' limit {limit}'
        self.execute(sql, params)
        result = self.fetchall()
        if not result:
            return None
        return result

    def select_by_id(self, table_name: str, id: Any, bean: Type) -> Any:
        """根据 ID 查询表中数据"""
        sql = f'select * from {table_name} where id=%s'
        self.execute(sql, (id,))
        result = self.fetchone()
        if result is None:
            return None
        return self.dict2bean(result, bean)

    def select_by_dict(self, table_name: str, dict_data: Dict[str, Any], bean: Type, limit: int = 10) -> List[Any]:
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

        self.execute(sql, tuple(values))
        result = self.fetchall()

        if not result:
            return None

        return self.dict_list2bean_list(result, bean)


xxlxdb = MySQLConnect("xxlxdb")
smart_counselor = MySQLConnect("smart_counselor")

if __name__ == '__main__':
    sql = "SELECT * FROM `school_info`"
    result = smart_counselor.execute_all2dict(sql)
    print(result)
    smart_counselor.close()
