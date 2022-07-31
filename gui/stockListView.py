from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from method.fileMethod import *
from method.logMethod import MainLog
from method.sortCode import sift_codes

import pandas as pd
import numpy as np


class CodesDataFrame:

    def __init__(self, code_list, current_index):
        # self.df_all = load_pkl("..\\basicData\\code_df_src.pkl")
        self.df_all = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")
        self.df_mask = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table_mask.pkl")

        # drop_columns = ['cn_name', 'key_remark', 'remark']
        # self.df_all = self.df_all.drop(drop_columns, axis=1)
        # self.df_mask = self.df_mask.drop(drop_columns, axis=1)

        self.df = pd.DataFrame()

        self.group_list = [self.df_all.index.tolist()]
        self.index_list = [0]
        self.group_flag = 0
        self.current_index = 0

        self.load_code_list(code_list, current_index)

    def load_code_list(self, code_list, code_index):
        if self.df.size != 0:
            code = self.df.iloc[self.current_index, 0]
            self.index_list[self.group_flag] = code

        self.df = self.df_all.loc[code_list, :].copy()
        self.df.index = range(self.df.shape[0])

        self.group_flag += 1
        if self.group_flag < len(self.group_list):
            self.group_list = self.group_list[:self.group_flag]
            self.index_list = self.index_list[:self.group_flag]

        # if len(self.index_list) > 0:
        #     code = self.df.iloc[self.current_index, 0]
        #     self.index_list[-1] = code

        self.group_list.append(code_list)
        self.index_list.append(0)

        self.init_current_index(code_index)

    def sort_df(self, column_num, condition):

        code = self.df.iloc[self.current_index, 0]
        if condition == 0:

            code_list = self.group_list[self.group_flag]
            self.df = self.df_all.loc[code_list, :].copy()
            self.df.index = range(self.df.shape[0])
        else:
            column = self.df.columns[column_num]

            if condition == 1:
                ascending = False
            else:
                ascending = True
            self.df = self.df.sort_values(by=column, ascending=ascending)
            self.df.index = range(self.df.shape[0])

        self.init_current_index(code)

    def backward(self):
        if self.group_flag < 1:
            return
        self.index_list[self.group_flag] = self.current_index

        self.group_flag -= 1
        self.load_flag()

    def forward(self):
        if self.group_flag >= len(self.group_list)-1:
            return
        self.index_list[self.group_flag] = self.current_index

        self.group_flag += 1
        self.load_flag()

    def load_flag(self):
        code_list = self.group_list[self.group_flag]
        code_index = self.index_list[self.group_flag]

        self.df = self.df_all.loc[code_list, :].copy()
        self.df.index = range(self.df.shape[0])

        self.init_current_index(code_index)

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
        super().__init__()
        self.code_df = code_df
        self.sort_flags = []

        self.load_code_df()

        self.loaded_row = set()

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # self.setSortingEnabled(True)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().sectionClicked.connect(self.sort_df)

        # self.verticalHeader().setVisible(False)
        # self.clicked.connect(self.on_clicked)
        self.doubleClicked.connect(self.on_double_clicked)

        # self.verticalScrollBar().valueChanged.connect(self.load_item)

    def load_code_df(self):
        df = self.code_df.df
        code_list = self.code_df.df['code'].tolist()
        mask = self.code_df.df_mask.reindex(code_list)
        # mask = self.code_df.df_mask.loc[code_list, :].copy()
        # mask.index = range(mask.shape[0])
        arr = mask.values

        row_size = df.shape[0]
        column_size = df.shape[1]
        self.setRowCount(row_size)
        self.setColumnCount(column_size)

        self.sort_flags = [0] * column_size

        h_header = np.vectorize(lambda x: str(x))(df.columns.values)
        v_header = np.vectorize(lambda x: str(x))(df.index.values)

        self.setHorizontalHeaderLabels(h_header)
        self.setVerticalHeaderLabels(v_header)

        # arr = df.values
        for i in range(row_size):
            for j in range(column_size):
                item = QTableWidgetItem(str(arr[i, j]))
                self.setItem(i, j, item)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)

        row = self.code_df.current_index
        self.resizeColumnsToContents()

        width = 100
        for i in range(10):
            self.setColumnWidth(i, width)

        self.verticalScrollBar().setSliderPosition(row)
        self.selectRow(row)

    def on_double_clicked(self, item):
        row = item.row()
        column = item.column()

        level = column - 1
        if level in [1, 2, 3]:
            name = self.code_df.df.iloc[row, column]
            code = self.code_df.df.iloc[row, 0]

            ids_name = '%s-%s' % (level, name)
            code_list = sift_codes(ids_names=[ids_name])

            if len(code_list) > 0:
                MainLog.add_log('show industry --> %s' % ids_name)

                self.code_df.load_code_list(code_list, code)
                self.load_code_df()
                self.change_signal.emit(self.code_df.current_index)
                return

        MainLog.add_log('move to row --> %s' % item.row())
        self.change_signal.emit(item.row())

    def backward(self):
        self.code_df.backward()
        self.load_code_df()
        self.change_signal.emit(self.code_df.current_index)

    def forward(self):
        self.code_df.forward()
        self.load_code_df()
        self.change_signal.emit(self.code_df.current_index)

    def sort_df(self, column):
        pos = self.horizontalScrollBar().sliderPosition()
        flag = self.sort_flags[column]
        flag = (flag + 1) % 3
        self.code_df.sort_df(column, flag)
        self.load_code_df()
        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(pos)
        self.sort_flags[column] = flag
        self.change_signal.emit(self.code_df.current_index)


class QStockListView(QWidget):
    def __init__(self, code_df):
        super().__init__()

        self.setWindowTitle('QTestWidget')
        # self.resize(800, 900)
        self.resize(1600, 900)

        self.table_view = QDataFrameTable(code_df)

        layout0 = QHBoxLayout()
        layout0.addStretch(1)

        self.button1 = QPushButton('<<')
        self.button2 = QPushButton('>>')

        layout0.addWidget(self.button1, 0)
        layout0.addWidget(QPushButton('select'), 0)
        layout0.addWidget(QPushButton('load'), 0)
        layout0.addWidget(self.button2, 0)

        layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(layout0)
        layout.addWidget(self.table_view)

        self.button1.clicked.connect(self.table_view.backward)
        self.button2.clicked.connect(self.table_view.forward)

        self.setLayout(layout)


if __name__ == '__main__':
    # arr0 = np.random.rand(40, 4)
    # df0 = pd.DataFrame(arr0)
    #
    # app = QApplication(sys.argv)
    # main = QStockListView(df0)
    # main.show()
    # sys.exit(app.exec_())

    # df = load_pkl("..\\basicData\\code_df_src.pkl")
    # print(df)
    pass
