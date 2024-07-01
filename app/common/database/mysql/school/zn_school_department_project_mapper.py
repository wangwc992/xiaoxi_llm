'''CREATE TABLE `zn_school_department_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `school_id` int(11) NOT NULL COMMENT '院校表ID',
  `campus_id` varchar(255) DEFAULT NULL COMMENT '校区id 已废 见中间表 zn_school_project_campus',
  `campus_name` varchar(255) DEFAULT NULL COMMENT '校区名称',
  `depart_id` int(11) NOT NULL COMMENT '院系表ID',
  `depart_name` varchar(255) DEFAULT NULL COMMENT '院系名称',
  `course_code` varchar(100) DEFAULT NULL COMMENT '课程编码',
  `chinese_name` varchar(200) DEFAULT NULL COMMENT '项目中文名',
  `english_name` varchar(600) DEFAULT NULL COMMENT '项目英文名',
  `introduction` text COMMENT '项目介绍',
  `degree_level` varchar(50) DEFAULT NULL COMMENT '学位等级',
  `degree_name` varchar(100) DEFAULT NULL COMMENT '学位名称',
  `degree_type` varchar(50) DEFAULT NULL COMMENT '学位类型',
  `length_of_full` text COMMENT '全日制学制',
  `length_of_schoolings` varchar(255) DEFAULT '' COMMENT '时间-年月日，学制时间',
  `length_of_part` text COMMENT '非全日制学制',
  `semester` varchar(200) DEFAULT NULL COMMENT '开学时间',
  `time_apply_deadline` text COMMENT '申请截止时间',
  `time_offer` varchar(200) DEFAULT NULL COMMENT 'Offer发放时间',
  `time_offer_deadline` varchar(200) DEFAULT NULL COMMENT 'Offer发放截止时间',
  `science_requirement` longtext COMMENT '学术要求',
  `major_link` varchar(1000) DEFAULT NULL COMMENT '专业链接',
  `fee_apply` varchar(200) DEFAULT NULL COMMENT '申请费用',
  `fee_tuition` varchar(200) DEFAULT NULL COMMENT '学费',
  `fee_book` varchar(200) DEFAULT NULL COMMENT '书本费',
  `fee_life` varchar(200) DEFAULT NULL COMMENT '生活费',
  `fee_traffic` varchar(200) DEFAULT NULL COMMENT '交通费',
  `fee_accommodation` varchar(200) DEFAULT NULL COMMENT '住宿费用',
  `fee_others` varchar(200) DEFAULT NULL COMMENT '其他费用',
  `fee_total` varchar(200) DEFAULT NULL COMMENT '总花费',
  `score_gpa` varchar(200) DEFAULT NULL COMMENT 'GPA成绩',
  `score_act` varchar(200) DEFAULT NULL COMMENT 'ACT成绩',
  `score_sat` varchar(200) DEFAULT NULL COMMENT 'SAT成绩',
  `score_sat2` varchar(200) DEFAULT NULL COMMENT 'SAT2成绩',
  `score_gre` varchar(200) DEFAULT NULL COMMENT 'GRE成绩',
  `score_gmat` varchar(200) DEFAULT NULL COMMENT 'GMAT成绩',
  `score_ielts` varchar(500) DEFAULT NULL COMMENT '雅思成绩',
  `score_ielts_total` varchar(500) DEFAULT NULL COMMENT '雅思总分',
  `score_toefl` varchar(1000) DEFAULT NULL COMMENT '托福成绩',
  `score_toefl_total` varchar(500) DEFAULT NULL COMMENT '托福总分',
  `score_native` varchar(200) DEFAULT NULL COMMENT 'native成绩',
  `score_others` varchar(300) DEFAULT NULL COMMENT '其他成绩',
  `material` text COMMENT '申请材料',
  `admission_elements` text COMMENT '申请要点',
  `reduce_status` bigint(1) DEFAULT '0' COMMENT '是否减免 1是0否',
  `reduce_condition` varchar(500) DEFAULT NULL COMMENT '减免条件',
  `spider_id` int(11) DEFAULT NULL COMMENT '爬虫ID',
  `delete_status` int(1) DEFAULT '0' COMMENT '是否删除  0-未删除,1-已删除',
  `create_by` int(11) NOT NULL COMMENT '创建人',
  `update_by` int(11) NOT NULL COMMENT '更新人',
  `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
  `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `attention_total` int(10) NOT NULL DEFAULT '0' COMMENT '关注总数',
  `score` decimal(3,1) DEFAULT NULL COMMENT '评分',
  `market_tags` varchar(200) DEFAULT NULL COMMENT '标签',
  `orderby` int(10) NOT NULL DEFAULT '0' COMMENT '排序',
  `application_fee_value` decimal(8,2) DEFAULT NULL COMMENT '申请费值',
  `currency_id` int(11) DEFAULT NULL COMMENT '币种id',
  `small_direction` text COMMENT '专业小方向',
  `project_abbreviations` varchar(255) DEFAULT '' COMMENT '专业简称',
  `opening_month` varchar(255) DEFAULT '' COMMENT '开学月份',
  `org_id` int(11) DEFAULT NULL COMMENT '洗数据保留原始表id',
  `career_opportunities` text COMMENT '职业规划',
  `cricos_code` text COMMENT '澳洲专用',
  `weight` bigint(20) NOT NULL DEFAULT '0' COMMENT '排序权重（23.7-24.1申请数）',
  PRIMARY KEY (`id`),
  KEY `idx_school` (`school_id`) USING BTREE,
  KEY `idx_depart` (`depart_id`) USING BTREE,
  KEY `uk_spider` (`spider_id`) USING BTREE,
  KEY `idx_order` (`orderby`) USING BTREE,
  KEY `idx_del_status` (`delete_status`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=209341 DEFAULT CHARSET=utf8mb4 COMMENT='院校院系招生项目表';'''

from datetime import datetime

# 创建实体类
from typing import Optional
from langchain_core.pydantic_v1 import Field
from pydantic import BaseModel

from app.common.database.mysql.mysql_client import MySQLConnect


class ZnSchoolDepartmentProject(MySQLConnect, BaseModel):
    id: Optional[int] = Field(None, description="院校院系招生项目表id")
    school_id: Optional[int] = Field(None, description="院校表ID")
    campus_id: Optional[str] = Field(None, description="校区id 已废 见中间表 zn_school_project_campus")
    campus_name: Optional[str] = Field(None, description="校区名称")
    depart_id: Optional[int] = Field(None, description="院系表ID")
    depart_name: Optional[str] = Field(None, description="院系名称")
    course_code: Optional[str] = Field(None, description="课程编码")
    chinese_name: Optional[str] = Field(None, description="项目中文名")
    english_name: Optional[str] = Field(None, description="项目英文名")
    introduction: Optional[str] = Field(None, description="项目介绍")
    degree_level: Optional[str] = Field(None, description="学位等级")
    degree_name: Optional[str] = Field(None, description="学位名称")
    degree_type: Optional[str] = Field(None, description="学位类型")
    length_of_full: Optional[str] = Field(None, description="全日制学制")
    length_of_schoolings: Optional[str] = Field(None, description="时间-年月日，学制时间")
    length_of_part: Optional[str] = Field(None, description="非全日制学制")
    semester: Optional[str] = Field(None, description="开学时间")
    time_apply_deadline: Optional[str] = Field(None, description="申请截止时间")
    time_offer: Optional[str] = Field(None, description="Offer发放时间")
    time_offer_deadline: Optional[str] = Field(None, description="Offer发放截止时间")
    science_requirement: Optional[str] = Field(None, description="学术要求")
    major_link: Optional[str] = Field(None, description="专业链接")
    fee_apply: Optional[str] = Field(None, description="申请费用")
    fee_tuition: Optional[str] = Field(None, description="学费")
    fee_book: Optional[str] = Field(None, description="书本费")
    fee_life: Optional[str] = Field(None, description="生活费")
    fee_traffic: Optional[str] = Field(None, description="交通费")
    fee_accommodation: Optional[str] = Field(None, description="住宿费用")
    fee_others: Optional[str] = Field(None, description="其他费用")
    fee_total: Optional[str] = Field(None, description="总花费")
    score_gpa: Optional[str] = Field(None, description="GPA成绩")
    score_act: Optional[str] = Field(None, description="ACT成绩")
    score_sat: Optional[str] = Field(None, description="SAT成绩")
    score_sat2: Optional[str] = Field(None, description="SAT2成绩")
    score_gre: Optional[str] = Field(None, description="GRE成绩")
    score_gmat: Optional[str] = Field(None, description="GMAT成绩")
    score_ielts: Optional[str] = Field(None, description="雅思成绩")
    score_ielts_total: Optional[str] = Field(None, description="雅思总分")
    score_toefl: Optional[str] = Field(None, description="托福成绩")
    score_toefl_total: Optional[str] = Field(None, description="托福总分")
    score_native: Optional[str] = Field(None, description="native成绩")
    score_others: Optional[str] = Field(None, description="其他成绩")
    material: Optional[str] = Field(None, description="申请材料")
    admission_elements: Optional[str] = Field(None, description="申请要点")
    reduce_status: Optional[int] = Field(None, description="是否减免 1是0否")
    reduce_condition: Optional[str] = Field(None, description="减免条件")
    spider_id: Optional[int] = Field(None, description="爬虫ID")
    delete_status: Optional[int] = Field(None, description="是否删除  0-未删除,1-已删除")
    create_by: Optional[int] = Field(None, description="创建人")
    update_by: Optional[int] = Field(None, description="更新人")
    create_name: Optional[str] = Field(None, description="创建人名称")
    update_name: Optional[str] = Field(None, description="更新人名称")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    attention_total: Optional[int] = Field(None, description="关注总数")
    score: Optional[float] = Field(None, description="评分")
    market_tags: Optional[str] = Field(None, description="标签")
    orderby: Optional[int] = Field(None, description="排序")
    application_fee_value: Optional[float] = Field(None, description="申请费值")
    currency_id: Optional[int] = Field(None, description="币种id")
    small_direction: Optional[str] = Field(None, description="专业小方向")
    project_abbreviations: Optional[str] = Field(None, description="专业简称")
    opening_month: Optional[str] = Field(None, description="开学月份")
    org_id: Optional[int] = Field(None, description="洗数据保留原始表id")
    career_opportunities: Optional[str] = Field(None, description="职业规划")
    cricos_code: Optional[str] = Field(None, description="澳洲专用")
    weight: Optional[int] = Field(None, description="排序权重（23.7-24.1申请数）")

    @classmethod
    def select_by_check_school(cls, check_school: object) -> object:
        """

        :rtype: object
        """
        conditions = []
        params = []

        if check_school.country_name:
            conditions.append('country_name = %s')
            params.append(check_school.country_name)

        if check_school.school_name:
            conditions.append('(zsi.chinese_name like %s or zsi.english_name like %s)')
            params.extend(['%' + check_school.school_name + '%'] * 2)

        if check_school.major_name:
            conditions.append('(zsdp.chinese_name like %s or zsdp.english_name like %s)')
            params.extend(['%' + check_school.major_name + '%'] * 2)

        if check_school.degree_type:
            conditions.append('degree_level = %s')
            params.append(check_school.degree_type)

        sql = ('select '
               'zsdp.chinese_name as major_chinese_name,'
               'zsdp.english_name as major_english_name,'
               'zsdp.degree_type,'
               'zsi.chinese_name as school_chinese_name,'
               'zsi.english_name as school_english_name,'
               'zsi.country_name '
               ' from zn_school_department_project zsdp inner join zn_school_info zsi on zsdp.school_id = zsi.id where ') + ' and '.join(
            conditions)

        return cls.execute_all2dict(sql, tuple(params))
