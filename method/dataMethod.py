from method.mainMethod import transpose_df, show_df
from method.sqlMethod import get_data_frame, sql_if_table_exists
from request.requestData import get_cursor
from request.requestData import get_header_df
from request.requestData import request_data2mysql

import mysql.connector
import datetime as dt

# from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from dateutil.relativedelta import relativedelta
import pandas as pd
import pickle
import time
import timeit


def load_df_from_mysql(stock_code, data_type):
    db, cursor = get_cursor(data_type)

    if data_type == 'fs':
        table = 'fs_%s' % stock_code
        check_field = 'standardDate'
    elif data_type == 'mvs':
        table = 'mvs_%s' % stock_code
        check_field = 'date'
    else:
        return

    flag = sql_if_table_exists(cursor=cursor, table=table)
    if flag:
        sql_df = get_data_frame(cursor=cursor, table=table)
        sql_df = sql_df.set_index(check_field, drop=False)
        # sql_df = sql_df.where(sql_df.notnull(), None)
        sql_df.sort_index(inplace=True)
        sql_df.index = sql_df.index.map(lambda x: x[:10])

        return sql_df
    else:
        header_df = get_header_df(data_type)
        return pd.DataFrame(columns=header_df.columns)


# def sql2df_fs(code):
#     config = {
#         'user': 'root',
#         'password': 'aQLZciNTq4sx',
#         'host': 'localhost',
#         'port': '3306',
#         'database': 'fsdata',
#         # 'database': 'bsdata',
#     }
#     db = mysql.connector.connect(**config)
#
#     table = 'fs_' + code
#
#     cursor = db.cursor()
#
#     flag = sql_if_table_exists(cursor=cursor, table=table)
#     if flag:
#         sql_df = get_data_frame(cursor=cursor, table=table)
#         sql_df = sql_df.set_index('standardDate', drop=False)
#         # sql_df = sql_df.where(sql_df.notnull(), None)
#         sql_df.sort_index(inplace=True)
#         sql_df.index = sql_df.index.map(lambda x: x[:10])
#
#         return sql_df
#     else:
#         header_df = get_header_df()
#         return pd.DataFrame(columns=header_df.columns)
#         # return pd.DataFrame()
#
#
# def sql2df_mvs(code):
#     config = {
#         'user': 'root',
#         'password': 'aQLZciNTq4sx',
#         'host': 'localhost',
#         'port': '3306',
#         'database': 'marketData',
#         # 'database': 'bsdata',
#     }
#     db = mysql.connector.connect(**config)
#
#     table = 'mvs_' + code
#
#     cursor = db.cursor()
#
#     flag = sql_if_table_exists(cursor=cursor, table=table)
#     if flag:
#         sql_df = get_data_frame(cursor=cursor, table=table)
#         sql_df = sql_df.set_index('date', drop=False)
#         # sql_df = sql_df.where(sql_df.notnull(), None)
#         sql_df.sort_index(inplace=True)
#         sql_df.index = sql_df.index.map(lambda x: x[:10])
#
#         return sql_df
#     else:
#         header_df = get_header_df_mvs()
#         return pd.DataFrame(columns=header_df.columns)


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


# def get_tree_df2():
#     header_df = get_header_df()
#
#     df = transpose_df(header_df)
#
#     df.insert(0, "ds_type", 'digit')
#     df.insert(0, "child", None)
#
#     df.insert(0, "index_name", df.index)
#     df.insert(1, "selected", False)
#
#     df.insert(2, "color", QColor(Qt.red))
#     df.insert(3, "line_thick", 2)
#     df.insert(4, "pen_style", Qt.SolidLine)
#
#     df.insert(5, "scale_min", 1)
#     df.insert(6, "scale_max", 1024)
#     df.insert(7, "scale_div", 10)
#     df.insert(8, "logarithmic", True)
#
#     df.insert(9, "info_priority", 0)
#
#     df.insert(10, "units", '亿')
#
#     df.insert(0, "show_name", '')
#     df.insert(0, "default_ds", False)
#
#     # show_df(df)
#
#     return df


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


def get_month_delta(df: pd.DataFrame, new_name, mode='QUARTERLY'):

    if mode == 'MONTHLY':
        step = 1
    elif mode == 'QUARTERLY':
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


# def get_default_style_df():
#     # df = get_tree_df2()
#     #
#     # df.loc['id_001_bs_ta', 'color'] = QColor(Qt.green)
#     # df.loc['id_001_bs_ta', 'selected'] = True
#     # df.loc['id_001_bs_ta', 'show_name'] = '资产合计'
#     # df.loc['id_001_bs_ta', 'info_priority'] = 3
#     # df.loc['id_001_bs_ta', 'default_ds'] = True
#     #
#     # df.loc['id_062_bs_tl', 'color'] = QColor(Qt.red)
#     # df.loc['id_062_bs_tl', 'selected'] = True
#     # df.loc['id_062_bs_tl', 'show_name'] = '负债合计'
#     # df.loc['id_062_bs_tl', 'info_priority'] = 2
#     #
#     # df.loc['id_110_bs_toe', 'color'] = QColor(Qt.yellow)
#     # df.loc['id_110_bs_toe', 'selected'] = True
#     # df.loc['id_110_bs_toe', 'show_name'] = '所有者权益'
#     # df.loc['id_110_bs_toe', 'info_priority'] = 1
#     #
#     # df.loc['first_update', 'ds_type'] = 'str'
#     # df.loc['last_update', 'ds_type'] = 'str'
#     # df.loc['stockCode', 'ds_type'] = 'const'
#     # df.loc['currency', 'ds_type'] = 'const'
#     # df.loc['standardDate', 'ds_type'] = 'str'
#     # df.loc['reportDate', 'ds_type'] = 'str'
#     # df.loc['reportType', 'ds_type'] = 'str'
#     # df.loc['date', 'ds_type'] = 'str'
#     #
#     # # show_df(df)
#     # # print(df['info_priority'].max())
#     # # print(df.quantile(0.5))
#
#     # path = '../gui/style_df_standard.pkl'
#     path = '../gui/style_default.pkl'
#     with open(path, 'rb') as pk_f:
#         df = pickle.load(pk_f)
#
#     # df.insert(0, "ma_mode", 0)
#     #
#     # df.loc['id_211_ps_np', 'ma_mode'] = 4
#
#     return df


def load_default_style():
    path = '../gui/styles/style_default.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)
    return df


def save_default_style(df):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    path1 = '../gui/styles/style_%s.pkl' % timestamp
    with open(path1, 'wb') as pk_f:
        pickle.dump(df, pk_f)

    path2 = '../gui/styles/style_default.pkl'
    with open(path2, 'wb') as pk_f:
        pickle.dump(df, pk_f)


def get_style_df_mvs():
    header_df = get_header_df_mvs()
    df = transpose_df(header_df)

    df.insert(0, "ma_mode", 0)
    df.insert(1, "delta_mode", False)
    df.insert(2, "default_ds", False)
    df.insert(3, "show_name", '')
    df.insert(4, "index_name", '')
    df.insert(5, "selected", False)

    df.insert(6, "color", QColor(Qt.red))
    df.insert(7, "line_thick", 2)
    df.insert(8, "pen_style", Qt.SolidLine)

    df.insert(9, "scale_min", 0)
    df.insert(10, "scale_max", 100)
    df.insert(11, "scale_div", 10)
    df.insert(12, "logarithmic", False)

    df.insert(13, "info_priority", 0)

    df.insert(14, "units", '倍')
    df.insert(15, "child", None)
    df.insert(16, "ds_type", 'digit')

    df.loc['first_update', 'ds_type'] = 'str'
    df.loc['last_update', 'ds_type'] = 'str'
    df.loc['stockCode', 'ds_type'] = 'const'
    df.loc['date', 'ds_type'] = 'str'

    df.loc['id_001_mvs_pe_ttm', 'selected'] = True

    return df


def combine_style_df():

    path = '../gui/styles/style_df_standard.pkl'
    with open(path, 'rb') as pk_f:
        df1 = pickle.load(pk_f)

    df1.insert(0, "frequency", "QUARTERLY")

    df2 = get_style_df_mvs()

    df2.insert(0, "frequency", "DAILY")

    res = pd.merge(df1.T, df2.T, how='outer', left_index=True, right_index=True,
                   suffixes=('_fs', '_mvs'), copy=True).T

    res["index_name"] = res.index.values

    res.loc['first_update_fs', 'txt_CN'] = '首次上传日期_fs'
    res.loc['last_update_fs', 'txt_CN'] = '最近上传日期_fs'

    res.loc['first_update_mvs', 'txt_CN'] = '首次上传日期_mvs'
    res.loc['last_update_mvs', 'txt_CN'] = '最近上传日期_mvs'

    # print(res)
    # print(res.index.values)
    # print(res.columns.values)
    #
    # for _, row in res.iterrows():
    #     print(row.values)

    # path = '../gui/style_combined_default0.pkl'
    path = '../gui/style_default.pkl'

    with open(path, 'wb') as pk_f:
        pickle.dump(res, pk_f)


def sql2df(code):
    # df1 = sql2df_mvs('code')
    # df1 = sql2df_mvs(code)

    # request_data2mysql(
    #     stock_code=code,
    #     data_type='fs',
    #     start_date="2021-01-01",
    # )
    #
    # request_data2mysql(
    #     stock_code=code,
    #     data_type='mvs',
    #     start_date="2021-01-01",
    # )

    df1 = load_df_from_mysql(code, 'fs')
    df2 = load_df_from_mysql(code, 'mvs')

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True,
                  sort=True, suffixes=('_mvs', '_fs'), copy=True)
    return df


if __name__ == '__main__':
    # sql2df('000002')
    str2 = "from __main__ import sql2df_mvs"
    t0 = timeit.Timer("sql2df_mvs('000004')", str2)
    print(t0.timeit(10))

    # combine_style_df()
    #
    # res = sql2df('600006')
    #
    # print(res)
    pass
