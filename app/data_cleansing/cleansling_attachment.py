import concurrent.futures

from app.common.utils.ocr_utlis import urlToText
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_knowledge_info_data, \
    search_notice_message_data
from app.database.mysql.mysql_client import xxlxdb, MySQLConnect

start_id = 0
limit = 1000
batch_size = 100


def knowledge_info():
    while True:
        knowledge_info_dict_list = search_knowledge_info_data(id=start_id, limit=limit)

        if not knowledge_info_dict_list:
            break

        # Accumulate records in batches of 100
        batch = []
        for knowledge_info_dict in knowledge_info_dict_list:
            # Prepare values for insertion
            values = (
                knowledge_info_dict['id'], knowledge_info_dict['type'],
                knowledge_info_dict['country'], knowledge_info_dict['school'],
                knowledge_info_dict['class'], knowledge_info_dict['name'],
                knowledge_info_dict['founder'], knowledge_info_dict['filename'],
                knowledge_info_dict['replyerTime'], knowledge_info_dict['content'],
                knowledge_info_dict['fileurl']
            )
            batch.append(values)

            # When batch size reaches 100, insert into database and reset batch
            if len(batch) >= batch_size:
                placeholders = ", ".join(["%s"] * len(batch[0]))
                insert_query = f"""INSERT INTO weaviate_knowledge_info 
                                (id, type, country, school, class, name, founder, filename, replyerTime, content, fileurl)
                                VALUES ({placeholders})"""
                xxlxdb.mysql_client.executemany(insert_query, batch)
                xxlxdb.mysql_client.connection.commit()
                print(f"Inserted batch of {len(batch)} records.")
                batch.clear()

        # Insert any remaining records in the batch
        if batch:
            placeholders = ", ".join(["%s"] * len(batch[0]))
            insert_query = f"""INSERT INTO weaviate_knowledge_info 
                            (id, type, country, school, class, name, founder, filename, replyerTime, content, fileurl)
                            VALUES ({placeholders})"""
            xxlxdb.mysql_client.executemany(insert_query, batch)
            xxlxdb.mysql_client.connection.commit()
            print(f"Inserted remaining batch of {len(batch)} records.")

        # If fewer than 1000 records were fetched, break the loop
        if len(knowledge_info_dict_list) < limit:
            break

        # Update start_id for the next iteration
        start_id = knowledge_info_dict_list[-1]['id']


def knowledge_info_fjtq():
    def process_record(knowledge_info):
        try:
            xxlxdb1 = MySQLConnect("xxlxdb")
            file_info = urlToText(knowledge_info["attachment_url"])
            update_query = "UPDATE weaviate_knowledge_info SET attachment_content = %s WHERE id = %s"
            xxlxdb1.execute(update_query, (file_info, knowledge_info.get('id')))
            xxlxdb1.close()
        except Exception as e:
            print(f"Failed to process record with id {knowledge_info.get('id')}: {e}")

    def knowledge_info_fjtq():
        global start_id
        global limit

        while True:
            # Fetch records where fileurl is not null and not empty
            select_query = "SELECT * FROM weaviate_knowledge_info WHERE fileurl IS NOT NULL AND fileurl != '' AND attachment_content IS NULL and id > %s"
            knowledge_info_dict_list = xxlxdb.execute_all2dict(select_query, limit=limit, params=(start_id,))

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


def notice_message():
    global start_id
    global limit
    global batch_size
    while True:
        # Fetch records starting from start_id with a limit
        notice_massage_dict_list = search_notice_message_data(id=start_id, limit=limit)

        if not notice_massage_dict_list:
            break

        # Accumulate records in batches of 100
        batch = []
        for knowledge_info_dict in notice_massage_dict_list:
            # Prepare values for insertion
            values = (
                knowledge_info_dict['notice_id'],
                knowledge_info_dict['school_english_name'],
                knowledge_info_dict['school_name'],
                knowledge_info_dict['notice_create_time'],
                knowledge_info_dict['notice_category'],
                knowledge_info_dict['notice_title'],
                knowledge_info_dict['notice_summary'],
                knowledge_info_dict['attachment_name'],
                knowledge_info_dict['attachment_url']
            )
            batch.append(values)

            # When batch size reaches 100, insert into database and reset batch
            if len(batch) >= batch_size:
                placeholders = ", ".join(["%s"] * len(batch[0]))
                insert_query = f"""INSERT INTO weaviate_notice_message 
                                    (notice_id, school_english_name, school_name, notice_create_time, notice_category, notice_title, notice_summary, attachment_name, attachment_url)
                                    VALUES ({placeholders})"""
                xxlxdb.mysql_client.executemany(insert_query, batch)
                xxlxdb.mysql_client.connection.commit()
                print(f"Inserted batch of {len(batch)} records.")
                batch.clear()

        # Insert any remaining records in the batch
        if batch:
            placeholders = ", ".join(["%s"] * len(batch[0]))
            insert_query = f"""INSERT INTO weaviate_notice_message 
                                (notice_id, school_english_name, school_name, notice_create_time, notice_category, notice_title, notice_summary, attachment_name, attachment_url)
                                VALUES ({placeholders})"""
            xxlxdb.mysql_client.executemany(insert_query, batch)
            xxlxdb.mysql_client.connection.commit()
            print(f"Inserted remaining batch of {len(batch)} records.")

        # If fewer than 1000 records were fetched, break the loop
        if len(notice_massage_dict_list) < limit:
            break

        # Update start_id for the next iteration
        start_id = notice_massage_dict_list[-1]['notice_id']


def notice_message_fjtq():
    def process_record(knowledge_info):
        try:
            xxlxdb1 = MySQLConnect("xxlxdb")
            file_info = urlToText(knowledge_info["attachment_url"])
            # Update the record in the database
            update_query = "UPDATE weaviate_notice_message SET attachment_content = %s WHERE notice_id = %s"
            xxlxdb1.execute(update_query, (file_info, knowledge_info.get('notice_id')))
            xxlxdb1.close()
        except Exception as e:
            print(f"Failed to process record with id {knowledge_info.get('notice_id')}: {e}")

    def knowledge_info_fjtq():
        global start_id
        global limit

        while True:
            # Fetch records where fileurl is not null and not empty           weaviate_notice_message:attachment_url      weaviate_knowledge_info
            select_query = "SELECT * FROM weaviate_notice_message WHERE attachment_url IS NOT NULL AND attachment_url != '' AND (attachment_content IS NULL OR   attachment_content != '') and notice_id > %s order by notice_id"

            knowledge_info_dict_list = xxlxdb.execute_all2dict(select_query, limit=limit, params=(start_id,))
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
            start_id = knowledge_info_dict_list[-1]['notice_id']

    knowledge_info_fjtq()


if __name__ == '__main__':
    # knowledge_info()
    # notice_message()
    # knowledge_info_fjtq()
    notice_message_fjtq()
    pass
