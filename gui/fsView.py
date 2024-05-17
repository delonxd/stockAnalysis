from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from method.fileMethod import *
from method.dataMethod import load_df_from_mysql

import pandas as pd
import sys
import numpy as np


class FsView(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('FsView')
        self.setGeometry(160, 120, 1600, 860)

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.code = None

        layout = QHBoxLayout()
        layout.addWidget(self.table_widget)

        self.setLayout(layout)

        self.header_dict = load_json_txt("..\\basicData\\header_df\\header_df_fs.txt")

    def load_df(self, code):
        if self.isHidden():
            return
        if code == self.code:
            return

        df = load_df_from_mysql(code, 'fs')

        df = df.sort_index(ascending=False)
        df = df.T

        self.setWindowTitle(code)
        self.table_widget.setRowCount(df.shape[0])
        self.table_widget.setColumnCount(df.shape[1])

        index = pd.Series(map(lambda x: x[3:6] if x[:2] == 'id' else '', df.index.values))
        header = pd.Series(map(lambda x: self.header_dict[x]['txt_CN'], df.index.values))

        h_header = np.vectorize(lambda x: str(x))(df.columns.values)
        v_header = header + ' ' + index

        self.table_widget.setHorizontalHeaderLabels(h_header)
        self.table_widget.setVerticalHeaderLabels(v_header)

        arr = df.values
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(regular_data(arr[i, j]))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
                self.table_widget.setItem(i, j, item)

        self.table_widget.resizeColumnsToContents()

        self.table_widget.verticalHeader().setDefaultAlignment(Qt.AlignRight)
        self.table_widget.verticalScrollBar().setSliderPosition(303)

        self.code = code

    def closeEvent(self, event):
        self.close_signal.emit(self)


def regular_data(data):
    if pd.isna(data):
        return ''
    elif isinstance(data, str):
        return data
    else:
        if data == int(data):
            return format(int(data), ',')
        else:
            return format(data, ',')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = FsView()
    main.show()
    main.load_df('002594')
    sys.exit(app.exec_())
