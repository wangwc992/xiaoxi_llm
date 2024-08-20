import os
from dotenv import load_dotenv
import yaml
import subprocess

# Load environment variables from .env file
load_dotenv()


def load_config():
    app_env = os.getenv('APP_ENV', 'dev')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, '..', '..', '..', 'configs', f'config.{app_env}.yaml')
    print(f"Loading configuration from {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


# 加载配置
settings = load_config()


def get_gpu_count():
    result = subprocess.run(['nvidia-smi', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        # 按行分割输出并计算行数，行数即为 GPU 的数量
        gpu_lines = result.stdout.strip().split('\n')
        return len(gpu_lines)
    else:
        print(f"Error executing nvidia-smi: {result.stderr}")
        return 0


# 获取 GPU 数量l
settings['gpu_count'] = get_gpu_count()

# 项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
settings['project_root'] = project_root
