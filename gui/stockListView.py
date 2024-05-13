from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.fileMethod import *
from method.logMethod import MainLog
from method.sortCode import sift_codes
from method.showTable import generate_show_table

import pandas as pd
import numpy as np
import json
import re


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
        self.sort_list = [[[], []]]
        self.group_flag = 0
        self.current_index = 0

        self.load_code_list(code_list, current_index)

    def load_code_list(self, code_list, code_index):
        if self.df.size != 0:
            code = self.df.iloc[self.current_index, 0]
            self.index_list[self.group_flag] = code

        self.group_flag += 1
        if self.group_flag < len(self.group_list):
            self.group_list = self.group_list[:self.group_flag]
            self.index_list = self.index_list[:self.group_flag]
            self.sort_list = self.sort_list[:self.group_flag]

        self.group_list.append(code_list)
        self.index_list.append(0)
        self.sort_list.append([[], []])

        self.init_df()
        self.init_current_index(code_index)

    def init_df(self):
        columns, conditions = self.sort_list[self.group_flag]
        code_list = self.group_list[self.group_flag]

        self.df = self.df_all.loc[code_list, :].copy()

        if len(columns) > 0:
            by_columns = self.df.columns[columns].tolist()
            self.df = self.df.sort_values(by=by_columns, ascending=conditions)

        self.df.index = range(self.df.shape[0])

    def sort_column(self, column):
        columns, conditions = self.sort_list[self.group_flag]
        code = self.df.iloc[self.current_index, 0]

        if column in columns:
            index = columns.index(column)
            columns.pop(index)
            condition = conditions.pop(index)
            condition = False if condition is True else None
        else:
            condition = True

        if condition is not None:
            columns.insert(0, column)
            conditions.insert(0, condition)
        self.sort_list[self.group_flag] = [columns, conditions]

        self.init_df()
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
        code_index = self.index_list[self.group_flag]

        self.init_df()
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

        for i in range(6):
            self.setColumnWidth(i, 100)

        for i in range(6, 11):
            self.setColumnWidth(i, 70)

        columns, conditions = self.code_df.sort_list[self.code_df.group_flag]
        for i in range(column_size):
            if i in columns:
                condition = conditions[columns.index(i)]
                if condition is True:
                    color = Qt.red
                else:
                    color = Qt.green
            else:
                color = Qt.black
            self.horizontalHeaderItem(i).setForeground(QBrush(color))

        pos = row - 5 if row > 5 else 0
        self.verticalScrollBar().setSliderPosition(pos)
        self.selectRow(row)

    def on_double_clicked(self, item):
        row = item.row()
        column = item.column()

        level = column - 1
        if level in [1, 2, 3]:
            name = self.code_df.df.iloc[row, column]
            code = self.code_df.df.iloc[row, 0]

            src = 'ids:%s:%s' % (level, name)
            code_list = sift_codes(source=src)

            if len(code_list) > 0:
                MainLog.add_log('show industry --> %s' % src)
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

        self.code_df.sort_column(column)
        self.load_code_df()
        self.verticalScrollBar().setSliderPosition(0)
        self.horizontalScrollBar().setSliderPosition(pos)

        self.change_signal.emit(self.code_df.current_index)

    def selected_codes(self):
        rect = self.selectedRanges()[0]
        ret = []
        for row in range(rect.topRow(), rect.bottomRow() + 1):
            code = self.code_df.df.iloc[row, 0]
            ret.append(code)
        return ret


class QStockListView(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self, code_df):
        super().__init__()

        self.setWindowTitle('QTestWidget')
        # self.resize(800, 900)
        self.resize(1600, 900)

        self.table_view = QDataFrameTable(code_df)
        self.generate_widget = GenerateCodeListWidget(code_df)

        layout0 = QHBoxLayout()
        layout0.addStretch(1)

        self.button1 = QPushButton('<<')
        self.button2 = QPushButton('>>')
        self.button3 = QPushButton('加载')
        self.button4 = QPushButton('选择')
        self.button5 = QPushButton('添加')
        self.button6 = QPushButton('删除')

        layout0.addWidget(self.button1, 0)
        layout0.addWidget(self.button4, 0)
        layout0.addWidget(self.button3, 0)
        layout0.addWidget(self.button5, 0)
        layout0.addWidget(self.button6, 0)
        layout0.addWidget(self.button2, 0)

        layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(layout0)
        layout.addWidget(self.table_view)

        self.button1.clicked.connect(self.table_view.backward)
        self.button2.clicked.connect(self.table_view.forward)
        self.button3.clicked.connect(self.generate_widget.show)
        self.button4.clicked.connect(self.select_code)

        self.button5.clicked.connect(self.add_codes)
        self.button6.clicked.connect(self.del_codes)

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

    def get_tag(self):
        items = [
            '忽略',
            '电池',
            '光伏',
            '芯片',
        ]
        tag, _ = QInputDialog.getItem(self, '获取列表中的选项', '列表', items, editable=False)
        return tag

    def add_codes(self):
        codes = self.table_view.selected_codes()
        tag = self.get_tag()
        # tags_operate(codes, tag, 'add')

    def del_codes(self):
        codes = self.table_view.selected_codes()
        tag = self.get_tag()
        # tags_operate(codes, tag, 'del')

    def closeEvent(self, event):
        self.generate_widget.close()
        self.close_signal.emit(self)


class GenerateCodeListWidget(QWidget):
    generate_signal = pyqtSignal(object, object)

    def __init__(self, code_df):
        super().__init__()

        self.code_df = code_df
        self.setWindowTitle('GenerateCodeList')
        self.resize(600, 450)

        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        h_layout.addStretch(1)
        h_layout.addLayout(v_layout, 0)
        h_layout.addStretch(1)

        self.labels = []
        self.editor = []
        self.values = []

        layout = QGridLayout()
        layout.setColumnMinimumWidth(1, 500)

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
            '6_toc',
            '7_ids',
            '8_new_sifted',
            '9',
            '10_gui_rate_dv',
        ]
        obj.addItems(flags)
        obj.setMaxVisibleItems(20)
        self.labels.append(QLabel('mission: '))
        self.editor.append(obj)

        src_flg = [
            '',
            'auto_select',
            'old',
            'old_random',
            'all',
            'hold',

            # 'latest_update',
            # 'salary',
            # 'pe',
            # 'real_pe',
            # 'roe_parent',
            # 'plate-50',
        ]
        obj = QTextEdit()
        # obj = QComboBox()
        # obj.addItems(src_flg)
        obj.setFixedHeight(200)
        self.labels.append(QLabel('source: '))
        self.editor.append(obj)

        sort_flag = self.code_df.df_all.columns.tolist()
        obj = QComboBox()
        obj.addItems(sort_flag)
        self.labels.append(QLabel('sort: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['', 'true', 'false'])
        self.labels.append(QLabel('ascending: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['true', 'false'])
        self.labels.append(QLabel('sort_ids: '))
        self.editor.append(obj)

        obj = QComboBox()
        obj.addItems(['true', 'false'])
        self.labels.append(QLabel('random: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('interval: '))
        self.editor.append(obj)

        obj = QLineEdit()
        self.labels.append(QLabel('code_index: '))
        self.editor.append(obj)

        for row, label in enumerate(self.labels):
            editor = self.editor[row]

            label.setFont(QFont('Consolas', 13))
            editor.setFont(QFont('Consolas', 13))

            if row in [2, 3]:
                editor.setEditable(True)

            layout.addWidget(label, row, 0, alignment=Qt.AlignRight)
            layout.addWidget(editor, row, 1)

        self.button = QPushButton('Generate')
        self.button.setFont(QFont('Consolas', 14))

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.button)
        layout1.addStretch(1)

        v_layout.addStretch(1)
        v_layout.addLayout(layout, 1)
        v_layout.addLayout(layout1, 0)
        v_layout.addStretch(1)

        self.setLayout(h_layout)

        self.editor_dict = dict()
        self.init_editor_dict()
        self.load_editor_dict()

        self.button.clicked.connect(self.read_value)
        self.editor[0].activated.connect(self.mission_change)
        # self.editor[0].currentIndexChanged.connect(self.mission_change)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def init_editor_dict(self):
        self.editor_dict = {
            'mission': '',
            'source': '',
            'sort': '',
            'ascending': '',
            'sort_ids': 'false',
            'random': 'false',
            'interval': '100',
            'code_index': '0',
        }

    def load_editor_dict(self):
        tmp_list = list(self.editor_dict.values())
        for row, editor in enumerate(self.editor):
            if isinstance(editor, QComboBox):
                editor.setCurrentText(tmp_list[row])

            else:
                editor.setText(tmp_list[row])

    def read_text_edit_line(self):
        obj = self.editor[1]

        start = 0
        ret = []
        while True:
            cursor = obj.textCursor()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
            end = cursor.position()

            if start == end:
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                string = cursor.selectedText()
                ret.append(string)
                break
            string = cursor.selectedText()
            ret.append(string)
            start = end

        return ret

    def read_value(self):
        self.values = []

        for editor in self.editor:
            if isinstance(editor, QComboBox):
                val = editor.currentText()
            elif isinstance(editor, QTextEdit):
                # val = editor.toPlainText()
                str_list = self.read_text_edit_line()
                val = ''
                for string in str_list:
                    sub = re.sub(r'\u2029', '', string)
                    sub = re.sub(r' *$', '', sub)
                    val = val + sub
            else:
                val = editor.text()
            try:
                val = json.loads(val)
            except Exception as e:
                if val == '':
                    val = None

            self.values.append(val)

        MainLog.add_log('condition -> %s' % self.values)
        code_index = self.values[-1]

        source = self.values[1]
        source = '' if source is None else source
        kw = {
            'source': source,
            'sort': self.values[2],
            'ascending': self.values[3],
            'sort_ids': self.values[4],
            'random': self.values[5],
            'interval': self.values[6],
            'df_all': self.code_df.df_all,
        }

        try:
            ret = sift_codes(**kw)
            # print(ret, code_index)

            if len(ret) == 0:
                MainLog.add_log('generate error: code_list == []')
                return

            self.generate_signal.emit(ret, code_index)

            path = '..\\basicData\\tmp\\code_list_latest.txt'
            write_json_txt(path, ret)

            MainLog.add_log('generate code_list complete')

        except BaseException as e:
            MainLog.add_log(e.__repr__())

    def mission_change(self, txt):
        self.init_editor_dict()
        editor_dict = self.editor_dict
        mission = self.editor[0].currentText()
        # mission = str(txt)

        editor_dict['mission'] = mission
        MainLog.add_log('change mission --> %s' % mission)

        if mission == '0_old':
            # editor_dict['source'] = 'old'

            editor_dict['source'] = 'all-except[0]'
            editor_dict['sort'] = '["gui_rate_dv", "code"]'
            editor_dict['ascending'] = '[false, true]'

        elif mission == '1_selected':
            editor_dict['source'] = '白名单'
            editor_dict['sort'] = '["gui_rate", "predict_discount"]'
            editor_dict['ascending'] = '[false, false]'

        elif mission == '2_hold':
            editor_dict['source'] = 'hold'

        elif mission == '3_random_s':
            editor_dict['source'] = 'mkt:main&自选'
            editor_dict['sort'] = '["gui_rate", "predict_discount"]'
            editor_dict['ascending'] = '[false, false]'

            editor_dict['random'] = 'true'
            editor_dict['interval'] = '20'

        elif mission == '4_random_w-s':
            editor_dict['source'] = 'mkt:main&白名单-自选'
            editor_dict['sort'] = '["gui_rate", "predict_discount"]'
            editor_dict['ascending'] = '[false, false]'
            editor_dict['random'] = 'true'
            editor_dict['interval'] = '30'

        elif mission == '5_random_a-w':
            editor_dict['source'] = 'all-白名单'
            editor_dict['sort'] = 'real_pe_return_rate'
            editor_dict['ascending'] = 'false'
            editor_dict['random'] = 'true'
            editor_dict['interval'] = '80'

        elif mission == '6_toc':
            editor_dict['source'] = 'Toc'
            editor_dict['sort'] = '["gui_rate", "code"]'
            editor_dict['ascending'] = '[false, true]'

        elif mission == '7_ids':
            editor_dict['source'] = '白名单&mkt:main&cnd:gui_rate>=14\n' \
                                    '&ids:3:医疗研发外包'
            editor_dict['sort'] = '["gui_rate", "code"]'
            editor_dict['ascending'] = '[false, true]'

        elif mission == '8_new_sifted':
            editor_dict['source'] = '白名单&mkt:main&cnd:gui_rate>=12\n' \
                                    '&cnd:predict_discount>9\n' \
                                    '-光伏-电池-新上市\n' \
                                    '-backup:20230816:\n' \
                                    '{白名单&mkt:main&cnd:gui_rate>=13\n' \
                                    '&cnd:predict_discount>9\n' \
                                    '-光伏-电池-新上市}'

            editor_dict['sort'] = '["gui_rate", "code"]'
            editor_dict['ascending'] = '[false, true]'
            editor_dict['sort_ids'] = 'true'

        elif mission == '9':
            editor_dict['source'] = '白名单&mkt:main&cnd:gui_rate>=13\n' \
                                    '&cnd:predict_discount>7\n' \
                                    '-国有-光伏-电池-新上市\n' \
                                    '-ids:3:\n' \
                                    '{消费电子零部件及组装|印制电路板\n' \
                                    '|医疗研发外包|体外诊断|医疗耗材\n' \
                                    '|线下药店|化学制剂|中药\n' \
                                    '|IT服务|垂直应用软件|农药|快递}' \

            editor_dict['sort'] = '["gui_rate", "code"]'
            editor_dict['ascending'] = '[false, true]'
            editor_dict['sort_ids'] = 'true'

        elif mission == '10_gui_rate_dv':
            editor_dict['source'] = '白名单&mkt:main&cnd:gui_rate_dv>=12\n' \
                                    '&cnd:predict_discount>7\n' \
                                    '-光伏-电池-CRO-新上市\n' \

            editor_dict['sort'] = '["gui_rate_dv", "code"]'
            editor_dict['ascending'] = '[false, true]'

        self.load_editor_dict()


def test_code_list_view():
    import sys

    app = QApplication(sys.argv)

    code_list = sift_codes(source='hold')
    codes_df = CodesDataFrame(code_list, 0)

    main = QStockListView(codes_df)
    # main = GenerateCodeListWidget()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_code_list_view()
    pass
