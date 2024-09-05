import requests

from app.common.core.config import settings


def google_search(query: str) -> dict:
    try:
        # 在 URI 前添加 'http://'
        uri = f'{settings.get("google_search")}{query}'
        response = requests.get(uri)
        json_data = response.json()
        return json_data
    except Exception as e:
        print(f"Error: {e}")
        return {}


if __name__ == '__main__':
    print(google_search("python"))
