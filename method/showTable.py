import pickle
import numpy as np
import json
import os
import pandas as pd
from method.fileMethod import *
import time
import matplotlib.pyplot as plt


def get_recent_val(df, column, default, shift=1):
    series = df.loc[:, column].copy().dropna()
    val = series[-shift] if series.size >= shift else default
    return val


def generate_gui_table():
    df = pd.DataFrame()

    path = "..\\basicData\\self_selected\\gui_blacklist.txt"
    df = add_bool_column(df, path, 'gui_blacklist')

    path = "..\\basicData\\self_selected\\gui_whitelist.txt"
    df = add_bool_column(df, path, 'gui_whitelist')

    path = "..\\basicData\\self_selected\\gui_selected.txt"
    df = add_bool_column(df, path, 'gui_selected')

    path = "..\\basicData\\self_selected\\gui_non_cyclical.txt"
    df = add_bool_column(df, path, 'gui_non_cyclical')

    path = "..\\basicData\\self_selected\\gui_fund.txt"
    df = add_bool_column(df, path, 'gui_fund')

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt")
    for value in res:
        code = value[0]
        df.loc[code, 'gui_hold'] = True

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_remark.txt")
    for key, value in res.items():
        df.loc[key, 'key_remark'] = value[1]
        df.loc[key, 'remark'] = value[2]

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_counter.txt")
    for key, value in res.items():
        df.loc[key, 'counter_last_date'] = value[0]
        df.loc[key, 'counter_date'] = value[1]
        df.loc[key, 'counter_number'] = value[2]
        df.loc[key, 'counter_real_pe'] = value[3]
        df.loc[key, 'counter_delta'] = value[4]

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_assessment.txt")
    for key, value in res.items():
        df.loc[key, 'gui_assessment'] = int(value) * 1e8

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl", df)

    return df


def add_bool_column(df, path, name):
    res = load_json_txt(path)
    for key in res:
        df.loc[key, name] = True
    return df


def sum_value(res, column):
    ret = pd.Series()

    for tmp in res:
        code = tmp[0]
        src = tmp[1]
        s1 = src.loc[:, column].copy().dropna()

        df = pd.concat([s1, ret], axis=1, sort=False)
        df = df.fillna(0)
        ret = df.sum(axis=1)
    ret = ret.sort_index()
    # print(ret)

    return ret


def generate_show_table():
    from method.dailyMethod import generate_daily_table
    df1 = generate_daily_table('latest')
    df2 = generate_gui_table()

    # df1 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z001_daily_table.pkl")
    # df2 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl")

    df = pd.concat([df1, df2], axis=1, sort=True)
    ################################################################################################################

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl", df)

    path = "..\\basicData\\dailyUpdate\\latest\\show_table.xlsx"
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="数据输出", index=True)

    dict0 = json.loads(df.to_json(orient="index", force_ascii=False))

    write_json_txt("..\\basicData\\dailyUpdate\\latest\\show_table.txt", dict0)

    # print(df)
    return df


def test_strategy():
    from method.dataMethod import load_df_from_mysql
    import datetime as dt

    df = load_df_from_mysql('600438', 'mvs')

    # s0 = df.loc[:, 'id_041_mvs_mc'].dropna()
    s0 = df.loc[:, 'id_035_mvs_sp'].dropna()
    s1 = s0[s0.index > '2021-01-04']

    profit = 0
    s2 = s1.copy()

    status = True
    value = s1[0]
    date = s1.index[0]
    print(status, value, profit)
    for index, val in s1.iteritems():
        if status is True:
            if val > value:
                profit += val - value
                value = val
                status = False
                d1 = dt.datetime.strptime(date, "%Y-%m-%d")
                d2 = dt.datetime.strptime(index, "%Y-%m-%d")
                delta = (d2 - d1).days
                print(date, index, delta)
                print(val, profit)
                # print('out')
        else:
            if val < value:
                value = val
                status = True
                date = index
        s2[index] = profit

    print(status, s1[-1], profit)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    xx = range(s1.size)
    yy = s1.values
    fig = plt.figure(figsize=(16, 9), dpi=50)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    # ax1.yaxis.grid(True, which='both')
    # ax1.xaxis.grid(True, which='both')

    ax1.plot(xx, yy, linestyle='-', alpha=0.8, color='r', label='test')
    # plt.show()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # test_figure([1] * 21)
    # show_distribution()
    # test_strategy()
    generate_show_table()

