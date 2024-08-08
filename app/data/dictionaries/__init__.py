import os

stopword_words = set()
sensitive_words = set()


def _get_abs_path(path):
    # 将相对路径转换为绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, path)
    return file_path


def load_dictionaries(words, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        # self.stopwords 追加 set([line.strip() for line in f])
        words.update(set([line.strip() for line in f]))

# 加载停用词和敏感词
# baidu_stopwords.txt
# chinese
# cn_stopwords.txt
# dictionary.txt
# english
# hit_stopwords.txt
# README.md
# scu_stopwords.txt
# stopwords.txt
load_dictionaries(stopword_words, _get_abs_path('stopwords/scu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/cn_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/hit_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/scu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/baidu_stopwords.txt'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/english'))
load_dictionaries(stopword_words, _get_abs_path('stopwords/chinese'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/广告.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/政治类.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/涉枪涉爆违法信息关键词.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/网址.txt'))
load_dictionaries(sensitive_words, _get_abs_path('sensitive/色情类.txt'))
