import contextvars

# 定义上下文变量
request_context = contextvars.ContextVar("request_context")
