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


def test_analysis():
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


def test_analysis_roe():
    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    data_type = 'fs'

    res_df = pd.DataFrame()

    length = len(code_list)
    start = 0
    end = length

    index = start
    while index < end:
        stock_code = code_list[index]
        print(index, '-->', stock_code)
        df = load_df_from_mysql(stock_code, data_type)
        data = DataAnalysis(df, None)

        revenue = data.get_revenue()
        revenue_rate = data.get_growth_rate(revenue, stock_code)

        res_df = pd.concat([res_df, revenue_rate], axis=1, sort=True)
        index += 1

        # print(res_df)

    with open("../basicData/analyzedData/revenue_rate.pkl", "wb") as f:
        pickle.dump(res_df, f)


def test_read():
    with open("../basicData/analyzedData/revenue_rate.pkl", "rb") as f:
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
    with open("../basicData/analyzedData/revenue_rate_codes.txt", "w", encoding='utf-8') as f:
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
    # 显示所有列
    pd.set_option('display.max_columns', None)
    # 显示所有行
    pd.set_option('display.max_rows', None)
    # # 设置value的显示长度为100，默认为50
    # pd.set_option('max_colwidth', 100)
    # test_analysis()
    # test_analysis_roe()
    # test_analysis_roe()
    test_read()
    # show_data_jlr()
