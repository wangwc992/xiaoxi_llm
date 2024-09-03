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


def get_link_title(items: list):
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
    # similarity_list = sorted(similarity_list, reverse=True)


    for index, similarity in enumerate(similarity_list):
        print(similarity,sentence_list[index])
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

def get_detokenize(tokens ):
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

async def networked_rag(query: str) -> str:
    response = invoke(query)
    items = response.get('items')
    title_list = get_link_title(items)
    similarity_list = similarity(query, title_list)

    # 根据similarity_list将items里面的link排序
    sorted_items = sorted(zip(similarity_list, items), key=lambda x: x[0], reverse=True)
    # 只取前5个
    networked_links = []

    for i in range(2):
        link = sorted_items[i][1].get('link')
        title = sorted_items[i][1].get('title')
        requests.get(link)
        print(link, title)
        networked_links.append(link)

    text_list = []
    for link in networked_links:
        link_test = get_link_text(link)
        soup = text2soup(link_test)
        text = cleat_text(get_text_from_html(soup))
        text_list.append(text)

    tokenize_request = {
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
        "prompt": ""
    }

    networked_reference_datas = []
    for text in text_list:
        tokenize_request["prompt"] += text
        generator = get_tokens(text)
        # [30709, 99658, 102536, 481, 58230, 237, 99658, 102536, 100133, 33424, 102, 102659, 99257, 33126, 100405, 1654, 2299, 14589, 714, 20908, 13651, 7090, 79032, 3171, 944, 975, 10277, 2041, 12914, 8970, 13, 5209, 7283, 432, 311, 3060, 13]
        tokens = generator.get("tokens")
        count = generator.get("count")
        if count > 400:
            # 将token 这个列表分成多个，300个一组，重叠100个
            token_sublists = [tokens[i:i + 300] for i in range(0, len(tokens) - 200, 200)]
            for token_sublist in token_sublists:
                networked_reference_datas.append(token_sublist)
        else:
            networked_reference_datas.append(tokens)

    networked_reference_prompt = []
    for item in networked_reference_datas:
        detokenize = get_detokenize(item)
        print(detokenize.get("prompt"))
        networked_reference_prompt.append(detokenize.get("prompt"))

    networked_reference_similarity_list = similarity(query, networked_reference_prompt)
    sorted_items = sorted(zip(networked_reference_similarity_list, networked_reference_prompt), key=lambda x: x[0], reverse=True)
    print(sorted_items)


if __name__ == "__main__":
    q = "党的二十届三中全会"
    asyncio.run(networked_rag(q))
