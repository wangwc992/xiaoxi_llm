import os
import http.client
import json
import threading
import time
import random
import pandas as pd

# Define the file path
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, 'data/24年定校数据对比专业库字段-0726-V2.xlsx')

# Read the Excel file
df = pd.read_excel(file_path, engine='openpyxl')
data = df.to_dict(orient='records')

# Initialize the starting index and a lock for thread safety
start_index = 3360
index_lock = threading.Lock()

# Store the outputs to avoid simultaneous writes to the Excel file
output_data = []

# Function to send a request
def send_request():
    global start_index
    global data
    global output_data

    # Safely update and access the start_index
    with index_lock:
        if start_index >= len(data):
            return  # Stop if we reach the end of the data
        current_index = start_index
        start_index += 1

    # Prepare the content for the request
    if isinstance(data, list) and isinstance(data[start_index], dict):
        content = data[start_index]['school_name'] + data[start_index]['english_name']
    else:
        raise TypeError("data[start_index] is not a dictionary")
    thread_id = current_index

    conn = http.client.HTTPSConnection("u430182-ac52-9e557856.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct",
        "messages": [
            {
                "role": "system",
                "content": "你是一个留学院校专业介绍大师，能够详细介绍提供的院校和专业，不要使用院校名字和专业名称开头,使用中文回复"
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
        print(thread_id, '*' * 10, output)

        # Store the result in the output_data list
        output_data.append((thread_id, output))

    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()

# Function to send periodic requests
def periodic_request():
    while True:
        # Randomly create 1 to 10 threads
        num_requests = 30
        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target=send_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Write accumulated results to the Excel file
        if output_data:
            with index_lock:  # Ensure thread safety while writing to the file
                for thread_id, output in output_data:
                    df.at[thread_id, 'introduce'] = output
                df.to_excel(file_path, engine='openpyxl', index=False)
                output_data.clear()  # Clear the output data after writing

        # Randomly wait 5 to 10 seconds
        time.sleep(random.randint(5, 10))

# Start the periodic requests
periodic_request()
