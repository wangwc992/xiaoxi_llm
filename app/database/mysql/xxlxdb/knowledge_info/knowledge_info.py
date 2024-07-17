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

from app.database.mysql.mysql_client import MySQLConnect, xxlxdb


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

def search_weaviate_data():
    sql = "SELECT * FROM `t_knowledge_info`"
    return xxlxdb.execute_all2dict(sql)

