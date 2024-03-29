import QtOpenGL
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from discount.discountModel import ValueModel2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor


class CalculatorTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1100, 200)

        self.column_type = {
            'mkv': 'float',
            'asset': 'float',
            'profit': 'float',
            'r_ratio': 'ratio',
            'rate0': 'rate0',
            'rate1': 'rate',
            't1': 'year',
            'rate2': 'rate',
            't2': 'year',
            'rate3': 'rate',
            't3': 'year',
            'val1': 'float',
            'val2': 'float',
            'val3': 'float',
        }

        self.setColumnCount(len(self.column_type))

        # width_list = [180, 22, 70, 22, 22, 90, 50, 50, 40, 10, 30, 200, 20, 40, 50, 20, 20, 20, 20]
        # for idx, val in enumerate(width_list):
        #     self.setColumnWidth(idx, val)

        self.df = pd.DataFrame()

        self.setHorizontalHeaderLabels(self.column_type.keys())
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.clicked.connect(self.table_clicked)
        # self.doubleClicked.connect(self.table_double_clicked)

    def init_table(self, df):
        self.df = df
        df.columns = self.column_type.keys()
        self.clear()

        self.setRowCount(df.shape[0])

        self.show_data()
        self.resizeColumnsToContents()
        self.setHorizontalHeaderLabels(self.column_type.keys())

        list0 = list(self.column_type.keys())

        for key in ['mkv', 'asset', 'profit', 'val1', 'val2', 'val3']:
            self.setColumnWidth(list0.index(key), 80)
        for key in ['r_ratio', 'rate0', 'rate1', 'rate2', 'rate3']:
            self.setColumnWidth(list0.index(key), 60)
        for key in ['t1', 't2', 't3']:
            self.setColumnWidth(list0.index(key), 50)

        # self.calculate()

    @staticmethod
    def init_model(row):
        rate = [row['rate1'], row['rate2'], row['rate3']]
        year = [row['t1'], row['t2'], row['t3']]
        ret = ValueModel2(
            rate, year,
            row['rate0'], row['asset'], row['profit'],
            row['r_ratio'],
        )
        return ret

    def show_data(self):
        df = self.df

        for i, row in df.iterrows():
            m = self.init_model(row)
            # df.loc[i, 'pe'] = m.sum_profit(1)[1]
            df.loc[i, 'val1'] = m.value_reserved
            df.loc[i, 'val2'] = m.value
            df.loc[i, 'val3'] = m.value_average

        for i, index in enumerate(df.index):
            for j, tmp in enumerate(self.column_type.items()):
                column, typ = tmp
                data = df.loc[index, column]
                item = QTableWidgetItem()
                self.setItem(i, j, item)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
                self.show_item(item, data, typ)

    def show_plot(self):
        df = self.df
        if plt.fignum_exists(2):
            plt.figure(2, figsize=(16, 9), dpi=100)
            rect = plt.get_current_fig_manager().window.geometry()
        else:
            rect = QRect(10, 32, 1600, 900)

        plt.close(2)
        plt.figure(2, figsize=(16, 9), dpi=100)
        plt.rcParams['font.sans-serif'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams.update({"font.size": 20})
        plt.grid(True)
        plt.get_current_fig_manager().window.setGeometry(rect)
        plt.title('test')
        plt.ylim([-20, 40])
        min_value = np.inf
        max_value = -np.inf

        for i, row in df.iterrows():
            m = self.init_model(row)

            mkv = row['mkv']
            t_year = int(sum(m.year))
            x = range(t_year)
            # y = m.iter_sum()
            y1 = m.iter_return(m.value, mkv, t_year)
            plt.plot(x, y1, color='r', linestyle=':', linewidth=1.2, marker='.',
                     markersize=7, markerfacecolor='b', markeredgecolor='g')

            y2 = m.iter_return(m.value_reserved, mkv, t_year)
            plt.plot(x, y2, color='r', linestyle=':', linewidth=1.2, marker='.',
                     markersize=7, markerfacecolor='yellow', markeredgecolor='g')

            y3 = m.iter_return(m.value_average, mkv, t_year)
            plt.plot(x, y3, color='r', linestyle=':', linewidth=1.2, marker='.',
                     markersize=7, markerfacecolor='red', markeredgecolor='g')

        # y_stick = []
        # y_label = []
        # v = int(max_value) + 1
        # while True:
        #     y_stick.insert(0, v)
        #     y_label.insert(0, '%d' % 2 ** v)
        #     if v < min_value:
        #         break
        #     v = v - 1
        #
        # plt.yticks(y_stick, y_label, fontsize=12)

        cursor = Cursor(plt.gca(), useblit=True, horizOn=False, color='grey', linewidth=1, linestyle='--')

        plt.show()

    @staticmethod
    def show_item(item, data, typ):
        item.setFont(QFont('consolas', 13))
        if typ == 'int':
            item.setText('%.0f' % data)

        elif typ == 'float':
            item.setText('%.2f' % data)

        elif typ == 'year':
            item.setText('%.0f' % data)

        elif typ == 'rate':
            item.setText('%.0f%%' % data)
            item.setForeground(QBrush(Qt.red))

        elif typ == 'rate0':
            item.setText('%.0f%%' % data)
            item.setForeground(QBrush(Qt.green))

        elif typ == 'ratio':
            item.setText('%.0f%%' % data)
            item.setForeground(QBrush(Qt.blue))

    # def calculate(self):
    #     df = self.df
    #     for i, row in df.iterrows():
    #         rate = [row['rate1'], row['rate2'], row['rate3']]
    #         year = [row['t1'], row['t2'], row['t3']]
    #         m = ValueModel2(rate, year, -10)
    #         df.loc[i, 'result'] = m.value
    #
    #     self.show_data()

    def table_clicked(self, item):
        df = self.df

        i = item.row()
        j = item.column()

        index = df.index[i]
        column_label = list(self.column_type.keys())
        column = column_label[j]

        title = str(index)
        label = column + ': '

        if column in [
            'asset',
            'profit',
            'rate0',
            'r_ratio',
            'rate1',
            't1',
            'rate2',
            't2',
            'rate3',
            't3',
            'mkv',
        ]:
            text, _ = QInputDialog.getText(self, title, label)
            if text is None:
                return
            try:
                value = float(text)
            except Exception as e:
                print(e)
                return

            df.loc[index, column] = value
            self.show_data()


class CalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        # self.main_widget = main_widget
        self.button1 = QPushButton('计算')
        self.button2 = QPushButton('显示')

        # self.resize(1600, 900)

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.button1, 0, Qt.AlignCenter)
        layout1.addWidget(self.button2, 0, Qt.AlignCenter)
        layout1.addStretch(1)

        self.cal_df = pd.DataFrame()
        self.cal_table = CalculatorTable()

        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.cal_table)
        self.setLayout(layout2)

        self.move(600, 300)
        # self.button1.clicked.connect(self.refresh_all_pix)
        self.button2.clicked.connect(self.cal_table.show_plot)

        self.load_code(0)

    def load_code(self, code):
        # l0 = [
        #     [120, 10, 15, 10, 10, 10, 0, np.inf, 0, 0],
        #     [-300, 10, 15, 10, 10, 10, 0, np.inf, 0, 0],
        #     [0, 10, 20, np.inf, 10, 10, 0, np.inf, 0, 0],
        # ]

        l0 = [
            [1000, 3471, 850, 3, 8, 0, 10, 0, 10, 0, 100, None, None, None],
            # [120, 10, 15, 10, 10, 10, 0, 100, 0, 0],
            # [-300, 10, 15, 10, 10, 10, 0, 100, 0, 0],
            # [0, 10, 20, np.inf, 10, 10, 0, 100, 0, 0],
        ]
        self.cal_df = pd.DataFrame(l0)

        self.cal_table.init_table(self.cal_df)


if __name__ == '__main__':
    import sys
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    main = CalculatorWidget()
    main.show()
    # main.showMinimized()
    sys.exit(app.exec_())

    pass