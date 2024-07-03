from app.common.database.mysql.smart_counselor.school.school_major_data import ChatSchoolMajorData, search_school_major


def get_school_major_prompt(chatSchoolMajorData: ChatSchoolMajorData):
    '''查询学校专业数据'''
    school_major_list_dict = search_school_major(chatSchoolMajorData)


if __name__ == '__main__':
    chatSchoolMajorData = ChatSchoolMajorData(school_name="The University of Sydney")
    result = get_school_major_prompt(chatSchoolMajorData)
    print(result)
