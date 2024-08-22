import logging
import sys
from datetime import datetime
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

LOG_FILE = "log.log"  # 日志文件名

class MillisecondFormatter(logging.Formatter):
    """
    自定义 Formatter，用于毫秒级日志记录。
    """
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime("%Y-%m-%d %H:%M:%S")
            s = f"{t},{int(record.msecs):03d}"
        return s

def get_logger(name: str) -> logging.Logger:
    """
    获取标准日志记录器，包含控制台输出和文件输出的处理器。
    """
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # 添加控制台输出处理程序
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = MillisecondFormatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 添加文件输出处理程序
        file_handler = logging.FileHandler(LOG_FILE)
        file_formatter = MillisecondFormatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# 定义数据模型
class MannerExecution(BaseModel):
    method_name: str
    limit: int
    start_id: int
    frequency: int

# 初始化 FastAPI 应用和路由
app = FastAPI()
router = APIRouter()

# 获取日志记录器
logger = get_logger("fastapi_logger")

@router.get("/", description="Cleansing the knowledge base.")
async def cleansing(manner_execution: str):
    """
    处理清洗请求
    """
    logger.info("Received cleansing request with args: %s", manner_execution)
    # 模拟处理请求
    return {"status": "cleansing started"}

# 将路由添加到应用
app.include_router(router)

# 启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)