from app.database.mysql.xxlxdb.ai_knowledge_base.ai_model import EducationalBackground, IntentionStudyAbroad
from app.database.mysql.xxlxdb.ai_knowledge_base.chat_model import ChatCompletionStreamResponse

s = """ 
{
    "intention_tudy_abroad":{
        "school_en_name": ["Massachusetts Institute of Technology", "University of Sydney"],
        "major_en_name": "Architecture",
        "degree": "预科",
        "semester": "02-28"
    },
    "educational_background":{
        "study_diploma": "本科",
        "study_school": "清华",
        "study_major": "信息技术",
        "study_score": "3.5"
    }
}
"""


def json_formatting(json_str: str) -> dict:
    start = json_str.find("{")
    end = json_str.rfind("}")
    json_str = json_str[start:end + 1]
    return eval(json_str)


s_dict = eval(s)
s_dict2 = json_formatting(s)
print(s_dict)


chat_completion_stream_response = ChatCompletionStreamResponse()

# 将s_dict的intention_tudy_abroad的key-value对赋值给chat_completion_stream_response
chat_completion_stream_response.intention_study_abroad = IntentionStudyAbroad(**s_dict['intention_tudy_abroad'])
chat_completion_stream_response.educational_background = EducationalBackground(**s_dict['educational_background'])


print(chat_completion_stream_response.dict())

x = chat_completion_stream_response.model_dump(exclude_unset=True)

print(x)