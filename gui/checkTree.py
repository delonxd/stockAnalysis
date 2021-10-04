from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
        self.df.loc[self.row, self.column] = self.isChecked()
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
            # 'format_fun',
            'txt_CN',
        ]

        self.column_names = columns

        self.setColumnCount(len(columns))

        width_list = [200, 20, 70, 10, 40, 90, 70, 70, 40, 10, 200]
        for idx, val in enumerate(width_list):
            self.setColumnWidth(idx, val)

        root = QRootItemDf(self)
        root.setText(0, 'root')
        root.df = df
        self.df = df

        for index, row in self.df.iterrows():
            child = QItemDf(root)

            # child.setText(0, row['index_name'])
            self.init_str_item(child, index, 'index_name')
            self.init_checkbox_item(child, index, 'selected')
            self.init_str_item(child, index, 'show_name')
            self.init_color_item(child, index, 'color')
            self.init_digit_item(child, index, 'line_thick')
            self.init_combobox_item(child, index, 'pen_style', combobox=PenStyleComboBox)

            self.init_format_item(child, index, 'scale_min', '{:.3e}')
            self.init_format_item(child, index, 'scale_max', '{:.3e}')
            self.init_digit_item(child, index, 'scale_div')
            self.init_checkbox_item(child, index, 'logarithmic')
            # self.init_repr_item(child, index, 'format_fun')
            self.init_str_item(child, index, 'txt_CN')

        self.setHeaderLabels(columns)
        self.expandAll()
        self.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.clicked.connect(self.tree_clicked)

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

            elif column_name in ['line_thick', "scale_div"]:
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


if __name__ == '__main__':
    pass

