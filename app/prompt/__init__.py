from app.database.mysql.xxlxdb.ai_knowledge_base.ai_knowledge_base import get_prompt_by_type

prompt_list = xiaoxi_chat_generate_prompt = get_prompt_by_type()
# 转换type为key，prompt为value
prompt_dict = {}
for prompt in prompt_list:
    prompt_dict[prompt['type']] = prompt['prompt']

xiaoXiChat = prompt_dict.get('xiaoXiChat')
classificationQuery = prompt_dict.get('classificationQuery')
matchingInformation = prompt_dict.get('matchingInformation')
matchingSummary = prompt_dict.get('matchingSummary')
