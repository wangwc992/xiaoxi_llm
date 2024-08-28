import time
from fastapi import FastAPI
from starlette.responses import StreamingResponse

app = FastAPI()

async def get_data():
    yield '''data: {"choices": [ { "index": 0, "delta": { "role": "2", "content": "chat线程数量超了" }} ]}'''
    yield '''data: {"choices": [ { "index": 0, "delta": { "role": "2", "content": "chat线程数量超了" }} ]}'''
    time.sleep(5)
    yield "3"
    yield "4"

@app.get("/")
async def read_root():
    yield StreamingResponse(get_data(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)