import logging
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

RUNNING_LOG = "running_log.txt"
LOG_FILE = "log.log"  # 日志文件名


class MillisecondFormatter(logging.Formatter):
    r"""
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
    r"""
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


def get_logger(name: str) -> logging.Logger:
    r"""
    Gets a standard logger with a stream handler to stdout and a file handler.
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


def reset_logging() -> None:
    r"""
    Removes basic config of root logger. (unused in script)
    """
    root = logging.getLogger()
    list(map(root.removeHandler, root.handlers))
    list(map(root.removeFilter, root.filters))
