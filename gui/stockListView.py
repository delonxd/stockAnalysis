from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pandas as pd
import sys
import numpy as np
import json


class QDataFrameTable(QTableWidget):
    change_signal = pyqtSignal(str)

    def __init__(self, df: pd.DataFrame):
        super().__init__(*df.shape)

        self.df = df
        h_header = np.vectorize(lambda x: str(x))(df.columns.values)
        v_header = np.vectorize(lambda x: str(x))(df.index.values)
        self.setHorizontalHeaderLabels(h_header)
        self.setVerticalHeaderLabels(v_header)

        arr = df.values
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.setItem(i, j, QTableWidgetItem(str(arr[i, j])))

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # self.clicked.connect(self.on_clicked)
        self.doubleClicked.connect(self.on_doubleClicked)

    def on_clicked(self, item):
        print(item.row())
        # QMessageBox.information(self, 'QListWidget', '您选择了: %s' % item.text())

    def on_doubleClicked(self, item):
        print(item.row())


class QStockListView(QWidget):
    def __init__(self, df):
        super().__init__()

        self.setWindowTitle('QTestWidget')
        self.resize(500, 300)

        self.table_view = QDataFrameTable(df)

        layout0 = QHBoxLayout()
        layout0.addStretch(1)
        layout0.addWidget(QPushButton('select'), 0)
        layout0.addWidget(QPushButton('load'), 0)
        layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(layout0)
        layout.addWidget(self.table_view)

        self.setLayout(layout)


class CodesDataFrame:

    def __init__(self, code_list):

        columns = ['code', 'name', 'level1', 'level2', 'level3']
        self.df = pd.DataFrame(columns=columns)

        with open('../basicData/code_names_dict.txt', 'r', encoding='utf-8') as f:
            self.code_names_dict = json.loads(f.read())

        with open('../basicData/industry/code_industry_dict.txt', 'r', encoding='utf-8') as f:
            self.code_industry_dict = json.loads(f.read())

        with open('../basicData/industry/industry_dict.txt', 'r', encoding='utf-8') as f:
            self.industry_name_dict = json.loads(f.read())

        for code in code_list:
            self.add_code(code)

    def add_code(self, code):
        row = pd.Series(index=self.df.columns, dtype=str)

        row['code'] = code
        row['name'] = self.code_names_dict[code]

        i_code = self.code_industry_dict.get(code)
        if i_code:
            i1 = i_code[:3]
            i2 = i_code[:5]
            i3 = i_code[:7]

            row['level1'] = self.industry_name_dict[i1]
            row['level2'] = self.industry_name_dict[i2]
            row['level3'] = self.industry_name_dict[i3]

        self.df.loc[code] = row


def test_codes_data_frame():
    import re
    # with open("F:\\Backups\\价值投资0406.txt", "r", encoding="utf-8", errors="ignore") as f:
    with open("C:\\Backups\\价值投资0514.txt", "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
        code_list = re.findall(r'([0-9]{6})', txt)
        code_list.reverse()

    tmp = CodesDataFrame(code_list)
    print(tmp.df)


if __name__ == '__main__':
    # arr0 = np.random.rand(40, 4)
    # df0 = pd.DataFrame(arr0)
    #
    # app = QApplication(sys.argv)
    # main = QStockListView(df0)
    # main.show()
    # sys.exit(app.exec_())

    test_codes_data_frame()