import os
import pandas as pd
import json
import http.client
import threading
import time
import random
from openpyxl import load_workbook

# Define the file path
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, 'data/zy.xlsx')

# Read the Excel file
df = pd.read_excel(file_path)

# Convert the DataFrame to a list of dictionaries
data = df.to_dict(orient='records')

def send_request(question):
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
                "content": question
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
        return data.decode("utf-8")
    except Exception as e:
        print(f"Request failed: {e}")
        return None
    finally:
        conn.close()


def periodic_request():
    while True:
        # Randomly generate 30 parallel requests
        num_requests = 30
        threads = []
        results = []

        for _ in range(num_requests):
            # Randomly select a question
            random_question = random.choice(data)['chinese_name']

            # Define the thread
            thread = threading.Thread(target=lambda q=random_question: results.append(send_request(q)))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Write results back to the Excel file
        if results:
            write_results_to_excel(results)

        # Random wait between 5 to 10 seconds before sending new requests
        time.sleep(random.randint(5, 10))

def write_results_to_excel(results):
    # Load the existing Excel file
    book = load_workbook(file_path)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    writer.book = book

    # Convert results to DataFrame
    results_df = pd.DataFrame({'Response': results})

    # Write the DataFrame to the Excel file, starting at the first empty row
    startrow = book['Sheet1'].max_row
    results_df.to_excel(writer, startrow=startrow, index=False, header=False)

    # Save the Excel file
    writer.save()
    writer.close()

# Start sending requests
periodic_request()
