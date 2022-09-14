from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.mainMethod import get_units_dict
from gui.styleDataFrame import load_default_style, save_default_style
from gui.priorityTable import PriorityTable

import pandas as pd
import time


class QItemDf(QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def df(self):
        return self.parent().df


class QRootItemDf(QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.df = None


class PenStyleComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        self.row = None
        self.column = None
        self.df = None
        self.tree = None

        for txt in self.pen_dict.values():
            self.addItem(txt)

        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self):
        txt = self.currentText()
        pen_style = 1
        for key, value in self.pen_dict.items():
            if txt == value:
                pen_style = key
                break

        self.df.loc[self.row, self.column] = pen_style
        self.update_tree()

    def update_tree(self):
        self.tree.update_style.emit()

    def wheelEvent(self, e):
        pass


class DataCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.row = None
        self.column = None
        self.df = None
        self.tree = None

        self.clicked.connect(self.self_clicked)

    def self_clicked(self):
        flag = self.isChecked()
        index = self.row

        if self.column == 'selected' and flag:
            # df0 = self.df[self.df['selected'] == True]
            if not self.df.loc[index, 'show_name']:
                self.df.loc[index, 'show_name'] = self.df.loc[index, 'txt_CN']

            self.df.loc[index, ['info_priority', self.column]] = [self.df['info_priority'].max() + 1, flag]

            row = self.df.loc[index]
            child = row['child']
            self.tree.init_child(child, index, row)
            self.update_tree()

        elif self.column == 'selected' and not flag:
            self.df.loc[index, ['info_priority', self.column]] = [0, flag]

            row = self.df.loc[index]
            child = row['child']
            self.tree.init_digit_item(child, row, 'info_priority')

            self.update_tree()

        elif self.column == 'default_ds' and flag:
            if self.df.loc[index, 'selected'] == True:
                if self.df.loc[index, 'ds_type'] == 'digit':
                    row_df = self.df.loc[self.df['default_ds'] == True]

                    self.df['default_ds'] = False
                    for _, row in row_df.iterrows():
                        child = row['child']
                        pos = self.tree.index_pos['default_ds']
                        checkbox = self.tree.itemWidget(child, pos)
                        checkbox.setChecked(False)

                    self.df.loc[index, 'default_ds'] = flag
                    self.update_tree()
                    return

            self.setChecked(False)
            return

        elif self.column == 'default_ds' and not flag:
            self.setChecked(True)

        else:
            self.df.loc[index, self.column] = flag
            self.update_tree()

    def update_tree(self):
        self.tree.update_style.emit()


class CheckTree(QTreeWidget):
    update_style = pyqtSignal()

    def __init__(self, df: pd.DataFrame):
        super().__init__()

        columns = [
            'index_name',
            'selected',
            'show_name',

            'color',
            'line_thick',
            'pen_style',

            'scale_min',
            'scale_max',
            'scale_div',
            'logarithmic',
            'units',

            'txt_CN',

            'default_ds',
            'info_priority',

            'ds_type',
            'delta_mode',

            'ma_mode',
        ]

        self.index_pos = dict()
        for i, value in enumerate(columns):
            self.index_pos[value] = i

        self.column_names = columns
        self.setColumnCount(len(columns))

        width_list = [180, 20, 70, 10, 40, 90, 50, 50, 40, 10, 30, 200, 20, 40, 50, 20, 20]
        for idx, val in enumerate(width_list):
            self.setColumnWidth(idx, val)

        root = QRootItemDf(self)
        root.setText(0, 'root')
        root.df = df
        self.df = df

        child_list = list()
        # self.df['child'] = QItemDf(root)
        for index, row in self.df.iterrows():
            child = QItemDf(root)
            self.init_child(child, index, row)
            child_list.append(child)
        self.df['child'] = child_list

        self.setHeaderLabels(columns)
        self.expandAll()
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.clicked.connect(self.tree_clicked)

        self.setMinimumSize(1200, 800)

    def update_tree(self):

        row_df = self.df.loc[self.df['selected'] == True]

        for index, row in row_df.iterrows():
            child = row['child']

            self.init_digit_item(child, row, 'scale_min')
            self.init_digit_item(child, row, 'scale_max')

        #     self.init_digit_item(child, row, 'scale_div')
        #     self.init_checkbox_item(child, index, row, 'logarithmic')
        #     self.init_str_item(child, row, 'units')
        #
        #     self.init_digit_item(child, row, 'info_priority')
        #     self.init_checkbox_item(child, index, row, 'default_ds')
        #
        #     self.init_digit_item(child, row, 'ma_mode')
        # self.update()

    def init_child(self, child, index, row):
        self.init_str_item(child, row, 'index_name')

        self.init_checkbox_item(child, index, row, 'selected')
        self.init_str_item(child, row, 'show_name')

        self.init_color_item(child, row, 'color')
        self.init_digit_item(child, row, 'line_thick')
        self.init_combobox_item(child, index, row, 'pen_style', combobox=PenStyleComboBox)

        self.init_digit_item(child, row, 'scale_min')
        self.init_digit_item(child, row, 'scale_max')
        self.init_digit_item(child, row, 'scale_div')
        self.init_checkbox_item(child, index, row, 'logarithmic')
        self.init_str_item(child, row, 'units')

        self.init_str_item(child, row, 'txt_CN')

        self.init_digit_item(child, row, 'info_priority')
        self.init_checkbox_item(child, index, row, 'default_ds')

        self.init_str_item(child, row, 'ds_type')
        self.init_checkbox_item(child, index, row, 'delta_mode')

        self.init_digit_item(child, row, 'ma_mode')

    def init_color_item(self, child, row, column):
        pix = QPixmap(64, 64)
        pix.fill(row[column])
        pos = self.index_pos[column]
        child.setIcon(pos, QIcon(pix))

    def init_digit_item(self, child, row, column):
        value = str(row[column])
        pos = self.index_pos[column]
        child.setText(pos, value)

    def init_str_item(self, child, row, column):
        value = row[column]
        pos = self.index_pos[column]
        child.setText(pos, value)

    def init_checkbox_item(self, child, index, row, column):
        check_box = DataCheckBox()

        check_box.row = index
        check_box.column = column
        check_box.df = self.df
        check_box.tree = self
        check_box.setStyleSheet('QComboBox{margin:3px};')

        value = row[column]
        pos = self.index_pos[column]

        check_box.setChecked(value)
        self.setItemWidget(child, pos, check_box)

    def init_combobox_item(self, child, index, row, column, combobox):
        combo_box = combobox()

        combo_box.row = index
        combo_box.column = column
        combo_box.df = self.df
        combo_box.tree = self
        combo_box.setStyleSheet('QComboBox{margin:3px};')

        value = row[column]
        pos = self.index_pos[column]

        combo_box.setCurrentText(combo_box.pen_dict[value])
        self.setItemWidget(child, pos, combo_box)

    def tree_clicked(self, index):

        item = self.currentItem()
        column = index.column()
        column_name = self.column_names[column]

        index_list = self.df.index.values.tolist()
        index_name = index_list[index.row()]

        if isinstance(item, QItemDf):
            df = self.df

            if column_name in ['color']:
                color = QColorDialog.getColor()
                pix = QPixmap(64, 64)
                pix.fill(color)
                item.setIcon(column, QIcon(pix))
                df.loc[index_name, column_name] = color
                self.update_style.emit()

            elif column_name in ['line_thick', "scale_div", "info_priority", "ma_mode"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')
                if text.isdigit():
                    df.loc[index_name, column_name] = int(text)
                    item.setText(column, text)
                    self.update_style.emit()

            elif column_name in ["scale_min", "scale_max"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')
                try:
                    if text == 'auto':
                        val = text
                    else:
                        val = float(text)
                    df.loc[index_name, column_name] = val
                    item.setText(column, text)
                    self.update_style.emit()

                except Exception as e:
                    print(e)

            elif column_name in ["show_name"]:
                ini = df.loc[index_name, column_name]
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ', text=ini)
                df.loc[index_name, column_name] = text
                item.setText(column, text)
                self.update_style.emit()

            elif column_name in ["units"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')

                if text in get_units_dict().keys():
                    df.loc[index_name, column_name] = text
                    item.setText(column, text)
                    self.update_style.emit()


class StyleTreeChild(QTreeWidgetItem):
    def __init__(self, parent, row_data):
        super().__init__(parent)
        self.row_data = row_data


class StyleTreeCheckBox(QCheckBox):
    def __init__(self, parent_item, column, tree):
        super().__init__()
        self.parent_item = parent_item
        self.column = column
        self.tree = tree

        self.clicked.connect(self.self_clicked)

    def self_clicked(self):
        flag = self.isChecked()
        tree = self.tree
        df = self.tree.style_df

        child = self.parent_item
        row = child.row_data
        column = self.column

        if column == 'selected':
            if flag:
                if not row['show_name']:
                    row['show_name'] = row['txt_CN']
                pr = df['info_priority'].max()
            else:
                pr = 0
            row['info_priority', 'selected'] = pr, flag

            tree.show_item(child, 'show_name', 'str')
            tree.show_item(child, 'info_priority', 'digit')

        elif column == 'default_ds':
            if flag:
                if row['selected'] is True:
                    row0 = df.loc[df['default_ds'] == True]
                    for index in row0.index:
                        child0 = tree.child_dict[index]
                        child0.row_data['default_ds'] = False
                        tree.show_item(child0, 'default_ds', typ='checkbox')

                    row['default_ds'] = True
                    tree.show_item(child, 'default_ds', 'checkbox')
                else:
                    self.setChecked(False)

            else:
                self.setChecked(True)

        else:
            row[column] = flag


class StyleTreeComboBox(QComboBox):
    def __init__(self, parent_item, column):
        super().__init__()
        self.parent_item = parent_item
        self.column = column

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
        for txt in self.pen_dict.values():
            self.addItem(txt)

        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self):
        txt = self.currentText()
        pen_style = 1
        for key, value in self.pen_dict.items():
            if txt == value:
                pen_style = key
                break
        self.parent_item.row_data[self.column] = pen_style

    def wheelEvent(self, e):
        pass


class StyleTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 800)

        self.column_type = {
            'index_name': 'str',
            'selected': 'checkbox',
            'show_name': 'str',
            'color': 'color',
            'line_thick': 'digit',
            'pen_style': 'combobox',
            'scale_min': 'digit',
            'scale_max': 'digit',
            'scale_div': 'digit',
            'logarithmic': 'checkbox',
            'units': 'str',
            'txt_CN': 'str',
            'default_ds': 'checkbox',
            'info_priority': 'digit',
            'ds_type': 'str',
            'delta_mode': 'checkbox',
            'ma_mode': 'digit',
        }

        self.index_pos = dict()
        for i, value in enumerate(self.column_type):
            self.index_pos[value] = i

        # self.column_names = self.column_type.keys()
        self.setColumnCount(len(self.column_type))

        width_list = [180, 20, 70, 10, 40, 90, 50, 50, 40, 10, 30, 200, 20, 40, 50, 20, 20]
        for idx, val in enumerate(width_list):
            self.setColumnWidth(idx, val)

        self.style_df = pd.DataFrame()
        self.child_dict = {}

        self.setHeaderLabels(self.column_type)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.clicked.connect(self.tree_clicked)

    def init_style_df(self, style_df):
        self.style_df = style_df
        self.show_style_df()
        self.expandAll()

    def show_style_df(self):
        df = self.style_df
        self.clear()
        self.child_dict.clear()

        root = QRootItemDf(self)
        root.setText(0, 'root')
        root.df = df

        for index, row in df.iterrows():
            child = StyleTreeChild(root, row)
            self.child_dict[index] = child
            for key, value in self.column_type.items():
                self.show_item(child, key, typ=value)

    def show_item(self, child, column, typ):
        row = child.row_data
        pos = self.index_pos[column]
        data = row[column]

        if typ == 'str':
            child.setText(pos, data)

        elif typ == 'digit':
            child.setText(pos, str(data))

        elif typ == 'color':
            pix = QPixmap(64, 64)
            pix.fill(data)
            child.setIcon(pos, QIcon(pix))

        elif typ == 'checkbox':
            check_box = StyleTreeCheckBox(child, column, self)
            check_box.setStyleSheet('QComboBox{margin:3px};')
            check_box.setChecked(data)
            self.setItemWidget(child, pos, check_box)

        elif typ == 'combobox':
            combo_box = StyleTreeComboBox(child, column)
            combo_box.setStyleSheet('QComboBox{margin:3px};')
            combo_box.setCurrentText(combo_box.pen_dict[data])
            self.setItemWidget(child, pos, combo_box)

    def tree_clicked(self, index):
        child = self.currentItem()
        column_label = list(self.column_type.keys())
        column = column_label[index.column()]
        typ = self.column_type[column]

        if isinstance(child, StyleTreeChild):
            index = child.row_data.name

            # print('index: %s, column: %s' % (index, column))

            if column in ['color']:
                color = QColorDialog.getColor()
                child.row_data[column] = color
                self.show_item(child, column, typ)

            elif column in ['line_thick', "scale_div", "info_priority", "ma_mode"]:
                text, _ = QInputDialog.getText(self, column, column + ': ')
                if text.isdigit():
                    child.row_data[column] = int(text)
                    self.show_item(child, column, typ)

            elif column in ["scale_min", "scale_max"]:
                text, _ = QInputDialog.getText(self, column, column + ': ')
                if text == 'auto':
                    val = text
                else:
                    try:
                        val = float(text)
                    except Exception as e:
                        print(e)
                        return
                child.row_data[column] = val
                self.show_item(child, column, typ)

            elif column in ["show_name"]:
                ini = child.row_data[column]
                text, _ = QInputDialog.getText(self, column, column + ': ', text=ini)
                child.row_data[column] = text
                self.show_item(child, column, typ)

            elif column in ["show_name"]:
                ini = child.row_data[column]
                text, _ = QInputDialog.getText(self, column, column + ': ', text=ini)

                if text in get_units_dict().keys():
                    child.row_data[column] = text
                    self.show_item(child, column, typ)


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
        self.style_tree = StyleTree()

        layout2 = QVBoxLayout()
        layout2.addLayout(layout1)
        layout2.addWidget(self.style_tree)
        self.setLayout(layout2)

        self.move(360, 80)
        self.button1.clicked.connect(self.refresh_all_pix)
        self.button2.clicked.connect(self.refresh_current_pix)
        self.button3.clicked.connect(self.load_default)
        self.button4.clicked.connect(self.save_default)
        self.button5.clicked.connect(self.config_priority)

    def refresh_style(self, new_df):
        df1 = self.style_df
        df2 = new_df

        flag = df1.equals(df2)

        if not flag:
            self.style_df = new_df.copy()
            self.style_tree.init_style_df(new_df)

    def refresh_all_pix(self):
        self.signal_all.emit(self.style_df)
        # print(self.style_df)

    def refresh_current_pix(self):
        self.signal_cur.emit(self.style_df)
        # print(self.style_df)

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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    main = StyleWidget()
    main.load_default()
    # main.show()
    main.showMinimized()
    sys.exit(app.exec_())

    pass

