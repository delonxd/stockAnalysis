from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import pandas as pd
import numpy as np


class PriorityTable(QDialog):
    update_style = pyqtSignal(object)

    def __init__(self, style_df):
        super().__init__()

        df = style_df.copy()
        df = df.loc[df['selected'] == True, :].copy()

        self.columns = ['index_name', 'show_name', 'info_priority']
        self.df = df.loc[:, self.columns].copy()

        self.table_view = QTableView()
        self.button1 = QPushButton('up')
        self.button2 = QPushButton('down')
        self.button3 = QPushButton('submit')
        self.model = QStandardItemModel()

        self.load_df()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QTableViewDemo')
        self.resize(500, 800)

        layout1 = QVBoxLayout()
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)
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

    # def refresh_table(self):
    #     self.load_df()


if __name__ == '__main__':
    a = pd.Series(np.zeros(10))

    app = QApplication(sys.argv)
    main = PriorityTable()
    main.show()
    sys.exit(app.exec_())
