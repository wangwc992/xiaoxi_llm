import os
import requests

from app.common.utils.logging import get_logger

logger = get_logger(__name__)


def download_file(pdf_url, save_directory):
    """下载远程文件到本地"""
    if pdf_url.startswith("http://") or pdf_url.startswith("https://"):
        response = requests.get(pdf_url)
        response.raise_for_status()

        # 如果目录不存在，则创建目录
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # 获取文件名
        file_name = pdf_url.split('/')[-1]  # Extract the file name from the URL
        file_path = os.path.join(save_directory, file_name)

        # Save the file content
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return file_path
    else:
        file_path = pdf_url
        logger.info(f"File path provided: {file_path}")
        return file_path


# 删除文件
def delete_file(file_path):
    """删除文件"""
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        logger.info(f"File not found: {file_path}")


if __name__ == '__main__':
    file_path = download_file("http://xiaoxi-cdn.globeedu.com/2023/09/04/png/2023090409434244503013.png", "downloads")
    delete_file(file_path)
