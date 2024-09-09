import re
from pypinyin import lazy_pinyin


# 判断是否为纯中文
def is_all_chinese(text):
    """中文的 Unicode 范围为 \u4e00-\u9fff"""
    return all(re.match(r"[\u4e00-\u9fff]", char) for char in text)


# 将中文转换为拼音
def chinese_to_pinyin(text) -> list:
    """使用 pypinyin 将中文字符转换为拼音"""
    return lazy_pinyin(text)
