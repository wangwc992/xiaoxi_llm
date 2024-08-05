import os

import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, 'data/24年定校数据对比专业库字段-0726-V2.xlsx')
df = pd.read_excel(file_path, engine='openpyxl')
data = df.to_dict(orient='records')
{'id': 1, 'school_name': 'Massachusetts Institute of Technology', 'english_name': 'Master of Finance'}
print(data[0])
import http.client
import json
import threading
import time
import random

start_index = 0


# 定义发送请求的函数
def send_request():
    global start_index
    global data
    global df
    global file_path

    # 随机选择一个问题
    if isinstance(data, list) and isinstance(data[start_index], dict):
        content = data[start_index]['school_name'] + data[start_index]['english_name']
    else:
        raise TypeError("data[start_index] is not a dictionary")
    threas_id = start_index
    start_index += 1
    conn = http.client.HTTPSConnection("u430182-ac52-9e557856.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "你是一个留学院校专业介绍大师,中文回复"
            },
            {
                "role": "user",
                "content": content
            }
        ]
    })
    headers = {
        'Authorization': '1001',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'u430182-ac52-9e557856.cqa1.seetacloud.com',
        'Connection': 'keep-alive'
    }
    try:
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        res_data = res.read()
        result_content = json.loads(res_data.decode('utf-8'))
        output = result_content['choices'][0]['message']['content']
        print(threas_id, '*' * 10, output)
        df.at[threas_id, 'introduce'] = output
        df.to_excel(file_path, engine='openpyxl', index=False)
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()


# 定义定时循环发送请求的函数
def periodic_request():
    while True:
        # 随机生成1到10个线程
        num_requests = 30
        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target=send_request)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 随机等待 5 到 10 秒
        time.sleep(random.randint(5, 10))


# 启动定时请求
periodic_request()
