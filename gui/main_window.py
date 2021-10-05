from method.dataMethod import *
from method.mainMethod import *
from gui.checkTree import CheckTree
from gui.dataPix import DataPix

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time
import pickle


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('绘制图形')

        self.resize(1920, 1000)
        self.label = QLabel(self)
        self.label_right = QLabel(self)
        pix = QPixmap(100, 800)
        pix.fill(Qt.white)

        self.style_df = get_default_style_df()

        # show_df(style_df)
        self.tree = CheckTree(self.style_df)
        self.tree.setMinimumSize(800, 800)
        # pix = QPixmap(200, 800)
        # pix.fill(Qt.white)
        # self.label_left.setPixmap(pix)

        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.tree, 0, Qt.AlignCenter)
        layout.addWidget(self.label, 0, Qt.AlignCenter)
        layout.addStretch(1)

        # layout.addWidget(self.label_right, 0, Qt.AlignCenter)

        layout1 = QVBoxLayout()
        button = QPushButton('export')
        layout1.addStretch(1)
        layout1.addLayout(layout, 0)
        layout1.addWidget(button, 0, Qt.AlignCenter)
        layout1.addStretch(1)
        self.setLayout(layout1)

        with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
            self.code_list = pickle.load(pk_f)

        self.code_index = 0
        self.df = sql2df(code=self.code_list[self.code_index])

        self.data_pix = DataPix(
            parent=self,
            m_width=1000,
            m_height=800,
            style_df=self.style_df,
            data_df=self.df
        )

        self.cross = False
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)

        self.center()

        button.clicked.connect(self.export_style)
        self.tree.update_signal.connect(self.update_data)
        self.data_pix.update_signal.connect(self.tree.update_tree)

    def export_style(self):
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        path = '../gui/style_df_%s.pkl' % timestamp
        df = self.tree.df.copy()
        df['child'] = None
        with open(path, 'wb') as pk_f:
            pickle.dump(df, pk_f)

    def update_data(self):
        self.data_pix.get_data_source()
        # print('update_data')
        self.update()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft().x() - 11, qr.topLeft().y() - 45)

    def draw_cross(self, x, y):
        self.data_pix.draw_cross(x, y)
        self.update()

    def paintEvent(self, e):
        self.label.setPixmap(self.data_pix.pix_show)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cross:
                # self.draw_cross(None, None)
                # self.cross = False
                pass
            else:
                pos = event.pos() - self.label.pos()
                self.draw_cross(pos.x(), pos.y())
                self.cross = True

        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        if self.cross:
            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())

    def wheelEvent(self, event):
        a = event.angleDelta().y() / 120
        if a < 0:
            # print('----------------------------------------')
            self.code_index += 1
            self.df = sql2df(code=self.code_list[self.code_index])
            self.update_data()
        elif a > 0:
            # print('----------------------------------------')
            self.code_index -= 1
            self.df = sql2df(code=self.code_list[self.code_index])
            self.update_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
