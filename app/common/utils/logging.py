import logging
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

RUNNING_LOG = "running_log.txt"


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


class LoggerHandler(logging.Handler):
    """
    Logger handler used in Web UI.
    """

    def __init__(self, output_dir: str) -> None:
        super().__init__()
        formatter = MillisecondFormatter(
            fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        self.setLevel(logging.INFO)
        self.setFormatter(formatter)

        os.makedirs(output_dir, exist_ok=True)
        self.running_log = os.path.join(output_dir, RUNNING_LOG)
        if os.path.exists(self.running_log):
            os.remove(self.running_log)

        self.thread_pool = ThreadPoolExecutor(max_workers=1)

    def _write_log(self, log_entry: str) -> None:
        with open(self.running_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n\n")

    def emit(self, record) -> None:
        if record.name == "httpx":
            return

        log_entry = self.format(record)
        self.thread_pool.submit(self._write_log, log_entry)

    def close(self) -> None:
        self.thread_pool.shutdown(wait=True)
        return super().close()


def get_log_file_path() -> str:
    """
    动态生成日志文件路径，按分钟命名
    """
    current_time = datetime.now().strftime('%Y_%m_%d_%H_%M')
    # log_file = f"log_{current_time}.log"
    log_file = f"run_log.log"
    log_dir = "/root/autodl-tmp/project/xiaoxi_llm/logs"
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, log_file)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 添加控制台输出处理程序
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = MillisecondFormatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 添加文件输出处理程序，日志文件按分钟命名
    log_file_path = get_log_file_path()
    file_handler = logging.FileHandler(log_file_path)
    file_formatter = MillisecondFormatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def reset_logging() -> None:
    """
    Removes basic config of root logger.
    """
    root = logging.getLogger()
    list(map(root.removeHandler, root.handlers))
    list(map(root.removeFilter, root.filters))


# 示例：获取日志器并记录日志
if __name__ == "__main__":
    logger = get_logger("MyLogger")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
