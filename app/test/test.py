import threading
from fastapi import FastAPI

app = FastAPI()

from app.start_init.mysql_binglog_monitoring import start_binlog_listener

# def start_binlog_listener():
#     print("Binlog listener started in thread.")
#     while True:
#         import time
#         time.sleep(1)
#         print("Listening for Binlog events...")

@app.on_event("startup")
async def startup_event():
    print("Binlog 监听已启动1")
    # 将 Binlog 监听器放到一个单独的线程中运行
    listener_thread = threading.Thread(target=start_binlog_listener, daemon=True)
    listener_thread.start()
    print("Binlog 监听已启动完成")
@app.get("/")
async def read_root():
    return {"message": "FastAPI server is running."}

# 主程序入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
