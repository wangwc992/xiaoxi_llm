import http.client
import json
import threading
import time
import random

# 留学相关问题列表
study_abroad_questions = [
    "我应该选择哪个国家作为留学目的地，如何比较不同国家的留学优势？",
    "如何选择适合我的专业和背景的院校？",
    "申请海外院校时，通常需要准备哪些材料？",
    "推荐信应该找谁写？内容如何把握？",
    "留学的总费用大概是多少，包括学费和生活费？",
    "我是否可以申请奖学金或助学金？申请条件是什么？",
    "IELTS和TOEFL之间有何区别？我应该选择哪个？",
    "如何有效备考语言考试以达到申请要求？",
    "留学签证的申请流程是什么？需要哪些材料？",
    "在签证面试中，我应该注意哪些问题？",
    "我如何选择适合我职业发展的专业或课程？",
    "不同专业的就业前景如何？",
    "在国外留学期间，选择校内宿舍还是校外住宿更好？",
    "生活费预算应该如何规划？",
    "如何适应国外的文化差异？有哪些常见的文化冲突需要注意？",
    "我应该如何在留学期间建立和维护社交圈？",
    "留学后回国和留在国外就业各有哪些优劣势？",
    "我如何利用留学经历提升自己的职业竞争力？",
    "当前全球疫情对留学计划有何影响？有哪些应对措施？",
    "如果疫情期间无法入境，我可以选择哪些在线课程或远程学习方案？"
]


# 定义发送请求的函数
def send_request():
    # 随机选择一个问题
    random_question = random.choice(study_abroad_questions)

    conn = http.client.HTTPSConnection("u430182-ac52-13068849.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
        "messages": [
            {
                "role": "system",
                "content": "小希留学助手"
            },
            {
                "role": "user",
                "content": random_question
            }
        ]
    })
    headers = {
        'Authorization': '1003',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'u430182-ac52-13068849.cqa1.seetacloud.com',
        'Connection': 'keep-alive'
    }
    try:
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()


# 定义定时循环发送请求的函数
def periodic_request():
    while True:
        # 随机生成1到10个线程
        num_requests = random.randint(1, 10)
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
