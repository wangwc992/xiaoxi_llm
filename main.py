from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.knowledge import knowledge_ik_index_controller
from app.api.openai import api_server
from app.api.knowledge_base import knowledge_base
from app.api.text2vec_custom import text2vec_custom as encode
from fastapi.middleware.cors import CORSMiddleware

from app.common.core.langchain_client import VllmClient

_running_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await VllmClient.initialize()

    # async def _force_log():
    #     while True:
    #         await asyncio.sleep(10)
    #         await VllmClient.engine.do_log_stats()
    #
    # if not VllmClient.engine_args.disable_log_stats:
    #     task = asyncio.create_task(_force_log())
    #     _running_tasks.add(task)
    #     task.add_done_callback(_running_tasks.remove)

    yield

app = FastAPI(lifespan=lifespan)

# app = FastAPI()

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定允许的域名列表，例如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 POST、OPTIONS 等
    allow_headers=["*"],  # 允许所有头部，包括自定义的头部
)

app.include_router(knowledge_ik_index_controller.router)
app.include_router(encode.router)
app.include_router(api_server.router)
app.include_router(knowledge_base.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=6006)
