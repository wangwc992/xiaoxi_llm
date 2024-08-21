import asyncio
import signal

from app.start_init.mysql_binglog_monitoring import start_binlog_listener


async def run_server() -> None:
    loop = asyncio.get_running_loop()

    binlog_task = loop.create_task(start_binlog_listener())

    def signal_handler() -> None:
        # prevents the uvicorn signal handler to exit early
        binlog_task.cancel()

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        # 等待 binlog 监听任务完成
        await binlog_task
    except asyncio.CancelledError:
        print("Gracefully stopping binlog listener")
        # 如果有任何需要执行的清理操作，可以在这里进行
        # await server.shutdown()


asyncio.run(run_server())
print("Done")
