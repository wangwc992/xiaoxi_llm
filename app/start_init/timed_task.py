import asyncio

import schedule
import time

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import cleansing_manner_execution, MannerExecution
from app.database.weaviate.knowledge_base import knowledge_base_weaviate

logger = get_logger(__name__)


def run_scheduler():
    logger.info("run_scheduler start...")
    # 每分钟 第三秒执行一次任务
    schedule.every().day.at("03:00").do(knowledge_base_cleansing)
    while True:
        schedule.run_pending()
        time.sleep(60)


def knowledge_base_cleansing():
    logger.info("knowledge_base_cleansing start...")
    method_lsit = ['platform_introduction', 'zn_school_info', 'zn_school_info_rank', 'zn_school_info_more',
                   'zn_school_selection_reason', 'zn_school_admission_undergraduate',
                   'zn_school_admission_graduate_student', 'zn_school_admission_art', 'zn_school_department_project']
    for method_name in method_lsit:
        result = knowledge_base_weaviate.clear_all_data(property="db_name", like_str=method_name)
        logger.info(f"清空{method_name}数据结果: {result}")
    logger.info("开始清洗数据")
    manner_execution = MannerExecution(
        method_name="t_knowledge_info",
        limit=1000,
        start_id=0,
        frequency=-1,
        is_async=True,
        insert_to_ai_mysql_weaviate=False
    )
    asyncio.run(cleansing_manner_execution(manner_execution))
