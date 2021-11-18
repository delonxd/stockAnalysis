from request.requestData import request_data2mysql
from method.mainMethod import get_part_codes

from method.dataMethod import load_df_from_mysql
from method.dataMethod import DataAnalysis

import json
import time
import pickle
import numpy as np
import pandas as pd
import datetime as dt


def daily_update():
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

    # with open("..\\bufferData\\codes\\blacklist.txt", "r", encoding="utf-8", errors="ignore") as f:
    #     blacklist = json.loads(f.read())

    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    # code_list = get_part_codes(code_list, blacklist=blacklist)
    # code_list = get_part_codes(code_list)

    length = len(code_list)
    print(length)

    # start = code_list.index('600000')
    start = 3
    end = 4

    res_list = list()

    today = dt.date.today().strftime("%Y-%m-%d")

    columns = [
        's_001_roe',
        # 's_002_equity',
        's_003_profit',
        's_004_pe',
        # 's_005_stocks',
        # 's_006_stocks_rate',
        # 's_007_asset',
        # 's_007_asset',
        # 's_008_revenue',
        's_009_revenue_rate',
        # 's_010_main_profit',
        # 's_011_main_profit_rate',
        # 's_012_return_year',
        # # 's_013_noc_asset',
        # 's_014_pe2',
        # 's_015_return_year2',
    ]

    index = start
    while index < end:
        code = code_list[index]
        print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())))
        print(index, '-->', code)

        df1 = load_df_from_mysql(code, 'fs')
        d0 = '' if df1.shape[0] == 0 else df1.iloc[-1, :]['last_update'][:10]

        if d0 < today:
            request_data2mysql(
                stock_code=code_list[index],
                data_type='fs',
                start_date='2021-04-01',
            )

        df2 = load_df_from_mysql(code, 'mvs')
        d0 = '' if df2.shape[0] == 0 else df2.iloc[-1, :]['last_update'][:10]
        if d0 < today:
            request_data2mysql(
                stock_code=code_list[index],
                data_type='mvs',
                start_date='2021-04-01',
            )

        data = DataAnalysis(df1, df2)
        data.config_widget_data()

        df = data.df[columns].copy()
        res_list.append(df)

        index += 1

    file = 'res_daily_%s.pkl' % timestamp
    with open("../basicData/dailyUpdate/%s" % file, "wb") as f:
        pickle.dump(res_list, f)

    ####################################################################################################

    dict0 = dict()
    for index, df in enumerate(res_list):

        code = code_list[index]

        roe = df['s_001_roe'].copy().dropna()
        a1 = roe[roe.index.values > '2019-06-01']

        flg = False

        if code[0] == '0' or code[0] == '6':
            if code[:3] != '688':
                flg = True

        for x in a1:
            if x < 0.13:
                flg = False
                # print(a)
                break

        pe = df['s_004_pe'].copy().dropna()
        if pe.size == 0:
            flg = False
        else:
            x = pe[-1]
            if x > 22:
                flg = False

        if a1.size == 0 or flg is False:
            dict0[code] = np.nan
        else:
            dict0[code] = a1[-1]

        # print(dict0[key])

    s1 = pd.Series(dict0)
    s1.dropna(inplace=True)
    s2 = s1.sort_values(ascending=False)

    print(s2)
    print(s2.size)

    code_list = s2.index.tolist()

    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    file = 'sift_daily_%s.txt' % timestamp
    with open("../basicData/dailyUpdate/%s" % file, "w", encoding='utf-8') as f:
        f.write(res)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    daily_update()