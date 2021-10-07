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


class BufferThread(QThread):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.buffer_dict = dict()
        self.un_buffer_codes = list()

    def run(self):
        while len(self.un_buffer_codes) > 0:
            code = self.un_buffer_codes[0]
            if code in self.buffer_dict.keys():
                pass
            else:
                tmp_dict = dict()
                df = sql2df(code=code)
                style_df = get_default_style_df()

                data_pix = DataPix(
                    df=df,
                    style_df=style_df,
                    m_width=1600,
                    m_height=800,
                )

                tree = CheckTree(style_df)

                # tree.update_style.connect(data_pix.update_pix)
                # data_pix.update_tree.connect(tree.update_tree)

                tmp_dict['df'] = df
                tmp_dict['style_df'] = style_df
                tmp_dict['data_pix'] = data_pix
                tmp_dict['tree'] = tree

                self.buffer_dict[code] = tmp_dict

            self.un_buffer_codes.pop(0)
            print(self.un_buffer_codes, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        print('buffer finished', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))


class MainWindow(QWidget):
    # code_index = 0

    def __init__(self):
        super().__init__()

        self.setWindowTitle('绘制图形')
        self.resize(1600, 900)

        self.buffer_dict = dict()

        with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
            self.code_list = pickle.load(pk_f)

        with open('../basicData/code_name.pkl', 'rb') as pk_f:
            self.code_dict = pickle.load(pk_f)

        stock = '600460'
        self.code_index = self.code_list.index(stock)

        # self.code_index = 0

        self.df = sql2df(code=self.code_list[self.code_index])
        self.style_df = get_default_style_df()

        print(1, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        self.data_pix = DataPix(
            parent=self,
            style_df=self.style_df,
            m_width=1600,
            m_height=800,
        )

        print(2, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        # self.tree = CheckTree(self.style_df)

        # self.tree.update_style.connect(self.update_data)
        # self.data_pix.update_tree.connect(self.tree.update_tree)

        print(3, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        # todo: add data buffer

        self.label = QLabel(self)

        layout = QHBoxLayout()
        layout.addStretch(1)
        # layout.addWidget(self.tree, 0, Qt.AlignCenter)
        layout.addWidget(self.label, 0, Qt.AlignCenter)
        layout.addStretch(1)

        button1 = QPushButton('export')
        button2 = QPushButton('x2')
        button3 = QPushButton('/2')
        button4 = QPushButton('style')

        editor1 = QLineEdit()
        editor1.setValidator(QIntValidator())
        editor1.setMaxLength(6)

        self.stock_label = QLabel()
        self.stock_label.setFont(QFont('Consolas', 20))
        self.show_stock_name()

        layout2 = QHBoxLayout()
        layout2.addStretch(1)
        layout2.addWidget(button1, 0, Qt.AlignCenter)
        layout2.addWidget(button2, 0, Qt.AlignCenter)
        layout2.addWidget(button3, 0, Qt.AlignCenter)
        layout2.addWidget(button4, 0, Qt.AlignCenter)
        layout2.addWidget(editor1, 0, Qt.AlignCenter)

        layout2.addStretch(1)
        # layout2.addWidget(button1, 0, Qt.AlignCenter)

        layout1 = QVBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout1.addLayout(layout, 0)
        layout1.addLayout(layout2, 0)
        layout1.addStretch(1)

        self.setLayout(layout1)

        self.cross = False
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.center()

        button1.clicked.connect(self.export_style)
        # button2.clicked.connect(self.scale_up)
        # button3.clicked.connect(self.scale_down)
        button4.clicked.connect(self.show_tree)
        editor1.textChanged.connect(self.editor1_changed)

        # buffer_codes = ['600461']
        # self.buffer = BufferThread(parent=self)
        # self.buffer.un_buffer_codes = buffer_codes
        # self.buffer.start()

        # print('buffer started', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    def show_tree(self):
        self.tree.show()
        # self.tree.exec_()

    def editor1_changed(self, txt):
        if txt in self.code_list:
            self.code_index = self.code_list.index(txt)
            self.change_stock()

    # def scale_up(self):
    #     for index, row in self.style_df.iterrows():
    #         if row['logarithmic'] is True:
    #             self.style_df.loc[index, 'scale_min'] = row['scale_min'] * 2
    #             self.style_df.loc[index, 'scale_max'] = row['scale_max'] * 2
    #
    #     self.update_data()
    #
    # def scale_down(self):
    #     for index, row in self.style_df.iterrows():
    #         if row['logarithmic'] is True:
    #             self.style_df.loc[index, 'scale_min'] = row['scale_min'] / 2
    #             self.style_df.loc[index, 'scale_max'] = row['scale_max'] / 2
    #
    #     self.update_data()

    def export_style(self):
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        path = '../gui/style_df_%s.pkl' % timestamp
        df = self.tree.df.copy()
        df['child'] = None
        with open(path, 'wb') as pk_f:
            pickle.dump(df, pk_f)

    def update_data(self):
        self.data_pix.update_pix()
        self.update()

    def change_stock(self):
        print('change started', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        self.df = sql2df(code=self.code_list[self.code_index])
        self.update_data()

        # code = self.code_list[self.code_index]
        #
        # if code in self.buffer.buffer_dict.keys():
        #     tmp = self.buffer.buffer_dict[code]
        #     # print(tmp)
        #     self.df = tmp['df']
        #     self.style_df = tmp['style_df']
        #     self.data_pix = tmp['data_pix']
        #     self.tree = tmp['tree']
        #
        #     self.tree.show()
        #     self.tree.update_style.connect(self.update_data)
        #     self.data_pix.update_tree.connect(self.tree.update_tree)
        #     self.update()

        self.show_stock_name()

        print('change finished', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    def show_stock_name(self):
        code = self.code_list[self.code_index]
        name = self.code_dict[code]
        txt = '%s: %s' % (code, name)
        self.stock_label.setText(txt)

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

        # elif event.button() == Qt.RightButton:
        #     self.close()

    def mouseMoveEvent(self, event):
        if self.cross:
            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())

    def wheelEvent(self, event):
        a = event.angleDelta().y() / 120
        if a < 0:
            self.code_index += 1
            self.change_stock()
        elif a > 0:
            self.code_index -= 1
            self.change_stock()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
