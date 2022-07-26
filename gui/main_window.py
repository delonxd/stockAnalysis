from method.dataMethod import sql2df
from request.requestData import request_data2mysql
from method.logMethod import log_it, MainLog
from method.sortCode import sort_discount, sift_codes
from method.fileMethod import *

from gui.checkTree import CheckTree
from gui.dataPix import DataPix
from gui.stockListView import QStockListView, CodesDataFrame

from gui.styleDataFrame import load_default_style
from gui.styleDataFrame import save_default_style
from gui.priorityTable import PriorityTable
from gui.showPix import ShowPix
from gui.showPlot import ShowPlot
from gui.remarkWidget import RemarkWidget
from gui.webWidget import WebWidget
from gui.equityChangeWidget import EquityChangeWidget
from gui.comparisonWidget import ComparisonWidget

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
import matplotlib.pyplot as plt


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
            # print(zip(*self.buffer_list).__next__())
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

        code_list, code_index = self.get_code_list()

        self.codes_df = CodesDataFrame(code_list)
        self.codes_df.init_current_index(index=code_index)

        self.style_df = load_default_style()

        time0 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.log_path = '../bufferData/logs/gui_log/gui_log_%s.txt' % time0

        path = "..\\basicData\\dailyUpdate\\latest\\a000_log_data.txt"
        self.date_ini = load_json_txt(path)['update_date']

        self.df_dict = dict()
        self.pix_dict = dict()

        self.buffer = ReadSQLThread()
        self.buffer.signal1.connect(self.update_data_pix)

        code = self.stock_code
        self.style_df = load_default_style()
        self.data_pix = DataPix(code=code, style_df=pd.DataFrame(), df=pd.DataFrame())

        self.label = QLabel(self)

        self.button1 = QPushButton('export')
        self.button2 = QPushButton('save_codes')
        self.button3 = QPushButton('comparison')

        # self.button2 = QPushButton('x2')
        # self.button3 = QPushButton('/2')
        self.button4 = QPushButton('style')
        self.button5 = QPushButton('request')
        self.button6 = QPushButton('remark')
        self.button7 = QPushButton('code list')
        self.button8 = QPushButton('priority')
        self.button9 = QPushButton('plot')
        self.button10 = QPushButton('web')
        self.button11 = QPushButton('equity_change')
        self.button12 = QPushButton('relocate')

        self.button9.setCheckable(True)
        self.button10.setCheckable(True)
        self.button11.setCheckable(True)
        self.button12.setCheckable(True)

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
        self.window2 = ShowPlot()

        self.counter_info = None
        self.real_cost = None
        self.equity = np.nan
        self.listing_date = None
        self.max_increase_30 = 0
        self.turnover = 0

        # self.window2 = ShowPix(main_window=self)

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
        self.button2.clicked.connect(self.save_codes)
        self.button3.clicked.connect(self.compare_codes)
        # self.button2.clicked.connect(self.scale_up)
        # self.button3.clicked.connect(self.scale_down)

        self.button4.clicked.connect(self.show_tree)
        # self.button5.clicked.connect(self.request_data)
        self.button5.clicked.connect(self.request_data_quick)
        self.button6.clicked.connect(self.show_remark)
        self.button7.clicked.connect(self.show_code_list)
        self.button8.clicked.connect(self.config_priority)
        # self.button9.clicked.connect(self.show_new_window)
        self.button9.clicked.connect(self.show_plot)
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

        action_mark0 = QAction('取消标记', menu)
        action_mark1 = QAction('标记1', menu)
        action_mark2 = QAction('标记2', menu)
        action_mark3 = QAction('标记3', menu)

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

        menu.addSeparator()
        menu.addAction(action_mark1)
        menu.addAction(action_mark2)
        menu.addAction(action_mark3)
        menu.addAction(action_mark0)

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

        action_mark0.triggered.connect(lambda x: self.add_mark(0))
        action_mark1.triggered.connect(lambda x: self.add_mark(1))
        action_mark2.triggered.connect(lambda x: self.add_mark(2))
        action_mark3.triggered.connect(lambda x: self.add_mark(3))

        menu.exec_(QCursor.pos())

    def save_codes(self):
        code_list = self.codes_df.df['code'].tolist()
        file = 'code_list_%s' % time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        write_json_txt('..\\basicData\\tmp\\%s' % file, code_list)

    def add_mark(self, mark):
        path = "../basicData/self_selected/gui_mark.txt"
        mark_dict = load_json_txt(path, log=False)

        row = self.codes_df.df.iloc[self.code_index]
        code = row['code']

        if mark == 0:
            if code in mark_dict:
                mark_dict.pop(code)
        else:
            mark_dict[code] = mark

        write_json_txt(path, mark_dict, log=False)
        self.show_stock_name()

    @staticmethod
    def compare_codes():
        pass
        # widget = ComparisonWidget()
        # widget.show()

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

    def request_data_quick(self):
        code = self.stock_code

        request_data2mysql(
            stock_code=code,
            data_type='fs',
            start_date="2021-01-01",
        )

        # request_data2mysql(
        #     stock_code=code,
        #     data_type='mvs',
        #     start_date="1970-01-01",
        # )

        if code in self.df_dict.keys():
            self.df_dict.pop(code)

        if code in self.pix_dict.keys():
            self.pix_dict.pop(code)

        self.run_buffer()

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

        if self.window2.isHidden():
            return
        else:
            self.show_plot()

    def update_counter(self, code):
        df = self.data_pix.df

        last_date = ''
        last_real_pe = np.inf
        number = 0

        if df.columns.size > 0:
            # date = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y-%m-%d')
            date = self.date_ini
        else:
            date = ''

        real_pe = np.inf
        # tmp_date = ''
        if 's_034_real_pe' in df.columns:
            s0 = self.data_pix.df['s_034_real_pe'].copy().dropna()
            if s0.size > 0:
                # tmp_date = max(s0.index[-1], tmp_date)
                real_pe = s0[-1]

        # if 'dt_fs' in df.columns:
        #     s0 = self.data_pix.df['dt_fs'].copy().dropna()
        #     if s0.size > 0:
        #         tmp_date = max(s0.index[-1], tmp_date)
        #
        # if tmp_date != '' and tmp_date != 'Invalid da':
        #     date = tmp_date

        self.max_increase_30 = np.inf
        self.listing_date = None
        if 's_028_market_value' in df.columns:
            s0 = self.data_pix.df['s_028_market_value'].copy().dropna()
            if s0.size > 0:
                recent = s0[-1]
                size0 = min(s0.size, 90)
                minimum = min(s0[-size0:])
                self.max_increase_30 = recent / minimum - 1
                self.listing_date = s0.index[0]

        self.real_cost = None
        if 's_025_real_cost' in df.columns:
            s0 = self.data_pix.df['s_025_real_cost'].copy().dropna()
            if s0.size > 0:
                self.real_cost = s0[-1] / 1e8

        self.turnover = 0
        if 's_043_turnover_volume_ttm' in df.columns:
            s0 = self.data_pix.df['s_043_turnover_volume_ttm'].copy().dropna()
            if s0.size > 0:
                self.turnover = s0[-1]

        self.equity = np.nan
        if 's_002_equity' in df.columns:
            s0 = self.data_pix.df['s_002_equity'].copy().dropna()
            if s0.size > 0:
                self.equity = s0[-1] / 1e8

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

        path = "../basicData/self_selected/gui_timestamp.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            timestamps = json.loads(f.read())

        timestamps[code] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        res = json.dumps(timestamps, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

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

        if code in load_json_txt("../basicData/self_selected/gui_selected.txt", log=False):
            list0.append('自选')
        if code in load_json_txt("../basicData/self_selected/gui_whitelist.txt", log=False):
            list0.append('白')
        if code in load_json_txt("../basicData/self_selected/gui_blacklist.txt", log=False):
            list0.append('黑')
        if code in load_json_txt("../basicData/self_selected/gui_non_cyclical.txt", log=False):
            list0.append('非周期')

        mark = load_json_txt("../basicData/self_selected/gui_mark.txt", log=False).get(code)
        if mark is not None:
            txt2 = txt2 + '(%s)' % mark

        data = self.counter_info
        if isinstance(data, list):
            txt_counter = '%s次/%.2f%%[%s]' % (data[2], data[4]*100, data[0])
        else:
            txt_counter = '%s次/%.2f%%[%s]' % (data, np.inf, '')

        list0.append('%.2f%%%s' % (self.max_increase_30*100, self.get_sign(self.max_increase_30)))

        if self.listing_date is not None:
            list0.insert(0, self.listing_date)

        list1.append(txt_counter)

        ass = None
        path = "../basicData/self_selected/gui_assessment.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
            ass_str = value_dict.get(code)
            if ass_str is not None:
                try:
                    ass = int(ass_str)
                except Exception as e:
                    print(e)

        real_cost = self.real_cost
        equity = self.equity

        txt_bottom1 = 'None'

        if real_cost is not None:
            if ass is not None:
                rate = real_cost / ass
                txt_bottom1 = '%.2f亿 / %s亿' % (real_cost, ass)
                list0.append('%.2f' % rate)
                rate = ass / equity
                list0.append('%.2f' % rate)
            else:
                txt_bottom1 = '%s%.2f亿' % ('cost: ', real_cost)

        if ass is not None:
            rate = self.turnover / 1e6 / ass
            txt2 = txt2 + '-%.2f%%' % rate

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
            # self.cross = not self.cross

            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())
            # GuiLog.write(self.log_path)
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

        mission = 5

        code_list = []
        code_index = 0

        if mission == 0:

            code_list = sift_codes(
                source='old',
            )

            # code_index = '688072'
            # code_index = 65

        elif mission == 1:

            code_list = sift_codes(
                source='real_pe',
                # sort='real_pe',
                market='all',
                # random=False,
                random=True,
                interval=80,
                mode='all-whitelist',
            )

        elif mission == 2:

            code_list = sift_codes(
                source='hold',
                # source='all',
                # source='latest_update',
                # source='sort-equity',
                # source='sort-ass',
            )

        elif mission == 3:

            code_list = sift_codes(
                source='all',
                sort='sort-ass/equity',
                # market='main',
                market='main+growth',
                # insert=0,
                random=True,
                interval=40,
                # mode='whitelist+selected',
                mode='whitelist-selected',
            )

        elif mission == 4:

            code_list = sift_codes(
                source='selected',
                # source='mark-1',
                sort='sort-ass/equity',
                # sort='sort-ass/turnover',
                # reverse=True,
                # market='main',
                # market='growth',
                market='main+growth',

                random=True,
                interval=100,
                mode='selected',
                # mode='whitelist+selected',
            )

            # code_index = '603666'
            # code_index = '002043'
            code_index = 0

        elif mission == 5:

            code_list = sift_codes(
                source='whitelist',
                sort='industry',
                # reverse=True,
                # market='main+growth',
            )
            # code_index = '002043'

        elif mission == 6:

            code_list = sift_codes(
                source='whitelist',
                blacklist='sort-ass/equity',
                # market='main',
                # market='non_main',
                market='growth',
            )

        elif mission == 7:

            code_list = sift_codes(
                ids_names=['2-光伏设备'],
                sort='real_pe',
                market='all',
            )

        ################################################################################################################

        if len(code_list) == 0:
            raise KeyboardInterrupt('len(code_list) == 0')

        path = '..\\basicData\\tmp\\code_list_latest.txt'
        write_json_txt(path, code_list)

        return code_list, code_index

    def config_priority(self):
        widget = PriorityTable(self.style_df)
        widget.update_style.connect(self.config_style_df)
        widget.exec()

    def config_style_df(self, df):
        self.style_df.loc[df.index, 'info_priority'] = df.values
        self.update_style()

    def show_new_window(self):
        self.window2.show()

    def show_plot(self):
        if self.button9.isChecked():

            df = self.data_pix.df
            s0 = pd.Series()
            if 's_028_market_value' in df.columns:
                s0 = self.data_pix.df['s_028_market_value'].copy().dropna()
                s0 = s0[-1250:]

            self.window2.show_plot(title=self.stock_code, series=s0)
        else:
            self.window2.close()

    def show_web(self):
        if self.button10.isChecked():
            self.web_widget.show()
            self.web_widget.load_code(self.stock_code)
        else:
            self.web_widget.close()

    def show_equity_change(self):
        if self.button11.isChecked():
            self.equity_change_widget.show()
            self.equity_change_widget.load_code(self.stock_code)
        else:
            self.equity_change_widget.close()

    def relocate(self):
        if self.button12.isChecked():
            self.web_widget.resize(960, 1008)
            self.web_widget.move(-971, -10)

            self.equity_change_widget.resize(940, 1008)
            self.equity_change_widget.move(-1916, -10)

            self.window2.move(-1906, 10)
            self.showMaximized()
        else:
            self.web_widget.resize(960, 500)
            self.web_widget.move(0, 0)

            self.equity_change_widget.resize(940, 800)
            self.equity_change_widget.move(0, 0)

            self.window2.move(10, 10)
            self.showMaximized()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.window_flag = 0
        elif e.key() == Qt.Key_2:
            self.window_flag = 1
        elif e.key() == Qt.Key_3:
            self.window_flag = 2
        elif e.key() == Qt.Key_4:
            self.window_flag = 3
        elif e.key() == Qt.Key_Space:
            self.cross = not self.cross
        elif e.key() == Qt.Key_S:
            GuiLog.write(self.log_path)

        # self.update_window()
        self.show_pix()

    def closeEvent(self, event):
        self.tree.close()
        self.code_widget.close()
        self.remark_widget.close()
        self.web_widget.close()
        self.equity_change_widget.close()
        self.window2.close()


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

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 100000)

    app = QApplication(sys.argv)
    # main = MainWindow()
    main = MainWidget()
    main.showMaximized()
    # main.showMinimized()
    sys.exit(app.exec_())
