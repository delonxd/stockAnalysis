from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from method.fileMethod import load_pkl
import sys
import numpy as np
import pandas as pd
import time


class TableViewGui(QWidget):
    def __init__(self, df: pd.DataFrame):
        super().__init__()

        df = df.reset_index()

        self.setWindowTitle('TableViewGui')
        self.resize(600, 800)

        self.table_view = QTableView()
        self.model = MyTableModel(df)
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)
        # self.table_view.sort(True)

        layout = QHBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def header_clicked(self, index):
        print('index')


class MyTableModel(QStandardItemModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        row = df.index.size
        column = df.columns.size

        self.df = df
        self.src = df
        self.setRowCount(row)
        self.setColumnCount(column)

        self.setHorizontalHeaderLabels(df.columns)
        # self.setVerticalHeaderLabels(df.index)

        self.init_df()
        # print(self.sortRole())

    def init_df(self):
        df = self.df
        for i in range(df.index.size):
            for j in range(df.columns.size):
                self.setItem(i, j, QStandardItem(''))

    def refresh_df(self):
        df = self.df
        for j in range(df.columns.size):
            flag = df.iloc[:, j].dtype == 'float64'
            for i in range(df.index.size):
                content = df.iloc[i, j]
                # print(i, j, type(content))
                if flag:
                    text = '%.2f' % content
                else:
                    text = '%s' % content
                self.item(i, j).setText(text)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()

        tmp = [True, False]

        self.df = self.df.sort_values(by=self.df.columns[column], ascending=tmp[order])

        # self.load_df()
        self.refresh_df()

        self.layoutChanged.emit()

        print()
        # print('column: %s' % column)
        # print('order: %s' % order)


def main():
    df = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")

    # row = 100
    # column = 10
    #
    # columns = list(map(lambda x: 'column'+str(x), range(column)))
    # index = list(map(lambda x: 'index'+str(x), range(row)))
    #
    # m = np.random.random(row * column) - 0.5
    # m.resize(row, column)
    # df = pd.DataFrame(m, index=index, columns=columns)

    df = regular_df_type(df)
    app = QApplication(sys.argv)
    widget = TableViewGui(df)
    # widget = TableViewGui2(df)
    widget.show()
    sys.exit(app.exec_())


def regular_df_type(src):
    df = src.copy()
    for j in df.columns:
        try:
            for i in df.index:
                content = df.loc[i, j]
                _ = float(content)
            df[j] = df[j].astype('float')
            # print(j, 'float')
        except:
            df[j] = df[j].astype('str')
            # print(j, 'str')
    return df


if __name__ == '__main__':
    main()