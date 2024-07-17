import MySQLdb
from app.common.core.config import settings


class MySQLConnect:
    mysql_dict = settings["mysql"]
    conn = MySQLdb.connect(
        host=mysql_dict["host"],
        user=mysql_dict["user"],
        passwd=mysql_dict["passwd"],
        database=mysql_dict["database"],
        port=mysql_dict["port"],

    )
