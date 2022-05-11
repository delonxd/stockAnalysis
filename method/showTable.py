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


def show_distribution(daily_dir):
    sub_dir = '%s\\res_daily\\' % daily_dir

    res = list()
    for file in os.listdir(sub_dir):
        res.extend(load_pkl('%s\\%s' % (sub_dir, file)))

    ret = [0] * 21
    for tmp in res:
        code = tmp[0]
        src = tmp[1]

        val1 = get_recent_val(src, 's_028_market_value', np.inf)
        val2 = get_recent_val(src, 's_028_market_value', np.inf, 2)

        r = val1 / val2 - 1

        if r < -0.1:
            r = -0.1
        if r > 0.1:
            r = 0.1

        index = round((r + 0.1) * 10)
        ret[index] = ret[index] + 1

    test_figure(ret)


def test_figure(yy):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    xx = np.arange(-10, 11, 1)
    fig = plt.figure(figsize=(16, 9), dpi=90)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    # title = '分路电流-频率%sHz'
    # ax1.set_title(title)

    # ax1.set_xlabel('断开电容')
    # ax1.set_ylabel('label-voltage')

    ax1.yaxis.grid(True, which='major')
    ax1.set_ylim([0, 2])

    # tmp = np.min(yy) * 1000
    # ax1.text(0.05, 0.95, '最小分路电流%.2fmA' % tmp, fontsize=10, color='blue', va='top', ha='left', transform=ax1.transAxes)

    ax1.plot(xx, yy, linestyle='-', alpha=0.8, color='blue', label='all')
    # ax1.plot(xx, yy2, linestyle='--', alpha=0.8, color='r', label='门限值')
    # ax1.plot(xx, yy3, linestyle='--', alpha=0.8, color='g', label='正常情况')

    ax1.set_xticks(xx)
    # ax1.set_xticklabels(xx2)

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
    test_figure([1] * 21)
    # generate_show_table()
    # generate_show_table()

