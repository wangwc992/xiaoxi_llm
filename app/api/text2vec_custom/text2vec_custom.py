
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.common.core.langchain_client import Embedding

router = APIRouter()


# 活跃状态检查
@router.get('/.well-known/live')
def live():
    return '', 204


# 准备状态检查
@router.get('/.well-known/ready')
def ready():
    # 在这里可以加上模型加载和其他准备工作的检查逻辑
    return '', 204


# 获取元信息
@router.get('/meta')
def meta():
    meta_info = {
        "model_name": "BAAI/bge-large-zh-v1.5",
        "description": "A small, efficient sentence transformer model."
    }
    # return json.dumps(meta_info, ensure_ascii=False)
    return meta_info

# {
#   "text": "ai _ chat _ log 你好",
#   "dims": 0,
#   "vector": "",
#   "error": "",
#   "config": {
#     "pooling_strategy": "masked_mean"
#   }
# }
class Text2VecRequest(BaseModel):
    text: str
    dims: int = 0
    vector: str = ""
    error: str = ""
    config: dict = {"pooling_strategy": "masked_mean"}

# 获取文本向量
@router.post('/vectors')
def get_vectors(text2VecRequest: Text2VecRequest):
    print(text2VecRequest.__dict__)
    text = text2VecRequest.text
    if not text:
        raise HTTPException(status_code=400, detail="No sentences provided")
    # ai _ chat _ log query:海贼王，获取query:之后的文本
    if "query:" in text:
        text = text.split("query:")[1]

    # 生成向量
    encoded_vector = Embedding.embed_query(text)
    response = {
        "text": text,
        "vector": encoded_vector,
        "dim": len(encoded_vector)
    }

    return response
