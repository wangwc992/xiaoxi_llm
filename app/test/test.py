import re
from pypinyin import lazy_pinyin

# 判断是否为纯中文
def is_all_chinese(text):
    # 中文的 Unicode 范围为 \u4e00-\u9fff
    return all(re.match(r"[\u4e00-\u9fff]", char) for char in text)

# 将中文转换为拼音
def chinese_to_pinyin(text):
    # 使用 pypinyin 将中文字符转换为拼音
    return lazy_pinyin(text)

# 示例
text = "张若尘"
if is_all_chinese(text):
    print("是纯中文")
    pi_yin_list = chinese_to_pinyin(text)
    fast_name = pi_yin_list[0]
    # 第二个往后取出来拼接
    last_name = ''.join(pi_yin_list[1:])
    print(fast_name, last_name)
else:
    print("不是纯中文")
