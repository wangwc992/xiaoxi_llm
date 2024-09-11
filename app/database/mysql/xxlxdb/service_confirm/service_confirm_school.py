from app.database.mysql.mysql_client import xxlxdb


def select_service_school(service_master_id: str):
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
    WHERE
        sm.id = '{service_master_id}'
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


def select_member_id_by_company_id(company_id: str):
    sql = f"SELECT wechat_id from user_adviser where company_id = {company_id} and delete_status = 0"
    member_id_dict_list = xxlxdb.execute_all2dict(sql)
    member_id_list = [member_id_dict['wechat_id'] for member_id_dict in member_id_dict_list]
    return member_id_list


def select_student_by_member_id(member_id_list: list, student_name: str):
    # 检查 member_id 是否为列表
    if not isinstance(member_id_list, list):
        raise TypeError("member_id 必须是一个列表")

    # 确保 member_id 列表中的所有元素都是字符串
    member_id = [str(id) for id in member_id_list]

    member_id_str = "','".join(member_id)
    sql = f"SELECT * from service_master where adviser_member_id in ('{member_id_str}') and user_real_name = '{student_name}'"
    student_dict_list = xxlxdb.execute_all2dict(sql)
    return student_dict_list


def select_student_by_name(member_id_list: list,fast_name:str , last_name:str):
    #     SELECT t1.id,t1.user_real_name,t3.first_name,t3.last_nam,t1.adviser_member_id from service_master t1
    # INNER JOIN apply_main t2 on t1.id = t2.service_id
    # INNER JOIN apply_basic_info t3 on t3.main_id = t2.id
    # where t3.first_name = 'huang' and t3.last_nam = 'xinyi' and adviser_member_id in ('107201')
    if not isinstance(member_id_list, list):
        raise TypeError("member_id 必须是一个列表")

    # 确保 member_id 列表中的所有元素都是字符串
    member_id = [str(id) for id in member_id_list]
    member_id_str = "','".join(member_id)

    sql = f"""
    SELECT
        t1.*
    FROM
        service_master t1
        INNER JOIN apply_main t2 ON t1.id = t2.service_id
        INNER JOIN apply_basic_info t3 ON t3.main_id = t2.id
    WHERE
        t3.first_name = '{fast_name}'
        AND t3.last_nam = '{last_name}'
        AND adviser_member_id IN ( '{member_id_str}' )
    """
    student_dict_list = xxlxdb.execute_all2dict(sql)
    return student_dict_list




if __name__ == '__main__':
    # SELECT * from service_master
    # where adviser_member_id in (11001692) and user_real_name = "玄天姬"
    print(select_student_by_member_id(['11002435'], 'Jessie Cheng'))
    # SELECT wechat_id from user_adviser where company_id = 853 and delete_status = 0
    # print(select_member_id_by_company_id('853'))
    # print(select_student_by_name(['107201'], 'huang', 'xinyi'))
    # for i in select_service_school('XT1028961'):
    #     print(i)