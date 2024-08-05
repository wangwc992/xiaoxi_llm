import concurrent.futures

from app.common.utils.FileToText import FileToText
from app.database.mysql.mysql_client import yhj

# Global variables
start_id = 3503
limit = 1000


def process_record(knowledge_info):
    try:
        file_info = FileToText.urlToText(knowledge_info.get('fileurl'))
        knowledge_info['attachment_content'] = file_info
        # Update the record in the database
        update_query = "UPDATE weaviate_knowledge_info SET attachment_content = %s WHERE id = %s"
        yhj.execute(update_query, (file_info, knowledge_info.get('id')))
        print(f"Updated record with id {knowledge_info.get('id')}.")
    except Exception as e:
        print(f"Failed to process record with id {knowledge_info.get('id')}: {e}")


def knowledge_info_fjtq():
    global start_id
    global limit

    while True:
        # Fetch records where fileurl is not null and not empty
        select_query = "SELECT * FROM weaviate_knowledge_info WHERE fileurl IS NOT NULL AND fileurl != '' AND id > %s"
        knowledge_info_dict_list = yhj.execute_all2dict(select_query, limit=limit, params=(start_id,))

        if not knowledge_info_dict_list:
            break

        # Use ThreadPoolExecutor to process 30 records concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(process_record, knowledge_info_dict_list)

        if len(knowledge_info_dict_list) < limit:
            break

        # Update start_id for the next iteration
        start_id = knowledge_info_dict_list[-1]['id']


# Call the function to start processing
knowledge_info_fjtq()
