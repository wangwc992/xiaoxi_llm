from app.database.mysql.mysql_client import xxlxdb
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_model import AiChatLogModel

'''CREATE TABLE `ai_knowledge_base_keyword` (
	`id` INT(10) NOT NULL COMMENT '主键id',
	`database` VARCHAR(512) NOT NULL COMMENT '数据库' COLLATE 'utf8mb4_0900_ai_ci',
	`keyword` VARCHAR(512) NOT NULL COMMENT '关键字' COLLATE 'utf8mb3_general_ci',
	`state` TINYINT(1) NOT NULL DEFAULT '1' COMMENT '是否启用'
)
COMMENT='ai知识库关键字' COLLATE='utf8mb4_0900_ai_ci' ENGINE=InnoDB;'''


def get_keyword_by_database(database: str = None):
    if database:
        sql = f"SELECT * FROM ai_knowledge_base_keyword WHERE `database` = '{database}' AND state = 1"
    else:
        sql = f"SELECT * FROM ai_knowledge_base_keyword WHERE state = 1"
    keyword_dict_list = xxlxdb.execute_all2dict(sql)
    return keyword_dict_list


'''CREATE TABLE `ai_prompt` (
  `id` int NOT NULL COMMENT '主键id',
  `type` varchar(128) NOT NULL COMMENT '使用类型，在哪使用',
  `prompt` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT '模板',
  `state` tinyint(1) NOT NULL DEFAULT '1' COMMENT '是否启用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='ai prompt';'''


def get_prompt_by_type():
    # 返回id最大的
    sql = f"SELECT type,prompt FROM ai_prompt WHERE state = 1 "
    prompt_list = xxlxdb.execute_all2dict(sql)
    return prompt_list


def insert_ai_chat_log(ai_chat_log: AiChatLogModel):
    # 过滤掉空值，并确保安全插入
    ai_chat_log_dict = ai_chat_log.model_dump(exclude_unset=True)

    if not ai_chat_log_dict:
        # 如果所有值都为空，直接返回
        return

    keys = ','.join(ai_chat_log_dict.keys())
    placeholders = ','.join(['%s'] * len(ai_chat_log_dict))  # 使用占位符
    values = list(ai_chat_log_dict.values())  # 提取出所有的值

    # 参数化查询，避免SQL注入
    sql = f"INSERT INTO ai_chat_log ({keys}) VALUES ({placeholders})"

    # 使用参数化的方式执行 SQL
    xxlxdb.execute(sql, values)

