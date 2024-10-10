from app.database.mysql.mysql_client import xxlxdb


def get_major_category_list():
    sql = "SELECT id,category_english_name,zh_category_name FROM zn_school_major_category WHERE category_level = 2 and deleted = 0"
    major_category_list = xxlxdb.execute_all2dict(sql)
    return major_category_list


if __name__ == "__main__":
    major_category_list = get_major_category_list()
    print(major_category_list)
