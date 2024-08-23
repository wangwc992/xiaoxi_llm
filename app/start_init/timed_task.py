import schedule
import time

from app.common.utils.logging import get_logger
from app.data_cleansing.knowledge_base_cleansing import cleansing_manner_execution, MannerExecution

logger = get_logger(__name__)

def run_scheduler():
    schedule.every().day.at("03:00").do(knowledge_base_cleansing)
    while True:
        schedule.run_pending()
        time.sleep(1)


async def knowledge_base_cleansing():
    logger.info("开始清洗知识库数据")
#     每天凌晨三点清洗一次
    manner_execution = MannerExecution(
        method_name="t_knowledge_info",
        limit=1000,
        start_id=0,
        frequency=-1,
        is_async=True
    )
    await cleansing_manner_execution(manner_execution)

