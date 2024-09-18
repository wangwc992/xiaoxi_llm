import os
import threading

from app.common.core.config import settings
from app.data.dictionaries import sensitive_words
from app.middleware.exception import ChatSuspendException, chat_suspend_exception_handler
from app.middleware.middleware import log_request_body, sensitive_word_filter, authentication
from app.start_init.mysql_binglog_monitoring import start_binlog_listener
from app.start_init.timed_task import run_scheduler

gpu_count = settings.get('gpu_count', 0)
# 根据配置文件中的 gpu_count 设置 CUDA_VISIBLE_DEVICES 环境变量
os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(map(str, range(gpu_count)))

import asyncio
import importlib
import inspect
import re
import signal
from contextlib import asynccontextmanager
from typing import Optional, Set

import fastapi
import uvicorn
from fastapi import APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client import make_asgi_app
from starlette.routing import Mount

import vllm.envs as envs
from vllm.entrypoints.openai.cli_args import make_arg_parser
from vllm.logger import init_logger
from vllm.utils import FlexibleArgumentParser
from vllm.version import __version__ as VLLM_VERSION

from app.api.openai.api_server import build_server
from app.api.openai import api_server
from app.api.knowledge_base import knowledge_base
from app.api.knowledge_base import knowledge_base_weaviate
from app.api.text2vec_custom import text2vec_custom
from app.api.html import chat_dome

logger = init_logger('vllm.entrypoints.openai.api_server')

_running_tasks: Set[asyncio.Task] = set()
TIMEOUT_KEEP_ALIVE = 5  # seconds


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


def build_app(args, **uvicorn_kwargs):
    app = fastapi.FastAPI()
    app.include_router(api_server.router)
    app.include_router(knowledge_base.router)
    app.include_router(text2vec_custom.router)
    app.include_router(knowledge_base_weaviate.router)
    app.include_router(chat_dome.router)
    app.root_path = args.root_path

    # TODO 注册启动事件
    @app.on_event("startup")
    async def startup_event():
        threading.Thread(target=start_binlog_listener, daemon=True).start()
        threading.Thread(target=run_scheduler, daemon=True).start()

    mount_metrics(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=args.allowed_origins,
        allow_credentials=args.allow_credentials,
        allow_methods=args.allowed_methods,
        allow_headers=args.allowed_headers,
    )

    # 注册自定义的 chat_suspend 异常处理器
    app.add_exception_handler(ChatSuspendException, chat_suspend_exception_handler)

    # 注册自定义的中间件
    middlewares = [log_request_body, sensitive_word_filter, authentication]
    for middleware in middlewares:
        app.middleware("http")(middleware)

    # 这段代码的主要目的是通过配置文件或命令行参数动态加载中间件，可以是中间件类或异步函数。它让应用更灵活，可以在运行时决定使用哪些中间件，而不是在代码中硬编码。这种方式非常适合需要根据不同环境或配置条件来加载不同中间件的场景
    for middleware in args.middleware:
        module_path, object_name = middleware.rsplit(".", 1)
        imported = getattr(importlib.import_module(module_path), object_name)
        if inspect.isclass(imported):
            app.add_middleware(imported)
        elif inspect.iscoroutinefunction(imported):
            app.middleware("http")(imported)
        else:
            raise ValueError(f"Invalid middleware {middleware}. "
                             f"Must be a function or a class.")

    app.root_path = args.root_path

    logger.info("Available routes are:")
    for route in app.routes:
        if not hasattr(route, 'methods'):
            continue
        methods = ', '.join(route.methods)
        logger.info("Route: %s, Methods: %s", route.path, methods)

    config = uvicorn.Config(
        app,
        host=args.host,
        port=args.port,
        log_level=args.uvicorn_log_level,
        timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
        ssl_ca_certs=args.ssl_ca_certs,
        ssl_cert_reqs=args.ssl_cert_reqs,
        **uvicorn_kwargs,
    )

    return uvicorn.Server(config)


async def run_server(args, llm_engine=None, **uvicorn_kwargs) -> None:
    logger.info("vLLM API server version %s", VLLM_VERSION)
    logger.info("args: %s", args)

    await build_server(args, llm_engine)
    server = build_app(args, **uvicorn_kwargs)

    loop = asyncio.get_running_loop()

    server_task = loop.create_task(server.serve())

    def signal_handler() -> None:
        # prevents the uvicorn signal handler to exit early
        server_task.cancel()

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    try:
        await asyncio.gather(server_task)
    except asyncio.CancelledError:
        print("Gracefully stopping http server and binlog listener")
        await server.shutdown()
        # 等待 binlog 监听任务完成


if __name__ == "__main__":
    # NOTE(simon):
    # This section should be in sync with vllm/scripts.py for CLI entrypoints.
    parser = FlexibleArgumentParser(
        description="vLLM OpenAI-Compatible RESTful API server.")
    parser = make_arg_parser(parser)
    args = parser.parse_args()
    asyncio.run(run_server(args))
