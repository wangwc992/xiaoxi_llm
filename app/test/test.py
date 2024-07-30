import jieba
import os

class CustomJieba:
    def __init__(self):
        self.lock = jieba.Tokenizer().lock
        self.dictionary = jieba.default_logger
        self.initialized = True

    def set_dictionary(self, dictionary_path):
        with self.lock:
            abs_path = self._get_abs_path(dictionary_path)
            if not os.path.isfile(abs_path):
                raise Exception("jieba: file does not exist: " + abs_path)
            self.dictionary = abs_path
            self.initialized = False

    def _get_abs_path(self, path):
        # 将相对路径转换为绝对路径
        return os.path.abspath(path)

# 示例用法
custom_jieba = CustomJieba()

# 设置自定义词典路径
dictionary_path = "dictionary.txt"
# custom_jieba.set_dictionary(dictionary_path)

# 使用自定义词典进行分词
jieba.load_userdict(dictionary_path)

sentence = "北京大学生前来报到"
print("未调整前:", "/".join(jieba.cut(sentence)))  # 未使用自定义词典的分词结果

# 使用 jieba.suggest_freq 调整词频
jieba.suggest_freq('北京大学', tune=True)  # 提升 "北京大学" 的频率
print("调整后 (北京大学分开):", "/".join(jieba.cut(sentence)))  # 分词结果

jieba.suggest_freq('大学生', tune=True)  # 提升 "大学生" 的频率
print("调整后 (大学生合并):", "/".join(jieba.cut(sentence)))  # 分词结果
