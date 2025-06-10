from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.mainMethod import get_units_dict
# from gui.priorityTable import PriorityTable
from method.fileMethod import load_json_txt
# from method.fileMethod import write_json_txt

import pandas as pd
import pickle
import time


class StyleTable(QTableWidget):
    def __init__(self):
        super().__init__()

        self.column_type = {
            'index_name': 'str',
            'selected': 'bool',
            'show_name': 'str',
            'color': 'color',
            'line_thick': 'digit',
            'pen_style': 'pen',
            'scale_min': 'digit',
            'scale_max': 'digit',
            'scale_div': 'digit',
            'logarithmic': 'bool',
            'delta_mode': 'bool',
            'ma_mode': 'digit',
            'units': 'str',
            'txt_CN': 'str',
            'info_priority': 'digit',
            'pix1': 'bool',
            'pix2': 'bool',
            'pix3': 'bool',
            'pix4': 'bool',
            'info1': 'bool',
            'info2': 'bool',
            'info3': 'bool',
            'info4': 'bool',
            'default_ds': 'bool',
            'ds_type': 'str',
            'frequency': 'str',
        }

        self.pen_dict = {
            Qt.PenStyle.NoPen: 'NoPen',
            Qt.PenStyle.SolidLine: 'SolidLine',
            Qt.PenStyle.DashLine: 'DashLine',
            Qt.PenStyle.DotLine: 'DotLine',
            # Qt.PenStyle.DashDotLine: 'DashDotLine',
            # Qt.PenStyle.DashDotDotLine: 'DashDotDotLine',
            # Qt.PenStyle.CustomDashLine: 'CustomDashLine',
            # Qt.PenStyle.MPenStyle: 'MPenStyle',
        }

        self.bool_dict = {
            True: '√',
            False: '',
        }

        # self.index_pos = dict()
        # for i, value in enumerate(self.column_type):
        #     self.index_pos[value] = i

        # self.column_names = self.column_type.keys()
        self.setColumnCount(len(self.column_type))

        # width_list = [180, 22, 70, 22, 22, 90, 50, 50, 40, 10, 30, 200, 20, 40, 50, 20, 20, 20, 20]
        # for idx, val in enumerate(width_list):
        #     self.setColumnWidth(idx, val)

        self.style_df = pd.DataFrame()

        self.setHorizontalHeaderLabels(self.column_type.keys())
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.clicked.connect(self.table_clicked)
        self.doubleClicked.connect(self.table_double_clicked)

    def init_style_df(self, style_df):
        self.style_df = df = style_df
        self.clear()

        self.setRowCount(df.shape[0])

        for i, index in enumerate(df.index):
            for j, tmp in enumerate(self.column_type.items()):
                column, typ = tmp
                data = df.loc[index, column]
                item = QTableWidgetItem()
                self.setItem(i, j, item)
                self.show_item(item, data, typ)

        self.resizeColumnsToContents()
        self.setHorizontalHeaderLabels(self.column_type.keys())
        self.setColumnWidth(0, 160)
        self.setColumnWidth(2, 180)
        self.setColumnWidth(13, 120)
        self.setColumnWidth(6, 60)
        self.setColumnWidth(7, 60)

    def get_item(self, index, column):
        df = self.style_df
        i = df.index.tolist().index(index)
        j = list(self.column_type.keys()).index(column)
        item = self.item(i, j)
        return item

    def show_data(self, index, column):
        df = self.style_df
        item = self.get_item(index, column)
        data = df.loc[index, column]
        typ = self.column_type[column]
        self.show_item(item, data, typ)

    def show_item(self, item, data, typ):
        if typ == 'str':
            item.setText(data)

        elif typ == 'digit':
            item.setText(str(data))

        elif typ == 'color':
            pix = QPixmap(64, 64)
            pix.fill(data)
            item.setIcon(QIcon(pix))

        elif typ == 'pen':
            txt = self.pen_dict[data]
            item.setText(txt)

        elif typ == 'bool':
            txt = self.bool_dict[data]
            item.setText(txt)

    def table_double_clicked(self, item):
        df = self.style_df

        i = item.row()
        j = item.column()

        index = df.index[i]
        column_label = list(self.column_type.keys())
        column = column_label[j]

        if column in [
            'selected',
            'logarithmic',
            'default_ds',
            'delta_mode',
            'pix1',
            'pix2',
            'pix3',
            'pix4',
            'info1',
            'info2',
            'info3',
            'info4',
        ]:
            data = df.loc[index, column]
            flag = not data

            row = df.loc[index, :]
            if column == 'selected':
                if flag:
                    if not row['show_name']:
                        df.loc[index, 'show_name'] = row['txt_CN']
                        self.show_data(index, 'show_name')
                #     pr = df['info_priority'].max() + 1
                # else:
                #     pr = 0
                # df.loc[index, 'info_priority'] = pr
                # self.show_data(index, 'info_priority')
                value = flag

            elif column == 'default_ds':
                if flag:
                    if row['selected']:
                        df0 = df.loc[df['default_ds'].isin([True])]
                        for index0 in df0.index:
                            df.loc[index0, 'default_ds'] = False
                            self.show_data(index0, 'default_ds')
                        value = True
                    else:
                        value = False
                else:
                    value = True
            else:
                value = flag

            df.loc[index, column] = value
            self.show_data(index, column)

    def table_clicked(self, item):
        df = self.style_df

        i = item.row()
        j = item.column()

        index = df.index[i]
        column_label = list(self.column_type.keys())
        column = column_label[j]

        title = index
        label = column + ': '
        ini = df.loc[index, column]

        value = None
        # print('index: %s, column: %s' % (index, column))

        if column in ['color']:
            value = QColorDialog.getColor(initial=ini)

        elif column in ['line_thick', 'scale_div', 'ma_mode']:
            text, _ = QInputDialog.getText(self, title, label)
            if text.isdigit():
                value = int(text)

        elif column in ['scale_min', 'scale_max']:
            text, _ = QInputDialog.getText(self, title, label)
            if text == 'auto':
                value = text
            else:
                try:
                    value = float(text)
                except Exception as e:
                    print(e)
                    return

        elif column in ['show_name']:
            value, _ = QInputDialog.getText(self, title, label, text=ini)

        elif column in ['units']:
            items = list(get_units_dict().keys())
            current = items.index(ini)
            value, _ = QInputDialog.getItem(self, title, label, items, current, False)

        elif column in ['pen_style']:
            value = self.item_dialog(title, label, self.pen_dict, ini)

        if value is not None:
            df.loc[index, column] = value
            self.show_data(index, column)

    def item_dialog(self, title, label, dict0, ini):
        items = list(dict0.values())
        current = items.index(dict0[ini])
        text, _ = QInputDialog.getItem(self, title, label, items, current, False)
        for key, value in dict0.items():
            if text == value:
                value = key
                return value


class StyleWidget(QWidget):
    signal_all = pyqtSignal(object)
    signal_cur = pyqtSignal(object)
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # self.main_widget = main_widget
        self.button1 = QPushButton('刷新所有')
        self.button2 = QPushButton('刷新当前')
        self.button3 = QPushButton('加载默认')
        self.button4 = QPushButton('保存默认')
        self.button5 = QPushButton('优先级')
        self.button6 = QPushButton('索引排序')
        self.button7 = QPushButton('添加行')
        self.button8 = QPushButton('删除行')

        self.setGeometry(380, 120, 1200, 800)

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        ali = Qt.AlignmentFlag.AlignCenter
        layout1.addWidget(self.button1, 0, ali)
        layout1.addWidget(self.button2, 0, ali)
        layout1.addWidget(self.button3, 0, ali)
        layout1.addWidget(self.button4, 0, ali)
        layout1.addWidget(self.button5, 0, ali)
        layout1.addWidget(self.button6, 0, ali)
        layout1.addWidget(self.button7, 0, ali)
        layout1.addWidget(self.button8, 0, ali)
        layout1.addStretch(1)

        self.style_df = pd.DataFrame()
        self.style_table = StyleTable()

        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.style_table)
        self.setLayout(layout2)

        self.button1.clicked.connect(self.refresh_all_pix)
        self.button2.clicked.connect(self.refresh_current_pix)
        self.button3.clicked.connect(self.load_default)
        self.button4.clicked.connect(self.save_default)
        self.button5.clicked.connect(self.config_priority)
        self.button6.clicked.connect(self.sort_index)
        self.button7.clicked.connect(self.add_row)
        self.button8.clicked.connect(self.drop_row)

    def refresh_style(self, new_df):
        if self.isHidden():
            return

        df1 = self.style_df
        df2 = new_df

        flag = df1.equals(df2)

        if not flag:
            self.style_df = new_df.copy()
            self.style_table.init_style_df(self.style_df)

    def refresh_all_pix(self):
        self.signal_all.emit(self.style_df)
        # print(self.style_df)

    def refresh_current_pix(self):
        # print(self.style_df.loc[:, 'pix4'])
        self.signal_cur.emit(self.style_df)

    def load_default(self):
        new_df = load_default_style()
        self.refresh_style(new_df)

    def save_default(self):
        df = self.style_df.copy()
        save_default_style(df)

    def config_priority(self):
        widget = PriorityTable(self.style_df)
        widget.update_style.connect(self.config_style_df)
        widget.exec()

    def config_style_df(self, df):
        new_df = self.style_df.copy()
        new_df.loc[df.index, 'info_priority'] = df.values
        self.refresh_style(new_df)

    def sort_index(self):
        widget = IndexTable(self.style_df)
        widget.update_style.connect(self.reindex)
        widget.exec()

    def reindex(self, index):
        new_df = self.style_df.copy()
        new_df = new_df.reindex(index)
        self.refresh_style(new_df)

    def add_row(self):
        df = self.style_df.copy()

        index_name, _ = QInputDialog.getText(self, '', '')
        if index_name in df.index:
            return
        items = [
            'bs-资产合计',
            'mvs-市值',
            's_016_roe_parent',
            's_027_pe_return_rate',
            's_040_profit_adjust2',
            's_051_core_profit',
        ]

        src, _ = QInputDialog.getItem(self, '', '', items, 0, False)
        if src not in df.index:
            return

        row = df.loc[[src], :].copy()

        row['default_ds'] = False
        row['selected'] = False

        row['show_name'] = index_name
        row['index_name'] = index_name

        row['txt_CN'] = index_name

        pr = df['info_priority'].max() + 1
        row['info_priority'] = pr

        # row['sql_type'] = ''
        # row['sheet_name'] = ''
        # row['api'] = ''

        row.index = [index_name]

        new_df = pd.concat([df, row])
        self.refresh_style(new_df)

    def drop_row(self):
        df = self.style_df.copy()

        index_name, _ = QInputDialog.getText(self, '', '')
        if index_name not in df.index:
            return
        new_df = df.drop(index_name)
        self.refresh_style(new_df)

    def closeEvent(self, event):
        self.close_signal.emit(self)


class PriorityTable(QDialog):
    update_style = pyqtSignal(object)

    def __init__(self, style_df):
        super().__init__()

        df = style_df.copy()
        df = df.loc[df['selected'].isin([True]), :].copy()

        self.columns = ['index_name', 'show_name', 'info_priority', 'txt_CN']
        self.df = df.loc[:, self.columns].copy()

        self.table_view = QTableView()
        self.button1 = QPushButton('up')
        self.button2 = QPushButton('down')
        self.button3 = QPushButton('submit')
        self.button4 = QPushButton('<<')
        self.button5 = QPushButton('>>')
        self.model = QStandardItemModel()

        self.load_df()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QTableViewDemo')
        self.resize(1200, 800)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.button4)
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)
        layout1.addWidget(self.button5)
        layout1.addWidget(self.button3)

        layout = QHBoxLayout()
        layout.addWidget(self.table_view)
        layout.addLayout(layout1)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setLayout(layout)
        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)
        self.button4.clicked.connect(self.on_button4_clicked)
        self.button5.clicked.connect(self.on_button5_clicked)

        self.table_view.setColumnWidth(0, 200)
        self.table_view.setColumnWidth(1, 400)
        self.table_view.setColumnWidth(2, 30)
        self.table_view.setColumnWidth(3, 400)

    def load_df(self):
        self.df = self.df.sort_values('info_priority')
        row = self.df.index.size
        self.model = QStandardItemModel(row, 3)

        self.model.setHorizontalHeaderLabels(self.columns)
        self.model.setVerticalHeaderLabels([str(i) for i in range(row)])

        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                value = self.df.iloc[i, j]

                item = QStandardItem(str(value))
                self.model.setItem(i, j, item)
        self.table_view.setModel(self.model)

    def on_button1_clicked(self):
        row1 = self.table_view.currentIndex().row()
        row2 = 0 if row1 == 0 else row1 - 1
        self.exchange_priority(row1, row2)

    def on_button2_clicked(self):
        size = self.df.index.size - 1
        row1 = self.table_view.currentIndex().row()
        row2 = size if row1 == size else row1 + 1
        self.exchange_priority(row1, row2)

    def on_button4_clicked(self):
        for _ in range(10):
            self.on_button1_clicked()

    def on_button5_clicked(self):
        for _ in range(10):
            self.on_button2_clicked()

    def exchange_priority(self, row1, row2):
        priority1 = self.df.iloc[row1, 2]
        priority2 = self.df.iloc[row2, 2]
        self.df.iloc[row1, 2] = priority2
        self.df.iloc[row2, 2] = priority1
        self.load_df()
        self.table_view.selectRow(row2)

    def on_button3_clicked(self):
        df = self.df['info_priority']

        self.update_style.emit(df)


class IndexTable(QDialog):
    update_style = pyqtSignal(object)

    def __init__(self, style_df):
        super().__init__()

        self.columns = ['index_name', 'show_name']
        self.df = style_df.loc[:, self.columns].copy()

        self.table_view = QTableView()
        self.button1 = QPushButton('<<')
        self.button2 = QPushButton('up')
        self.button3 = QPushButton('down')
        self.button4 = QPushButton('>>')
        self.button5 = QPushButton('submit')
        self.model = QStandardItemModel()

        self.load_df()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('IndexTable')
        self.resize(500, 700)

        layout1 = QVBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)
        layout1.addWidget(self.button3)
        layout1.addWidget(self.button4)
        layout1.addWidget(self.button5)
        layout1.addStretch(1)

        layout = QHBoxLayout()
        layout.addWidget(self.table_view)
        layout.addLayout(layout1)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setLayout(layout)
        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)
        self.button4.clicked.connect(self.on_button4_clicked)
        self.button5.clicked.connect(self.on_button5_clicked)

    def load_df(self):
        row = self.df.index.size
        self.model = QStandardItemModel(row, 2)

        self.model.setHorizontalHeaderLabels(self.columns)
        self.model.setVerticalHeaderLabels([str(i) for i in range(row)])

        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                value = self.df.iloc[i, j]
                item = QStandardItem(str(value))
                self.model.setItem(i, j, item)
        self.table_view.setModel(self.model)
        self.table_view.setColumnWidth(0, 150)
        self.table_view.setColumnWidth(1, 150)

    def on_button1_clicked(self):
        for _ in range(10):
            self.on_button2_clicked()

    def on_button2_clicked(self):
        row1 = self.table_view.currentIndex().row()
        row2 = 0 if row1 == 0 else row1 - 1
        self.exchange_index(row1, row2)

    def on_button3_clicked(self):
        size = self.df.index.size - 1
        row1 = self.table_view.currentIndex().row()
        row2 = size if row1 == size else row1 + 1
        self.exchange_index(row1, row2)

    def on_button4_clicked(self):
        for _ in range(10):
            self.on_button3_clicked()

    def exchange_index(self, row1: int, row2: int):
        index = list(self.df.index)

        index_name = index.pop(row1)
        index.insert(row2, index_name)

        self.df = self.df.reindex(index)
        self.load_df()
        self.table_view.selectRow(row2)

    def on_button5_clicked(self):
        index = self.df.index.copy()
        self.update_style.emit(index)


def load_default_style() -> pd.DataFrame:
    path = '../gui/styles/style_default.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)
    return df


def save_default_style(df: pd.DataFrame):
    check_style_df(df)

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    path1 = '../gui/styles/style_backups/style_%s.pkl' % timestamp
    with open(path1, 'wb') as pk_f:
        pickle.dump(df, pk_f)

    path2 = '../gui/styles/style_default.pkl'
    with open(path2, 'wb') as pk_f:
        pickle.dump(df, pk_f)


def check_style_df(df: pd.DataFrame):

    default_df = df.loc[df['default_ds'].isin([True]), :].copy()
    if default_df.shape[0] != 1:
        raise KeyboardInterrupt('style_df格式错误：存在两个default_ds')

    dup_index = df.loc[df.index.duplicated()].copy()
    if dup_index.shape[0] > 0:
        raise KeyboardInterrupt('style_df格式错误：重复的index名称')

    df0 = df.loc[df['info_priority'].duplicated()].copy()
    if df0.shape[0] > 0:
        raise KeyboardInterrupt('style_df格式错误：重复的info_priority')

    col = df['info_priority'].copy()
    if not col.apply(lambda x: isinstance(x, int)).all():
        raise KeyboardInterrupt('style_df格式错误：info_priority存在非整数项')
    # print(df)


def resort_info_priority():
    df = load_default_style()
    df1 = df.loc[df['selected'].isin([True]), :].copy()

    table = df1['info_priority'].copy().to_dict()
    lst = []
    for key, val in table.items():
        lst.append([val, key])
    lst.sort()
    lst = list(zip(*lst))
    lst = list(lst[1])

    df2 = df.loc[df['selected'].isin([False]), :].copy()
    lst2 = df2.index.to_list()
    lst.extend(lst2)

    df_pr = pd.Series(range(1, len(lst)+1), index=lst)
    df['info_priority'] = df_pr

    # check_style_df(df)


def add_futures_style_df():

    from method.fileMethod import load_pkl
    path = "..\\basicData\\futures\\futures_prices_history.pkl"
    df = load_pkl(path, log=False)
    df = df.dropna(axis=0, how='all')
    columns = []

    for index, val in enumerate(df.columns.tolist()):
        str1 = str(index + 1).rjust(2, '0')
        str2 = val.split('_')[0]
        str3 = val.split('_')[1]
        # column = 'futures_%s_%s' % (str1, str2)
        columns.append((str1, str2, str3))

    df = load_default_style()

    key_list = df.index.tolist()

    futures_style = dict()
    for index in df.index.tolist():
        if index[:7] == 'futures':
            row = df.loc[[index], :].copy()
            key = index.split('_')[2]
            futures_style[key] = row
            key_list.pop(key_list.index(index))

    df = df.reindex(index=key_list)

    index_list = []
    for str1, str2, str3 in columns:
        index_name = 'futures_%s_%s' % (str1, str2)
        index_list.append(index_name)

        show_name = 'f_0%s (期货) %s' % (str1, str3)

        if str2 in futures_style.keys():
            row = futures_style[str2]
        else:
            row = futures_style['V0']
            row['default_ds'] = False
            row['selected'] = False
            # todo
            row['info_priority'] = None

        row['show_name'] = show_name
        row['index_name'] = index_name
        row['txt_CN'] = index_name

        row.index = [index_name]
        df = pd.concat([df, row])

    reindex_list = []
    for index in key_list:
        reindex_list.append(index)

        if index == 'eq_002_rate':
            reindex_list.extend(index_list)

    # df = df.reindex(index=reindex_list)


# def config_data_method2_style():
#     from method.fileMethod import load_json_txt
#     df = load_default_style()
#     # print(df)
#
#     d_total = dict()
#     path = '../basicData/mappingTable/fs_m_table_cn_non_financial.txt'
#     d1 = load_json_txt(path, log=False)
#     for key, value in d1.items():
#         d_total[value] = key
#
#     path = '../basicData/mappingTable/mvs_m_table_cn.txt'
#     d2 = load_json_txt(path, log=False)
#
#     for key, value in d2.items():
#         d_total[value] = key
#
#     # key_list = df.index.tolist()
#     del_list = [
#         'first_update_fs',
#         'last_update_fs',
#         'stockCode_fs',
#         'currency',
#         'standardDate',
#         'reportDate',
#         'reportType',
#         'date_fs',
#         'first_update_mvs',
#         'last_update_mvs',
#         'stockCode_mvs',
#         'date_mvs',
#     ]
#
#     row_list = []
#     for index in df.index.tolist():
#         row = df.loc[[index], :].copy()
#         if index[:3] == 'id_':
#             index_name = row['index_name'].iloc[0]
#
#             if index_name in d_total.keys():
#                 row['index_name'] = d_total[index_name]
#                 row_list.append(row)
#         else:
#             if index not in del_list:
#                 row_list.append(row)
#     ret = pd.concat(row_list)
#     ret.index = ret['index_name'].values
#     save_default_style(ret)


# def config_data_method3_style():
#     from method.fileMethod import load_json_txt, write_json_txt
#
#     df = load_default_style()
#
#     # path = '../gui/styles/style_df_index3.txt'
#     # index = load_json_txt(path)
#     # df.index = index
#     # df['index_name'] = index
#     #
#     # save_default_style(df)
#
#     index = list(df.index)
#     path = '../gui/styles/style_df_index.txt'
#     write_json_txt(path, index)


# def config_data_style_index():
#     from method.fileMethod import load_json_txt, write_json_txt
#     path = '../gui/styles/style_df_index.txt'
#     index = load_json_txt(path)
#
#     path = '../basicData/mappingTable/fs_m_table_cn_bank.txt'
#     m_table = load_json_txt(path)
#
#     ret = []
#     for key in m_table.keys():
#         if key not in index:
#             ret.append(key)
#     path = '../gui/styles/style_df_index_add_bank.txt'
#     write_json_txt(path, ret)


# def add_style_df_bank():
#     from method.fileMethod import load_json_txt, write_json_txt
#     df = load_default_style()
#     df = df.drop(['sql_type', 'sheet_name', 'api'], axis=1)
#
#     path = '../gui/styles/style_df_index.txt'
#     index_list = load_json_txt(path)
#
#     row_default = df.loc[['cfs-附注'], :].copy()
#
#     ret = pd.DataFrame(columns=df.columns)
#     for index in index_list:
#         if index in df.index:
#             row_df = df.loc[[index], :].copy()
#         else:
#             row_df = row_default.copy()
#             row_df.index = [index]
#             row_df.loc[index, 'index_name'] = index
#
#             show_name = index.split('-')[-1]
#             show_name = '(银行)%s' % show_name
#             row_df.loc[index, 'show_name'] = show_name
#             row_df.loc[index, 'txt_CN'] = show_name
#
#             # print(row_df)
#
#         ret = pd.concat([ret, row_df], axis=0)
#     # print(ret)
#     # print(row_default)


# def test():
#     from method.fileMethod import load_pkl
#     path = '../gui/styles/style_tmp/style_default_data_method1.pkl'
#     df = load_pkl(path)
#     print(df)
#     # for index, row in df.iterrows():
#     #     if row['selected'] == True:
#     #         print(row['index_name'], row['show_name'])

def add_style_df_hk():
    df = load_default_style()

    path = '../basicData/mappingTable/fs_m_table_hk_004.txt'
    table = load_json_txt(path)

    row_default = df.loc[['cfs-附注'], :].copy()

    # print(df.index)

    add_df = pd.DataFrame(columns=df.columns)
    for index in table.keys():
        if index in df.index:
            # row_df = df.loc[[index], :].copy()
            # print(index)
            continue
        else:
            row_df = row_default.copy()
            row_df.index = [index]
            row_df.loc[index, 'index_name'] = index

            lst = index.split('-')
            sheet = lst[0]

            if sheet not in ['bs', 'ps', 'cfs']:
                continue

            show_name = '-'.join(lst[1:])
            show_name = '(HK)%s' % show_name

            row_df.loc[index, 'show_name'] = show_name
            row_df.loc[index, 'txt_CN'] = show_name

            # print(row_df)

        add_df = pd.concat([add_df, row_df], axis=0)

    ret = pd.DataFrame(columns=df.columns)
    for index in df.index:
        row = df.loc[[index], :].copy()
        ret = pd.concat([ret, row], axis=0)

        if index == 'cfs-融资租入固定资产':
            ret = pd.concat([ret, add_df], axis=0)

    print(ret)

    # save_default_style(ret)


def copy_row_style():
    # table = {
    #     'bs-物业厂房及设备': 'bs-固定资产',
    # }

    path = '../gui/styles/copy_row_style_table.txt'
    table = load_json_txt(path)

    df = load_default_style()
    for index1, index2 in table.items():
        if index2 is None:
            continue
        row1 = df.loc[index1, :].copy()
        row2 = df.loc[index2, :].copy()

        for col_name in row1.index:
            if col_name not in [
                'default_ds',
                'show_name',
                'index_name',
                'info_priority',
                'txt_CN',
            ]:
                row1[col_name] = row2[col_name]
        print(index1, index2)

        df.loc[index1, :] = row1

    pr_lst = df.sort_values(by='info_priority').index.tolist()

    for index1, index2 in table.items():
        if index2 is None:
            continue
        print(index1, index2)

        pr_lst.pop(pr_lst.index(index1))
        pos = pr_lst.index(index2) + 1
        pr_lst.insert(pos, index1)

    df_pr = pd.Series(range(1, len(pr_lst)+1), index=pr_lst)
    df['info_priority'] = df_pr


# def test001():
#     df = load_default_style()
#
#     ret = dict()
#     for index, row in df.iterrows():
#         txt = row['txt_CN']
#         if txt[:4] == '(HK)':
#             ret[index] = None
#
#     path = '../gui/styles/copy_row_style_table.txt'
#     write_json_txt(path, ret)


if __name__ == '__main__':
    import sys

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    main = StyleWidget()
    main.show()
    # main.showMinimized()
    main.load_default()
    sys.exit(app.exec_())
    pass
