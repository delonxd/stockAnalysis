import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from method.dataMethod import load_df_from_mysql

import matplotlib.pyplot as plt
import numpy as np
import sys
import datetime as dt


class ShowPlot(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('show_plot')
        self.label = QLabel(self)
        self.resize(300, 300)
        self.move(10, 10)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def show_plot(self, title, series):
        s0 = series

        if s0.size == 0:
            self.label.setPixmap(QPixmap())
            self.show()
            return

        x_stick = []
        x_label = []
        tmp = s0.index[0]
        for index, timestamp in enumerate(s0.index):
            month = timestamp[:7]
            if month > tmp:
                tmp = month
                date = dt.datetime.strptime(month + '-01', "%Y-%m-%d")
                if date.month in [2, 5, 8, 11]:
                    x_stick.append(index)
                    x_label.append(timestamp[:7])

        plt.cla()
        plt.close("all")
        plt.figure(figsize=(16, 9), dpi=100)
        plt.rcParams['font.sans-serif'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams.update({"font.size": 20})
        plt.grid(True)
        plt.title(title)

        x = range(s0.size)
        y0 = s0.values / 1e8
        y = np.log2(y0)

        plt.plot(x, y, color='r', linestyle=':', linewidth=1.2, marker='.',
                 markersize=7, markerfacecolor='b', markeredgecolor='g')

        index_min = np.argmin(y)
        index_max = np.argmax(y)
        min_value = y[index_min]
        max_value = y[index_max]

        mark_index = [index_min, index_max, -1]
        for index in mark_index:
            plt.text(x[index], y[index], "%.2f" % y0[index], color='r', fontsize=14)

        plt.xticks(x_stick, x_label, fontsize=12, rotation=-45)

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

        # plt.ylim([0, max(y) * 1.2])
        path = 'tmp_plot.png'
        plt.savefig('tmp_plot.png')

        self.label.setPixmap(QPixmap(path))
        self.show()

    def show_test_plot(self):
        code = '600438'
        df2 = load_df_from_mysql(code, 'mvs')
        s0 = df2['id_041_mvs_mc'].copy().dropna()

        s0 = s0[-750:]
        if s0.size == 0:
            return
        self.show_plot(code, s0)
        # self.show_plot(code, pd.Series())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ShowPlot()
    # main.show()
    main.show_test_plot()

    sys.exit(app.exec_())
