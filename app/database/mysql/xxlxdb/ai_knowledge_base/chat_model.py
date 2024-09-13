from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field
from app.database.mysql.xxlxdb.ai_knowledge_base.ai_model import ClassificationModel, ReferenceDataDto
from vllm.entrypoints.chat_utils import CustomChatCompletionMessageParam


class Message(CustomChatCompletionMessageParam):
    """对话消息,重新方便使用"""
    pass


class DeltaFunctionCall(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class DeltaToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    index: int
    function: Optional[DeltaFunctionCall] = None


class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None
    tool_calls: List[DeltaToolCall] = Field(default_factory=list)


class ChatCompletionLogProb(BaseModel):
    token: str
    logprob: float = -9999.0
    bytes: Optional[List[int]] = None


class ChatCompletionLogProbsContent(ChatCompletionLogProb):
    top_logprobs: List[ChatCompletionLogProb] = Field(default_factory=list)


class ChatCompletionLogProbs(BaseModel):
    content: Optional[List[ChatCompletionLogProbsContent]] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: Optional[DeltaMessage] = Field(default_factory=DeltaMessage)
    message: Optional[DeltaMessage] = Field(default_factory=DeltaMessage)
    logprobs: Optional[ChatCompletionLogProbs] = None
    finish_reason: Optional[str] = None
    stop_reason: Optional[Union[int, str]] = None


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0


class ChatCompletionStreamResponse(BaseModel):
    id: Optional[str] = "default_id"
    object: str = "chat.completion.chunk"
    created: Optional[int] = 0  # Provide a default value
    model: Optional[str] = "default_model"  # Provide a default value
    choices: List[ChatCompletionResponseStreamChoice] = Field(
        default_factory=lambda: [ChatCompletionResponseStreamChoice(index=0, delta=DeltaMessage())])
    usage: Optional[UsageInfo] = Field(default_factory=UsageInfo)

    conversation_id: Optional[str] = None
    classification_model: Optional[ClassificationModel] = None
    reference_data_dto: Optional[ReferenceDataDto] = None


def datat_to_chat_completion_stream_response(data_str: str) -> ChatCompletionStreamResponse:
    """对话完成流响应转换"""
    print("*" * 20, data_str, "*" * 20)
    if data_str.startswith("data: "):
        data_str = data_str[len("data: "):]
    chat_completion_stream_response = ChatCompletionStreamResponse.parse_raw(data_str)
    return chat_completion_stream_response


if __name__ == "__main__":
    data_str = '''data: {
    "id": "chat-f7bb3ad9824444a9962c24ccbf443f35",
    "object": "chat.completion.chunk",
    "created": 1726110573,
    "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
    "choices": [
        {
            "index": 0,
            "delta": {
                "content": "你的"
            },
            "logprobs": null,
            "finish_reason": null
        }
    ],
    "usage": null
}'''
    print(datat_to_chat_completion_stream_response(data_str).dict())
    x = ChatCompletionStreamResponse()
    x.choices[0].delta.content = "你好"
    x.choices[0].delta.role = "小王"
    print(x.dict())
