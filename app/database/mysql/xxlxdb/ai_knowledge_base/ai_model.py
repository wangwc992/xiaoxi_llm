

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class MyChatCompletionRequestModel(BaseModel):
    """对话完成请求模型"""
    query: str = Field(..., description="用户输入的问题")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    model: Optional[str] = Field("/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4", description="模型名称")
    conversation_id: Optional[str] = Field(None, description="会话id，用于标识一个会话")
    user_type: Optional[str] = Field("1", description="用户类型2，顾问，3，机构")
    user_id: Optional[str] = Field("0", description="2为member_id,3为机构id")
    reanswer: Optional[bool] = Field(False, description="是否再次回答")


class ClassificationModel(BaseModel):
    """分类模型"""
    query_type: Optional[str] = Field(None, description="问题类型")
    task: Optional[int] = Field(None, description="任务编号")
    student_name: Optional[str] = Field(None, description="学生姓名")
    school_name: Optional[str] = Field(None, description="学校名称")
    major_name: Optional[str] = Field(None, description="专业名称")
    service_school_id: Optional[list] = Field(None, description="服务学校id")


class AiChatLogModel(BaseModel):
    """对话记录模型"""
    id: Optional[int] = Field(None, description="主键id")
    chat_id: Optional[str] = Field(None, description="聊天id")
    conversation_id: Optional[str] = Field(None, description="会话id")
    user_id: Optional[str] = Field(None, description="用户id")
    model_name: Optional[str] = Field(None, description="模型名称")
    message_type: Optional[str] = Field(None, description="消息类型")
    query: Optional[str] = Field(None, description="用户输入")
    prompt: Optional[str] = Field(None, description="prompt")
    prompt_tokens: Optional[int] = Field(None, description="prompt token")
    output: Optional[str] = Field(None, description="ai回答")
    completion_tokens: Optional[int] = Field(None, description="ai token")
    total_tokens: Optional[int] = Field(None, description="总token")
    start_time: Optional[datetime] = Field(default_factory=datetime.now, description="开始时间")
    total_duration: Optional[int] = Field(None, description="总耗时（秒）")
    delete_status: Optional[int] = Field(default=0, description="逻辑删除")


class ReferenceDataDto(BaseModel):
    """参考数据模型"""
    reference_data: str = Field(None, description="参考数据")
    knowledge_link: list = Field(None, description="知识链接")
    reference_data_count: int = Field(None, description="参考数据数量")
