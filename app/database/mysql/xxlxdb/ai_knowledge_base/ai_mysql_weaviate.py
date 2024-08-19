'''CREATE TABLE `ai_mysql_weaviate` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `weaviate_id` varchar(100) NOT NULL COMMENT '向量数据库id',
  `db_id` varchar(100) NOT NULL COMMENT 'mysql_id',
  `db_name` varchar(100) NOT NULL COMMENT 'mysql数据库表名',
  `instruction` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '描述',
  `input` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '输入',
  `output` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '输出',
  `file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '文件地址',
  `file_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '文件内容',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `status` tinyint(1) DEFAULT '0' COMMENT '是否开启',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;'''
from typing import Optional, Union

from pydantic import BaseModel, Field

from app.database.mysql.mysql_client import yhj


class AiMysqlWeaviate(BaseModel):
    id: Optional[int] = Field(None, description="主键id")
    weaviate_id: Optional[str] = Field(None, description="向量数据库id")
    db_id: Optional[str] = Field(None, description="mysql_id")
    db_name: Optional[str] = Field(None, description="mysql数据库表名")
    instruction: Optional[str] = Field(None, description="描述")
    input: Optional[str] = Field(None, description="输入")
    output: Optional[str] = Field(None, description="输出")
    file_url: Optional[str] = Field(None, description="文件地址")
    file_content: Optional[str] = Field(None, description="文件内容")
    create_time: Optional[str] = Field(None, description="创建时间")
    update_time: Optional[str] = Field(None, description="修改时间")
    status: Optional[int] = Field(None, description="是否开启")


def insert_ai_mysql_weaviate(ai_mysql_weaviate: Union[AiMysqlWeaviate, dict]):
    if isinstance(ai_mysql_weaviate, dict):
        ai_mysql_weaviate = AiMysqlWeaviate(**ai_mysql_weaviate)
    # 使用预编译的格式ai_mysql_weaviate 插入数据
    sql = '''INSERT INTO ai_mysql_weaviate (weaviate_id, db_id, db_name, instruction, input, output, file_url, file_content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    params = (
        ai_mysql_weaviate.weaviate_id,
        ai_mysql_weaviate.db_id,
        ai_mysql_weaviate.db_name,
        ai_mysql_weaviate.instruction,
        ai_mysql_weaviate.input,
        ai_mysql_weaviate.output,
        ai_mysql_weaviate.file_url,
        ai_mysql_weaviate.file_content
    )
    yhj.execute(sql, params)


def update_ai_mysql_weaviate(ai_mysql_weaviate: Union[AiMysqlWeaviate, dict]):
    if isinstance(ai_mysql_weaviate, dict):
        ai_mysql_weaviate = AiMysqlWeaviate(**ai_mysql_weaviate)
    # 使用预编译的格���ai_mysql_weaviate 更新数据,数据值不为空的字段作为查询条件
    sql = '''UPDATE ai_mysql_weaviate SET '''
    values = []
    for key, value in ai_mysql_weaviate.dict().items():
        if value is not None and value != "":
            sql += f'{key}=%s, '
            values.append(value)
    if not values:
        return
    sql = sql[:-2]
    sql += ''' WHERE id=%s'''
    values.append(ai_mysql_weaviate.id)
    yhj.execute(sql, tuple(values))


def insert_ai_mysql_weaviate_bath(ai_mysql_weaviate_list: list[Union[AiMysqlWeaviate, dict]]):
    #     批处理插入
    if isinstance(ai_mysql_weaviate_list, list):
        ai_mysql_weaviate_list = [AiMysqlWeaviate(**ai_mysql_weaviate) for ai_mysql_weaviate in ai_mysql_weaviate_list]
    # 使用预编译的格式ai_mysql_weaviate 插入数据
    sql = '''INSERT INTO ai_mysql_weaviate (weaviate_id, db_id, db_name, instruction, input, output, file_url, file_content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    params = [(ai_mysql_weaviate.weaviate_id, ai_mysql_weaviate.db_id, ai_mysql_weaviate.db_name,
               ai_mysql_weaviate.instruction, ai_mysql_weaviate.input, ai_mysql_weaviate.output,
               ai_mysql_weaviate.file_url, ai_mysql_weaviate.file_content) for ai_mysql_weaviate in
              ai_mysql_weaviate_list]
    yhj.mysql_client.executemany(sql, params)
    yhj.mysql_client.connection.commit()


def select_ai_mysql_weaviate(ai_mysql_weaviate: Union[AiMysqlWeaviate, dict], limit: int):
    if isinstance(ai_mysql_weaviate, AiMysqlWeaviate):
        ai_mysql_weaviate = ai_mysql_weaviate.dict()
    # 使用预编译的格式ai_mysql_weaviate 查询数据,数据值不为空的字段作为查询条件
    sql = '''SELECT * FROM ai_mysql_weaviate WHERE '''
    values = []
    for key, value in ai_mysql_weaviate.items():
        if value is not None and value != "":
            sql += f'{key}=%s and '
            values.append(value)
    if not values:
        sql = sql[:-7]
    else:
        sql = sql[:-4]
    sql += f' limit {limit}'
    ai_mysql_weaviate_list = yhj.execute_all2dict(sql, params=tuple(values))
    return ai_mysql_weaviate_list


def update_ai_mysql_weaviate(ai_mysql_weaviate: Union[AiMysqlWeaviate, dict]):
    if isinstance(ai_mysql_weaviate, AiMysqlWeaviate):
        ai_mysql_weaviate = ai_mysql_weaviate.dict()
    # 使用预编译的格式ai_mysql_weaviate 更新数据,数据值不为空的字段作为查询条件
    sql = '''UPDATE ai_mysql_weaviate SET '''
    values = []
    for key, value in ai_mysql_weaviate.items():
        if value is not None and value != "":
            sql += f'{key}=%s, '
            values.append(value)
    if not values:
        return
    sql = sql[:-2]
    sql += ''' WHERE id=%s'''
    values.append(ai_mysql_weaviate.get('id'))
    yhj.execute(sql, tuple(values))


if __name__ == '__main__':
    ai_mysql_weaviate = {
        # "id": 1,
        "weaviate_id": "weaviasadate_id1",
        "db_id": "db_id2312321",
        "db_name": "db_name",
        "instruction": "instruction",
        "input": "input",
        "output": "output",
        "file_url": "file_url",
        "file_content": "file_content",
    }
    insert_ai_mysql_weaviate(ai_mysql_weaviate)
    # ai_mysql_weaviate_list = select_ai_mysql_weaviate(ai_mysql_weaviate, 10)
    # for ai_mysql_weaviate in ai_mysql_weaviate_list:
    #     print(ai_mysql_weaviate)
    # update_ai_mysql_weaviate(ai_mysql_weaviate)
