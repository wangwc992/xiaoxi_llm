from fastapi import FastAPI, BackgroundTasks
import schedule
import time
import threading

app = FastAPI()


async def job():
    print("任务执行中...")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


@app.on_event("startup")
def start_scheduler():
    # 设置每分钟 第三秒执行一次任务
    schedule.every().minute.at(":03").do(job)

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