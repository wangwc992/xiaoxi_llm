import asyncio
import signal
import time

from app.start_init.mysql_binglog_monitoring import start_binlog_listener
async def run_server():
    binlog_task = asyncio.create_task(start_binlog_listener())

    loop = asyncio.get_running_loop()



    def signal_handler() -> None:
        # prevents the uvicorn signal handler to exit early
        binlog_task.cancel()  # 取消 binlog 监听任务


    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        await asyncio.gather(binlog_task)
    except asyncio.CancelledError:
        print("Gracefully stopping http server and binlog listener")

asyncio.run(run_server())
print("Done")
time.sleep(3000)