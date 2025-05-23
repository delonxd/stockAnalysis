from request.requestData import *
from method.fileMethod import *

import datetime as dt
import json
import pandas as pd


@try_request(None)
def request_dividend(code, ipo_date=None):
    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    url = 'https://open.lixinger.com/api/cn/company/dividend'

    ret = []

    start = dt.date(dt.date.today().year - 9, 1, 1)
    end = dt.date.today()

    if ipo_date is not None:
        ipo_date = dt.datetime.strptime(ipo_date[:10], "%Y-%m-%d").date()
        ipo_date = dt.date(ipo_date.year - 7, 1, 1)

    while True:
        api = {
            "token": token,
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
            "stockCode": code,
        }

        res = data_request(url=url, api_dict=api)
        data = json.loads(res.decode())['data']

        if ipo_date is None:
            if len(data) == 0:
                break
        else:
            if end < ipo_date:
                break

        if not len(data) == 0:
            ret.extend(data)

        start = dt.date(start.year - 10, 1, 1)
        end = dt.date(start.year + 9, 12, 31)

    # print(config_equity_change_data(data))
    return ret


def dv_res2dataframe(data):

    path = '../basicData/chineseComparison/zh_cmp_table_dv_cn.txt'
    src = load_json_txt(path, log=False)
    columns = list(src.values())

    df = pd.DataFrame().from_dict(data, orient='columns')

    if 'dividendAmount' in df.columns:
        df['originalValue'] = df['dividendAmount']
    df = df.reindex(columns, axis=1)

    s1 = df['date'].map(lambda x: x[:10])
    if s1.is_unique is False:
        tmp = dict()
        s2 = list()
        for date in s1:
            if date in tmp:
                num = tmp.get(date)
                tmp[date] = num + 1
                s2.append(date + '_' + str(num+1))
            else:
                tmp[date] = 0
                s2.append(date)
        s1 = pd.Series(s2)
    df['id'] = s1
    return df


def request_dv2mysql(stock_codes, ini=False):
    ipo_dates = load_json_txt('..\\basicData\\ipo_date.txt')
    for code in stock_codes:
        res = request_dividend(code, ipo_date=ipo_dates.get(code))
        df = dv_res2dataframe(res)
        table = 'dv_%s' % code
        df2mysql(
            df=df,
            database='dvData',
            table=table,
            ini=ini,
        )
        MainLog.add_split('-')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 3)
    pd.set_option('display.width', 10000)

    # list1 = load_json_txt("..\\basicData\\self_selected\\gui_whitelist.txt")
    # list2 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")
    # list3 = list(set(list1 + list2))
    list1 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
    request_dv2mysql(list1)
    # request_dv2mysql(['600007'])
    # request_dv2mysql(['600071'])
    pass
