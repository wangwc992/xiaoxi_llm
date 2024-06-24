from fastapi import FastAPI

from fastapi import HTTPException
from app.common.core.langchain_client import embedding

app = FastAPI()

# 活跃状态检查
@app.get('/.well-known/live')
def live():
    return '', 204


# 准备状态检查
@app.get('/.well-known/ready')
def ready():
    # 在这里可以加上模型加载和其他准备工作的检查逻辑
    return '', 204


# 获取元信息
@app.get('/meta')
def meta():
    meta_info = {
        "model_name": "BAAI/bge-large-zh-v1.5",
        "description": "A small, efficient sentence transformer model."
    }
    # return json.dumps(meta_info, ensure_ascii=False)
    return meta_info


# 获取文本向量
@app.post('/vectors')
def get_vectors(text: str):
    if not text:
        raise HTTPException(status_code=400, detail="No sentences provided")

    # 生成向量
    encoded_vector = embedding.embed_query(text)
    response = {
        "text": text,
        "vector": encoded_vector,
        "dim": len(encoded_vector)
    }

    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8090)
