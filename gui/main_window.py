from method.dataMethod import sql2df
from request.requestData import request_data2mysql
from method.logMethod import log_it, MainLog
from method.mainMethod import sift_codes
from method.sortCode import random_code_list, sort_discount

from gui.checkTree import CheckTree
from gui.dataPix import DataPix
from gui.stockListView import QStockListView, CodesDataFrame

from gui.styleDataFrame import load_default_style
from gui.styleDataFrame import save_default_style
from gui.priorityTable import PriorityTable
from gui.showPix import ShowPix
from gui.remarkWidget import RemarkWidget
from gui.webWidget import WebWidget
from gui.equityChangeWidget import EquityChangeWidget

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import re
import threading
import time
import datetime as dt

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
        # self.codes_df.init_current_index(index=1100)
        self.codes_df.init_current_index(index=0)
        # self.codes_df.init_current_index(code='688261')
        # self.codes_df.init_current_index(code='002260')

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
        self.button6 = QPushButton('remark')
        self.button7 = QPushButton('code list')
        self.button8 = QPushButton('priority')
        self.button9 = QPushButton('new_window')
        self.button10 = QPushButton('web')
        self.button11 = QPushButton('equity_change')
        self.button12 = QPushButton('relocate')

        self.location_state = False

        self.editor1 = QLineEdit()
        self.editor1.setValidator(QIntValidator())
        self.editor1.setMaxLength(6)

        self.head_label1 = QLabel()
        self.head_label2 = QLabel()
        self.head_label3 = QLabel()

        self.bottom_label1 = QLabel()
        self.bottom_label2 = QLabel()

        self.tree = CheckTree(self.style_df)
        self.code_widget = QStockListView(self.codes_df)
        self.remark_widget = RemarkWidget(self)
        self.web_widget = WebWidget()
        self.equity_change_widget = EquityChangeWidget()
        self.counter_info = None
        self.real_cost = None
        self.max_increase_30 = 0

        self.window2 = ShowPix(main_window=self)

        self.tree.update_style.connect(self.update_style)
        self.code_widget.table_view.change_signal.connect(self.change_stock)

        self.cross = False
        self.ratio = 16
        self.init_ui()

        self.window_flag = 3
        self.show_list = list()
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

        self.head_label3.setFont(QFont('Consolas', 16))
        self.head_label3.setPalette(p)

        self.bottom_label1.setFont(QFont('Consolas', 12))
        self.bottom_label1.setPalette(p)
        self.bottom_label2.setFont(QFont('Consolas', 12))
        self.bottom_label2.setPalette(p)

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
        # layout2.addStretch(1)
        layout2.addWidget(self.bottom_label1, 1, Qt.AlignLeft | Qt.AlignTop)

        layout2.addWidget(self.button1, 0, Qt.AlignCenter)
        layout2.addWidget(self.button2, 0, Qt.AlignCenter)
        layout2.addWidget(self.button3, 0, Qt.AlignCenter)
        layout2.addWidget(self.button4, 0, Qt.AlignCenter)
        layout2.addWidget(self.button5, 0, Qt.AlignCenter)
        layout2.addWidget(self.button6, 0, Qt.AlignCenter)
        layout2.addWidget(self.button7, 0, Qt.AlignCenter)
        layout2.addWidget(self.button8, 0, Qt.AlignCenter)
        layout2.addWidget(self.button9, 0, Qt.AlignCenter)
        layout2.addWidget(self.button10, 0, Qt.AlignCenter)
        layout2.addWidget(self.button11, 0, Qt.AlignCenter)
        layout2.addWidget(self.button12, 0, Qt.AlignCenter)
        layout2.addWidget(self.editor1, 0, Qt.AlignCenter)

        layout2.addWidget(self.bottom_label2, 1, Qt.AlignRight | Qt.AlignTop)
        # layout2.addStretch(1)
        # layout2.addWidget(button1, 0, Qt.AlignCenter)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.bottom_label1, 1, Qt.AlignLeft | Qt.AlignTop)
        layout3.addWidget(self.bottom_label2, 1, Qt.AlignRight | Qt.AlignTop)
        # layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addStretch(1)
        # layout.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout.addLayout(layout0, 0)
        layout.addLayout(layout1, 0)
        layout.addLayout(layout2, 0)
        # layout.addLayout(layout3, 0)
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
        self.button6.clicked.connect(self.show_remark)
        self.button7.clicked.connect(self.show_code_list)
        self.button8.clicked.connect(self.config_priority)
        self.button9.clicked.connect(self.show_new_window)
        self.button10.clicked.connect(self.show_web)
        self.button11.clicked.connect(self.show_equity_change)
        self.button12.clicked.connect(self.relocate)
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
        action10 = QAction('添加非周期', menu)
        action11 = QAction('删除非周期', menu)

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
        menu.addAction(action10)
        menu.addAction(action11)
        menu.addSeparator()
        menu.addAction(action6)
        menu.addAction(action7)

        action1.triggered.connect(self.request_data)
        action6.triggered.connect(self.scale_down)
        action7.triggered.connect(self.scale_up)

        action2.triggered.connect(lambda x: self.add_code("../basicData/self_selected/gui_selected.txt"))
        action3.triggered.connect(lambda x: self.del_code("../basicData/self_selected/gui_selected.txt"))
        action4.triggered.connect(lambda x: self.add_code("../basicData/self_selected/gui_blacklist.txt"))
        action5.triggered.connect(lambda x: self.del_code("../basicData/self_selected/gui_blacklist.txt"))
        action8.triggered.connect(lambda x: self.add_code("../basicData/self_selected/gui_whitelist.txt"))
        action9.triggered.connect(lambda x: self.del_code("../basicData/self_selected/gui_whitelist.txt"))
        action10.triggered.connect(lambda x: self.add_code("../basicData/self_selected/gui_non_cyclical.txt"))
        action11.triggered.connect(lambda x: self.del_code("../basicData/self_selected/gui_non_cyclical.txt"))
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

    def show_remark(self):
        self.remark_widget.show()

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
            # self.show_pix()

    def show_pix(self):
        self.label.setPixmap(self.data_pix.pix_list[self.window_flag])

    def update_window(self):
        code = self.stock_code
        self.update_counter(code)
        self.show_pix()
        self.show_stock_name()
        self.remark_widget.download()

        self.web_widget.load_code(code)
        self.equity_change_widget.load_code(code)

    def update_counter(self, code):
        df = self.data_pix.df

        last_date = ''
        last_real_pe = np.inf
        number = 0

        if df.columns.size > 0:
            date = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            date = ''

        real_pe = np.inf
        if 's_034_real_pe' in df.columns:
            s0 = self.data_pix.df['s_034_real_pe'].copy().dropna()
            if s0.size > 0:
                date = s0.index[-1]
                real_pe = s0[-1]

        self.max_increase_30 = np.inf
        if 's_028_market_value' in df.columns:
            s0 = self.data_pix.df['s_028_market_value'].copy().dropna()
            if s0.size > 0:
                recent = s0[-1]
                size0 = min(s0.size, 30)
                minimum = min(s0[-size0:])
                self.max_increase_30 = recent / minimum - 1

        self.real_cost = None
        if 's_025_real_cost' in df.columns:
            s0 = self.data_pix.df['s_025_real_cost'].copy().dropna()
            if s0.size > 0:
                self.real_cost = s0[-1] / 1e8

        path = "../basicData/self_selected/gui_counter.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            res_dict = json.loads(f.read())
            data = res_dict.get(code)

        if isinstance(data, list):
            last_date = data[1]
            number = data[2]
            last_real_pe = data[3]
        elif data is not None:
            number = data

        if date > last_date:
            number += 1
            delta = (1/real_pe - 1/last_real_pe) * abs(last_real_pe)
            self.counter_info = [last_date, date, number, real_pe, delta]
            res_dict[code] = self.counter_info
            res = json.dumps(res_dict, indent=4, ensure_ascii=False)
            with open(path, "w", encoding='utf-8') as f:
                f.write(res)
        else:
            self.counter_info = res_dict.get(code)

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
        list1 = []

        path = "../basicData/self_selected/gui_selected.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('自选')

        path = "../basicData/self_selected/gui_whitelist.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('白')

        path = "../basicData/self_selected/gui_blacklist.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('黑')

        path = "../basicData/self_selected/gui_non_cyclical.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())
        if code in code_list:
            list0.append('非周期')

        data = self.counter_info
        if isinstance(data, list):
            txt_counter = '%s次/%.2f%%[%s]' % (data[2], data[4]*100, data[0])
        else:
            txt_counter = '%s次/%.2f%%[%s]' % (data, np.inf, '')

        list0.append('%.2f%%%s' % (self.max_increase_30*100, self.get_sign(self.max_increase_30)))
        list1.append(txt_counter)

        ass = None
        path = "../basicData/self_selected/gui_assessment.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
            ass_str = value_dict.get(code)
            if ass_str is not None:
                ass = int(ass_str)

        real_cost = self.real_cost

        txt_bottom1 = 'None'

        if real_cost is not None:
            if ass is not None:
                rate = real_cost / ass
                txt_bottom1 = '%.2f亿 / %s亿' % (real_cost, ass)
                list0.append('%.2f' % rate)
            else:
                txt_bottom1 = '%s%.2f亿' % ('cost: ', real_cost)

        txt3 = '/'.join(list0)
        txt_bottom2 = '/'.join(list1)

        GuiLog.add_log('show stock --> ' + txt1)
        self.head_label1.setText(txt1)
        self.head_label2.setText(txt2)
        self.head_label3.setText(txt3)

        self.bottom_label1.setText(txt_bottom1)
        self.bottom_label2.setText(txt_bottom2)

        if code in self.show_list:
            index = self.show_list.index(code)
            self.show_list.pop(index)
        self.show_list.append(code)
        if len(self.show_list) > 30:
            code = self.show_list.pop(0)
            self.df_dict.pop(code)
            self.pix_dict.pop(code)
            GuiLog.add_log('release stock --> ' + code)

    @staticmethod
    def get_sign(data):
        if not isinstance(data, (int, float)):
            return ''
        elif data > 0:
            return '↑'
        elif data < 0:
            return '↓'
        else:
            return '-'

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

    def get_code_list(self):
        blacklist = self.get_blacklist()

        ################################################################################################################

        # dir0 = 'update_20220331153503'
        dir0 = 'latest'

        # root = "..\\basicData\\analyzedData"
        # root = "..\\basicData\\self_selected"
        # root = "..\\basicData\\dailyUpdate\\%s" % dir0

        # file = "new_enter_code.txt"
        # file = "increase_code.txt"
        # file = "code_sorted_real_pe.txt"

        # file = "code_sorted_real_pe.txt"
        # file = "code_sorted_roe_parent.txt"
        # file = "sift_001_roe.txt"
        # file = "sift_002_real_pe.txt"
        # file = "sift_003_real_pe_current.txt"
        # file = "hs300.txt"

        # with open("%s\\jlr_codes.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\roe_codes2.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\return_year_codes.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\sift_code_006.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\sift_code_011.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\sift_003_real_pe_current.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\gui_selected.txt" % root, "r", encoding="utf-8", errors="ignore") as f:
        # with open("%s\\code_list.txt" % root, "r", encoding="utf-8", errors="ignore") as f:

        # with open("%s\\%s" % (root, file), "r", encoding="utf-8", errors="ignore") as f:
        #     code_list = json.loads(f.read())

        ################################################################################################################

        root = "..\\basicData\\dailyUpdate\\%s" % dir0
        # file = "code_sorted_real_pe.txt"
        file = "s002_code_sorted_real_pe.txt"

        with open("%s\\%s" % (root, file), "r", encoding="utf-8", errors="ignore") as f:
            code_list = json.loads(f.read())

        ################################################################################################################

        root = "..\\basicData\\dailyUpdate\\%s" % dir0
        # file = "code_latest_update.txt"
        file = "s004_code_latest_update.txt"

        with open("%s\\%s" % (root, file), "r", encoding="utf-8", errors="ignore") as f:
            latest_update = json.loads(f.read())

        ################################################################################################################

        with open("..\\basicData\\self_selected\\gui_hold.txt", "r", encoding="utf-8", errors="ignore") as f:
            tmp = json.loads(f.read())
            hold_list = list(zip(*tmp).__next__())

        ################################################################################################################

        # with open('../basicData/code_names_dict.txt', 'r', encoding='utf-8') as f:
        #     code_name_dict = json.loads(f.read())
        #
        # name_code_dict = dict()
        # for code, name in code_name_dict.items():
        #     name_code_dict[name] = code
        #
        # with open("..\\basicData\\self_selected\\gui_daily_select.txt", "r", encoding="utf-8", errors="ignore") as f:
        #     tmp = json.loads(f.read())
        #     tmp0 = list(zip(*tmp))
        # name_list = list(tmp0[1])
        # code_list = []
        #
        # for name in name_list:
        #     code_list.append(name_code_dict.get(name))

        ################################################################################################################

        # industry_list = [
        #     "C110101",
        #     "C110102",
        #     "C110103",
        #     "C030201",
        #     "C020203",
        #     "C070101",
        # ]
        # code_list = get_part_codes(code_list, exclude_industry=industry_list)

        ################################################################################################################

        # with open("..\\basicData\\self_selected\\板块50.txt", "r", encoding="utf-8", errors="ignore") as f:
        #     txt = f.read()
        #     code_list = re.findall(r'([0-9]{6})', txt)
        #     code_list.reverse()

        ################################################################################################################

        # path = "..\\basicData\\dailyUpdate\\latest\\s003_code_sorted_roe_parent.txt"
        # with open(path, "r", encoding="utf-8", errors="ignore") as f:
        #     code_list = json.loads(f.read())

        # code_list = sort_discount()

        code_list = sift_codes(
            source=code_list,
            # source=['C01'],
            blacklist=blacklist,
            # whitelist=whitelist,
            sort=code_list,
            # market='main',
            market='all',
        )
        # code_list = random_code_list(code_list, pick_weight=[30, 40, 30])
        # code_list = random_code_list(code_list, pick_weight=[75, 10, 15])
        # code_list = random_code_list(code_list, pick_weight=[1, 0, 0])

        # path = "..\\basicData\\dailyUpdate\\latest\\s005_code_random.txt"
        # # path = "..\\basicData\\dailyUpdate\\latest\\s003_code_sorted_roe_parent.txt"
        # with open(path, "r", encoding="utf-8", errors="ignore") as f:
        #     code_list = json.loads(f.read())

        # code_list = hold_list + code_list
        # code_list = latest_update + hold_list + code_list

        # code_list = hold_list

        # res = json.dumps(code_list, indent=4, ensure_ascii=False)
        # file = '..\\basicData\\analyzedData\\temp_codes.txt'
        # with open(file, "w", encoding='utf-8') as f:
        #     f.write(res)

        return code_list

    @staticmethod
    def get_blacklist():
        blacklist = []

        # with open("..\\bufferData\\codes\\blacklist.txt", "r", encoding="utf-8", errors="ignore") as f:
        #     blacklist = json.loads(f.read())

        ################################################################################################################

        path = "../basicData/dailyUpdate/latest/a003_report_date_dict.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            report_date_dict = json.loads(f.read())

        with open("..\\basicData\\self_selected\\gui_counter.txt", "r", encoding="utf-8", errors="ignore") as f:
            gui_counter = json.loads(f.read())
            # blacklist = list(gui_counter.keys())

        for key, value in gui_counter.items():
            report_date = report_date_dict.get(key)
            if report_date is None or report_date == 'Invalid da':
                report_date = ''
            if report_date <= value[1]:
                blacklist.append(key)

        #     tup_list = []
        #     for key, value in result.items():
        #         tup_list.append((key, value[1]))
        #
        #     tup_list = sorted(tup_list, key=lambda x: x[1])
        #     whitelist = zip(*tup_list).__next__()
        #     whitelist = whitelist[:50]

        return blacklist

    def config_priority(self):
        widget = PriorityTable(self.style_df)
        widget.update_style.connect(self.config_style_df)
        widget.exec()

    def config_style_df(self, df):
        self.style_df.loc[df.index, 'info_priority'] = df.values
        self.update_style()

    def show_new_window(self):
        self.window2.show()

    def show_web(self):
        self.web_widget.show()
        self.web_widget.load_code(self.stock_code)

    def show_equity_change(self):
        self.equity_change_widget.show()
        self.equity_change_widget.load_code(self.stock_code)

    def relocate(self):

        if self.location_state is False:

            self.web_widget.resize(960, 1008)
            self.web_widget.move(-971, -10)

            self.equity_change_widget.resize(940, 1008)
            self.equity_change_widget.move(-1916, -10)

            self.showMaximized()
            self.location_state = True

        else:
            self.web_widget.resize(960, 500)
            self.web_widget.move(0, 0)

            self.equity_change_widget.resize(940, 800)
            self.equity_change_widget.move(0, 0)
            self.location_state = False

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.window_flag = 0
        elif e.key() == Qt.Key_2:
            self.window_flag = 1
        elif e.key() == Qt.Key_3:
            self.window_flag = 2
        elif e.key() == Qt.Key_4:
            self.window_flag = 3
        # self.update_window()
        self.show_pix()


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
