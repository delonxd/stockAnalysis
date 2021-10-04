from method.mainMethod import get_header_df, transpose_df
from method.sqlMethod import get_data_frame
import mysql.connector
import datetime as dt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from dateutil.rrule import *
import pandas as pd
import numpy as np
import sys


def sql2df():
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'fsdata',
        # 'database': 'bsdata',
    }
    db = mysql.connector.connect(**config)

    cursor = db.cursor()
    sql_df = get_data_frame(cursor=cursor, table='fs_600008')

    sql_df = sql_df.set_index('standardDate', drop=False)

    sql_df = sql_df.where(sql_df.notnull(), None)
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

    df.insert(0, "index_name", df.index)
    df.insert(1, "selected", False)

    df.insert(2, "color", QColor(Qt.red))
    df.insert(3, "line_thick", 2)
    df.insert(4, "pen_style", Qt.SolidLine)

    df.insert(5, "scale_min", 2e8)
    df.insert(6, "scale_max", 2048*1e8)
    df.insert(7, "scale_div", 10)
    df.insert(8, "logarithmic", True)
    df.insert(9, "format_fun", lambda x: '%i亿' % (x / 1e8))

    df.loc['id_001_bs_ta', 'color'] = QColor(Qt.yellow)
    df.loc['id_001_bs_ta', 'selected'] = True

    return df


if __name__ == '__main__':
    pass
