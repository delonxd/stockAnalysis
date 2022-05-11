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


def generate_daily_table(dir_name):
    df = pd.DataFrame()

    daily_dir = "..\\basicData\\dailyUpdate\\%s" % dir_name
    ################################################################################################################

    res = load_json_txt("%s\\name_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'cn_name'] = value

    ################################################################################################################

    res = load_json_txt("%s\\report_date_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'report_date'] = value

    ################################################################################################################

    path = "%s\\code_latest_update.txt" % daily_dir
    df = add_bool_column(df, path, 'update_recently')

    ################################################################################################################

    sub_dir = '%s\\res_daily\\' % daily_dir

    res = list()
    for file in os.listdir(sub_dir):
        res.extend(load_pkl('%s\\%s' % (sub_dir, file)))

    for tmp in res:
        code = tmp[0]
        src = tmp[1]

        val = get_recent_val(src, 's_037_real_pe_return_rate', -np.inf)
        df.loc[code, 'real_pe_return_rate'] = val

        val = get_recent_val(src, 's_016_roe_parent', -np.inf)
        df.loc[code, 'roe_parent'] = val

        val = get_recent_val(src, 's_027_pe_return_rate', -np.inf)
        df.loc[code, 'pe_return_rate'] = val

        val = get_recent_val(src, 's_025_real_cost', np.inf)
        df.loc[code, 'real_cost'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf)
        df.loc[code, 'market_value_1'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf, 2)
        df.loc[code, 'market_value_2'] = val

    dump_pkl('%s\\daily_table.pkl' % daily_dir, df)

    return df


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
        df.loc[key, 'gui_assessment'] = value

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl", df)

    return df


def add_bool_column(df, path, name):
    res = load_json_txt(path)
    for key in res:
        df.loc[key, name] = True
    return df


def generate_show_table():
    df1 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z001_daily_table.pkl")
    df2 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl")

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


def show_distribution():
    path = "..\\basicData\\self_selected\\gui_selected.txt"
    gui_selected = load_json_txt(path)

    path = "..\\basicData\\dailyUpdate\\latest\\z001_daily_table.pkl"
    df = load_pkl(path)

    root = '..\\basicData\\dailyUpdate\\latest\\res_daily\\'
    res = list()
    for file in os.listdir(root):
        res.extend(load_pkl('%s\\%s' % (root, file)))

    # df = pd.DataFrame()
    ret1 = np.zeros(41)
    ret2 = np.zeros(41)
    ret3 = np.zeros(41)

    total1 = 0
    total2 = 0
    total3 = 0

    # for tmp in df.iterrows():
    for tmp in res:
        code = tmp[0]
        src = tmp[1]

        # val1 = tmp[1]['market_value_1']
        # val2 = tmp[1]['market_value_2']

        try:
            val1 = src.loc['2022-05-10', 'market_value']
        except:
            val1 = np.inf

        try:
            val2 = src.loc['2022-04-25', 'market_value']
        except:
            val2 = np.inf

        r = val1 / val2 - 1

        if r < -0.1:
            r = -0.1
        if r > 0.1:
            r = 0.1
        if val1 == np.inf or val2 == np.inf:
            r = np.nan

        if not np.isnan(r):
            index = round((r + 0.1) * 200)

            ret1[index] = ret1[index] + 1
            total1 += 1

            if code[0] == '0' or code[0] == '6':
                if code[:3] != '688':
                    # print(code)
                    ret2[index] = ret2[index] + 1
                    total2 += 1
            if code in gui_selected:
                ret3[index] = ret3[index] + 1
                total3 += 1

    ret1 = ret1 / total1
    ret2 = ret2 / total2
    ret3 = ret3 / total3

    test_figure(ret1, ret2, ret3)


def test_figure(yy, yy2, yy3):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    length = len(yy)
    xx = range(length)
    fig = plt.figure(figsize=(16, 9), dpi=90)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    # title = '分路电流-频率%sHz'
    # ax1.set_title(title)

    # ax1.set_xlabel('断开电容')
    # ax1.set_ylabel('label-voltage')

    ax1.yaxis.grid(True, which='both')
    ax1.xaxis.grid(True, which='both')
    # ax1.set_ylim([0, 0.5])

    # tmp = np.min(yy) * 1000
    # ax1.text(0.05, 0.95, '最小分路电流%.2fmA' % tmp, fontsize=10, color='blue', va='top', ha='left', transform=ax1.transAxes)

    ax1.plot(xx, yy, linestyle='-', alpha=0.8, color='blue', label='all')
    ax1.plot(xx, yy2, linestyle='--', alpha=0.8, color='r', label='main')
    ax1.plot(xx, yy3, linestyle='--', alpha=0.8, color='g', label='selected')

    interval = round((length - 1) / 20)
    major_xx = range(0, length, interval)
    label_xx = range(-10, 11, 1)

    ax1.set_xticks(major_xx)
    ax1.set_xticklabels(label_xx)

    ax1.legend()
    for label in ax1.xaxis.get_ticklabels():
        # label is a Text instance
        label.set_color('blue')
        # label.set_rotation(50)

    plt.show()


if __name__ == '__main__':
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    # generate_daily_table('update_20220506153503')
    # test_figure([1] * 21)
    show_distribution()
    # generate_show_table()
    # generate_show_table()

