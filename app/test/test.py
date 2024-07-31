import requests

url = "http://59.108.41.117:5001/urlToText"
headers = {
    "Content-Type": "application/json"
}
data = {
    "url": "http://xiaoxi-cdn.globeedu.com/2023/03/20/pdf/2023032019262545103013.pdf"
}

response = requests.post(url, headers=headers, json=data)

# 打印返回的状态码和响应内容
print("Status Code:", response.status_code)
print("Response Text:", response.text)
