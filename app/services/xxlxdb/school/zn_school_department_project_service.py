from app.common.database.mysql.xxlxdb.school.zn_school_department_project_mapper import select_by_check_school, \
    CheckSchool


def get_school_Project_data(check_school: CheckSchool):
    zn_school_department_project_dict = select_by_check_school(check_school)
    return zn_school_department_project_dict
