import datetime as dt
import json
import pandas as pd
from method.urlMethod import data_request
from method.fileMethod import *


def request_mir_y10():
    MainLog.add_split('#')

    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    url = 'https://open.lixinger.com/api/macro/national-debt'

    start = dt.date(dt.date.today().year - 9, 1, 1)
    end = dt.date.today()

    data = []

    while True:
        api = {
            "token": token,
            "areaCode": "cn",
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
            "metricsList": ["tcm_y10"],
        }

        res = data_request(url=url, api_dict=api)
        tmp = json.loads(res.decode())['data']
        if len(tmp) == 0:
            break
        else:
            start = dt.date(start.year - 10, 1, 1)
            end = dt.date(start.year + 9, 12, 31)
        data.extend(tmp)

    dict0 = dict()
    for row in data:
        date = row['date'][:10]
        value = row['tcm_y10']
        dict0[date] = value

    tmp = json.dumps(dict0, indent=4, ensure_ascii=False)
    with open("..\\basicData\\nationalDebt\\mir_y10.txt", "w", encoding="utf-8") as f:
        f.write(tmp)

    MainLog.add_log('request_mir_y10 complete')
    MainLog.add_split('#')


def load_mir_y10():
    with open("..\\basicData\\nationalDebt\\mir_y10.txt", "r", encoding="utf-8", errors="ignore") as f:
        tmp = json.loads(f.read())
    s1 = pd.Series(tmp)
    s1.name = 'mir_y10'
    print(s1)
    return s1


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 100000)

    request_mir_y10()
    # load_mir_y10()

