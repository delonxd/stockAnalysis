from request.requestData import request_data2mysql
from method.logMethod import MainLog
import json
import time
import datetime as dt


def auto_update():

    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    length = len(code_list)
    index = 0

    today = dt.datetime.today()
    start_date = (today - dt.timedelta(days=5)).strftime("%Y-%m-%d")

    time0 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    log_path = '../bufferData/logs/auto_update/update_log_%s.txt' % time0

    while index < length:
        try:
            code = code_list[index]

            log_str = 'start request: index --> %s, code --> %s' % (index, code)
            MainLog.add_log(log_str)

            new_data1 = request_data2mysql(
                stock_code=code,
                data_type='fs',
                start_date=start_date,
            )
            MainLog.add_log('-'*150)

            new_data2 = request_data2mysql(
                stock_code=code,
                data_type='mvs',
                start_date=start_date,
            )
            MainLog.add_log('-'*150)

            index += 1
        except Exception as e:
            log_str = 'index --> %s\n%s\n' % (index, e)
            MainLog.add_log(log_str)
            time.sleep(5)
        finally:
            MainLog.write_add(log_path)
            MainLog.init_log()


if __name__ == '__main__':
    auto_update()
