from request.requestData import try_request, data_request
from method.fileMethod import load_json_txt
from method.logMethod import MainLog
from method.profileMethod import get_code_profile_df
from method.sqlMethod import df2mysql

import pandas as pd
import datetime as dt
import requests
import time


@try_request(None)
def request_equity_change(code):
    token = load_json_txt("../request/lxr_token.txt", log=False)
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
        data = res['data']
        if len(data) == 0:
            print(code)
            break
        else:
            start = dt.date(start.year - 10, 1, 1)
            end = dt.date(start.year + 9, 12, 31)
        ret.extend(data)

    # print(config_equity_change_data(data))
    return ret


def request_equity_change_hk(code) -> pd.DataFrame | None:
    time.sleep(1)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/135.0.0.0 Safari/537.36"
    }

    area = code[:2]
    if area != 'hk':
        return

    symbol = code[3:] + '.HK'

    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    params = {
        "reportName": "RPT_HKF10_INFO_EQUITY",
        "columns": "SECUCODE,CHANGE_DATE,TOTAL_SHARES,HK_SHARES,CHANGE_REASON,NOTICE_DATE",
        "quoteColumns": "",
        "filter": f'(SECUCODE="{symbol}")',
        "pageNumber": "1",
        "pageSize": "",
        "sortTypes": "-1",
        "sortColumns": "NOTICE_DATE",
        "source": "F10",
        "client": "PC",
        "v": "034881457840342045"
    }
    r = requests.get(url, params=params, headers=headers)
    data_json = r.json()

    res = data_json.get("result")
    if res is None:
        return

    df = pd.DataFrame(data_json['result']['data'])

    df['CHANGE_DATE'] = df['CHANGE_DATE'].str[:10]
    df['NOTICE_DATE'] = df['NOTICE_DATE'].str[:10]
    df['date'] = df['CHANGE_DATE']
    df = df.sort_values('date')
    return df


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


def request_eq2mysql_cn(stock_codes: list = None, ini=False):

    if stock_codes is None:
        df = get_code_profile_df()
        df = df[df['area'] == 'cn']
        stock_codes = df.index.to_list()

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

    # request_equity_change_hk('hk-00003')
    pass
