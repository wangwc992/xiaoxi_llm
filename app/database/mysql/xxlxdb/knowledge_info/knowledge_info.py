'''CREATE TABLE `t_knowledge_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `startup_status` int(1) NOT NULL DEFAULT '0' COMMENT '状态 1开启/0关闭',
  `type` int(1) NOT NULL COMMENT '类型 1问题、2文件',
  `class` varchar(50) DEFAULT NULL COMMENT '类别（文件共享）',
  `name` varchar(350) DEFAULT NULL COMMENT '问题名称',
  `country` varchar(350) DEFAULT NULL COMMENT '国家',
  `school` varchar(350) DEFAULT NULL COMMENT '学校',
  `content` text CHARACTER SET utf8mb4,
  `fileurl` varchar(255) DEFAULT NULL COMMENT '文件',
  `views` int(7) DEFAULT '0' COMMENT '浏览量',
  `updater` varchar(50) NOT NULL COMMENT '更新人',
  `updateTime` datetime NOT NULL COMMENT '更新时间',
  `founder` varchar(45) NOT NULL COMMENT '创建人',
  `creationTime` datetime NOT NULL COMMENT '创建时间',
  `filename` varchar(255) DEFAULT NULL COMMENT '文件原名称',
  `countryId` varchar(100) DEFAULT NULL COMMENT '国家ID',
  `schoolId` varchar(100) DEFAULT NULL COMMENT '学院ID',
  `submit_type` int(1) NOT NULL COMMENT '1发布  2提问 ',
  `like_num` int(15) DEFAULT '0' COMMENT '点赞数量',
  `bad_num` int(15) DEFAULT '0' COMMENT '差评数量',
  `apply_status` int(1) NOT NULL COMMENT '0未回复   1已回复    2待审批  3驳回  4 已审批  5驳回副本',
  `founder_id` varchar(45) NOT NULL COMMENT '创建人ID',
  `replyer` varchar(45) DEFAULT NULL COMMENT '回复人',
  `replyerTime` datetime DEFAULT NULL COMMENT '回复时间',
  `audit_id` int(15) DEFAULT NULL COMMENT '审批ID，驳回副本关联用',
  `share_num` int(11) DEFAULT '0' COMMENT '分享数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=24809 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;'''

from datetime import datetime

# 创建实体类
from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field

from app.database.mysql.mysql_client import xxlxdb, smart_counselor


class KnowledgeInfo(BaseModel):
    id: Optional[int] = Field(None, description="知识库表id")
    startup_status: int = Field(None, description="状态 1开启/0关闭")
    type: int = Field(None, description="类型 1问题、2文件")
    class_: Optional[str] = Field(None, description="类别（文件共享）")
    name: Optional[str] = Field(None, description="问题名称")
    country: Optional[str] = Field(None, description="国家")
    school: Optional[str] = Field(None, description="学校")
    content: Optional[str] = Field(None, description="内容")
    fileurl: Optional[str] = Field(None, description="文件")
    views: int = Field(None, description="浏览量")
    updater: str = Field(None, description="更新人")
    updateTime: datetime = Field(None, description="更新时间")
    founder: str = Field(None, description="创建人")
    creationTime: datetime = Field(None, description="创建时间")
    filename: Optional[str] = Field(None, description="文件原名称")
    countryId: Optional[str] = Field(None, description="国家ID")
    schoolId: Optional[str] = Field(None, description="学院ID")
    submit_type: int = Field(None, description="1发布  2提问 ")
    like_num: int = Field(None, description="点赞数量")
    bad_num: int = Field(None, description="差评数量")
    apply_status: int = Field(None, description="0未回复   1已回复    2待审批  3驳回  4 已审批  5驳回副本")
    founder_id: str = Field(None, description="创建人ID")
    replyer: Optional[str] = Field(None, description="回复人")
    replyerTime: Optional[datetime] = Field(None, description="回复时间")
    audit_id: Optional[int] = Field(None, description="审批ID，驳回副本关联用")
    share_num: int = Field(None, description="分享数")


def search_knowledge_info_data(id=0, limit=10):
    sql = f"SELECT id, country, school, class, name, founder, replyerTime, content, fileurl FROM t_knowledge_info where startup_status = 1 and id > {id}"
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


def search_notice_message_data(id: int = 0, limit: int = 10):
    '''小希平台院校资讯'''
    sql = f'''SELECT 
        nm.id AS notice_id,
        si.english_name AS school_english_name,
        si.name AS school_name,
        nm.create_time AS notice_create_time,
        CASE 
            WHEN nm.category = 1 THEN '培训材料'
            WHEN nm.category = 2 THEN '申请指南'
            WHEN nm.category = 3 THEN '奖学金'
            WHEN nm.category = 4 THEN '活动预告'
            WHEN nm.category = 5 THEN '简报'
            ELSE '未知类别'
        END AS notice_category,
        nm.name AS notice_title,
        nm.summary AS notice_summary,
        ac.name AS attachment_name,
        ac.url AS attachment_url 
    FROM 
        notice_message nm 
    LEFT JOIN 
        school_notice_relation snr ON snr.notice_id = nm.id AND snr.delete_status = 0 
    LEFT JOIN 
        school_info si ON si.id = snr.school_id 
    LEFT JOIN 
        content_student_visibility csv ON csv.associated_id = nm.id AND csv.delete_status = 0 AND csv.type = 1 
    LEFT JOIN 
        content_wechat_visibility cwv ON cwv.associated_id = nm.id AND cwv.delete_status = 0 AND cwv.type = 1 
    LEFT JOIN 
        content_visibility cv ON cv.associated_id = nm.id AND cv.delete_status = 0 AND cv.type = 1 
    LEFT JOIN 
        attachment_collection ac ON ac.associate_id = nm.id AND ac.delete_status = 0 
    WHERE 
        nm.delete_status = 0 AND nm.type IN (1,2,3) AND nm.id > {id}
    '''
    return smart_counselor.execute_all2dict(sql=sql, limit=limit)


def search_school_info_basic_data(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        id,
        chinese_name,
        english_name,
        school_abbreviations,
        country_name,
        city_path,
        website,
        CASE 
            WHEN fee_dimension = 1 THEN '按院校'
            WHEN fee_dimension = 2 THEN '按专业'
            WHEN fee_dimension = 3 THEN '其他'
            ELSE ''
        END AS fee_dimension,
        fee_dimension,
        apply_cycle_algorithm,
        apply_cycle_manual
    FROM 
        zn_school_info where delete_status = 0 and id > {id}
    '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


# 院校排名查询信息，带上zn_school_info表关联
# CREATE TABLE `zn_school_rank` (
#     `id` int(11) NOT NULL AUTO_INCREMENT,
#zn_school_rank
def search_school_info_ranking_data(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.world_rank_usnews as world_rank_usnews,
        b.world_rank_the as world_rank_the,
        b.world_rank_qs as world_rank_qs, 
        b.local_rank_usnews as local_rank_usnews,
        b.local_rank_the as local_rank_the,
        b.local_rank_qs as local_rank_qs
    FROM 
        zn_school_info a 
        left join zn_school_rank b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0 and a.id > {id}
    '''

    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

# zn_school_intro
def search_school_info_more_data(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.employment_rate as employment_rate,
        b.employment_salary as employment_salary,
        b.student_amount as student_amount,
        b.undergraduate_amount as undergraduate_amount,
        b.graduate_amount as graduate_amount,
        b.international_ratio as international_ratio,
        b.faculty_ratio as faculty_ratio,
        b.boy_girl_ratio as boy_girl_ratio,
        b.introduction as introduction,
        b.history as history,
        b.location as location,
        b.campus as campus,
        b.accommodation as accommodation,
        b.library as library,
        b.installation as installation,
        b.admissions_office as admissions_office,
        b.covid_rule as covid_rule
    FROM 
        zn_school_info a 
        left join zn_school_intro b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0
        and a.id > {id}
        '''

    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

def search_zn_school_selection_reason(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.selection_reason as selection_reason,
        b.feature as feature,
        b.strong_majors as strong_majors,
        b.hot_majors as hot_majors,
        b.department_major as department_major,
        b.evaluation_good as evaluation_good,
        b.evaluation_bad as evaluation_bad
    FROM 
        zn_school_info a 
        left join zn_school_selection_reason b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0
        and a.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

# CREATE TABLE `zn_school_recruit_graduate` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `school_id` int(11) DEFAULT NULL COMMENT '院校表ID',
# `recruit_type` int(1) DEFAULT NULL COMMENT '招生类型 1本科 2研究生',
# `introduction` text COMMENT '申请简介',
# `admission_rate` varchar(200) DEFAULT NULL COMMENT '录取率',
# `time_apply_deadline` varchar(300) DEFAULT NULL COMMENT '申请截止时间',
# `apply_amount` varchar(200) DEFAULT NULL COMMENT '申请人数',
# `semester` varchar(200) DEFAULT NULL COMMENT '申请学期',
# `time_offer` varchar(200) DEFAULT NULL COMMENT 'Offer发放时间',
# `fee_apply` varchar(200) DEFAULT NULL COMMENT '申请费用',
# `fee_tuition` varchar(300) DEFAULT NULL COMMENT '学费',
# `fee_book` varchar(200) DEFAULT NULL COMMENT '书本费',
# `fee_life` varchar(200) DEFAULT NULL COMMENT '生活费',
# `fee_traffic` varchar(200) DEFAULT NULL COMMENT '交通费',
# `fee_accommodation` varchar(200) DEFAULT NULL COMMENT '住宿费用',
# `fee_others` varchar(200) DEFAULT NULL COMMENT '其他费用',
# `fee_total` varchar(200) DEFAULT NULL COMMENT '总花费',
# `score_gpa` varchar(500) DEFAULT NULL COMMENT 'GPA成绩',
# `score_act` varchar(200) DEFAULT NULL COMMENT 'ACT成绩',
# `score_sat` varchar(200) DEFAULT NULL COMMENT 'SAT成绩',
# `score_sat2` varchar(200) DEFAULT NULL COMMENT 'SAT2成绩',
# `score_gre` varchar(200) DEFAULT NULL COMMENT 'GRE成绩',
# `score_gmat` varchar(200) DEFAULT NULL COMMENT 'GMAT成绩',
# `score_ielts` varchar(500) DEFAULT NULL COMMENT '雅思成绩',
# `score_toefl` varchar(500) DEFAULT NULL COMMENT '托福成绩',
# `score_native` varchar(200) DEFAULT NULL COMMENT 'native成绩',
# `score_others` varchar(500) DEFAULT NULL COMMENT '其他成绩',
# `scholarship` text COMMENT '奖学金',
# `material` text COMMENT '申请材料',
# `recruit_flow` text COMMENT '申请流程',
# `delete_status` int(1) DEFAULT '0' COMMENT '是否删除  0-未删除,1-已删除',
# `create_by` int(11) NOT NULL COMMENT '创建人',
# `update_by` int(11) NOT NULL COMMENT '更新人',
# `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
# `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
# `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
# `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
# `application_fee_value` decimal(8,2) DEFAULT NULL COMMENT '申请费值',
# `currency_id` int(11) DEFAULT NULL COMMENT '币种id',
# PRIMARY KEY (`id`) USING BTREE,
# UNIQUE KEY `uk_school` (`school_id`,`recruit_type`) USING BTREE
# ) ENGINE=InnoDB AUTO_INCREMENT=16275 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='院校本研招生表';
def search_zn_school_recruit_graduate_1(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.introduction as introduction,
        b.admission_rate as admission_rate,
        b.time_apply_deadline as time_apply_deadline,
        b.apply_amount as apply_amount,
        b.semester as semester,
        b.time_offer as time_offer,
        b.fee_apply as fee_apply,
        b.fee_tuition as fee_tuition,
        b.fee_book as fee_book,
        b.fee_life as fee_life,
        b.fee_traffic as fee_traffic,
        b.fee_accommodation as fee_accommodation,
        b.fee_others as fee_others,
        b.fee_total as fee_total,
        b.score_gpa as score_gpa,
        b.score_act as score_act,
        b.score_sat as score_sat,
        b.score_sat2 as score_sat2,
        b.score_gre as score_gre,
        b.score_gmat as score_gmat,
        b.score_ielts as score_ielts,
        b.score_toefl as score_toefl,
        b.score_native as score_native,
        b.score_others as score_others,
        b.scholarship as scholarship,
        b.material as material,
        b.recruit_flow as recruit_flow,
        b.delete_status as delete_status,
        b.create_by as create_by,
        b.update_by as update_by,
        b.create_name as create_name,
        b.update_name as update_name,
        b.create_time as create_time,
        b.update_time as update_time,
        b.application_fee_value as application_fee_value,
        b.currency_id as currency_id
    FROM 
        zn_school_info a 
        left join zn_school_recruit_graduate b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0 and b.recruit_type = 1
        and a.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

def search_zn_school_recruit_graduate_2(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.introduction as introduction,
        b.admission_rate as admission_rate,
        b.time_apply_deadline as time_apply_deadline,
        b.apply_amount as apply_amount,
        b.semester as semester,
        b.time_offer as time_offer,
        b.fee_apply as fee_apply,
        b.fee_tuition as fee_tuition,
        b.fee_book as fee_book,
        b.fee_life as fee_life,
        b.fee_traffic as fee_traffic,
        b.fee_accommodation as fee_accommodation,
        b.fee_others as fee_others,
        b.fee_total as fee_total,
        b.score_gpa as score_gpa,
        b.score_act as score_act,
        b.score_sat as score_sat,
        b.score_sat2 as score_sat2,
        b.score_gre as score_gre,
        b.score_gmat as score_gmat,
        b.score_ielts as score_ielts,
        b.score_toefl as score_toefl,
        b.score_native as score_native,
        b.score_others as score_others,
        b.scholarship as scholarship,
        b.material as material,
        b.recruit_flow as recruit_flow,
        b.delete_status as delete_status,
        b.create_by as create_by,
        b.update_by as update_by,
        b.create_name as create_name,
        b.update_name as update_name,
        b.create_time as create_time,
        b.update_time as update_time,
        b.application_fee_value as application_fee_value,
        b.currency_id as currency_id
    FROM 
        zn_school_info a 
        left join zn_school_recruit_graduate b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0 and b.recruit_type = 2
        and a.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

def search_zn_school_department_project04(id: int = 0, limit: int = 10):
    sql = f'''
            select znsdp.id                 as 'id',
                   zsi.chinese_name         as 'school_name',
                   zsi.english_name         as 'english_name',
                   zsi.school_abbreviations as 'school_abbreviations',
                   znsdp.chinese_name       as 'chinese_name',
                   znsdp.english_name       as 'english_name',
                   znsdp.school_id          as 'school_id',
                   znsdp.campus_name        as 'campus',
                   znsds.atar_ask           as 'atar_requirement',
                   znsds.atar_score         as 'atar_score',
                   znsds.sat_ask            as 'sat_requirement',
                   znsds.sat_score          as 'sat_score',
                   znsds.ukalevel3_ask      as 'ukalevel3_requirement',
                   znsds.ukalevel3_score    as 'ukalevel3_score',
                   znsds.act_ask            as 'act_requirement',
                   znsds.act_score          as 'act_score',
                   znsds.ukalevel3_score1   as 'ukalevel3_score1',
                   znsds.ukalevel3_score2   as 'ukalevel3_score2',
                   znsds.ukalevel3_score3   as 'ukalevel3_score3',
                   znsds.ukalevel4_ask      as 'ukalevel4_requirement',
                   znsds.ukalevel4_score    as 'ukalevel4_score',
                   znsds.ap_ask             as 'ap_requirement',
                   znsds.ap_score           as 'ap_score',
                   znsds.ib_ask             as 'ib_requirement',
                   znsds.ib_score           as 'ib_score',
                   znsds.gaokao_ask         as 'gaokao_requirement',
                   znsds.gaokao_score       as 'gaokao_score',
                   znsds.ossd_ask           as 'ossd_requirement',
                   znsds.ossd_score         as 'ossd_score',
                   znsds.bc_ask             as 'bc_requirement',
                   znsds.bc_score           as 'bc_score'
            from 
                zn_school_department_project znsdp
                inner join zn_school_deparment_admission_score znsds on znsdp.id = znsds.zsdp_id
                inner join zn_school_info zsi on znsdp.school_id = zsi.id
            where znsdp.delete_status = 0
                and znsds.delete_status = 0
                and zsi.delete_status = 0
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


def search_zn_school_department_project05(id: int = 0, limit: int = 10):
    sql = f'''
            select 
                znsdp.id as 'id',
                zsi.chinese_name as 'school_name',
                zsi.english_name as 'english_name',
                zsi.school_abbreviations as 'school_abbreviations',
                znsdp.chinese_name as 'chinese_name',
                znsdp.english_name as 'english_name',
                znsdp.school_id as 'school_id',
                znsdp.campus_name as 'campus',
                znsds.c9_ask as 'c9_requirement',
                znsds.c9_score as 'c9_score',
                znsds.s211_ask as 's211_requirement',
                znsds.s211_score as 's211_score',
                znsds.s985_ask as 's985_requirement',
                znsds.s985_score as 's985_score',
                znsds.sn211_ask as 'sn211_requirement',
                znsds.sn211_score as 'sn211_score',
                znsds.accept_md_bg as 'professional_background_requirement',
                znsds.b_accept_md_bg as 'accept_cross_major'
            from 
                zn_school_department_project znsdp
                inner join zn_school_deparment_admission_score znsds on znsdp.id = znsds.zsdp_id
                inner join zn_school_info zsi on znsdp.school_id = zsi.id
            where 
                znsdp.delete_status = 0
                and znsds.delete_status = 0
                and zsi.delete_status = 0
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


def search_zn_school_department_project06(id: int = 0, limit: int = 10):
    sql = f'''
            select 
                znsdp.id as 'id',
                zsi.chinese_name as 'school_name',
                zsi.english_name as 'english_name',
                zsi.school_abbreviations as 'school_abbreviations',
                znsdp.chinese_name as 'chinese_name',
                znsdp.english_name as 'english_name',
                znsdp.school_id as 'school_id',
                znsdp.campus_name as 'campus',
                znsdp.science_requirement as 'academic_requirement',
                znsdp.material as 'application_materials',
                znsdp.admission_elements as 'application_elements',
                znsdp.reduce_status as 'credit_reduction',
                znsdp.reduce_condition as 'credit_reduction_condition'
            from
                zn_school_department_project znsdp
                inner join zn_school_info zsi on znsdp.school_id = zsi.id
            where
                znsdp.delete_status = 0
                and zsi.delete_status = 0
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)

# CREATE TABLE `zn_school_recruit_art` (
# `id` int(11) NOT NULL AUTO_INCREMENT,
# `school_id` int(11) DEFAULT NULL COMMENT '院校表ID',
# `strong_majors` varchar(500) DEFAULT NULL COMMENT '优势专业',
# `admission_rate` varchar(200) DEFAULT NULL COMMENT '录取率',
# `fee_apply` varchar(200) DEFAULT NULL COMMENT '申请费用',
# `fee_tuition` varchar(200) DEFAULT NULL COMMENT '学费',
# `fee_book` varchar(200) DEFAULT NULL COMMENT '书本费',
# `fee_life` varchar(200) DEFAULT NULL COMMENT '生活费',
# `fee_traffic` varchar(200) DEFAULT NULL COMMENT '交通费',
# `fee_accommodation` varchar(200) DEFAULT NULL COMMENT '住宿费用',
# `fee_others` varchar(200) DEFAULT NULL COMMENT '其他费用',
# `fee_total` varchar(200) DEFAULT NULL COMMENT '总花费',
# `graduate_majors` text COMMENT '研究生专业',
# `graduate_score_ielts` varchar(200) DEFAULT NULL COMMENT '研究生雅思成绩',
# `graduate_score_toefl` varchar(200) DEFAULT NULL COMMENT '研究生托福成绩',
# `graduate_requirements` text COMMENT '研究生申请要求',
# `graduate_works_requirement` text COMMENT '研究生作品集要求',
# `graduate_apply_deadline` varchar(200) DEFAULT NULL COMMENT '研究生申请截止日期',
# `undergraduate_majors` text COMMENT '本科专业',
# `undergraduate_score_ielts` varchar(200) DEFAULT NULL COMMENT '本科雅思成绩',
# `undergraduate_score_toefl` varchar(200) DEFAULT NULL COMMENT '本科托福成绩',
# `undergraduate_requirements` text COMMENT '本科申请要求',
# `undergraduate_works_requirement` text COMMENT '本科作品集要求',
# `undergraduate_apply_deadline` varchar(200) DEFAULT NULL COMMENT '本科申请截止日期',
# `difficulty_name` varchar(20) DEFAULT NULL COMMENT '申请难度',
# `apply_experience` text COMMENT '申请经验',
# `alumni` text COMMENT '明星校友',
# `delete_status` int(1) DEFAULT '0' COMMENT '是否删除  0-未删除,1-已删除',
# `create_by` int(11) NOT NULL COMMENT '创建人',
# `update_by` int(11) NOT NULL COMMENT '更新人',
# `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
# `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
# `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
# `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
# `application_fee_value` decimal(8,2) DEFAULT NULL COMMENT '申请费值',
# `currency_id` int(11) DEFAULT NULL COMMENT '币种id',
# PRIMARY KEY (`id`),
# UNIQUE KEY `uk_school` (`school_id`) USING BTREE
# ) ENGINE=InnoDB AUTO_INCREMENT=837 DEFAULT CHARSET=utf8mb4 COMMENT='院校艺术生招生表';
def search_zn_school_recruit_art(id: int = 0, limit: int = 10):
    sql = f'''SELECT 
        a.id as id,
        a.chinese_name as chinese_name,
        a.english_name as english_name, 
        a.school_abbreviations as school_abbreviations,
        b.strong_majors as strong_majors,
        b.admission_rate as admission_rate,
        b.fee_apply as fee_apply,
        b.fee_tuition as fee_tuition,
        b.fee_book as fee_book,
        b.fee_life as fee_life,
        b.fee_traffic as fee_traffic,
        b.fee_accommodation as fee_accommodation,
        b.fee_others as fee_others,
        b.fee_total as fee_total,
        b.graduate_majors as graduate_majors,
        b.graduate_score_ielts as graduate_score_ielts,
        b.graduate_score_toefl as graduate_score_toefl,
        b.graduate_requirements as graduate_requirements,
        b.graduate_works_requirement as graduate_works_requirement,
        b.graduate_apply_deadline as graduate_apply_deadline,
        b.undergraduate_majors as undergraduate_majors,
        b.undergraduate_score_ielts as undergraduate_score_ielts,
        b.undergraduate_score_toefl as undergraduate_score_toefl,
        b.undergraduate_requirements as undergraduate_requirements,
        b.undergraduate_works_requirement as undergraduate_works_requirement,
        b.undergraduate_apply_deadline as undergraduate_apply_deadline,
        b.difficulty_name as difficulty_name,
        b.apply_experience as apply_experience,
        b.alumni as alumni,
        b.delete_status as delete_status,
        b.create_by as create_by,
        b.update_by as update_by,
        b.create_name as create_name,
        b.update_name as update_name,
        b.create_time as create_time,
        b.update_time as update_time,
        b.application_fee_value as application_fee_value,
        b.currency_id as currency_id
    FROM 
        zn_school_info a 
        left join zn_school_recruit_art b on a.id = b.school_id
        where a.delete_status = 0 and b.delete_status = 0
        and a.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


if __name__ == '__main__':
    print(search_school_info_basic_data(5, 6))
