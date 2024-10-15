import os

import threading

from app.common.core.config import settings
from app.middleware.exception import ChatSuspendException, chat_suspend_exception_handler
from app.middleware.middleware import log_request_body, sensitive_word_filter, authentication
from app.start_init.mysql_binglog_monitoring import start_binlog_listener
from app.start_init.rename_log_file_task import run_rename_log_file_task
from app.start_init.timed_task import run_scheduler

import asyncio
import importlib
import inspect
import re
import signal
from typing import Set

import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.routing import Mount

from app.api.knowledge_base import knowledge_base
from app.api.knowledge_base import knowledge_base_weaviate
from app.api.text2vec_custom import text2vec_custom


_running_tasks: Set[asyncio.Task] = set()
TIMEOUT_KEEP_ALIVE = 5  # seconds

gpu_count = settings.get('gpu_count', 0)
# 根据配置文件中的 gpu_count 设置 CUDA_VISIBLE_DEVICES 环境变量
model_environ = ','.join(map(str, range(gpu_count)))
app_environ = str(max(gpu_count - 1, 0))


def set_fastapi_gpu():
    # 设置FastAPI在GPU 0上运行
    os.environ['CUDA_VISIBLE_DEVICES'] = app_environ


def set_vllm_gpus():
    # 设置vLLM在GPU 1, 2, 3, 4上运行
    os.environ['CUDA_VISIBLE_DEVICES'] = model_environ


# @asynccontextmanager
# async def lifespan(app: fastapi.FastAPI):
#     async def _force_log():
#         while True:
#             await asyncio.sleep(10)
#             await engine.do_log_stats()
#
#     if not engine_args.disable_log_stats:
#         task = asyncio.create_task(_force_log())
#         _running_tasks.add(task)
#         task.add_done_callback(_running_tasks.remove)
#
#     yield


def mount_metrics(app: fastapi.FastAPI):
    # Add prometheus asgi middleware to route /metrics requests
    metrics_route = Mount("/metrics", make_asgi_app())
    # Workaround for 307 Redirect for /metrics
    metrics_route.path_regex = re.compile('^/metrics(?P<path>.*)$')
    app.routes.append(metrics_route)


def build_app():
    app = fastapi.FastAPI()
    app.include_router(knowledge_base.router)
    app.include_router(text2vec_custom.router)
    app.include_router(knowledge_base_weaviate.router)

    # TODO 注册启动事件
    # @app.on_event("startup")
    async def startup_event():
        threading.Thread(target=start_binlog_listener, daemon=True).start()
        threading.Thread(target=run_scheduler, daemon=True).start()
        threading.Thread(target=run_rename_log_file_task, daemon=True).start()

    mount_metrics(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册自定义的 chat_suspend 异常处理器
    app.add_exception_handler(ChatSuspendException, chat_suspend_exception_handler)

    # 注册自定义的中间件
    middlewares = [log_request_body, sensitive_word_filter, authentication]
    for middleware in middlewares:
        app.middleware("http")(middleware)

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=6006,
    )

    return uvicorn.Server(config)


async def run_server() -> None:

    # 设置 FastAPI 运行在 GPU 0
    set_fastapi_gpu()
    server = build_app()

    loop = asyncio.get_running_loop()

    server_task = loop.create_task(server.serve())

    def signal_handler() -> None:
        # prevents the uvicorn signal handler to exit early
        server_task.cancel()

    # loop.add_signal_handler(signal.SIGINT, signal_handler)
    # loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        await asyncio.gather(server_task)
    except asyncio.CancelledError:
        print("Gracefully stopping http server and binlog listener")
        await server.shutdown()
        # 等待 binlog 监听任务完成


if __name__ == "__main__":
    asyncio.run(run_server())
