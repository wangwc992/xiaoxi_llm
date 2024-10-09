import os
import re

import jieba


class JiebaTool:
    def __init__(self):
        self.lock = jieba.Tokenizer().lock
        self.dictionary = jieba.default_logger
        self.initialized = False
        self.stopwords = set()
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/stopwords.txt'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/english'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/chinese'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/hit_stopwords.txt'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/cn_stopwords.txt'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/baidu_stopwords.txt'))
        self.load_stopwords(self._get_abs_path('../../data/dictionaries/stopwords/scu_stopwords.txt'))

    def initialize(self):
        with self.lock:
            if not self.initialized:
                jieba.initialize()  # 初始化 jieba
                self.initialized = True

    def load_stopwords(self, filepath):
        with self.lock:
            self.initialize()
            with open(filepath, 'r', encoding='utf-8') as f:
                # self.stopwords 追加 set([line.strip() for line in f])
                self.stopwords.update(set([line.strip() for line in f]))

    def cut(self, text) -> list:
        """精确模式
        详细说明：对句子进行分词，精确模式，返回一个列表
        """
        with self.lock:
            self.initialize()
            words = jieba.lcut(text)
            return [word for word in words if word not in self.stopwords]

    def cut_for_search(self, text) -> list:
        """搜索引擎模式
        详细说明：对句子进行分词，搜索引擎模式，返回一个列表
        """
        with self.lock:
            self.initialize()
            words = jieba.cut_for_search(text)
            return [word for word in words if word not in self.stopwords and len(word) > 1]

    def lcut_for_search(self, text) -> list:
        """搜索引擎模式
        详细说明：对句子进行分词，搜索引擎模式，返回一个列表
        """
        with self.lock:
            self.initialize()
            words = jieba.lcut_for_search(text)
            return [word for word in words if word not in self.stopwords]

    def add_word(self, word):
        with self.lock:
            self.initialize()
            jieba.add_word(word)

    def remove_word(self, word):
        with self.lock:
            self.initialize()
            jieba.del_word(word)

    def load_userdict(self, filepath):
        with self.lock:
            self.initialize()
            jieba.load_userdict(filepath)

    def _get_abs_path(self, path):
        # 将相对路径转换为绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, path)
        return file_path

    @staticmethod
    def chinese_sent_tokenize(text):
        sentences = re.split(r'(?<=[。！？；?!])', text)
        # 去掉空字符串
        return [sentence for sentence in sentences if sentence.strip()]


# 使用示例
jieba_tool = JiebaTool()

if __name__ == "__main__":
    text = "悉尼大学的免申请费活动怎么样才可以申请呢？ 有什么条件吗？"
    print(jieba_tool.cut(text))
    print(jieba_tool.cut_for_search(text))
    print(jieba_tool.lcut_for_search(text))
