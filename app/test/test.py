result_format = '''data: {"choices": [ { "index": 0, "delta": { "role": "%s", "content": "%s" }} ]}'''
result = result_format % ("1", "学生姓名为空")
print(result)