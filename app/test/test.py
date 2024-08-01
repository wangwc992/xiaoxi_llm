# 定义全局变量
global_var = 0

def increment_global_var():
    global global_var
    for _ in range(1000):
        global_var += 1

# 创建多个线程，尝试修改全局变量
import threading
threads = [threading.Thread(target=increment_global_var) for _ in range(10)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(global_var)  # 输出结果可能小于10000，因为存在竞争条件
