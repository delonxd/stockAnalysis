from request.requestData import *
from method.fileMethod import *
from method.sqlMethod import sql_format_drop_table

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


def config_eq_res(data):
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

    # func = lambda x: '-' if x == 0 else x

    # ipo_rate = 1
    # for row in res:
    #     if last:
    #         d1 = row[1] - last[1]
    #         d2 = row[2] - last[2]
    #         d3 = row[3] - last[3]
    #         d4 = row[4] - last[4]
    #
    #         # if d1 == d2 == d3 == d4 == 0 and row[5] == '定期报告':
    #         if d1 == d2 == d3 == d4 == 0 and row[5] == 'periodicReport':
    #             new = [*row, d1, d2, d3, d4, last[10], 1]
    #             res2.append(new)
    #
    #         else:
    #             rate = row[1] / last[1]
    #             # if row[5] == '送、转股' or row[5] == '拆细':
    #             if row[5] == 'dividend' or row[5] == 'split':
    #                 # if abs(row[2] - last[2] * rate) <= 50:
    #                 #     if abs(row[3] - last[3] * rate) <= 50:
    #                 #         if abs(row[4] - last[4] * rate) <= 50:
    #                 rate = 1.0
    #
    #             tmp = last[10]*rate
    #             if row[5] == 'IPO':
    #                 ipo_rate = tmp
    #             # new = [*row, func(d1), func(d2), func(d3), func(d4), tmp, round(rate, 4)]
    #             new = [*row, d1, d2, d3, d4, tmp, round(rate, 4)]
    #             res2.append(new)
    #     else:
    #         d1 = row[1]
    #         d2 = row[2]
    #         d3 = row[3]
    #         d4 = row[4]
    #
    #         # new = [*row, func(d1), func(d2), func(d3), func(d4), 1, 1]
    #         new = [*row, d1, d2, d3, d4, 1, 1]
    #         res2.append(new)
    #     last = res2[-1]

    ipo_rate = 1
    ipo_date = ''
    for row in res:
        if last:
            d1 = row[1] - last[1]
            d2 = row[2] - last[2]
            d3 = row[3] - last[3]
            d4 = row[4] - last[4]

            rate = row[1] / last[1]
            if row[5] == 'dividend' or row[5] == 'split':
                rate = 1.0

            tmp = last[10]*rate
            if row[5] == 'IPO':
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
            if row[5] == 'IPO':
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

    header_df = get_header_df('eq')
    check_field = 'date'

    res_df = pd.DataFrame(data_list, columns=header_df.columns[2:])
    res_df.set_index(check_field, drop=False, inplace=True)

    return res_df, check_field, header_df


def eq_res2mysql(res, code, ini=False):

    df, check_field, header_df = config_eq_res(res)
    db, cursor = get_cursor('eq')

    table = '%s_%s' % ('eq', code)

    MainLog.add_log('    table --> %s' % table)

    if ini is True:
        cursor.execute(sql_format_drop_table(table))

    header_str = sql_format_header_df(header_df)
    cursor.execute(sql_format_create_table(table, header_str))
    db.commit()

    new_data = update_df2sql(
        cursor=cursor,
        table=table,
        df_data=df,
        check_field=check_field,
        ini=ini,
        # ini=False,
    )

    # if len(new_data.index) == 0:
    #     MainLog.add_log('    new data: None')
    #     return
    # else:
    #     MainLog.add_log('    new data:\n%s' % repr(new_data))

    db.close()

    return new_data


def request_eq2mysql(stock_codes, ini=True):
    for code in stock_codes:
        res = request_equity_change(code)
        eq_res2mysql(res, code, ini)
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
