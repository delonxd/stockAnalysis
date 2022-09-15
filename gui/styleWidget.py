from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.mainMethod import get_units_dict
from gui.priorityTable import PriorityTable

import pandas as pd
import pickle
import time


class StyleTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 800)

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
            'units': 'str',
            'txt_CN': 'str',
            'default_ds': 'bool',
            'info_priority': 'digit',
            'ds_type': 'str',
            'delta_mode': 'bool',
            'ma_mode': 'digit',
            # 'pix1': 'checkbox',
            # 'pix2': 'checkbox',
            'pix3': 'bool',
            'pix4': 'bool',
        }

        self.pen_dict = {
            Qt.NoPen: 'NoPen',
            Qt.SolidLine: 'SolidLine',
            Qt.DashLine: 'DashLine',
            Qt.DotLine: 'DotLine',
            # Qt.DashDotLine: 'DashDotLine',
            # Qt.DashDotDotLine: 'DashDotDotLine',
            # Qt.CustomDashLine: 'CustomDashLine',
            # Qt.MPenStyle: 'MPenStyle',
        }

        self.bool_dict = {
            True: '√',
            False: '',
        }

        self.index_pos = dict()
        for i, value in enumerate(self.column_type):
            self.index_pos[value] = i

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
        self.setColumnWidth(0, 180)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(11, 200)

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
            'pix3',
            'pix4',
        ]:
            data = df.loc[index, column]
            flag = not data

            row = df.loc[index, :]
            if column == 'selected':
                if flag:
                    if not row['show_name']:
                        df.loc[index, 'show_name'] = row['txt_CN']
                        self.show_data(index, 'show_name')
                    pr = df['info_priority'].max() + 1
                else:
                    pr = 0
                df.loc[index, 'info_priority'] = pr
                self.show_data(index, 'info_priority')
                value = flag

            elif column == 'default_ds':
                if flag:
                    if row['selected'] is True:
                        df0 = df.loc[df['default_ds'] == True]
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
            value = QColorDialog.getColor()

        elif column in ['line_thick', 'scale_div', 'info_priority', 'ma_mode']:
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

    def __init__(self):
        super().__init__()
        # self.main_widget = main_widget
        self.button1 = QPushButton('刷新所有')
        self.button2 = QPushButton('刷新当前')
        self.button3 = QPushButton('加载默认')
        self.button4 = QPushButton('保存默认')
        self.button5 = QPushButton('优先级')

        # self.resize(1600, 900)

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.button1, 0, Qt.AlignCenter)
        layout1.addWidget(self.button2, 0, Qt.AlignCenter)
        layout1.addWidget(self.button3, 0, Qt.AlignCenter)
        layout1.addWidget(self.button4, 0, Qt.AlignCenter)
        layout1.addWidget(self.button5, 0, Qt.AlignCenter)
        layout1.addStretch(1)

        self.style_df = pd.DataFrame()
        self.style_table = StyleTable()

        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.style_table)
        self.setLayout(layout2)

        self.move(360, 80)
        self.button1.clicked.connect(self.refresh_all_pix)
        self.button2.clicked.connect(self.refresh_current_pix)
        self.button3.clicked.connect(self.load_default)
        self.button4.clicked.connect(self.save_default)
        self.button5.clicked.connect(self.config_priority)

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


def load_default_style():
    path = '../gui/styles/style_default.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)
    return df


def save_default_style(df):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    path1 = '../gui/styles/style_%s.pkl' % timestamp
    with open(path1, 'wb') as pk_f:
        pickle.dump(df, pk_f)

    path2 = '../gui/styles/style_default.pkl'
    with open(path2, 'wb') as pk_f:
        pickle.dump(df, pk_f)


if __name__ == '__main__':
    import sys
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    main = StyleWidget()
    main.show()
    # main.showMinimized()
    main.load_default()
    sys.exit(app.exec_())

    pass

