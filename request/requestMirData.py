import datetime as dt
import json
import pandas as pd
from method.urlMethod import data_request


def request_mir_y10():
    token = "e7a7f2e5-181b-4caa-9142-592ab6787871"
    today = dt.date.today().strftime("%Y-%m-%d")
    url = 'https://open.lixinger.com/api/macro/national-debt'
    api = {
        "token": token,
        "areaCode": "cn",
        "startDate": "1970-01-01",
        "endDate": today,
        "metricsList": ["mir_y10"],
    }

    res = data_request(url=url, api_dict=api)
    data = json.loads(res.decode())['data']

    dict0 = dict()
    for row in data:
        date = row['date'][:10]
        value = row['mir_y10']
        dict0[date] = value

    tmp = json.dumps(dict0, indent=4, ensure_ascii=False)
    with open("..\\basicData\\nationalDebt\\mir_y10.txt", "w", encoding="utf-8") as f:
        f.write(tmp)


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

    # request_mir_y10()
    load_mir_y10()

