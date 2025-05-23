from request.requestData import *
from method.fileMethod import *

import datetime as dt
import json
import pandas as pd


@try_request(None)
def request_equity_change(code):
    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    url = 'https://open.lixinger.com/api/cn/company/equity-change'

    ret = []

    start = dt.date(dt.date.today().year - 9, 1, 1)
    end = dt.date.today()

    while True:
        api = {
            "token": token,
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
            "stockCode": code,
        }

        res = data_request(url=url, api_dict=api)
        data = json.loads(res.decode())['data']
        if len(data) == 0:
            break
        else:
            start = dt.date(start.year - 10, 1, 1)
            end = dt.date(start.year + 9, 12, 31)
        ret.extend(data)

    # print(config_equity_change_data(data))
    return ret


def eq_res2dataframe(data):
    res = []
    for row in data:
        date = row['date'][:10]

        cap0 = row.get('capitalization')
        cap1 = row.get('outstandingSharesA')
        cap2 = row.get('limitedSharesA')

        cap0 = 0 if cap0 is None else cap0
        cap1 = 0 if cap1 is None else cap1
        cap2 = 0 if cap2 is None else cap2
        cap3 = cap0 - cap1 - cap2

        reason = row.get('changeReason')
        # res.append([date, cap0, cap1, cap2, cap3, dict0.get(reason)])
        res.append([date, cap0, cap1, cap2, cap3, reason])

    res.reverse()
    last = None
    res2 = []

    ipo_rate = 1
    ipo_date = ''
    for row in res:
        if last:
            d1 = row[1] - last[1]
            d2 = row[2] - last[2]
            d3 = row[3] - last[3]
            d4 = row[4] - last[4]

            rate = row[1] / last[1]
            # if row[5] == 'dividend' or row[5] == 'split':
            if row[5] == '送、转股' or row[5] == '拆分':
                rate = 1.0

            tmp = last[10]*rate
            if row[5] == 'IPO' and ipo_date == '':
                ipo_rate = tmp
                ipo_date = row[0]

            new = [*row, d1, d2, d3, d4, tmp, round(rate, 4)]
            if new[0] == last[0]:
                d1 = last[6] + new[6]
                d2 = last[7] + new[7]
                d3 = last[8] + new[8]
                d4 = last[9] + new[9]
                r1 = new[10]
                r2 = round(last[11] * new[11], 4)
                res2[-1] = [*row, d1, d2, d3, d4, r1, r2]
            else:
                res2.append(new)
        else:
            if row[5] == 'IPO' and ipo_date == '':
                ipo_rate = 1
                ipo_date = row[0]

            d1 = row[1]
            d2 = row[2]
            d3 = row[3]
            d4 = row[4]
            new = [*row, d1, d2, d3, d4, 1, 1]
            res2.append(new)
        last = res2[-1]

    data_list = []
    for row in res2:
        date = row[0]
        dilution_val = row[10] / ipo_rate

        if ipo_date != '':
            date1 = dt.datetime.strptime(date, "%Y-%m-%d").date()
            date2 = dt.datetime.strptime(ipo_date, "%Y-%m-%d").date()
            delta = (date1 - date2).days
            if delta <= 0:
                dilution_rate = 1
            else:
                dilution_rate = dilution_val ** (365 / delta)
            dilution_rate = (dilution_rate - 1) * 100
        else:
            dilution_rate = 0

        data_list.append([
            row[0], row[5], round(dilution_val, 4), row[11],
            row[1], row[2], row[3], row[4],
            row[6], row[7], row[8], row[9], round(dilution_rate, 4)
        ])

    path = '../basicData/chineseComparison/zh_cmp_table_eq_cn.txt'
    src = load_json_txt(path, log=False)
    columns = list(src.values())

    df = pd.DataFrame(data_list, columns=columns[2:])
    df = df.reindex(columns, axis=1)
    return df


def request_eq2mysql(stock_codes, ini=False):
    for code in stock_codes:
        res = request_equity_change(code)
        df = eq_res2dataframe(res)
        table = 'eq_%s' % code
        df2mysql(
            df=df,
            database='eqData',
            table=table,
            ini=ini,
        )
        MainLog.add_split('-')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # list1 = load_json_txt("..\\basicData\\self_selected\\gui_whitelist.txt")
    # list2 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")
    # list3 = list(set(list1 + list2))
    # request_eq2mysql(list3)
    code_list = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
    request_eq2mysql(code_list)
    # request_eq2mysql(['002594'])
    pass
