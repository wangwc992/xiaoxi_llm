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
# `school_id` int(11) DEFAULT NULL COMMENT '院校表ID',
# `world_rank_usnews` int(5) DEFAULT NULL COMMENT '世界USNEWS排名',
# `world_rank_the` int(5) DEFAULT NULL COMMENT '世界泰晤士高等教育排名',
# `world_rank_qs` int(5) DEFAULT NULL COMMENT '世界QS排名',
# `local_rank_usnews` int(5) DEFAULT NULL COMMENT '地区USNEWS排名',
# `local_rank_the` int(5) DEFAULT NULL COMMENT '地区泰晤士高等教育排名',
# `local_rank_qs` int(5) DEFAULT NULL COMMENT '地区QS排名',
# `delete_status` int(1) DEFAULT '0' COMMENT '是否删除  0-未删除,1-已删除',
# `create_by` int(11) NOT NULL COMMENT '创建人',
# `update_by` int(11) NOT NULL COMMENT '更新人',
# `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
# `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
# `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
# `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
# PRIMARY KEY (`id`) USING BTREE,
# UNIQUE KEY `uk_school` (`school_id`) USING BTREE,
# KEY `idx_school_id_world_rank_qs` (`school_id`,`world_rank_qs`)
# ) ENGINE=InnoDB AUTO_INCREMENT=20021 DEFAULT CHARSET=utf8mb4 COMMENT='院校排名表';
def search_school_info_ranking_data(id: int = 0, limit: int = 10):
    pass


def search_zn_school_department_project01(id: int = 0, limit: int = 300):
    sql = f'''
            select 
                znsdp.id as 'id',
                zsi.chinese_name as 'school_name',
                zsi.english_name as 'english_name',
                zsi.school_abbreviations as 'school_abbreviations',
                znsdp.depart_name as 'department',
                znsdp.campus_name as 'campus',
                znsdp.chinese_name as 'chinese_name',
                znsdp.english_name as 'english_name',
                znsdp.course_code as 'course_code',
                znsdp.major_link as 'major_link',
                znsdp.length_of_full as 'full_time_duration',
                znsdp.small_direction as 'specialization',
                znsdp.length_of_part as 'part_time_duration',
                znsdp.degree_name as 'degree_name',
                znsdp.degree_type as 'degree_type',
                znsdp.degree_level as 'degree_level',
                znsdp.project_abbreviations as 'abbreviation',
                znsdp.semester as 'start_semester',
                zsi.city_path as 'city_path',
                znsdp.introduction as 'introduction',
                znsdp.career_opportunities as 'career_opportunities'
            from 
                zn_school_department_project znsdp
            left join zn_school_info zsi on zsi.id = znsdp.school_id
            where znsdp.delete_status = 0 
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


def search_zn_school_department_project02(id: int = 0, limit: int = 10):
    sql = f'''
            select znsdp.id                  as 'id',
                   zsi.chinese_name          as 'school_name',
                   zsi.english_name          as 'english_name',
                   zsi.school_abbreviations  as 'school_abbreviations',
                   znsdp.chinese_name        as 'chinese_name',
                   znsdp.english_name        as 'english_name',
                   znsdp.school_id           as 'school_id',
                   znsdp.campus_name         as 'campus',
                   znsdp.semester            as 'start_semester',
                   znsdp.time_apply_deadline as 'application_deadline',
                   znsdp.time_offer          as 'offer_release_time',
                   znsdp.time_offer_deadline as 'offer_deadline',
                   znsdp.fee_apply           as 'application_fee',
                   znsdp.fee_tuition         as 'tuition_fee',
                   znsdp.fee_life            as 'living_expenses',
                   znsdp.fee_traffic         as 'traffic_fee',
                   znsdp.fee_accommodation   as 'accommodation_fee',
                   znsdp.fee_others          as 'other_fees',
                   znsdp.fee_total           as 'total_cost'
            from zn_school_department_project znsdp
                     left join zn_school_info zsi on zsi.id = znsdp.school_id
            where znsdp.delete_status = 0
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


def search_zn_school_department_project03(id: int = 0, limit: int = 10):
    sql = f'''
            select znsdp.id                 as 'id',
                   zsi.chinese_name         as 'school_name',
                   zsi.english_name         as 'english_name',
                   zsi.school_abbreviations as 'school_abbreviations',
                   znsdp.chinese_name       as 'chinese_name',
                   znsdp.english_name       as 'english_name',
                   znsdp.score_ielts        as 'ielts_score',
                   znsdp.score_ielts_total  as 'ielts_total_score',
                   znsdp.score_toefl        as 'toefl_score',
                   znsdp.score_toefl_total  as 'toefl_total_score'
            from zn_school_department_project znsdp
                     left join zn_school_info zsi on znsdp.school_id = zsi.id
            where znsdp.delete_status = 0
                and zsi.delete_status = 0
                and znsdp.id > {id}
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
            from zn_school_department_project znsdp
                 join zn_school_deparment_admission_score znsds on znsdp.id = znsds.zsdp_id
                 join zn_school_info zsi on znsdp.school_id = zsi.id
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
                join zn_school_deparment_admission_score znsds on znsdp.id = znsds.zsdp_id
                join zn_school_info zsi on znsdp.school_id = zsi.id
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
                join zn_school_info zsi on znsdp.school_id = zsi.id
            where
                znsdp.delete_status = 0
                and zsi.delete_status = 0
                and znsdp.id > {id}
        '''
    return xxlxdb.execute_all2dict(sql=sql, limit=limit)


if __name__ == '__main__':
    print(search_school_info_basic_data(5, 6))
