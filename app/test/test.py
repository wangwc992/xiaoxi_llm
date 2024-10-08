import datetime
import threading

import schedule
import time

# 定义文件重命名函数
def rename_log_file():
    #  打印当前时间
    print(f"rename_log_file running...{datetime.datetime.now()}")


def run_rename_log_file_task():
    print("rename_log_file start ...")
    # 每天定时执行
    # schedule.every().day.at("00:00").do(rename_log_file)
    # 每分钟执行一次
    schedule.every().minute.do(rename_log_file)

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每60秒检查一次任务

# 开启一个线程，运行定时任务
threading.Thread(target=run_rename_log_file_task, daemon=True).start()

while True:
    time.sleep(1)