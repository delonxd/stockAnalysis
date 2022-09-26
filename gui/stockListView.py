from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.fileMethod import *
from method.logMethod import MainLog
from method.sortCode import sift_codes
from method.showTable import generate_show_table

import pandas as pd
import numpy as np


class CodesDataFrame:

    def __init__(self, code_list, current_index):
        # self.df_all = load_pkl("..\\basicData\\code_df_src.pkl")

        generate_show_table()

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
                self.load_code_list(code_list, code)
                return

        MainLog.add_log('move to row --> %s' % item.row())
        self.change_signal.emit(item.row())

    def load_code_list(self, code_list, code_index):
        self.code_df.load_code_list(code_list, code_index)
        self.load_code_df()
        self.change_signal.emit(self.code_df.current_index)

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
        self.generate_widget = GenerateCodeListWidget()

        layout0 = QHBoxLayout()
        layout0.addStretch(1)

        self.button1 = QPushButton('<<')
        self.button2 = QPushButton('>>')
        self.button3 = QPushButton('load')
        self.button4 = QPushButton('select')

        layout0.addWidget(self.button1, 0)
        layout0.addWidget(self.button4, 0)
        layout0.addWidget(self.button3, 0)
        layout0.addWidget(self.button2, 0)

        layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(layout0)
        layout.addWidget(self.table_view)

        self.button1.clicked.connect(self.table_view.backward)
        self.button2.clicked.connect(self.table_view.forward)
        self.button3.clicked.connect(self.generate_widget.show)
        self.button4.clicked.connect(self.select_code)

        self.generate_widget.generate_signal.connect(self.table_view.load_code_list)

        self.setLayout(layout)

    def select_code(self):
        txt, _ = QInputDialog.getText(self, '选择', '请输入:')

        name_dict = load_json_txt('..\\basicData\\code_names_dict.txt')

        if txt in name_dict.keys():
            self.table_view.load_code_list([txt], 0)
            return
        if txt in name_dict.values():
            for key, value in name_dict.items():
                if value == txt:
                    self.table_view.load_code_list([key], 0)
                    return

    def closeEvent(self, event):
        self.generate_widget.close()


class GenerateCodeListWidget(QWidget):
    generate_signal = pyqtSignal(object, object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle('GenerateCodeList')
        self.resize(400, 600)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        h_layout.addStretch(1)
        h_layout.addLayout(v_layout, 0)
        h_layout.addStretch(1)

        self.labels = []
        self.editor = []
        self.values = []

        layout = QGridLayout()

        str_flg = [
            '',
            'old',
            'old_random',
            'all',
            'hold',
            'mark-0',
            'mark-1',
            'mark-2',
            'mark-3',
            'selected',
            'whitelist',
            'blacklist',
            'industry',

            'latest_update',
            'sort-report',
            'sort-ass',
            'sort-equity',
            'sort-ass/equity',
            'sort-ass/real_cost',
            'sort-ass/turnover',
            'industry-ass/equity',

            'salary',
            'pe',
            'real_pe',
            'roe_parent',
            'plate-50',
        ]

        obj = QComboBox()
        # flags = list(map(lambda x: str(x), range(10)))
        flags = [
            '',
            '0_old',
            '1_selected',
            '2_hold',
            '3_random_s',
            '4_random_w-s',
            '5_random_a-w',
            '6',
            '7',
            '8',
        ]
        obj.addItems(flags)
        self.labels.append(QLabel('mission: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(str_flg)
        self.labels.append(QLabel('source: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('ids_names: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(str_flg)
        self.labels.append(QLabel('whitelist: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(str_flg)
        self.labels.append(QLabel('blacklist: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(str_flg)
        self.labels.append(QLabel('sort: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['', 'True', 'False'])
        self.labels.append(QLabel('reverse: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['', '0', '-1'])
        self.labels.append(QLabel('insert: '))
        self.editor.append(obj)

        obj = QComboBox()
        market_flag = [
            'all',
            'main',
            'non_main',
            'growth',
            'main+growth',
        ]
        obj.addItems(market_flag)
        self.labels.append(QLabel('market: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('timestamp: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['True', 'False'])
        self.labels.append(QLabel('random: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('pick_weight: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('interval: '))
        self.editor.append(obj)

        obj = QComboBox()
        mode_flag = [
            'normal',
            'selected',
            'whitelist+selected',
            'whitelist-selected',
            'all-whitelist',
        ]
        obj.addItems(mode_flag)
        self.labels.append(QLabel('mode: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('code_index: '))
        self.editor.append(obj)

        for row, label in enumerate(self.labels):
            editor = self.editor[row]

            label.setFont(QFont('Consolas', 14))
            editor.setFont(QFont('Consolas', 14))

            layout.addWidget(label, row, 0, alignment=Qt.AlignRight)
            layout.addWidget(editor, row, 1)

        self.button = QPushButton('Generate')
        self.button.setFont(QFont('Consolas', 14))

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.button)
        layout1.addStretch(1)

        v_layout.addStretch(1)
        v_layout.addLayout(layout, 0)
        v_layout.addLayout(layout1, 0)
        v_layout.addStretch(1)

        self.setLayout(h_layout)
        self.editor_dict = dict()
        self.init_editor_dict()
        self.load_editor_dict()

        self.button.clicked.connect(self.read_value)
        self.editor[0].currentIndexChanged.connect(self.mission_change)

    def init_editor_dict(self):
        self.editor_dict = {
            'mission': '',
            'source': '',
            'ids_names': '',
            'whitelist': '',
            'blacklist': '',

            'sort': '',
            'reverse': 'False',
            'insert': '',

            'market': 'all',
            'timestamp': '',

            'random': 'False',
            'pick_weight': '',
            'interval': '100',
            'mode': 'normal',

            'code_index': '0',
        }

    def load_editor_dict(self):
        tmp_list = list(self.editor_dict.values())
        for row, editor in enumerate(self.editor):
            if isinstance(editor, QComboBox):
                editor.setCurrentText(tmp_list[row])

            else:
                editor.setText(tmp_list[row])

    def read_value(self):
        self.values = []
        for editor in self.editor:
            if isinstance(editor, QComboBox):
                val = editor.currentText()
            else:
                val = editor.text()

            if val == '':
                val = None
            elif val == 'True':
                val = True
            elif val == 'False':
                val = False
            elif val.isdecimal():
                try:
                    val = int(val)
                except BaseException as e:
                    print(e)

            self.values.append(val)

        val = self.values[2]
        if val is not None:
            val = val.split(',')
            self.values[2] = val
        # print(self.values)

        args = self.values[1: -1]
        code_index = self.values[-1]
        # print(args)

        try:
            ret = sift_codes(*args)
            # print(ret, code_index)

            self.generate_signal.emit(ret, code_index)

            path = '..\\basicData\\tmp\\code_list_latest.txt'
            write_json_txt(path, ret)

            MainLog.add_log('generate code_list')

        except Exception as e:
            MainLog.add_log(e)

    def mission_change(self, txt):
        self.init_editor_dict()
        editor_dict = self.editor_dict
        mission = self.editor[0].currentText()
        # mission = str(txt)

        editor_dict['mission'] = mission
        print(mission)

        if mission == '0_old':
            editor_dict['source'] = 'old'

        elif mission == '1_selected':
            editor_dict['source'] = 'whitelist'
            editor_dict['sort'] = 'sort-ass/equity'

        elif mission == '2_hold':
            editor_dict['source'] = 'hold'

        elif mission == '3_random_s':
            editor_dict['source'] = 'selected'
            editor_dict['sort'] = 'sort-ass/equity'
            editor_dict['market'] = 'main+growth'

            editor_dict['random'] = 'True'
            editor_dict['interval'] = '20'
            editor_dict['mode'] = 'selected'

        elif mission == '4_random_w-s':
            editor_dict['source'] = 'all'
            editor_dict['sort'] = 'sort-ass/equity'
            editor_dict['market'] = 'main+growth'

            editor_dict['random'] = 'True'
            editor_dict['interval'] = '30'
            editor_dict['mode'] = 'whitelist-selected'

        elif mission == '5_random_a-w':
            editor_dict['source'] = 'real_pe'
            editor_dict['random'] = 'True'
            editor_dict['interval'] = '80'
            editor_dict['mode'] = 'all-whitelist'

        elif mission == '6':
            editor_dict['source'] = 'whitelist'
            editor_dict['sort'] = 'industry-ass/equity'
            editor_dict['code_index'] = '203'

        elif mission == '7':
            editor_dict['source'] = 'whitelist'
            editor_dict['blacklist'] = 'sort-ass/equity'
            editor_dict['market'] = 'growth'

        elif mission == '8':
            editor_dict['ids_names'] = '2-光伏设备'
            editor_dict['sort'] = 'real_pe'
            editor_dict['market'] = 'growth'

        self.load_editor_dict()


def test_code_list_view():
    import sys

    app = QApplication(sys.argv)

    code_list = sift_codes(source='all')
    codes_df = CodesDataFrame(code_list, 0)

    main = QStockListView(codes_df)
    # main = GenerateCodeListWidget()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_code_list_view()
    pass
