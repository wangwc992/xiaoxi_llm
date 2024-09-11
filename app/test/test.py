from datetime import datetime

from pydantic import BaseModel, Field


class AiChatWeaviateModel(BaseModel):
    conversation_id: str = Field(None, description="会话id，用于标识一个会话")
    message_id: str = Field(None, description="消息id，用于标识一个消息")
    user_id: str = Field(None, description="用户id，用于标识一个用户")
    instruction: str = Field(None, description="用户输入的问题")
    output: str = Field(None, description="小希的回答")
    created_time: datetime = Field(None, description="消息创建时间")



z = AiChatWeaviateModel(conversation_id="1", message_id="2", user_id="3", instruction="4", output="5", created_time=datetime.now())

print(z.dict())
print(z.__dict__)

