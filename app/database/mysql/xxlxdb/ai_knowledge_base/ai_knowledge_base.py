'''CREATE TABLE `ai_knowledge_base_keyword` (
	`id` INT(10) NOT NULL COMMENT '主键id',
	`database` VARCHAR(512) NOT NULL COMMENT '数据库' COLLATE 'utf8mb4_0900_ai_ci',
	`keyword` VARCHAR(512) NOT NULL COMMENT '关键字' COLLATE 'utf8mb3_general_ci',
	`state` TINYINT(1) NOT NULL DEFAULT '1' COMMENT '是否启用'
)
COMMENT='ai知识库关键字'
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB;
'''

from app.database.mysql.mysql_client import yhj

def get_keyword_by_database(database: str = None):
    if database:
        sql = f"SELECT * FROM ai_knowledge_base_keyword WHERE `database` = '{database}' AND state = 1"
    else:
        sql = f"SELECT * FROM ai_knowledge_base_keyword WHERE state = 1"
    keyword_dict_list = yhj.execute_all2dict(sql)
    return keyword_dict_list

