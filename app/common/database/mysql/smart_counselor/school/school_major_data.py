'''CREATE TABLE `school_major_data` (
  `school_name` varchar(100) DEFAULT NULL COMMENT '学校名称',
  `major_name` varchar(100) DEFAULT NULL COMMENT '专业名称',
  `dgree_name` varchar(100) DEFAULT NULL COMMENT '学位名称',
  `country` varchar(50) DEFAULT NULL COMMENT '国家',
  `gpa_type` varchar(20) DEFAULT NULL COMMENT 'GPA类型',
  `gpa_require` varchar(30) DEFAULT NULL COMMENT 'GPA要求',
  `score_type_1` varchar(50) DEFAULT NULL COMMENT '提交成绩-托福',
  `score_1` varchar(30) DEFAULT NULL COMMENT '成绩分数',
  `score_type_2` varchar(30) DEFAULT NULL COMMENT '提交成绩-sat',
  `score_2` varchar(50) DEFAULT NULL COMMENT '成绩分数',
  `school_system_type` varchar(20) DEFAULT NULL COMMENT '学制类型 如：年，月',
  `school_system` varchar(20) DEFAULT NULL COMMENT '学制',
  `school_fee` varchar(50) DEFAULT NULL COMMENT '学费',
  `fee_type` varchar(50) DEFAULT NULL COMMENT '货币如：美元/年',
  `province` varchar(200) DEFAULT NULL COMMENT '所在州/省中文全称',
  `province_eng` varchar(100) DEFAULT NULL COMMENT '所在州/省英文文全称',
  `city` varchar(100) DEFAULT NULL COMMENT '所在城市中文',
  `city_eng` varchar(100) DEFAULT NULL COMMENT '所在城市英文',
  `school_area_name` varchar(200) DEFAULT NULL COMMENT '校区名称',
  `school_depart` varchar(200) DEFAULT NULL COMMENT '院系设置',
  `international_ratio` varchar(100) DEFAULT NULL COMMENT '国际学生比例',
  `teacher_student_ratio` varchar(100) DEFAULT NULL COMMENT '师生比例',
  `men_women_ratio` varchar(100) DEFAULT NULL COMMENT '男女比例',
  `total_student` varchar(100) DEFAULT NULL COMMENT '学生总数量',
  `Undergraduate_total` varchar(100) DEFAULT NULL COMMENT '本科生数量',
  `graduate_total` varchar(100) DEFAULT NULL COMMENT '研究生数量',
  `work_ratio` varchar(100) DEFAULT NULL COMMENT '就业率',
  `selary` varchar(100) DEFAULT NULL COMMENT '毕业薪资',
  `school_type` varchar(20) DEFAULT NULL COMMENT '院校类型（中学）',
  `religion` varchar(100) DEFAULT NULL COMMENT '宗教背景（中学）',
  `lodging` varchar(100) DEFAULT NULL COMMENT '寄宿方式（中学）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;'''

from datetime import datetime

from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field

from app.common.database.mysql.mysql_client import smart_counselor


# 创建实体类

class SchoolMajorData(BaseModel):
    '''数据实体'''
    school_name: Optional[str] = Field(description="学校名称")
    major_name: Optional[str] = Field(description="专业名称")
    dgree_name: Optional[str] = Field(description="学位名称")
    country: Optional[str] = Field(description="国家")
    gpa_type: Optional[str] = Field(description="GPA类型")
    gpa_require: Optional[str] = Field(description="GPA要求")
    score_type_1: Optional[str] = Field(description="提交成绩-托福")
    score_1: Optional[str] = Field(description="成绩分数")
    score_type_2: Optional[str] = Field(description="提交成绩-sat")
    score_2: Optional[str] = Field(description="成绩分数")
    school_system_type: Optional[str] = Field(description="学制类型 如：年，月")
    school_system: Optional[str] = Field(description="学制")
    school_fee: Optional[str] = Field(description="学费")
    fee_type: Optional[str] = Field(description="货币如：美元/年")
    province: Optional[str] = Field(description="所在州/省中文全称")
    province_eng: Optional[str] = Field(description="所在州/省英文文全称")
    city: Optional[str] = Field(description="所在城市中文")
    city_eng: Optional[str] = Field(description="所在城市英文")
    school_area_name: Optional[str] = Field(description="校区名称")
    school_depart: Optional[str] = Field(description="院系设置")
    international_ratio: Optional[str] = Field(description="国际学生比例")
    teacher_student_ratio: Optional[str] = Field(description="师生比例")
    men_women_ratio: Optional[str] = Field(description="男女比例")
    total_student: Optional[str] = Field(description="学生总数量")
    Undergraduate_total: Optional[str] = Field(description="本科生数量")
    graduate_total: Optional[str] = Field(description="研究生数量")
    work_ratio: Optional[str] = Field(description="就业率")
    selary: Optional[str] = Field(description="毕业薪资")
    school_type: Optional[str] = Field(description="院校类型（中学）")
    religion: Optional[str] = Field(description="宗教背景（中学）")
    lodging: Optional[str] = Field(description="寄宿方式（中学）")


# 用于function calling回调实体
class ChatSchoolMajorData(BaseModel):
    school_name: Optional[str] = Field(description="学校名称")
    major_name: Optional[str] = Field(description="专业名称")
    dgree_name: Optional[str] = Field(description="学位名称")
    country: Optional[str] = Field(description="国家")
    gpa_require: Optional[str] = Field(description="GPA要求")
    school_fee: Optional[str] = Field(description="学费")
    #    背景学历，背景国家，背景毕业院校，用于案例库查询
    background_degree: Optional[str] = Field(description="背景学历")
    background_country: Optional[str] = Field(description="背景国家")
    background_school: Optional[str] = Field(description="背景毕业院校")


def search_school_major(chatSchoolMajorData: ChatSchoolMajorData):
    '''查询学校专业数据'''
    # 查询条件
    condition = []
    if chatSchoolMajorData.school_name:
        condition.append(f"school_name = '{chatSchoolMajorData.school_name}'")
    if chatSchoolMajorData.major_name:
        condition.append(f"major_name = '{chatSchoolMajorData.major_name}'")
    if chatSchoolMajorData.dgree_name:
        condition.append(f"dgree_name = '{chatSchoolMajorData.dgree_name}'")
    if chatSchoolMajorData.country:
        condition.append(f"country = '{chatSchoolMajorData.country}'")
    if chatSchoolMajorData.gpa_require:
        condition.append(f"gpa_require = '{chatSchoolMajorData.gpa_require}'")
    if chatSchoolMajorData.school_fee:
        condition.append(f"school_fee = '{chatSchoolMajorData.school_fee}'")
    # 拼接查询条件
    where = " and ".join(condition)
    # 查询sql
    sql = f"select school_name,major_name,dgree_name,country,gpa_require,school_fee from school_major_data where {where}"
    # 查询
    result = smart_counselor.execute_all2dict(sql)
    return result
