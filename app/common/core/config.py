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

# 项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
settings['project_root'] = project_root
