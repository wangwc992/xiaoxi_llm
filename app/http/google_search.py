import requests


def google_search(query: str) -> dict:
    try:
        # 在 URI 前添加 'http://'
        uri = f'http://fcgvfm.natappfree.cc/google/search?query={query}'
        response = requests.get(uri)
        json_data = response.json()
        return json_data
    except Exception as e:
        print(f"Error: {e}")
        return {}


if __name__ == '__main__':
    print(google_search("python"))
