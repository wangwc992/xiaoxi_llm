import asyncio

from fastapi import FastAPI, BackgroundTasks
import schedule
import time
import threading

from app.common.utils.logging import get_logger

logger = get_logger(__name__)
app = FastAPI()


async def job():
    print("任务执行中...")
def sync_job():
    asyncio.run(job())

def run_scheduler():
    logger.info("启动定时任务")
    # 设置每分钟 第三秒执行一次任务
    schedule.every().minute.at(":03").do(sync_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.on_event("startup")
def start_scheduler():
    # 启动一个后台线程来运行调度器
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # 守护线程，主线程退出时也随之退出
    scheduler_thread.start()


@app.get("/")
def read_root():
    return {"message": "FastAPI with schedule is running"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)