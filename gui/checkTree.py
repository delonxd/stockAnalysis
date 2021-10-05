from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.mainMethod import get_units_dict
import pandas as pd


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
        self.tree.update_signal.emit()

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

        if self.column == 'selected' and flag:
            # df0 = self.df[self.df['selected'] == True]
            if not self.df.loc[self.row, 'show_name']:
                self.df.loc[self.row, 'show_name'] = self.df.loc[self.row, 'txt_CN']
                a = self.df.loc[self.row]
                # print(type(a), '-->', a)

            self.df.loc[self.row, 'info_priority'] = self.df['info_priority'].max() + 1
            self.df.loc[self.row, self.column] = flag
            child = self.df.loc[self.row, 'child']
            self.tree.init_child(child, self.row)
        elif self.column == 'selected' and not flag:
            self.df.loc[self.row, 'info_priority'] = 0
            self.df.loc[self.row, self.column] = flag
            self.update_tree()
        else:
            self.df.loc[self.row, self.column] = flag
            self.update_tree()

    def update_tree(self):
        self.tree.update_signal.emit()


class CheckTree(QTreeWidget):
    update_signal = pyqtSignal()

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
        ]

        self.column_names = columns

        self.setColumnCount(len(columns))

        width_list = [180, 20, 70, 10, 40, 90, 50, 50, 40, 10, 30, 200, 20, 40]
        for idx, val in enumerate(width_list):
            self.setColumnWidth(idx, val)

        root = QRootItemDf(self)
        root.setText(0, 'root')
        root.df = df
        self.df = df

        for index, _ in self.df.iterrows():
            child = QItemDf(root)
            self.init_child(child, index)
            self.df.loc[index, 'child'] = child

        self.setHeaderLabels(columns)
        self.expandAll()
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.clicked.connect(self.tree_clicked)

    def update_tree(self):
        for index, _ in self.df.iterrows():
            child = self.df.loc[index, 'child']
            self.init_digit_item(child, index, 'scale_min')
            self.init_digit_item(child, index, 'scale_max')
            self.init_digit_item(child, index, 'scale_div')
            self.init_checkbox_item(child, index, 'logarithmic')
            self.init_digit_item(child, index, 'info_priority')

    def init_child(self, child, index):
        self.init_str_item(child, index, 'index_name')

        self.init_checkbox_item(child, index, 'selected')
        self.init_str_item(child, index, 'show_name')

        self.init_color_item(child, index, 'color')
        self.init_digit_item(child, index, 'line_thick')
        self.init_combobox_item(child, index, 'pen_style', combobox=PenStyleComboBox)

        self.init_digit_item(child, index, 'scale_min')
        self.init_digit_item(child, index, 'scale_max')
        self.init_digit_item(child, index, 'scale_div')
        self.init_checkbox_item(child, index, 'logarithmic')
        self.init_str_item(child, index, 'units')

        self.init_str_item(child, index, 'txt_CN')

        self.init_digit_item(child, index, 'info_priority')
        self.init_checkbox_item(child, index, 'default_ds')

    def init_color_item(self, child, index, column):
        pix = QPixmap(64, 64)
        pix.fill(self.df.loc[index, column])
        pos = self.column_names.index(column)
        child.setIcon(pos, QIcon(pix))

    def init_digit_item(self, child, index, column):
        value = str(self.df.loc[index, column])
        pos = self.column_names.index(column)
        child.setText(pos, value)

    def init_format_item(self, child, index, column, format_str: str):
        value = format_str.format(self.df.loc[index, column])
        pos = self.column_names.index(column)
        child.setText(pos, value)

    def init_repr_item(self, child, index, column):
        value = repr(self.df.loc[index, column])
        pos = self.column_names.index(column)
        child.setText(pos, value)

    def init_str_item(self, child, index, column):
        value = self.df.loc[index, column]
        pos = self.column_names.index(column)
        child.setText(pos, value)

    def init_checkbox_item(self, child, index, column):
        check_box = DataCheckBox()

        check_box.row = index
        check_box.column = column
        check_box.df = self.df
        check_box.tree = self
        check_box.setStyleSheet('QComboBox{margin:3px};')

        value = self.df.loc[index, column]
        check_box.setChecked(value)

        pos = self.column_names.index(column)
        self.setItemWidget(child, pos, check_box)

    def init_combobox_item(self, child, index, column, combobox):
        combo_box = combobox()

        combo_box.row = index
        combo_box.column = column
        combo_box.df = self.df
        combo_box.tree = self
        combo_box.setStyleSheet('QComboBox{margin:3px};')

        value = self.df.loc[index, column]
        combo_box.setCurrentText(combo_box.pen_dict[value])

        pos = self.column_names.index(column)
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
                self.update_signal.emit()

            elif column_name in ['line_thick', "scale_div", "info_priority"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')
                if text.isdigit():
                    df.loc[index_name, column_name] = int(text)
                    item.setText(column, text)
                    self.update_signal.emit()

            elif column_name in ["scale_min", "scale_max"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')
                try:
                    val = float(text)
                    df.loc[index_name, column_name] = val
                    item.setText(column, text)
                    self.update_signal.emit()

                except Exception as e:
                    print(e)

            elif column_name in ["show_name"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')
                df.loc[index_name, column_name] = text
                item.setText(column, text)
                self.update_signal.emit()

            elif column_name in ["units"]:
                text, _ = QInputDialog.getText(self, column_name, column_name + ': ')

                if text in get_units_dict().keys():
                    df.loc[index_name, column_name] = text
                    item.setText(column, text)
                    self.update_signal.emit()


if __name__ == '__main__':
    pass

