from langchain_core.messages import BaseMessage

function_message = BaseMessage(
    type="tool_calls",
    content=(
        f"asdas"
    )
)