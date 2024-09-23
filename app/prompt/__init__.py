from app.database.mysql.xxlxdb.ai_knowledge_base.ai_knowledge_base import get_prompt_by_type

prompt_list = xiaoxi_chat_generate_prompt = get_prompt_by_type()
# 转换type为key，prompt为value
prompt_dict = {}
for prompt in prompt_list:
    prompt_dict[prompt['type']] = prompt['prompt']

# 小希正常加载RAG对话
xiao_xi_chat = prompt_dict.get('xiao_xi_chat')
# 进行任务分类
classification_query = prompt_dict.get('classification_query')
# C类任务，匹配使用prompt
matching_information = prompt_dict.get('matching_information')
# C类任务的申请进度总结使用prompt
matching_summary = prompt_dict.get('matching_summary')
# C类任务信息不全使用prompt
information_completion = prompt_dict.get('information_completion')
# 再次回答分类任务的问题
reanswer_classification_query = prompt_dict.get('reanswer_classification_query')
# json格式化
json_formatting = prompt_dict.get('json_formatting')
# small_talk
small_talk = prompt_dict.get('small_talk')
# 分类失败,走提示prompt
information_cue = prompt_dict.get('information_cue')
