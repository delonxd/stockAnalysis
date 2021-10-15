from method.dataMethod import *
from method.mainMethod import *
from gui.checkTree import CheckTree
from gui.dataPix import DataPix
from request.requestStockFs import request_fs_data2mysql
from request.requestStockMvs import request_mvs_data2mysql

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time
import pickle

import threading
import time


class ReadSQLThread(QThread):
    signal1 = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.code_list = list()
        self.lock = threading.Lock()

    def run(self):
        print(time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
        print('thread start')

        while True:
            self.lock.acquire()
            if len(self.code_list) > 0:
                code = self.code_list[0]
                self.code_list.pop(0)
            else:
                break
            self.lock.release()

            res0 = (code, sql2df(code))
            print(code)
            self.signal1.emit(res0)

        print('thread end')
        self.lock.release()

    def append(self, code):
        self.lock.acquire()
        if code in self.code_list:
            index = self.code_list.index(code)
            self.code_list.pop(index)
        self.code_list.insert(0, code)
        self.lock.release()

    def extend(self, code_list):
        self.lock.acquire()
        code_list.reverse()
        for code in code_list:
            if code in self.code_list:
                index = self.code_list.index(code)
                self.code_list.pop(index)
            self.code_list.insert(0, code)
        self.lock.release()

    def clear(self):
        self.lock.acquire()
        self.code_list.clear()
        self.lock.release()


class MainWindow(QWidget):
    # code_index = 0

    def __init__(self):
        super().__init__()

        self.df_dict = dict()
        self.buffer = ReadSQLThread()
        self.buffer.signal1.connect(self.update_df_dict)

        # self.code_list = ['000002', '000004', '600004', '600006', '600007', '600008']

        # with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        #     self.code_list = pickle.load(pk_f)

        # with open("F:\\Backups\\价值投资0406.txt", "r", encoding="utf-8", errors="ignore") as f:
        with open("C:\\Backups\\价值投资0514.txt", "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
            self.code_list = re.findall(r'([0-9]{6})', txt)

        with open('../basicData/code_name.pkl', 'rb') as pk_f:
            self.code_dict = pickle.load(pk_f)

        self.stock_code = '002410'
        self.code_index = self.code_list.index(self.stock_code)

        # self.code_index = 0
        # self.stock_code = self.code_list[0]

        self.df = sql2df(code=self.stock_code)
        self.df_dict[self.stock_code] = self.df
        self.style_df = load_default_style()

        self.data_pix = DataPix(
            parent=self,
            style_df=self.style_df,
            m_width=1600,
            m_height=800,
        )

        self.label = QLabel(self)

        self.button1 = QPushButton('export')
        self.button2 = QPushButton('x2')
        self.button3 = QPushButton('/2')
        self.button4 = QPushButton('style')
        self.button5 = QPushButton('request')

        self.editor1 = QLineEdit()
        self.editor1.setValidator(QIntValidator())
        self.editor1.setMaxLength(6)

        self.stock_label = QLabel()
        self.stock_label.setFont(QFont('Consolas', 20))

        # print(2, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        self.tree = CheckTree(self.style_df)
        #
        self.tree.update_style.connect(self.update_data)
        self.data_pix.update_tree.connect(self.tree.update_tree)

        # print(3, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

        self.cross = False
        self.init_ui()

        self.buffer_df()

    def update_df_dict(self, tup):
        self.df_dict[tup[0]] = tup[1]

    def buffer_df(self):
        index1 = self.code_index
        index2 = self.code_index
        arr = np.array([], dtype='int32')

        l0 = len(self.code_list)
        l1 = (l0 - 1) / 2
        l2 = 10

        offset = int(min(l1, l2))

        for _ in range(offset):
            index1 += 1
            index2 -= 1
            arr = np.append(arr, index1)
            arr = np.append(arr, index2)
        arr = arr % l0

        tmp = list()
        for index in arr:
            stock_code = self.code_list[index]
            if stock_code in self.df_dict.keys():
                pass
            else:
                tmp.append(stock_code)

        self.buffer.extend(tmp)
        self.buffer.start()

    def init_ui(self):

        self.setWindowTitle('绘制图形')
        self.resize(1600, 900)

        layout = QHBoxLayout()
        layout.addStretch(1)
        # layout.addWidget(self.tree, 0, Qt.AlignCenter)
        layout.addWidget(self.label, 0, Qt.AlignCenter)
        layout.addStretch(1)

        layout2 = QHBoxLayout()
        layout2.addStretch(1)
        layout2.addWidget(self.button1, 0, Qt.AlignCenter)
        layout2.addWidget(self.button2, 0, Qt.AlignCenter)
        layout2.addWidget(self.button3, 0, Qt.AlignCenter)
        layout2.addWidget(self.button4, 0, Qt.AlignCenter)
        layout2.addWidget(self.button5, 0, Qt.AlignCenter)
        layout2.addWidget(self.editor1, 0, Qt.AlignCenter)

        layout2.addStretch(1)
        # layout2.addWidget(button1, 0, Qt.AlignCenter)

        layout1 = QVBoxLayout()
        layout1.addStretch(1)
        layout1.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout1.addLayout(layout, 0)
        layout1.addLayout(layout2, 0)
        layout1.addStretch(1)

        self.setLayout(layout1)

        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.center()

        self.show_stock_name()

        self.button1.clicked.connect(self.export_style)
        # self.button2.clicked.connect(self.scale_up)
        # self.button3.clicked.connect(self.scale_down)
        self.button4.clicked.connect(self.show_tree)
        self.button5.clicked.connect(self.request_data)
        self.editor1.textChanged.connect(self.editor1_changed)

    def request_data(self):
        stock_code = self.stock_code
        with open('../basicData/metricsList.pkl', 'rb') as pk_f:
            metrics_list = pickle.load(pk_f)

        with open('../basicData/metricsMvs.pkl', 'rb') as pk_f:
            metrics0 = pickle.load(pk_f)

        # datetime0 = dt.datetime(2021, 10, 9, 16, 30, 0)
        datetime0 = dt.datetime.now()

        request_fs_data2mysql(
            stock_code=stock_code,
            metrics_list=metrics_list,
            start_date="1970-01-01",
            datetime=datetime0,
        )

        request_mvs_data2mysql(
            stock_code=stock_code,
            metrics=metrics0,
            start_date="1970-01-01",
            datetime=datetime0,
        )

        self.df = sql2df(code=self.stock_code)

        self.change_stock()
        # self.tree.exec_()

    def show_tree(self):
        self.tree.show()
        # self.tree.exec_()

    def editor1_changed(self, txt):
        if txt in self.code_list:
            self.code_index = self.code_list.index(txt)
            self.stock_code = txt
            self.buffer.clear()
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
        df = self.tree.df.copy()
        df['child'] = None
        save_default_style(df)

    def update_data(self):
        self.data_pix.update_pix()
        self.update()

    def change_stock(self):
        # print(stock_code, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        self.buffer_df()
        if self.stock_code in self.df_dict.keys():
            self.df = self.df_dict[self.stock_code]
        else:
            self.df = sql2df(code=self.stock_code)
        self.update_data()
        self.show_stock_name()

        # print('finished', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    def show_stock_name(self):
        name = self.code_dict.get(self.stock_code)
        txt = '%s: %s' % (self.stock_code, name)
        self.stock_label.setText(txt)

        # todo: show stock_list, show type

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
            self.code_index = self.code_index % len(self.code_list)
            self.stock_code = self.code_list[self.code_index]
            self.change_stock()

        elif a > 0:
            self.code_index -= 1
            self.code_index = self.code_index % len(self.code_list)
            self.stock_code = self.code_list[self.code_index]
            self.change_stock()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
