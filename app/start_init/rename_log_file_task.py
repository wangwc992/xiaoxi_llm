import os
import schedule
import time
from datetime import datetime


# 定义文件重命名函数
def rename_log_file():
    # 当前时间
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')

    # 原日志文件路径
    old_file_path = '/root/autodl-tmp/project/xiaoxi_llm/log.log'

    # 新的文件路径
    new_file_name = f'log_{current_time}.log'
    new_file_path = f'/root/autodl-tmp/project/xiaoxi_llm/{new_file_name}'

    # 如果旧文件存在，则重命名
    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)
        print(f'Renamed log file to {new_file_name}')
        # 再创建一个新的日志文件old_file_path
        with open(old_file_path, 'w') as f:
            f.write('')

    else:
        print('Log file does not exist.')


def run_rename_log_file_task():
    # 每天定时执行
    # schedule.every().day.at("00:00").do(rename_log_file)
    # 每分钟执行一次
    schedule.every().minute.do(rename_log_file)

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每60秒检查一次任务
