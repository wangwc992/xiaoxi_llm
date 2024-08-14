import http.client
import json
import threading
import time
import random

# 留学相关问题列表
study_abroad_questions = [
    "我应该选择哪个国家作为留学目的地，如何比较不同国家的留学优势？",
    "如何选择适合我的专业和背景的院校？",
    "申请海外院校时，通常需要准备哪些材料？",
    "推荐信应该找谁写？内容如何把握？",
    "留学的总费用大概是多少，包括学费和生活费？",
    "我是否可以申请奖学金或助学金？申请条件是什么？",
    "IELTS和TOEFL之间有何区别？我应该选择哪个？",
    "如何有效备考语言考试以达到申请要求？",
    "留学签证的申请流程是什么？需要哪些材料？",
    "在签证面试中，我应该注意哪些问题？",
    "我如何选择适合我职业发展的专业或课程？",
    "不同专业的就业前景如何？",
    "在国外留学期间，选择校内宿舍还是校外住宿更好？",
    "生活费预算应该如何规划？",
    "如何适应国外的文化差异？有哪些常见的文化冲突需要注意？",
    "我应该如何在留学期间建立和维护社交圈？",
    "留学后回国和留在国外就业各有哪些优劣势？",
    "我如何利用留学经历提升自己的职业竞争力？",
    "当前全球疫情对留学计划有何影响？有哪些应对措施？",
    "如果疫情期间无法入境，我可以选择哪些在线课程或远程学习方案？",
    "如果读Unitec工程造价GD 本科必须是相关专业吗",
    "麻烦问一下莫那什托福送分的数字代码",
    "爱尔兰城市大学2024年9月入学新生注册指南",
    "伦敦城市学院为大家带来24 年秋季入学线上宣讲会",
    "学生托福送分的时候只能查到莫纳什本校，查不到莫纳什，请问可以把分送给本校吗？还是有分校的代码呢？",
    "杨鹏禹的申请费已经递交",
    "山东师范， 汉语国际教育专业87.92， 墨尔本25年2月份入学的tesol能申请减免到一年吗？ pte目前67 60， 墨尔本语言班怎么申？11月份开学的十周够吗",
    "澳洲纽卡斯尔大学teaching专业一年学费多少呀",
    "新南的Bachelor of Interior Architecture (Honours)需要提供作品集吗？直录",
    "想问下老师，新南威尔士大学 master of PR and Advertising 25.2月入学的接受offer截止日期有更新吗，另外想问问这个专业语言打包申请政策和截止日期",
    "40%及格，有希望吗？",
    "如果现在申请语言班，配读语言班情况下可否接受offer呢",
    "KCL有预科吗？可以申请吗？",
    "学生雅思5.5（单项也全部5.5），想申请新南硕士语言班+主课，语言班开课时间分别是几月？主课Master of Engineering (Biomedical)代码8621",
    "学生雅思5.5（单项也全部5.5），想申请新南硕士语言班+主课，语言班开课时间分别是几月？",
    "阿伯丁春季硕士预科有语言班可以衔接吗",
    "有哪些大学的MOT是接受莫纳什Human Biology short course？",
    "申请新南硕士语言班+主课，语言班开课时间分别是几月？",
    "另一个英国预科申澳本咨询：学生bristol英国预科，一门挂科，均分50%，可以申请monash本科直录吗？",
    "想问下老师悉尼大学 25 S1，master of media practice，我看信息说要8.26日前接受offer，如果学生语言成绩还未达标，是否有资格缴费接受占位置呢，语言未达标只缴费这样算接受offer吗  谢谢",
    "英国布里斯托大学 51分 法律本科 22学位 40分及格 申请澳洲那个学校可以 2025年2月入学",
    "咨询UTS COLLEGE国际大一课程录取要求，学生英国预科Bristol提供的课程，目前成绩：学术写作61，text response 60, foundations of statistis 52, psychology 29(挂科）， biomedical sciences 28（挂科）， 均分46%， 要申请Diploma of Business.可以办理吗？",
    "请问墨大开学前提出退费可以退还多少的押金?",
    "在澳洲护理读下来去美国加拿大通用么？",
    "老师，这个学生加读的语言课7.22开课，上期语言课6.28结课，现在学校因为他签证处理问题不能入读，签证中心也是要求他联系之前递交签证的邮箱账号去联系处理，这种情况学生签证是属于非法滞留了吗？想要继续留在新西兰读书应该怎么操作呢？辛苦您给下建议",
    "悉尼大学关于2025年第一学期MDCC数字通信(和嵌入式)Master of Digital Communication and Culture硕士课程接受信息（8月21日前）",
    "UTS言语治疗硕士2025年入学是否接受莫纳什online课程？",
    "老师 ，请问下24年12月底 有高三上5学期成绩单+在读证明 递交悉大/新南/昆大/莫纳什的本科直读，26年2月入学，学校可以先出条件offer吗？",
    "老师，之前看到很多人发新南威尔士大学现在要求学生提供毕业证学位证和成绩单学信网认证，那今年9月入学的学生需要现在做么？学生没有收到邮件通知。另外申请25年入学的大三学生现在也做不了认证吧？",
    "新南Bachelor of Materials Science & Engineering (Honours) /Master of Biomedical Engineering针对BC省的录取要求是？",
]


# 定义发送请求的函数
def send_request():
    # 随机选择一个问题
    random_question = random.choice(study_abroad_questions)

    conn = http.client.HTTPSConnection("u430182-ac52-9e557856.cqa1.seetacloud.com")
    payload = json.dumps({
        "model": "/root/autodl-tmp/llm/Qwen2-72B-Instruct-GPTQ-Int4",
        "query": random_question,
        "stream": False
    })
    headers = {
        'Authorization': '1001',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'u430182-ac52-9e557856.cqa1.seetacloud.com',
        'Connection': 'keep-alive'
    }
    try:
        conn.request("POST", "/knowledge_base/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
    except Exception as e:
        print(f"Request failed: {e}")
    finally:
        conn.close()


# 定义定时循环发送请求的函数
def periodic_request():
    while True:
        # 随机生成1到10个线程
        num_requests = random.randint(1, 40)
        threads = []
        for _ in range(num_requests):
            thread = threading.Thread(target=send_request)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 随机等待 5 到 10 秒
        time.sleep(random.randint(20, 30))


# 启动定时请求
periodic_request()
