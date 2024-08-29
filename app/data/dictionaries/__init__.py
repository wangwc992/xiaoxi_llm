import os

stopword_words = set()
sensitive_words = set()
school_abbreviations = list()


def _get_abs_path(path):
    # 将相对路径转换为绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, path)
    return file_path


def load_dictionaries(words, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        # self.stopwords 追加 set([line.strip() for line in f])
        words.update(set([line.strip() for line in f]))

# 加载停用词
load_dictionaries(stopword_words, _get_abs_path('stopwords/scu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/cn_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/hit_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/scu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/baidu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/english'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/chinese'))

# 加载敏感词
load_dictionaries(sensitive_words, _get_abs_path('sensitive/广告.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/政治类.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/涉枪涉爆违法信息关键词.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/网址.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/色情类.txt'))
sensitive_words.remove('')

with open(_get_abs_path("dictionary/school_abbreviation"), 'r', encoding='utf-8') as f:
    lines = f.readlines()
    # 使用 , 分割,去除前后空格，去除换行符
    school_abbreviations = [line.strip().split(",") for line in lines]
