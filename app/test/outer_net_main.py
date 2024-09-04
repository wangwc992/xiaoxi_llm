from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# 设置全局变量
__URL = 'https://www.googleapis.com/customsearch/v1'


def invoke(query: str):
    global __URL
    data = {
        "q": query,
        "key": "AIzaSyCyRtRDgM-DWUpDQbF9OcIEnKiTCbZ1M74",
        "cx": "675fae59c36af4e5f",
    }
    response = requests.get(__URL, params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error calling Google Custom Search API")


@app.get("/google/search")
def search(query: str):
    try:
        result = invoke(query)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
