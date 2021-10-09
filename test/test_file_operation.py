import time
import os
import datetime as dt


def get_file_list(path):

    path = str(path)

    if path == "":
        return []

    path = path.replace("/", "\\")

    if path[-1] != "\\":
        path = path + "\\"

    list0 = os.listdir(path)

    res = [x for x in list0 if os.path.isfile(path + x)]

    return res


def get_create_time(filePath):
    t = os.path.getctime(filePath)
    return t


if __name__ == '__main__':
    path = '..\\bufferData\\FinancialData\\'

    file_list = [x for x in os.listdir(path) if os.path.isfile(path + x)]

    date0 = dt.date(2021, 9, 10)

    res_list = list()
    for file in file_list:
        file_path = '/'.join([path, file])
        t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
        delta = (t0.date() - date0).days
        if delta > 0:
            print(type(t0), t0)
            res_list.append(file)

    startTime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

    print(type(startTime), '-->', startTime)
    print(res_list)