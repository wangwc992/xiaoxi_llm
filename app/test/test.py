from datetime import datetime

now = datetime.now()
print(now.strftime('%Y-%m-%d %H:%M:%S') + f".{now.microsecond // 1000:03d}")