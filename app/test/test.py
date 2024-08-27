from fastapi import Request, FastAPI, BackgroundTasks

from langchain_core.prompts import PromptTemplate

from app.api.openai.api_server import create_chat_completion
from app.common.utils.logging import get_logger
from app.prompt import classificationQuery
from pydantic import BaseModel, Field
from typing import Optional

logger = get_logger(__name__)
app = FastAPI()


class MyChatCompletionRequestModel(BaseModel):
    query: str = Field(None, description="用户输入的问题")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    model: Optional[str] = Field("/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4", description="模型名称")
    conversation_id: Optional[str] = Field(None, description="会话id，用于标识一个会话")
    member_id: Optional[str] = Field("1001", description="用户ID")


@app.post("/")
async def read_root(request: MyChatCompletionRequestModel, raw_request: Request, background_tasks: BackgroundTasks):
    classification_query = PromptTemplate.from_template(classificationQuery)
    classification_query_prompt = classification_query.format(input=request.query)
    system = {"role": "system", "content": "你是问题分类助手"}
    human = {"role": "human", "content": classification_query_prompt}
    chat_request = ChatCompletionRequest(
        messages=[system, human],
        model=request.model,
    )
    result = await create_chat_completion(chat_request, raw_request)
    print(result)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=6006)
