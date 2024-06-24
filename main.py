from fastapi import FastAPI

from app.api.chat import knowledge_ik_index_controller
from app.api.text2vec_custom import text2vec_custom as encode

app = FastAPI()

app.include_router(knowledge_ik_index_controller.router)
app.include_router(encode.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
