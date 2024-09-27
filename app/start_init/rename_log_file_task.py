import os
import schedule
import time
from datetime import datetime

from app.common.utils.logging import get_logger

logger = get_logger(__name__)

# 定义文件重命名函数
def rename_log_file():
    logger.info("rename_log_file running...")
    # 当前时间
    current_time = datetime.now().strftime('%Y_%m_%d:%H-%M-%S')

    log_dir = "/root/autodl-tmp/project/xiaoxi_llm/logs"
    # 根据当前时间创建新的日志文件，将run_log.log的文件内容写入新的日志文件，并清空run_log.log

    # 获取run_log.log文件的路径
    run_log_file_path = os.path.join(log_dir, "run_log.log")
    # 获取新的日志文件的路径
    new_log_file_path = os.path.join(log_dir, f"run_log_{current_time}.log")
    # 将run_log.log文件的内容写入新的日志文件
    with open(run_log_file_path, "r") as f:
        log_content = f.read()
        with open(new_log_file_path, "w") as new_f:
            new_f.write(log_content)
    # 清空run_log.log文件
    with open(run_log_file_path, "w") as f:
        f.write("")
    print(f"rename log file success, new log file path: {new_log_file_path}")


def run_rename_log_file_task():
    logger.info("rename_log_file start ...")
    # 每天定时执行
    schedule.every().day.at("00:00").do(rename_log_file)
    # 每分钟执行一次
    # schedule.every().minute.do(rename_log_file)

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每60秒检查一次任务
