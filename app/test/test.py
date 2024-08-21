import asyncio
import signal

from app.start_init.mysql_binglog_monitoring import start_binlog_listener


async def run_server() -> None:
    loop = asyncio.get_running_loop()

    binlog_task = loop.run_in_executor(None, start_binlog_listener)

    def signal_handler() -> None:
        # prevents the uvicorn signal handler to exit early
        binlog_task.cancel()

    # loop.add_signal_handler(signal.SIGINT, signal_handler)
    # loop.add_signal_handler(signal.SIGTERM, signal_handler)

    await binlog_task
asyncio.run(run_server())
print("Done")