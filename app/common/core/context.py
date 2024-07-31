import contextvars

# 用于创建线程本地的上下文变量，这些变量在不同的线程或异步任务之间是独立的
request_context = contextvars.ContextVar("request_context")


