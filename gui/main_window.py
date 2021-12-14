from method.dataMethod import sql2df
from request.requestData import request_data2mysql
from method.logMethod import log_it, MainLog
from method.mainMethod import get_part_codes

from gui.checkTree import CheckTree
from gui.dataPix import DataPix
from gui.stockListView import QStockListView, CodesDataFrame

from gui.styleDataFrame import load_default_style
from gui.styleDataFrame import save_default_style
from gui.priorityTable import PriorityTable
from gui.showPix import ShowPix

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import re
import threading
import time

import numpy as np
import pandas as pd


class GuiLog(MainLog):
    content = ''


class ReadSQLThread(QThread):
    signal1 = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.buffer_list = list()
        self.lock = threading.Lock()

    def run(self):
        GuiLog.add_log('thread start')

        while True:
            self.lock.acquire()
            if len(self.buffer_list) > 0:
                code, style_df, df, ratio = self.buffer_list.pop(0)
            else:
                break
            self.lock.release()

            res0 = DataPix(code=code, style_df=style_df, df=df, ratio=ratio)
            GuiLog.add_log('    add buffer %s' % code)
            self.signal1.emit(res0)

        GuiLog.add_log('thread end')
        self.lock.release()

    def extend(self, message_list):
        self.lock.acquire()
        message_list.reverse()
        for message in message_list:
            code = message[0]

            if len(self.buffer_list) > 0:
                x = list(zip(*self.buffer_list))[0]
                if code in x:
                    index = x.index(code)
                    self.buffer_list.pop(index)

            self.buffer_list.insert(0, message)
        self.lock.release()

    def clear(self):
        self.lock.acquire()
        self.buffer_list.clear()
        self.lock.release()


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()

        code_list = self.get_code_list()

        self.codes_df = CodesDataFrame(code_list)
        self.codes_df.init_current_index(index=0)
        # self.codes_df.init_current_index(index=100)
        # self.codes_df.init_current_index(code='002493')
        # self.codes_df.init_current_index(code='000921')

        self.style_df = load_default_style()

        time0 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.log_path = '../bufferData/logs/gui_log/gui_log_%s.txt' % time0

        self.df_dict = dict()
        self.pix_dict = dict()

        self.buffer = ReadSQLThread()
        self.buffer.signal1.connect(self.update_data_pix)

        code = self.stock_code
        self.style_df = load_default_style()
        self.data_pix = DataPix(code=code, style_df=pd.DataFrame(), df=pd.DataFrame())

        self.label = QLabel(self)

        self.button1 = QPushButton('export')
        self.button2 = QPushButton('x2')
        self.button3 = QPushButton('/2')
        self.button4 = QPushButton('style')
        self.button5 = QPushButton('request')
        self.button6 = QPushButton('save code')
        self.button7 = QPushButton('code list')
        self.button8 = QPushButton('priority')
        self.button9 = QPushButton('new_window')

        self.editor1 = QLineEdit()
        self.editor1.setValidator(QIntValidator())
        self.editor1.setMaxLength(6)

        self.head_label1 = QLabel()
        self.head_label2 = QLabel()
        self.head_label3 = QLabel()

        self.tree = CheckTree(self.style_df)
        self.code_widget = QStockListView(self.codes_df)

        self.window2 = ShowPix(main_window=self)

        self.tree.update_style.connect(self.update_style)
        self.code_widget.table_view.change_signal.connect(self.change_stock)

        self.cross = False
        self.ratio = 16
        self.init_ui()

        self.window_flag = 0
        self.run_buffer()

    @property
    def code_index(self):
        return self.codes_df.current_index

    @property
    def stock_code(self):
        return str(self.codes_df.df.iloc[self.code_index]['code'])

    @property
    def stock_name(self):
        return str(self.codes_df.df.iloc[self.code_index]['name'])

    @property
    def len_list(self):
        return int(self.codes_df.df.shape[0])

    def init_ui(self):

        self.setWindowTitle('main_window')
        self.resize(1600, 900)

        p = QPalette()
        p.setColor(QPalette.WindowText, Qt.red)
        self.head_label1.setFont(QFont('Consolas', 20))
        self.head_label1.setPalette(p)
        self.head_label2.setFont(QFont('Consolas', 16))
        self.head_label2.setPalette(p)
        self.head_label3.setFont(QFont('Consolas', 16))
        self.head_label3.setPalette(p)

        layout0 = QHBoxLayout()
        layout0.addWidget(self.head_label2, 1, Qt.AlignLeft | Qt.AlignBottom)
        layout0.addWidget(self.head_label1, 0, Qt.AlignCenter)
        layout0.addWidget(self.head_label3, 1, Qt.AlignRight | Qt.AlignBottom)
        # layout0.addStretch(1)

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
        layout2.addWidget(self.button8, 0, Qt.AlignCenter)
        layout2.addWidget(self.button9, 0, Qt.AlignCenter)
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

        self.button1.clicked.connect(self.export_style)
        self.button2.clicked.connect(self.scale_up)
        self.button3.clicked.connect(self.scale_down)
        self.button4.clicked.connect(self.show_tree)
        self.button5.clicked.connect(self.request_data)
        self.button6.clicked.connect(self.save_code)
        self.button7.clicked.connect(self.show_code_list)
        self.button8.clicked.connect(self.config_priority)
        self.button9.clicked.connect(self.show_new_window)
        self.editor1.textChanged.connect(self.editor1_changed)

        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(40, 40, 40, 255))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)  # 开放右键策略

    def show_menu(self, pos):  # 添加右键菜单
        menu = QMenu(self)

        action1 = QAction('更新数据', menu)
        action2 = QAction('添加自选', menu)
        action3 = QAction('删除自选', menu)
        action4 = QAction('添加黑名单', menu)
        action5 = QAction('删除黑名单', menu)
        action6 = QAction('上移', menu)
        action7 = QAction('下移', menu)
        action8 = QAction('添加白名单', menu)
        action9 = QAction('删除白名单', menu)

        menu.addAction(action1)
        menu.addSeparator()
        menu.addAction(action2)
        menu.addAction(action3)
        menu.addSeparator()
        menu.addAction(action4)
        menu.addAction(action5)
        menu.addSeparator()
        menu.addAction(action8)
        menu.addAction(action9)

        menu.addSeparator()
        menu.addAction(action6)
        menu.addAction(action7)

        action1.triggered.connect(self.request_data)
        action2.triggered.connect(self.add_selected)
        action3.triggered.connect(self.del_selected)
        action4.triggered.connect(self.add_blacklist)
        action5.triggered.connect(self.del_blacklist)
        action6.triggered.connect(self.scale_down)
        action7.triggered.connect(self.scale_up)
        action8.triggered.connect(self.add_whitelist)
        action9.triggered.connect(self.del_whitelist)

        menu.exec_(QCursor.pos())

    def add_code(self, path):
        row = self.codes_df.df.iloc[self.code_index]
        code = row['code']

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())

        if code in code_list:
            return

        code_list.append(code)
        res = json.dumps(code_list, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)
        self.show_stock_name()

    def del_code(self, path):
        row = self.codes_df.df.iloc[self.code_index]
        code = row['code']

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())

        if code in code_list:
            index = code_list.index(code)
            code_list.pop(index)
        else:
            return

        res = json.dumps(code_list, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

        self.show_stock_name()

    def add_selected(self):
        path = "../basicData/self_selected/gui_selected.txt"
        self.add_code(path)

    def del_selected(self):
        path = "../basicData/self_selected/gui_selected.txt"
        self.del_code(path)

    def add_blacklist(self):
        path = "../basicData/self_selected/gui_blacklist.txt"
        self.add_code(path)

    def del_blacklist(self):
        path = "../basicData/self_selected/gui_blacklist.txt"
        self.del_code(path)

    def add_whitelist(self):
        path = "../basicData/self_selected/gui_whitelist.txt"
        self.add_code(path)

    def del_whitelist(self):
        path = "../basicData/self_selected/gui_whitelist.txt"
        self.del_code(path)

    def save_code(self):
        pass

    def request_data(self):
        code = self.stock_code

        request_data2mysql(
            stock_code=code,
            data_type='fs',
            start_date="1970-01-01",
        )

        request_data2mysql(
            stock_code=code,
            data_type='mvs',
            start_date="1970-01-01",
        )

        if code in self.df_dict.keys():
            self.df_dict.pop(code)

        if code in self.pix_dict.keys():
            self.pix_dict.pop(code)

        self.run_buffer()
        # self.df_dict[code] = sql2df(code=code)
        # self.change_stock(self.code_index)

    def show_tree(self):
        self.tree.show()

    def show_code_list(self):
        self.code_widget.show()

    def editor1_changed(self, txt):
        code_list = self.codes_df.df['code'].tolist()
        if txt in code_list:
            new_index = code_list.index(txt)
            self.change_stock(new_index)
            self.editor1.setText('')
            self.label.setFocus()

    def scale_up(self):
        self.ratio = self.ratio * 2
        self.refresh_ratio()

    def scale_down(self):
        self.ratio = self.ratio / 2
        self.refresh_ratio()

    def refresh_ratio(self):
        code = self.stock_code
        if code in self.df_dict.keys():
            df = self.df_dict[code].copy()
        else:
            return
        style_df = self.style_df.copy()
        message_list = [[code, style_df, df, self.ratio]]
        self.buffer.extend(message_list)
        self.buffer.start()
        print('buffer start')

    def export_style(self):
        df = self.tree.df.copy()
        df['child'] = None
        save_default_style(df)

    def run_buffer(self):
        index1 = self.code_index
        index2 = self.code_index
        arr = np.array([], dtype='int32')

        codes_df = self.codes_df.df

        l0 = codes_df.shape[0]
        l1 = (l0 - 1) / 2
        l2 = 20

        offset = int(min(l1, l2))

        arr = np.append(arr, index1)
        for i in range(offset):
            if i < 20:
                index1 += 1
                arr = np.append(arr, index1)

            if i < 2:
                index2 -= 1
                arr = np.append(arr, index2)
        arr = arr % l0

        message_list = list()
        for index in arr:
            code = codes_df.iloc[index]['code']
            message = self.emit_code_message(code)
            if message is not None:
                message_list.append(message)

        self.buffer.extend(message_list)
        self.buffer.start()

    def emit_code_message(self, code):
        if code in self.pix_dict.keys():
            return
        else:
            df = None
            if code in self.df_dict.keys():
                df = self.df_dict[code].copy()
            style_df = self.style_df.copy()
            return code, style_df, df, None

    def update_data_pix(self, data_pix):
        self.pix_dict[data_pix.code] = data_pix
        self.df_dict[data_pix.code] = data_pix.df

        if data_pix.code == self.stock_code:
            self.data_pix = data_pix
            self.update_window()

    def update_window(self):
        self.label.setPixmap(self.data_pix.pix_list[self.window_flag])
        self.show_stock_name()

    def update_style(self):
        self.pix_dict.clear()
        self.run_buffer()

    def change_stock(self, new_index):
        if abs(new_index - self.codes_df.current_index) > 1:
            self.buffer.clear()

        self.codes_df.current_index = new_index
        self.run_buffer()

        code = self.stock_code
        if code in self.pix_dict.keys():
            self.data_pix = self.pix_dict[code]
        else:
            self.data_pix = DataPix(code=code, style_df=pd.DataFrame(), df=pd.DataFrame())
        self.update_window()

    def show_stock_name(self):
        row = self.codes_df.df.iloc[self.code_index]
        len_df = self.codes_df.df.shape[0]

        txt1 = '%s: %s(%s/%s)' % (row['code'], row['name'], self.code_index, len_df)
        txt2 = '行业: %s-%s-%s' % (row['level1'], row['level2'], row['level3'])

        code = row['code']
        list0 = []

        path = "../basicData/self_selected/gui_selected.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('自选股')

        path = "../basicData/self_selected/gui_whitelist.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('白名单')

        path = "../basicData/self_selected/gui_blacklist.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('黑名单')

        txt3 = '/'.join(list0)

        GuiLog.add_log('show stock --> ' + txt1)
        self.head_label1.setText(txt1)
        self.head_label2.setText(txt2)
        self.head_label3.setText(txt3)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft().x() - 11, qr.topLeft().y() - 45)

    def draw_cross(self, x, y):
        self.data_pix.draw_cross(x, y, self.cross)
        self.label.setPixmap(self.data_pix.pix_list[self.window_flag])

        # self.window2.pix = self.data_pix.pix_list[1]
        # self.window2.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.cross = not self.cross

            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())
            GuiLog.write(self.log_path)

            self.label.setFocus()

        # elif event.button() == Qt.RightButton:
        #     self.close()

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

    @staticmethod
    def get_code_list():
        with open("..\\bufferData\\codes\\blacklist.txt", "r", encoding="utf-8", errors="ignore") as f:
            blacklist = json.loads(f.read())

        # code_list = ['000002', '000004', '600004', '600006', '600007', '600008']

        # with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        #     code_list = json.loads(f.read())

        # with open("..\\basicData\\analyzedData\\jlr_codes.txt", "r", encoding="utf-8", errors="ignore") as f:
        # with open("..\\basicData\\analyzedData\\roe_codes2.txt", "r", encoding="utf-8", errors="ignore") as f:
        # with open("..\\basicData\\analyzedData\\return_year_codes.txt", "r", encoding="utf-8", errors="ignore") as f:
        with open("..\\basicData\\analyzedData\\sift_code_011.txt", "r", encoding="utf-8", errors="ignore") as f:
        # with open("..\\basicData\\self_selected\\gui_whitelist.txt", "r", encoding="utf-8", errors="ignore") as f:
        # with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        # with open("..\\basicData\\dailyUpdate\\update_20211213153503\\sift_code_20211213153503.txt", "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())

        # code_list = get_part_codes(code_list, blacklist=blacklist)
        industry_list = [
            "C110101",
            "C110102",
            "C110103",
            "C030201",
            "C020203",
            "C070101",
        ]
        code_list = get_part_codes(code_list, exclude_industry=industry_list)

        # with open("..\\basicData\\self_selected\\板块50.txt", "r", encoding="utf-8", errors="ignore") as f:
        #     txt = f.read()
        #     code_list = re.findall(r'([0-9]{6})', txt)
            # code_list.reverse()
        return code_list

    def config_priority(self):
        widget = PriorityTable(self.style_df)
        widget.update_style.connect(self.config_style_df)
        widget.exec()

    def config_style_df(self, df):
        self.style_df.loc[df.index, 'info_priority'] = df.values
        self.update_style()

    def show_new_window(self):
        self.window2.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.window_flag = 0
        elif e.key() == Qt.Key_2:
            self.window_flag = 1
        elif e.key() == Qt.Key_3:
            self.window_flag = 2
        elif e.key() == Qt.Key_4:
            self.window_flag = 3
        self.update_window()


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
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    # main = MainWindow()
    main = MainWidget()
    # main.showMaximized()
    main.showMinimized()
    sys.exit(app.exec_())
