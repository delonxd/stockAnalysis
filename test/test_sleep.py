import time

for i in range(10):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))) #格式化时间
    time.sleep(0.2)