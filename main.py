from fastapi import FastAPI

from app.api.chat import chat_gpt
from app.api.text2vec_custom import text2vec_custom as encode
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者指定允许的域名列表，例如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 POST、OPTIONS 等
    allow_headers=["*"],  # 允许所有头部，包括自定义的头部
)

app.include_router(chat_gpt.router)
app.include_router(encode.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
