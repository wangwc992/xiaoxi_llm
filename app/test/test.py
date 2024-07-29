from app.common.utils.object_utils import ObjectFormatter
from app.database.mysql.xxlxdb.knowledge_info.knowledge_info import search_school_info_basic_data

school_info_basic = search_school_info_basic_data(id=1, limit=10)
key_name_list02 = [{'': 'chinese_name'}, {'': 'english_name'}, {"所属国家": "country_name"},
                   {"": "city_path"}, {"官网地址": "website"}, {"申请费支付维度": "fee_dimension"},
                   {"申请周期-算法统计": "apply_cycle_algorithm"}, {"申请周期-人工配置": "apply_cycle_manual"}]
dict_list01 = ObjectFormatter.attribute_concatenation(key_name_list02, school_info_basic)
print(dict_list01)