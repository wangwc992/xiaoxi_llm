# 加载小希平台介绍数据的xlsx文件
import pandas as pd

file_path = 'C:\\Users\\wishfyc\\PycharmProjects\\xiaoxi_llm\\app\\data_cleansing\\data\\platform_introduction.xlsx'
df = pd.read_excel(file_path)

# Extract the necessary information
data = df.to_dict(orient='records')
knowledge_base_model = [{
    "database": "datasets",
    "db_id": i,
    "instruction": info.get('instruction'),
    "input": "",
    "output": info.get('output'),
    "keyword": "",
    "file_info": "",
} for i, info in enumerate(data)]

print(knowledge_base_model)