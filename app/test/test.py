import re

import requests
from bs4 import BeautifulSoup


def text2soup(text: str) -> BeautifulSoup:
    # 使用BeautifulSoup解析HTML文本
    soup = BeautifulSoup(text, 'html.parser')
    return soup


def get_text_from_html(soup: BeautifulSoup) -> str:
    # 从HTML文本中提取纯文本
    text = soup.get_text()
    return text


def cleat_text(text):  # 定义清理文本的方法
    text = text.strip().replace("\n\n", "").replace(" ", " ")
    # 多空格变成一个空格
    text = re.sub(r"\s+", " ", text)
    return text
def get_link_text(link: str):
    response = requests.get(link)

    # 自动检测编码
    response.encoding = response.apparent_encoding

    # 如果知道具体的编码，可以手动指定，比如 'utf-8'
    # response.encoding = 'utf-8'

    text = response.text
    return text

text = get_link_text("https://www.12371.cn/special/20jszqh/")
soup = text2soup(text)
text = get_text_from_html(soup)
text = cleat_text(text)
print(text)