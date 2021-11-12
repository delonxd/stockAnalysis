from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import pandas as pd
import numpy as np


class ShowPix(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.label = QLabel()
        self.pix = QPixmap(1600, 900)
        # self.pix = QPixmap(300, 200)
        color = QColor(40, 40, 40, 255)
        self.pix.fill(color)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QTableViewDemo')
        self.label.setPixmap(self.pix)

        layout = QHBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)

    def paintEvent(self, e):
        self.label.setPixmap(self.pix)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ShowPix()
    main.show()
    sys.exit(app.exec_())
