from method.mainMethod import get_header_df, transpose_df, show_df
from method.sqlMethod import get_data_frame
import mysql.connector
import datetime as dt

# from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import sys
import pickle
import json


def sql2df(code):
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'fsdata',
        # 'database': 'bsdata',
    }
    db = mysql.connector.connect(**config)

    table = 'fs_' + code

    cursor = db.cursor()
    sql_df = get_data_frame(cursor=cursor, table=table)

    sql_df = sql_df.set_index('standardDate', drop=False)

    # sql_df = sql_df.where(sql_df.notnull(), None)
    sql_df.sort_index(inplace=True)

    sql_df.index = sql_df.index.map(lambda x: x[:10])

    return sql_df


def data_by_dates(df: pd.DataFrame, dates: list):
    res_df = pd.DataFrame(columns=df.columns.tolist())
    date0 = dates[0]

    ps_src = list()
    for tup in df.itertuples():
        if tup[1]:
            if isinstance(tup[1], (int, float)):
                date = dt.datetime.strptime(tup[0], "%Y-%m-%d")
                offset = (date - date0).days
                ps_src.append((offset, tup[1]))

    if len(ps_src) < 2:
        return res_df

    it = iter(ps_src)
    p1 = it.__next__()
    p2 = it.__next__()

    for date in dates:
        x = (date - date0).days
        index = date.strftime("%Y-%m-%d")
        while x > p2[0]:
            try:
                p_tmp = it.__next__()
                p1 = p2
                p2 = p_tmp
            except StopIteration:
                break

        if p1[0] <= x <= p2[0]:
            y = get_y_from_points(x, p1, p2)
            # ps_res.append((x, y))

            res_df.loc[index] = y

    return res_df


def get_y_from_points(x: int, point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    res = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    return res


def get_tree_df2():
    header_df = get_header_df()

    df = transpose_df(header_df)

    df.insert(0, "ds_type", 'digit')
    df.insert(0, "child", None)

    df.insert(0, "index_name", df.index)
    df.insert(1, "selected", False)

    df.insert(2, "color", QColor(Qt.red))
    df.insert(3, "line_thick", 2)
    df.insert(4, "pen_style", Qt.SolidLine)

    df.insert(5, "scale_min", 1)
    df.insert(6, "scale_max", 1024)
    df.insert(7, "scale_div", 10)
    df.insert(8, "logarithmic", True)

    df.insert(9, "info_priority", 0)

    df.insert(10, "units", '亿')

    df.insert(0, "show_name", '')
    df.insert(0, "default_ds", False)

    # show_df(df)

    return df


def process_df():
    df = sql2df(code='000004')
    # print(df)

    data = df.loc[:, ['id_211_ps_np']]
    res = get_mouth_delta(data, 'id_211_ps_np_DELTA')

    print(res)

    style_df = get_default_style_df()
    style_df = add_style_row(style_df, 'id_211_ps_np', 'id_211_ps_np_DELTA')


def add_style_row(df: pd.DataFrame, src_name, new_name):
    series = df.loc[src_name]
    series.name = new_name
    df2 = df.append(series)
    return df2


def get_value_from_ratio(date0, value0, date, ratio_year):
    x = (date - date0).days
    res = value0 * (ratio_year ** (x / 365))
    return res


def get_month_data(df: pd.DataFrame, new_name):
    df = df.dropna()

    date0 = None
    year0 = None
    month0 = None
    index0 = None
    value0 = None

    indexes = list()
    values = list()

    for tup in df.itertuples():
        date = dt.datetime.strptime(tup[0], "%Y-%m-%d")

        if date0:
            year1 = date.year
            month1 = date.month
            value1 = tup[1]

            d_month = (year1 - year0) * 12 + month1 - month0
            d_value = (value1 - value0) / d_month

            indexes.append(index0)
            values.append(value0)

            for m in range(3, d_month, 3):
                date1 = date0 + dt.timedelta(days=1)
                date_tmp = date1 + relativedelta(months=m, days=-1)

                index = date_tmp.strftime("%Y-%m-%d")

                indexes.append(index)
                values.append(value0 + d_value * m)

        date0 = date
        year0 = date.year
        month0 = date.month
        value0 = tup[1]
        index0 = tup[0]

    if index0:
        indexes.append(index0)
        values.append(value0)

    res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    # print(res_df)
    # raise KeyboardInterrupt

    return res_df


def get_month_delta(df: pd.DataFrame, new_name, mode='Season'):

    if mode == 'Monthly':
        step = 1
    elif mode == 'Season':
        step = 3
    else:
        step = 1
    year = None
    month0 = 0
    value0 = 0

    indexes = list()
    values = list()

    for tup in df.itertuples():
        date = dt.datetime.strptime(tup[0], "%Y-%m-%d")
        if not year == date.year:
            month0 = 0
            value0 = 0
        month1 = date.month
        value1 = tup[1]
        year = date.year

        d_value = (value1 - value0) / (month1 - month0)

        for m in range((month0 + step), (month1 + 1), step):
            date1 = dt.date(date.year, m, 1)
            date_tmp = date1 + relativedelta(months=1, days=-1)

            index = date_tmp.strftime("%Y-%m-%d")
            # res_df.loc[index] = d_value * 12

            indexes.append(index)
            values.append(d_value * 12)

        month0 = month1
        value0 = value1

    res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    return res_df


def get_default_style_df():
    # df = get_tree_df2()
    #
    # df.loc['id_001_bs_ta', 'color'] = QColor(Qt.green)
    # df.loc['id_001_bs_ta', 'selected'] = True
    # df.loc['id_001_bs_ta', 'show_name'] = '资产合计'
    # df.loc['id_001_bs_ta', 'info_priority'] = 3
    # df.loc['id_001_bs_ta', 'default_ds'] = True
    #
    # df.loc['id_062_bs_tl', 'color'] = QColor(Qt.red)
    # df.loc['id_062_bs_tl', 'selected'] = True
    # df.loc['id_062_bs_tl', 'show_name'] = '负债合计'
    # df.loc['id_062_bs_tl', 'info_priority'] = 2
    #
    # df.loc['id_110_bs_toe', 'color'] = QColor(Qt.yellow)
    # df.loc['id_110_bs_toe', 'selected'] = True
    # df.loc['id_110_bs_toe', 'show_name'] = '所有者权益'
    # df.loc['id_110_bs_toe', 'info_priority'] = 1
    #
    # df.loc['first_update', 'ds_type'] = 'str'
    # df.loc['last_update', 'ds_type'] = 'str'
    # df.loc['stockCode', 'ds_type'] = 'const'
    # df.loc['currency', 'ds_type'] = 'const'
    # df.loc['standardDate', 'ds_type'] = 'str'
    # df.loc['reportDate', 'ds_type'] = 'str'
    # df.loc['reportType', 'ds_type'] = 'str'
    # df.loc['date', 'ds_type'] = 'str'
    #
    # # show_df(df)
    # # print(df['info_priority'].max())
    # # print(df.quantile(0.5))

    path = '../gui/style_df_standard.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)

    # df.insert(0, "ma_mode", 0)
    #
    # df.loc['id_211_ps_np', 'ma_mode'] = 4

    return df


if __name__ == '__main__':
    # process_df()

    path = '../basicData/BasicData.pkl'
    with open(path, 'rb') as pk_f:
        res = pickle.load(pk_f)

    d = json.loads(res)['data']

    res = dict()
    for v in d:
        res[v['stockCode']] = v['name']
    print(res)

    # with open("../comparisonTable/basic_table.txt", "w", encoding="utf-8") as f:
    #     f.write(str0)

    with open("../basicData/code_name.pkl", 'wb') as pk_f:
        pickle.dump(res, pk_f)

    pass
