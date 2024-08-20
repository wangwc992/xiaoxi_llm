# 在一个独立线程中启动 Binlog 监听
import threading

from app.start_init.mysql_binglog_monitoring import start_binlog_listener

binlog_thread = threading.Thread(target=start_binlog_listener)
binlog_thread.daemon = True  # 设为守护线程，主程序退出时该线程自动结束
binlog_thread.start()

# 继续执行主线程的其他代码
print("主程序继续启动，不会被阻塞")
