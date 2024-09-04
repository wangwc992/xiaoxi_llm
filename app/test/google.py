import asyncio
import re
import http.client
import json
from bs4 import BeautifulSoup

import requests
from sentence_transformers.util import cos_sim

from app.common.core.langchain_client import Embedding

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


# def cos_sim(a, b):
#     '''余弦距离 -- 越大越相似'''
#     return dot(a, b) / (norm(a) * norm(b))


def similarity(query: str, sentence_list: list):
    query_vec = Embedding.embed_query(query)
    doc_vecs = Embedding.embed_documents(sentence_list)
    similarity = cos_sim(query_vec, doc_vecs)
    similarity_list = similarity.tolist()[0]
    for index, item in enumerate(similarity_list):
        print(item, sentence_list[index])
    return similarity_list


def get_link_text(link: str):
    response = requests.get(link)

    # 自动检测编码
    response.encoding = response.apparent_encoding

    # 如果知道具体的编码，可以手动指定，比如 'utf-8'
    # response.encoding = 'utf-8'

    text = response.text
    return text


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


def get_tokens(prompt):
    conn = http.client.HTTPSConnection("u430182-ac52-13068849.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
        "prompt": prompt
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/tokenize", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    json_data = json.loads(data)
    return json_data


def get_detokenize(tokens):
    conn = http.client.HTTPSConnection("u430182-ac52-13068849.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
        "tokens": tokens
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/detokenize", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    json_data = json.loads(data)
    return json_data


async def reference_networked_rag(query: str):
    response = invoke(query)
    items = response.get('items')
    title_list = get_link_title(items)
    similarity_list = similarity(query, title_list)

    # Sort items by similarity and take top 2 links
    sorted_items = sorted(zip(similarity_list, items), key=lambda x: x[0], reverse=True)[:2]

    for item in sorted_items:
        print(item[1].get("link"), item[1].get("title"))

    networked_links = [item[1].get('link') for item in sorted_items]

    text_list = [cleat_text(get_text_from_html(text2soup(get_link_text(link)))) for link in networked_links]

    networked_reference_datas = []
    for text in text_list:
        generator = get_tokens(text)
        tokens = generator.get("tokens")
        count = generator.get("count")
        if count > 400:
            token_sublists = [tokens[i:i + 300] for i in range(0, len(tokens) - 200, 200)]
            networked_reference_datas.extend(token_sublists)
        else:
            networked_reference_datas.append(tokens)

    networked_reference_prompt = [get_detokenize(item).get("prompt") for item in networked_reference_datas]

    networked_reference_similarity_list = similarity(query, networked_reference_prompt)
    sorted_items = sorted(zip(networked_reference_similarity_list, networked_reference_prompt), key=lambda x: x[0], reverse=True)
    reference_networked_data = "\n\n".join([f"{index + 1}. {item[1]}" for index, item in enumerate(sorted_items)])
    print(reference_networked_data)
    return sorted_items


if __name__ == "__main__":
    q = "党的二十届三中全会"
    print(q)
    asyncio.run(reference_networked_rag(q))


