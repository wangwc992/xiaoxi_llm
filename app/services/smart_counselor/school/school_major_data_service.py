from app.common.database.mysql.smart_counselor.school.school_major_data import ChatSchoolMajorData, search_school_major
from app.common.utils.object_utils import ObjectFormatter
from app.prompt.prompt_load import generate_prompt


def get_school_major_prompt(chatSchoolMajorData: ChatSchoolMajorData):
    '''查询学校专业数据'''
    school_major_list_dict = search_school_major(chatSchoolMajorData)
    school_major_list_format = ObjectFormatter.format_dicts(school_major_list_dict)
    template = generate_prompt("search_school.txt")
    prompt = template.format(query=chatSchoolMajorData, reference_data=school_major_list_dict)
    return prompt

if __name__ == '__main__':
    chatSchoolMajorData = ChatSchoolMajorData(school_name="The University of Sydney")
    result = get_school_major_prompt(chatSchoolMajorData)
    print(result)
