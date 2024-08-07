from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict

values = ai_knowledge_base_keyword_dict.values()
# {'notice_message': ['院系', '专业'], 't_knowledge_info': ['知识库']}
x = "院校专业字典"
# 遍历字典
for key, value in ai_knowledge_base_keyword_dict.items():
   for v in value:
       if v in x:
           print(key)
           break