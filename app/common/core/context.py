# context.py
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import contextvars

# 忽略所有的 DeprecationWarning

# 你的应用程序代码

# 定义上下文变量
request_context = contextvars.ContextVar("request_context")
