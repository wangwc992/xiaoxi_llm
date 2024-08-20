import os

# 获取当前脚本的绝对路径
current_file_path = os.path.abspath(__file__)
print("当前脚本的绝对路径:", current_file_path)


# 获取当前脚本所在目录的绝对路径
current_dir_path = os.path.dirname(os.path.abspath(__file__))
print("当前脚本所在目录的绝对路径:", current_dir_path)


# 获取当前工作目录的绝对路径
current_working_directory = os.getcwd()
print("当前工作目录的绝对路径:", current_working_directory)


# 获取项目根目录的绝对路径（假设项目结构为：项目根目录/子目录/脚本文件.py）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("项目根目录的绝对路径:", project_root)

from pathlib import Path

# 获取当前脚本的绝对路径
current_file_path = Path(__file__).resolve()
print("当前脚本的绝对路径:", current_file_path)

# 获取当前脚本所在目录的绝对路径
current_dir_path = current_file_path.parent
print("当前脚本所在目录的绝对路径:", current_dir_path)

# 获取当前工作目录的绝对路径
current_working_directory = Path.cwd()
print("当前工作目录的绝对路径:", current_working_directory)
