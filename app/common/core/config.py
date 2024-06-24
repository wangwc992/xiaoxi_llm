import os
from dotenv import load_dotenv
import yaml

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

settings = load_config()
