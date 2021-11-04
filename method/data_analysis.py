from method.dataMethod import load_df_from_mysql
from method.dataMethod import get_month_delta
from method.dataMethod import get_month_data
from method.dataMethod import DataAnalysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import json
import pickle


def func(x, a, b):
    return a * x + b


def potential_rate(arr_y):
    arr_x = np.arange(0, arr_y.size, 1)
    p = np.polyfit(arr_x, arr_y, 2)
    q = np.polyder(p)

    r1 = np.polyval(q, arr_y[-1])
    r2 = arr_y[-1] - arr_y[-2]

    weight = 0

    rate = r1 * (1 - weight) + r2 * weight
    print(arr_y)
    print(rate)
    return rate


def potential_delta(arr_y, n, delay):
    x1 = arr_y.size - 1
    x2 = x1 + delay

    arr_x = np.arange(0, arr_y.size, 1)
    p = np.polyfit(arr_x, arr_y, n)
    delta = np.polyval(p, x2) - np.polyval(p, x1)

    print(arr_y)
    print(delta)
    return delta


def test_window(arr_y):
    tmp = np.where(np.isnan(arr_y))[0]
    if tmp.size > 0:
        index = tmp[-1] + 1
        arr_y = arr_y[index:]
        sample_min = 12
    else:
        sample_min = 2

    arr_x = np.arange(0, arr_y.size, 1)
    if arr_x.size < sample_min:
        return np.nan

    # delta = potential_delta(arr_y, 6, 4)
    delta = potential_rate(arr_y) * 4
    return delta


def test_analysis01():
    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    mysql_index = 'id_211_ps_np'
    data_type = 'fs'

    res_df = pd.DataFrame()

    start = 1
    for index, stock_code in enumerate(code_list[start:start+1]):
        print(index, '-->', stock_code)
        df = load_df_from_mysql(stock_code, data_type)
        data = df.loc[:, [mysql_index]]
        data.dropna(inplace=True)
        data2 = get_month_delta(data, mysql_index)
        data3 = data2.rolling(4, min_periods=1).mean()
        data4 = np.log(data3)
        data5 = data4.rolling(12, min_periods=1).apply(test_window, raw=True)
        data6 = (np.exp(data5) - 1) * 10
        data6.columns = [stock_code]
        # print(data6)

        # res_df = pd.merge(res_df, data6, how='outer', left_index=True, right_index=True,
        #                   sort=True, suffixes=('_1', '_2'), copy=True)

        # res_df = pd.concat([res_df, data6], axis=1, sort=True)

        # print(res_df)

        # print(res_df)
        arr_y = data4.iloc[:, 0].values
        arr_y2 = data6.iloc[:, 0].values

        arr_x = np.arange(0, arr_y.size, 1)

        # plt.plot(arr_x, arr_y, '.-', label='original values')

        plt.plot(arr_x, arr_y, 'b-', label='original values')
        plt.plot(arr_x, arr_y2, 'r-', label='original values')
        # plt.plot(arr_x, yvals, 'r', label='log_fit values')

        plt.xlabel('x axis')
        plt.ylabel('y axis')

        plt.title('curve_fit')
        plt.show()
        # plt.savefig('p2.png')

    # with open("../basicData/analyzedData/jlr_rate.pkl", "wb") as f:
    #     pickle.dump(res_df, f)


def test_window_roe(arr_y):
    tmp = np.where(np.isnan(arr_y))[0]
    if tmp.size > 0:
        index = tmp[-1] + 1
        arr_y = arr_y[index:]

    if arr_y.size == 0:
        return np.nan

    if arr_y.size < 2:
        return arr_y[-1]

    arr_x = np.arange(0, arr_y.size, 1)
    p = np.polyfit(arr_x, arr_y, 1)
    res = np.polyval(p, (arr_y.size - 1))

    return res
    # return np.nan


def test_analysis():
    import time
    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    data_type = 'fs'

    res_df = pd.DataFrame()

    length = len(code_list)
    print(length)
    start = 0
    end = length

    res_dict = dict()
    index = start
    while index < end:
        stock_code = code_list[index]
        # print(index, '-->', stock_code)
        print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())))
        print(index)
        # df = load_df_from_mysql(stock_code, data_type)
        # data = DataAnalysis(df, None)

        df1 = load_df_from_mysql(stock_code, 'fs')
        df2 = load_df_from_mysql(stock_code, 'mvs')
        data = DataAnalysis(df1, df2)
        data.config_widget_data()
        # res = data.df_mvs

        # revenue = data.get_revenue()
        # revenue_rate = data.get_growth_rate(revenue, stock_code)
        #
        # res = data.config_sub_fs()
        # res_dict[stock_code] = res

        # revenue_rate = res['s_012_return_year'].copy().dropna()
        # print(revenue_rate)

        # revenue_rate.name = stock_code
        #
        # res_df = pd.concat([res_df, revenue_rate], axis=1, sort=True)

        a1 = data.df['s_004_pe'].copy().dropna()
        a2 = data.df['s_012_return_year'].copy().dropna()
        a3 = data.df['s_014_pe2'].copy().dropna()
        a4 = data.df['s_015_return_year2'].copy().dropna()

        res_dict[stock_code] = (a1, a2, a3, a4)
        index += 1

        # print(res_df)

    # with open("../basicData/analyzedData/return_year.pkl", "wb") as f:
    #     pickle.dump(res_df, f)

    with open("../basicData/analyzedData/res_dict.pkl", "wb") as f:
        pickle.dump(res_dict, f)


def test_read():
    with open("../basicData/analyzedData/revenue_rate2.pkl", "rb") as f:
        res_df = pickle.load(f)

    a = res_df.loc[['2021-03-31', '2021-06-30', '2021-09-30'], :]
    a.fillna(method='pad', axis=0, inplace=True)
    a = a.iloc[-1, :]
    # a.dropna(inplace=True)
    b = a.sort_values(ascending=False)
    print(b)
    code_list = b.index.tolist()
    # print(code_list)

    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    with open("../basicData/analyzedData/revenue_rate_codes3.txt", "w", encoding='utf-8') as f:
        f.write(res)


def test_read2():
    with open("../basicData/analyzedData/return_year.pkl", "rb") as f:
        res_dict = pickle.load(f)

    # code_list = list()
    dict0 = dict()
    for key, value in res_dict.items():
        # s1 = value['s_003_profit'].copy().dropna()
        a = value[value.index.values > '2021-06-01']

        if a.size > 0:
            dict0[key] = a[-1]
        else:
            dict0[key] = np.nan

        # print(dict0[key])

    s1 = pd.Series(dict0)
    s2 = s1.sort_values(ascending=True)
    print(s2)
    code_list = s2.index.tolist()

        # b = a > 0
    #     if False in b:
    #         code_list.append(key)
    #         print(key)
    #
    # print(len(code_list))
    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    with open("../basicData/analyzedData/return_year_codes.txt", "w", encoding='utf-8') as f:
        f.write(res)


def show_data_jlr():
    with open("../basicData/analyzedData/jlr_codes.txt", "r", encoding='utf-8') as f:
        code_list = json.loads(f.read())

    mysql_index = 'id_211_ps_np'
    data_type = 'fs'
    stock_code = code_list[28]

    print(stock_code)

    df = load_df_from_mysql(stock_code, data_type)
    data = df.loc[:, [mysql_index]]
    data.dropna(inplace=True)
    # a = data[:, ['sss']]
    # print(data)
    data2 = get_month_delta(data, mysql_index)
    data3 = data2.rolling(4, min_periods=1).mean()
    data4 = np.log(data3)
    # print(data4)

    data5 = data4.rolling(12, min_periods=1).apply(test_window, raw=True)

    data6 = (np.exp(data5 * 4) - 1) * 10
    data6.columns = [stock_code]

    print(data6 * 10)

    arr_y = data4.iloc[:, 0].values
    arr_y2 = data6.iloc[:, 0].values

    arr_x = np.arange(0, arr_y.size, 1)

    # plt.plot(arr_x, arr_y, '.-', label='original values')

    plt.plot(arr_x, arr_y, 'b-', label='original values')
    plt.plot(arr_x, arr_y2, 'r-', label='original values')
    # plt.plot(arr_x, yvals, 'r', label='log_fit values')

    plt.xlabel('x axis')
    plt.ylabel('y axis')

    plt.title('curve_fit')
    plt.show()
    # plt.savefig('p2.png')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)
    test_analysis()

    # with open("../basicData/analyzedData/res_dict.pkl", "rb") as f:
    #     res_dict = pickle.load(f)
    # print(res_dict)
    # test_read()
    # test_read2()
    # show_data_jlr()
