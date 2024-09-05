import requests

from app.common.core.config import settings


async def google_search(query: str) -> dict:
    try:
        # 在 URI 前添加 'http://'
        uri = f'{settings.get("google_search")}{query}'
        response = requests.get(uri, timeout=2)
        json_data = response.json()
        return json_data
    except Exception as e:
        print(f"Error: {e}")
        return {}

async def google_search_text(url: str) -> str:
    try:
        url = f'{settings.get("search_text")}{url}'
        response = requests.get(url, timeout=2)
        # 自动检测编码
        response.encoding = response.apparent_encoding
        # 如果知道具体的编码，可以手动指定，比如 'utf-8'
        response.encoding = 'utf-8'
        text = response.text
    except:
        text = ""
    return text

if __name__ == '__main__':
    print(google_search("python"))
