from app.common.utils.jieba_utils import jieba_tool

# Use ' '.join(x) to join the list elements into a single string with spaces
x = jieba_tool.cut_for_search("萨里大学电影、动画与数字艺术Film, Animation and Digital Arts MA")
print(' '.join(x))