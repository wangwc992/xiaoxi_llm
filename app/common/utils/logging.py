import logging
import sys
from datetime import datetime

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