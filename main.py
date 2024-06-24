from fastapi import FastAPI

from app.api.chat import knowledge_ik_index_controller

app = FastAPI()

app.include_router(knowledge_ik_index_controller.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
