from app.database.mysql.mysql_client import xxlxdb


def select_service_school(student_name: str):
    sql = f"""
    SELECT
        scs.id,
        scs.school_chinese_name,
        scs.school_english_name,
        scs.project_chinese_name,
        scs.project_english_name,
        scs.create_time
    FROM
        service_confirm_school scs
        INNER JOIN service_master sm ON sm.id = scs.service_id 
        AND scs.is_asny = 1 
    WHERE
        sm.user_real_name = '{student_name}'
	"""
    service_school_dict_list = xxlxdb.execute_all2dict(sql)
    return service_school_dict_list


def select_service_history(service_school_id_list: list):
    # SELECT confirm_schl_id,status_name,create_time FROM `service_history` where confirm_schl_id in ('XT1020156-1', 'XT1020156-3', 'XT1020156-4')
    # ORDER BY confirm_schl_id,status
    service_school_id_str = "','".join(service_school_id_list)
    sql = f"""
    SELECT
        confirm_schl_id,
        status_name,
        create_time 
    FROM
        `service_history` 
    WHERE
        confirm_schl_id IN ( '{service_school_id_str}' ) 
    ORDER BY
        confirm_schl_id,
        `status`
    """

    service_history_dict_list = xxlxdb.execute_all2dict(sql)
    return service_history_dict_list
