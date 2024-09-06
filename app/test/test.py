json_str = "adsf{撒的{发生}的}adsf"
# 找到第一个{的位置 和最后一个}的位置

start = json_str.find("{")
end = json_str.rfind("}")
json_str = json_str[start:end + 1]
print(json_str)
