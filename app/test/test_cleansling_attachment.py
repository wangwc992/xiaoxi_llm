import concurrent.futures
from functools import partial
from app.common.utils.ocr_utlis import urlToText
from app.database.mysql.mysql_client import MySQLConnect, yhj

start_id = 0
limit = 1000
batch_size = 30


def process_record(knowledge_info):
    try:
        yhj1 = MySQLConnect("yhj")
        file_info = urlToText(knowledge_info["attachment_url"])
        # Update the record in the database
        update_query = "UPDATE weaviate_notice_message SET attachment_content = %s WHERE notice_id = %s"
        yhj1.execute(update_query, (file_info, knowledge_info.get('notice_id')))
        yhj1.close()
    except Exception as e:
        print(f"Failed to process record with id {knowledge_info.get('notice_id')}: {e}")


def knowledge_info_fjtq():
    global start_id
    global limit

    while True:
        # Fetch records where fileurl is not null and not empty           weaviate_notice_message:attachment_url      weaviate_knowledge_info
        select_query = "SELECT * FROM weaviate_notice_message WHERE attachment_url IS NOT NULL AND attachment_url != '' AND (attachment_content IS NULL OR   attachment_content != '') and notice_id > %s order by notice_id"

        knowledge_info_dict_list = yhj.execute_all2dict(select_query, limit=limit, params=(start_id,))
        # 排除notice_id重复的数据
        knowledge_info_dict_list = [dict(t) for t in set([tuple(d.items()) for d in knowledge_info_dict_list])]

        if not knowledge_info_dict_list:
            break

        # Use ThreadPoolExecutor to process 30 records concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(process_record, knowledge_info_dict_list)

        if len(knowledge_info_dict_list) < limit:
            break

        # Update start_id for the next iteration
        start_id = knowledge_info_dict_list[-1]['id']


knowledge_info_fjtq()