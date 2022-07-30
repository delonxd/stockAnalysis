from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from method.fileMethod import *
from method.logMethod import MainLog

import pandas as pd
import sys
import numpy as np
import json


class CodesDataFrame:

    def __init__(self, code_list, current_index=0):

        columns = ['code', 'name', 'level1', 'level2', 'level3', 'i_code']
        self.df = pd.DataFrame(columns=columns)

        path = '..\\basicData\\code_names_dict.txt'
        self.code_names_dict = load_json_txt(path)

        path = '..\\basicData\\industry\\sw_2021_dict.txt'
        # path = '../basicData/industry/code_industry_dict.txt'
        self.code_industry_dict = load_json_txt(path)

        path = '..\\basicData\\industry\\sw_2021_name_dict.txt'
        # path = '../basicData/industry/industry_dict.txt'
        self.industry_name_dict = load_json_txt(path)

        self.index_dict = dict()
        for index, code in enumerate(code_list):
            self.add_code(index, code)
            self.index_dict[code] = index

        self.current_index = current_index

    def add_code(self, index, code):
        row = pd.Series(index=self.df.columns, dtype=str)

        row['code'] = code
        row['name'] = self.code_names_dict.get(code)

        i_code = self.code_industry_dict.get(code)
        if i_code:
            # i1 = i_code[:3]
            # i2 = i_code[:5]
            # i3 = i_code[:7]

            i1 = i_code[:2] + '0000'
            i2 = i_code[:4] + '00'
            i3 = i_code[:6]

            row['level1'] = self.industry_name_dict.get(i1)
            row['level2'] = self.industry_name_dict.get(i2)
            row['level3'] = self.industry_name_dict.get(i3)
            row['i_code'] = i_code

        self.df.loc[index] = row

    def sort_values(self, columns, ascending=True):
        self.df.sort_values(columns, ascending=ascending, inplace=True)

    def init_current_index(self, index=0):
        if isinstance(index, str):
            code = index
            code_list = self.df['code'].tolist()
            if code in code_list:
                self.current_index = code_list.index(code)
        else:
            try:
                tmp = int(index)
                self.current_index = tmp
            except Exception as e:
                print(e)

    def generate_buffer_list(self, forward, backward):
        # forward = 20
        # backward = 2

        buffer = list(range(forward+1))

        for i in range(1, backward+1):
            buffer.insert(i*2, -i)

        arr = np.array(buffer, dtype='int32')
        arr = (arr + self.current_index) % self.df.shape[0]

        ret = []
        for index in arr:
            code = self.df.iloc[index]['code']
            if code not in ret:
                ret.append(code)
        return ret


class QDataFrameTable(QTableWidget):
    change_signal = pyqtSignal(int)

    def __init__(self, code_df: CodesDataFrame):
        df = code_df.df
        super().__init__(*df.shape)

        self.code_df = code_df
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
        # self.verticalHeader().setVisible(False)
        #
        # self.clicked.connect(self.on_clicked)
        self.doubleClicked.connect(self.on_doubleClicked)

    @property
    def df(self):
        return self.code_df.df

    def on_clicked(self, item):
        print(item.row())
        # QMessageBox.information(self, 'QListWidget', '您选择了: %s' % item.text())

    def on_doubleClicked(self, item):
        # print(item.row())
        MainLog.add_log('move to row --> %s' % item.row())
        self.change_signal.emit(item.row())


class QStockListView(QWidget):
    def __init__(self, code_df):
        super().__init__()

        self.setWindowTitle('QTestWidget')
        self.resize(600, 900)

        self.table_view = QDataFrameTable(code_df)

        layout0 = QHBoxLayout()
        layout0.addStretch(1)
        layout0.addWidget(QPushButton('select'), 0)
        layout0.addWidget(QPushButton('load'), 0)
        layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(layout0)
        layout.addWidget(self.table_view)

        self.setLayout(layout)


def test_codes_data_frame():
    # import re
    # with open("..\\basicData\\selected_0514.txt", "r", encoding="utf-8", errors="ignore") as f:
    #     txt = f.read()
    #     code_list = re.findall(r'([0-9]{6})', txt)
    #     code_list.reverse()

    with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    tmp = CodesDataFrame(code_list)
    print(tmp.df)

    tmp.init_current_index(code='600000')


if __name__ == '__main__':
    # arr0 = np.random.rand(40, 4)
    # df0 = pd.DataFrame(arr0)
    #
    # app = QApplication(sys.argv)
    # main = QStockListView(df0)
    # main.show()
    # sys.exit(app.exec_())

    test_codes_data_frame()
