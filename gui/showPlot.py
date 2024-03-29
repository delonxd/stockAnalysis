import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from method.dataMethod import load_df_from_mysql

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

import numpy as np
import datetime as dt


def show_test_plot():
    code = '600438'
    df2 = load_df_from_mysql(code, 'mvs')
    df = df2[['id_041_mvs_mc', 'id_048_mvs_ta']].copy()

    df = df.iloc[-1250:, :]
    # df = df.iloc[:750, :]
    df = df.dropna(axis=0, how='all')

    # print(df)
    # s0 = s0[-750:]
    # if s0.size == 0:
    #     return
    show_plt(code, df, 10, 33, 1600, 900)
    print(222)
    show_plt(code, df, 10, 33, 1600, 900)
    # self.show_plot(code, pd.Series())


def show_plt(title, df, x00, y00, width, height):
    if df.index.size == 0:
        return

    if plt.fignum_exists(1):
        plt.figure(1, figsize=(16, 9), dpi=100)
        rect = plt.get_current_fig_manager().window.geometry()
    else:
        rect = QRect(x00, y00, width, height)

    plt.close(1)
    plt.figure(1, figsize=(16, 9), dpi=100)
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams.update({"font.size": 20})
    plt.grid(True)
    plt.get_current_fig_manager().window.setGeometry(rect)

    plt.title(title)

    x_stick = []
    x_label = []
    tmp = df.index[0]
    for index, timestamp in enumerate(df.index):
        month = timestamp[:7]
        if month > tmp:
            tmp = month
            date = dt.datetime.strptime(month + '-01', "%Y-%m-%d")
            if date.month in [2, 5, 8, 11]:
                x_stick.append(index)
                x_label.append(timestamp[:7])

    plt.xticks(x_stick, x_label, fontsize=12, rotation=-45)

    x = range(df.index.size)

    min_value = np.inf
    max_value = -np.inf

    for column in df.columns:
        s0 = df[column]
        y0 = s0.values / 1e8
        y = np.log2(y0)

        plt.plot(x, y, color='r', linestyle=':', linewidth=1.2, marker='.',
                 markersize=7, markerfacecolor='b', markeredgecolor='g')

        index_min = np.argmin(s0.fillna(np.inf).values)
        index_max = np.argmax(s0.fillna(-np.inf).values)

        min_value = min(y[index_min], min_value)
        max_value = max(y[index_max], max_value)

        mark_index = [index_min, index_max, -1]
        for index in mark_index:
            plt.text(x[index], y[index], "%.2f" % y0[index], color='r', fontsize=14)

    y_stick = []
    y_label = []
    v = int(max_value) + 1
    while True:
        y_stick.insert(0, v)
        y_label.insert(0, '%d' % 2**v)
        if v < min_value:
            break
        v = v - 1

    plt.yticks(y_stick, y_label, fontsize=12)

    cursor = Cursor(plt.gca(), useblit=True, horizOn=False, color='grey', linewidth=1, linestyle='--')

    plt.show()


if __name__ == '__main__':

    show_test_plot()

