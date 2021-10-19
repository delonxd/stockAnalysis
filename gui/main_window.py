from method.dataMethod import *
from request.requestData import request_data2mysql
from method.logMethod import log_it, MainLog

from gui.checkTree import CheckTree
from gui.dataPix import DataPix
from gui.stockListView import QStockListView, CodesDataFrame

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import re
import threading
import time

import numpy as np


class GuiLog(MainLog):
    content = ''


class ReadSQLThread(QThread):
    signal1 = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.code_list = list()
        self.lock = threading.Lock()

    def run(self):
        GuiLog.add_log('thread start')

        while True:
            self.lock.acquire()
            if len(self.code_list) > 0:
                code = self.code_list[0]
                self.code_list.pop(0)
            else:
                break
            self.lock.release()

            res0 = (code, sql2df(code))
            GuiLog.add_log('    add buffer %s' % code)
            self.signal1.emit(res0)

        GuiLog.add_log('thread end')
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


class QDataFrameModel(QStandardItemModel):
    def __init__(self, df: pd.DataFrame):
        self.df = df
        super().__init__(*df.shape)
        h_header = np.vectorize(lambda x: str(x))(df.columns.values)
        v_header = np.vectorize(lambda x: str(x))(df.index.values)
        self.setHorizontalHeaderLabels(h_header)
        self.setVerticalHeaderLabels(v_header)

        arr = df.values
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.setItem(i, j, QStandardItem(str(arr[i, j])))


class MainWidget(QWidget):
    # code_index = 0

    def __init__(self):
        super().__init__()

        # self.code_list = ['000002', '000004', '600004', '600006', '600007', '600008']

        # with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        #     self.code_list = pickle.load(pk_f)

        # with open("F:\\Backups\\价值投资0406.txt", "r", encoding="utf-8", errors="ignore") as f:
        with open("C:\\Backups\\价值投资0514.txt", "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
            code_list = re.findall(r'([0-9]{6})', txt)
            code_list.reverse()

        self.codes_df = CodesDataFrame(code_list, current_index=21)

        time0 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.log_path = '../bufferData/logs/gui_log/gui_log_%s.txt' % time0

        self.df_dict = dict()
        self.buffer = ReadSQLThread()
        self.buffer.signal1.connect(self.update_df_dict)

        # self.code_index = 21

        code = self.stock_code
        self.df = sql2df(code=code)
        self.df_dict[code] = self.df
        self.style_df = load_default_style()

        self.data_pix = DataPix(
            parent=self,
            style_df=self.style_df,
            m_width=1600,
            m_height=900,
        )

        self.label = QLabel(self)

        self.button1 = QPushButton('export')
        self.button2 = QPushButton('x2')
        self.button3 = QPushButton('/2')
        self.button4 = QPushButton('style')
        self.button5 = QPushButton('request')
        self.button6 = QPushButton('save code')
        self.button7 = QPushButton('code list')

        self.editor1 = QLineEdit()
        self.editor1.setValidator(QIntValidator())
        self.editor1.setMaxLength(6)

        self.stock_label = QLabel()
        self.industry_label = QLabel()

        self.tree = CheckTree(self.style_df)
        self.code_widget = QStockListView(self.codes_df)

        self.tree.update_style.connect(self.update_data)
        self.data_pix.update_tree.connect(self.tree.update_tree)
        self.code_widget.table_view.change_signal.connect(self.change_stock)

        self.cross = False
        self.init_ui()

        self.buffer_df()

    @property
    def code_index(self):
        return self.codes_df.current_index

    @property
    def stock_code(self):
        return str(self.codes_df.df.iloc[self.code_index]['code'])

    @property
    def len_list(self):
        return int(self.codes_df.df.shape[0])

    def update_df_dict(self, tup):
        self.df_dict[tup[0]] = tup[1]

    def init_ui(self):

        self.setWindowTitle('绘制图形')
        self.resize(1600, 900)

        p = QPalette()
        p.setColor(QPalette.WindowText, Qt.red)
        self.stock_label.setFont(QFont('Consolas', 20))
        self.stock_label.setPalette(p)
        self.industry_label.setFont(QFont('Consolas', 16))
        self.industry_label.setPalette(p)

        layout0 = QHBoxLayout()
        layout0.addWidget(self.industry_label, 1, Qt.AlignLeft | Qt.AlignBottom)
        layout0.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout0.addStretch(1)

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        # layout.addWidget(self.tree, 0, Qt.AlignCenter)
        layout1.addWidget(self.label, 0, Qt.AlignCenter)
        layout1.addStretch(1)

        layout2 = QHBoxLayout()
        layout2.addStretch(1)
        layout2.addWidget(self.button1, 0, Qt.AlignCenter)
        layout2.addWidget(self.button2, 0, Qt.AlignCenter)
        layout2.addWidget(self.button3, 0, Qt.AlignCenter)
        layout2.addWidget(self.button4, 0, Qt.AlignCenter)
        layout2.addWidget(self.button5, 0, Qt.AlignCenter)
        layout2.addWidget(self.button6, 0, Qt.AlignCenter)
        layout2.addWidget(self.button7, 0, Qt.AlignCenter)
        layout2.addWidget(self.editor1, 0, Qt.AlignCenter)
        layout2.addStretch(1)
        # layout2.addWidget(button1, 0, Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch(1)
        # layout.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout.addLayout(layout0, 0)
        layout.addLayout(layout1, 0)
        layout.addLayout(layout2, 0)
        layout.addStretch(1)

        m_layout = QHBoxLayout()
        m_layout.addStretch(1)
        m_layout.addLayout(layout, 0)
        m_layout.addStretch(1)

        self.setLayout(m_layout)
        # self.setCentralWidget(layout)

        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.center()

        self.show_stock_name()

        self.button1.clicked.connect(self.export_style)
        self.button2.clicked.connect(self.scale_up)
        self.button3.clicked.connect(self.scale_down)
        self.button4.clicked.connect(self.show_tree)
        self.button5.clicked.connect(self.request_data)
        self.button6.clicked.connect(self.save_code)
        self.button7.clicked.connect(self.show_code_list)
        # self.editor1.textChanged.connect(self.editor1_changed)

        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(40, 40, 40, 255))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

    def save_code(self):
        row = self.codes_df.df.iloc[self.code_index]

        code = row['code']
        name = row['name']

        path = "../bufferData/codes/self_select.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())

        if code_list:
            x, y = zip(*code_list)

            if code in x:
                return

        code_list.append((code, name))
        res = json.dumps(code_list, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

    def request_data(self):
        code = self.stock_code

        request_data2mysql(
            stock_code=code,
            data_type='fs',
            start_date="2021-04-01",
        )

        request_data2mysql(
            stock_code=code,
            data_type='mvs',
            start_date="2021-04-01",
        )

        self.df_dict[code] = sql2df(code=code)
        self.change_stock(self.code_index)
        # self.tree.exec_()

    def show_tree(self):
        self.tree.show()
        # self.tree.exec_()

    def show_code_list(self):
        self.code_widget.show()

    def editor1_changed(self, txt):
        name_list = self.codes_df.df['name'].values
        if txt in name_list:
            new_index = name_list.index(txt)
            self.change_stock(new_index)

    def scale_up(self):
        self.data_pix.scale_ratio = self.data_pix.scale_ratio * 2
        self.update_data()

    def scale_down(self):
        self.data_pix.scale_ratio = self.data_pix.scale_ratio / 2
        self.update_data()

    def export_style(self):
        df = self.tree.df.copy()
        df['child'] = None
        save_default_style(df)

    def update_data(self):
        self.data_pix.update_pix()
        self.update()

    def buffer_df(self):
        index1 = self.code_index
        index2 = self.code_index
        arr = np.array([], dtype='int32')

        codes_df = self.codes_df.df

        l0 = codes_df.shape[0]
        l1 = (l0 - 1) / 2
        l2 = 10

        offset = int(min(l1, l2))

        for i in range(offset):
            if i < 10:
                index1 += 1
                arr = np.append(arr, index1)

            if i < 2:
                index2 -= 1
                arr = np.append(arr, index2)
        arr = arr % l0

        tmp = list()
        for index in arr:
            stock_code = codes_df.iloc[index]['code']
            if stock_code in self.df_dict.keys():
                pass
            else:
                tmp.append(stock_code)

        self.buffer.extend(tmp)
        self.buffer.start()

    def change_stock(self, new_index):
        if abs(new_index - self.codes_df.current_index) > 1:
            self.buffer.clear()

        self.codes_df.current_index = new_index
        self.buffer_df()
        code = self.stock_code
        if code in self.df_dict.keys():
            self.df = self.df_dict[code]
        else:
            self.df = sql2df(code=code)
        self.update_data()
        self.show_stock_name()

    def show_stock_name(self):
        row = self.codes_df.df.iloc[self.code_index]
        len_df = self.codes_df.df.shape[0]

        txt1 = '%s: %s(%s/%s)' % (row['code'], row['name'], self.code_index, len_df)
        txt2 = '行业: %s-%s-%s' % (row['level1'], row['level2'], row['level3'])

        GuiLog.add_log('show stock --> ' + txt1)
        self.stock_label.setText(txt1)
        self.industry_label.setText(txt2)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft().x() - 11, qr.topLeft().y() - 45)

    def draw_cross(self, x, y):
        self.data_pix.draw_cross(x, y, self.cross)
        self.update()

    def paintEvent(self, e):
        self.label.setPixmap(self.data_pix.pix_show)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cross = not self.cross

            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())
            GuiLog.write(self.log_path)

        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        # if self.cross:
        pos = event.pos() - self.label.pos()
        self.draw_cross(pos.x(), pos.y())

    def wheelEvent(self, event):
        a = event.angleDelta().y() / 120
        if a < 0:
            new_index = (self.code_index + 1) % self.len_list
            self.change_stock(new_index)

        elif a > 0:
            new_index = (self.code_index - 1) % self.len_list
            self.change_stock(new_index)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('绘制图形')
        self.resize(1600, 900)

        widget1 = MainWidget()
        self.setCentralWidget(widget1)
        #
        # self.setObjectName('MainWindow')
        # self.setStyleSheet("#MainWindow{border-color:url(./images/welcome.jpg);}")

        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(40, 40, 40, 255))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # main = MainWindow()
    main = MainWidget()
    # main.showMaximized()
    sys.exit(app.exec_())
