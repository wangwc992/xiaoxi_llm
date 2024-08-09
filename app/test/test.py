import concurrent.futures

from app.common.utils.ocr_utlis import urlToText
from app.database.mysql.mysql_client import MySQLConnect, yhj

start_id = 0
limit = 1000
batch_size = 100

def process_record(knowledge_info):
    try:
        yhj1 = MySQLConnect("yhj")
        file_info = urlToText(knowledge_info["fileurl"])
        knowledge_info['attachment_content'] = file_info
        # Update the record in the database
        update_query = "UPDATE weaviate_knowledge_info SET attachment_content = %s WHERE id = %s"
        yhj1.execute(update_query, (file_info, knowledge_info.get('id')))
        print(f"Updated record with id {knowledge_info.get('id')}.")
        yhj1.close()
    except Exception as e:
        print(f"Failed to process record with id {knowledge_info.get('id')}: {e}")


def knowledge_info_fjtq():
    global start_id
    global limit
    global batch_size

    while True:
        # Fetch records where fileurl is not null and not empty
        select_query = "SELECT * FROM weaviate_knowledge_info WHERE fileurl IS NOT NULL AND fileurl != '' AND attachment_content IS NULL  and id > %s"
        knowledge_info_dict_list = yhj.execute_all2dict(select_query, limit=limit, params=(start_id,))

        if not knowledge_info_dict_list:
            break

        # Use ThreadPoolExecutor to process 30 records concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            executor.map(process_record, knowledge_info_dict_list)

        if len(knowledge_info_dict_list) < limit:
            break

        # Update start_id for the next iteration
        start_id = knowledge_info_dict_list[-1]['id']


knowledge_info_fjtq()
