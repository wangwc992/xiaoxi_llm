import asyncio

from app.api.knowledge_base.knowledge_base_weaviate import create_collection, delete_collection, cleansing, \
    search_weaviate_data
from app.data_cleansing.knowledge_base_cleansing import MannerExecution

# asyncio.run(delete_collection())
# asyncio.run(create_collection())

manner_execution = MannerExecution(
    # method_name="t_knowledge_info",
    # method_name="notice_message",
    # method_name="platform_introduction",
    # method_name="zn_school_info",
    # method_name="zn_school_info_rank",
    # method_name="zn_school_info_more",
    # method_name="zn_school_selection_reason",
    # method_name="zn_school_admission_undergraduate",
    # method_name = "zn_school_admission_graduate_student",
    # method_name = "zn_school_admission_art",
    # method_name="zn_school_department_project",
    limit=5,
    start_id=0,
    frequency=1
)
# asyncio.run(cleansing(manner_execution))
asyncio.run(search_weaviate_data(database=manner_execution.method_name))
