from weaviate.collections.classes.filters import Filter

from app.database.mysql.xxlxdb.ai_knowledge_base import ai_knowledge_base_keyword_dict
from app.database.weaviate.knowledge_base import knowledge_base_weaviate
import asyncio

async def load_reference_data(query, limit):
    # 匹配关键字使用特定知识库
    filters = None
    for key, values in ai_knowledge_base_keyword_dict.items():
        if any(v in query for v in values):
            filters = Filter.by_property("database").equal(key)
            break

    response_list = await knowledge_base_weaviate.search_hybrid(query, limit, filters)
    reference_data = "\n\n".join([
        f"{response_list[n].instruction}: {response_list[n].output}"
        for n in range(len(response_list))])
    knowledge_link = [eval(response.link) for response in response_list if
                      response.database == "t_knowledge_info" and response.link]

    return {"reference_data": reference_data,
            "knowledge_link": knowledge_link,
            }

asyncio.run(load_reference_data("test",  10))
