class ObjectFormatter:
    @staticmethod
    def format_object(obj):
        """
      将对象的所有属性值取出，用 "——" 拼接成字符串。

      :param obj: 需要格式化的对象
      :return: 拼接好的字符串
      """
        # 获取对象所有的属性名和值
        attributes = [getattr(obj, attr) for attr in dir(obj) if
                      not callable(getattr(obj, attr)) and not attr.startswith("__")]

        # 过滤掉 None 值
        attributes = [str(attr) for attr in attributes if attr is not None]

        # 使用 "——" 拼接
        return "——".join(attributes)

    @staticmethod
    def format_objects(objects):
        """
      格式化一个对象列表的信息。

      :param objects: 对象列表
      :return: 每个对象拼接好的字符串列表
      """
        return [ObjectFormatter.format_object(obj) for obj in objects]


# 示例 CheckSchool 类
class CheckSchool:
    def __init__(self, country_name, school_name, major_name, gpa_req, degree_type):
        self.country_name = country_name
        self.school_name = school_name
        self.major_name = major_name
        self.gpa_req = gpa_req
        self.degree_type = degree_type


# 示例使用：
schools = [
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='口腔健康学士/Bachelor of Oral Health', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='心理学学士/Bachelor of Psychology', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='高级研究学士（荣誉）/Bachelor of Advanced Studies (Honours)', gpa_req=None,
                degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='音乐学士/Bachelor of Music', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='文学学士（荣誉）/Bachelor of Arts (Honours)', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='项目管理学士/Bachelor of Project Management', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='视觉艺术学士/Bachelor of Visual Arts', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='项目管理学士（荣誉）/Bachelor of Project Management (Honours)', gpa_req=None,
                degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='经济学学士（荣誉）/Bachelor of Economics (Honours)', gpa_req=None, degree_type='本科'),
    CheckSchool(country_name='澳大利亚', school_name='悉尼大学/The University of Sydney',
                major_name='设计计算学士（2022年入学）/Bachelor of Design Computing (2022 entry)', gpa_req=None,
                degree_type='本科')
]

# 使用工具类格式化对象
formatted_schools = ObjectFormatter.format_objects(schools)

# 打印结果
for formatted_school in formatted_schools:
    print(formatted_school)
