import requests

__URL = 'https://www.googleapis.com/customsearch/v1'

def invoke(query: str):
    global __URL
    data = {
        "q": query,
        "key": "AIzaSyCyRtRDgM-DWUpDQbF9OcIEnKiTCbZ1M74",
        "cx": "675fae59c36af4e5f",
    }
    response = requests.get(__URL, params=data)
    return response.json()

def get_link_title(items: list) -> list:
    title_list = []
    for item in items:
        title = item.get('title') + item.get('snippet')
        title_list.append(title)
        print(item.get("link"), title)
    return title_list

def get_link_text(link: str):
    response = requests.get(link)

    # 自动检测编码
    response.encoding = response.apparent_encoding

    # 如果知道具体的编码，可以手动指定，比如 'utf-8'
    # response.encoding = 'utf-8'

    text = response.text
    return text