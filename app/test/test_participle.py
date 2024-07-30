import re
import jieba
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


def to_keywords(input_string):
    """将句子转成检索关键词序列"""
    jieba.add_word("经济学硕士")
    jieba.add_word("pte成绩")
    # 按搜索引擎模式分词
    word_tokens = jieba.cut_for_search(input_string)
    # 加载停用词表
    stop_words = set(stopwords.words('chinese'))
    # 去除停用词
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return ' '.join(filtered_sentence)
def to_keywords2(input_string):
    sentence = "北京大学生前来报到"

    # 未调整前的分词结果
    print("未调整前: " + "/".join(jieba.cut(sentence)))  # 输出: 北京大学/生/前来/报到

    # 调整词频，确保 "北京大学" 被分开
    jieba.suggest_freq('北京大学', tune=1000)

    # 调整后的分词结果
    print("调整后 (北京大学分开): " + "/".join(jieba.cut(sentence)))  # 输出: 北京/大学/生/前来/报到

    # 再次调整词频，确保 "大学生" 被合并
    jieba.suggest_freq('大学生', tune=10000)

    # 调整后的分词结果
    print("调整后 (大学生合并): " + "/".join(jieba.cut(sentence)))  # 输出: 北京/大学生/前来/报到

def sent_tokenize(input_string):
    """按标点断句"""
    # 按标点切分
    sentences = re.split(r'(?<=[。！？；?!])', input_string)
    # 去掉空字符串
    return [sentence for sentence in sentences if sentence.strip()]


def jieba_cut(text):
    words = jieba.cut(text, cut_all=False)
    # print("精确模式: " + "/".join(words))

    # 全模式
    words = jieba.cut(text, cut_all=True)
    # print("全模式: " + "/".join(words))

    # 搜索引擎模式
    words = jieba.cut_for_search(text)
    print("搜索引擎模式: " + "/".join(words))
if "__main__" == __name__:
    text= "因为2025年s1经济学硕士语言班满位了 如果学生考不到直读的需要成绩 可以申请2025年s2的语言+正课打包offer么？最晚几月份申请才能确保语言班有位置呢？ 另外目前她pte成绩是59（听力59 阅读52 口语57 写作69）请问配语言班的话要配多少周的呢"
    # 测试关键词提取
    # print(to_keywords(text))
    to_keywords2(text)
    # 测试断句
    # print(sent_tokenize("这是，第一句。这是第二句吗？是的！啊"))
    # jieba_cut(text)