from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.mainMethod import get_units_dict
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


if __name__ == '__main__':
    pass

