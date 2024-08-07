from request.requestData import request2mysql
from request.requestEquityData import request_eq2mysql
from method.sortCode import sift_codes
from method.fileMethod import *
from method.mainMethod import deco_show_stock_name, discount_to_date, sort_tags
from method.mainMethod import try_decorator
from method.recognitionMethod import get_except_list
from method.showTable import get_recent_val, get_recent_index

from gui.styleWidget import StyleWidget
from gui.dataPix import DataPix
from gui.stockListView import QStockListView, CodesDataFrame
from gui.fsView import FsView

from gui.showPlot import show_plt

from gui.remarkWidget import RemarkWidget
from gui.checkWidget import CheckWidget
from gui.webWidget import WebWidget
from gui.equityChangeWidget import EquityChangeWidget

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# import sys
# import json
# import re
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
        self.current = ''
        self.lock = threading.Lock()

    def run(self):
        GuiLog.add_log('thread start')

        while True:
            self.lock.acquire()
            if len(self.buffer_list) > 0:
                code, style_df, df, ratio, _ = self.buffer_list.pop(0)
                self.current = code
            else:
                break
            self.lock.release()
            res0 = DataPix(code=code, style_df=style_df, df=df, ratio=ratio)
            GuiLog.add_log('    add buffer %s' % code)
            # print(len(self.buffer_list))
            # if len(self.buffer_list) > 0:
            #     print(zip(*self.buffer_list).__next__())
            self.signal1.emit(res0)

        self.current = ''
        GuiLog.add_log('thread end')
        self.lock.release()

    def extend(self, message_list):
        self.lock.acquire()
        message_list.reverse()
        for message in message_list:
            code = message[0]

            if code == self.current and message[-1] is False:
                continue

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

        self.backup_data()
        code_list, code_index = self.init_code_list()

        self.codes_df = CodesDataFrame(code_list, code_index)

        time0 = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.log_path = '..\\bufferData\\logs\\gui_log\\gui_log_%s.txt' % time0

        path = "..\\basicData\\dailyUpdate\\latest\\a000_log_data.txt"
        self.date_ini = load_json_txt(path)['update_date']

        self.df_dict = dict()
        self.pix_dict = dict()

        self.buffer = ReadSQLThread()
        self.buffer.signal1.connect(self.update_data_pix)

        code = self.stock_code
        self.style_df = load_pkl('..\\gui\\styles\\style_default.pkl')
        self.data_pix = DataPix(code=code, style_df=pd.DataFrame(), df=pd.DataFrame())

        self.label = QLabel(self)

        self.pad_l = QLabel()
        self.pad_r = QLabel()

        self.pad_l_pix = QPixmap(130, 900)
        self.pad_r_pix = QPixmap(130, 900)

        self.pad_l_pix.fill(QColor(40, 40, 40, 255))
        self.pad_r_pix.fill(QColor(40, 40, 40, 255))

        # self.button1 = QPushButton('export')
        # self.button2 = QPushButton('save_codes')
        # self.button3 = QPushButton('comparison')

        self.button12 = QPushButton('relocate')

        self.editor1 = QLineEdit()
        self.editor1.setValidator(QIntValidator())
        self.editor1.setMaxLength(6)

        self.head_label1 = QLabel()
        self.head_label2 = QLabel()
        self.head_label3 = QLabel()

        self.bottom_label1 = QLabel()
        self.bottom_label2 = QLabel()

        self.code_widget = QStockListView(self.codes_df)
        self.style_widget = StyleWidget()
        self.style_dict = {}

        self.remark_widget = RemarkWidget(self)
        self.check_widget = CheckWidget(self)

        self.web_widget = WebWidget()
        self.equity_change_widget = EquityChangeWidget()
        self.fs_view = FsView()

        self.widgets_layer = [self]
        self.widgets_button = {
            self.fs_view: QPushButton('fs_data'),
            self.style_widget:  QPushButton('style'),
            self.remark_widget: QPushButton('remark'),
            self.code_widget: QPushButton('code list'),
            self.check_widget: QPushButton('check'),
            self.web_widget: QPushButton('web'),
            self.equity_change_widget: QPushButton('equity_change'),
        }

        self.page_button1 = QPushButton('<<')
        self.page_button2 = QPushButton('>>')
        # self.window2 = ShowPlot()

        self.data = dict()

        self.plt_rect = [10, 32, 1600, 900]
        self.mouse_pos = [None, None]
        # self.window2 = ShowPix(main_window=self)

        # self.tree.update_style.connect(self.update_style)
        self.code_widget.table_view.change_signal.connect(self.change_stock)
        self.style_widget.signal_all.connect(self.change_style_all)
        self.style_widget.signal_cur.connect(self.change_style_current)

        self.cross = False
        self.box = 1
        self.draw_flag = False
        self.draw_pos = None
        self.ratio_dict = dict()
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

    @property
    def current_style(self):
        code = self.stock_code
        style_df = self.style_df
        if code in self.style_dict:
            style_df = self.style_dict[code]
        return style_df

    def df_dict_copy(self, code):
        df = self.df_dict.get(code)
        return None if df is None else df.copy()

    def init_ui(self):

        self.setWindowTitle('main_window')
        self.resize(1600, 900)

        p = QPalette()
        p.setColor(QPalette.WindowText, Qt.GlobalColor.red)
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

        ali = Qt.AlignmentFlag
        layout0 = QHBoxLayout()
        layout0.addWidget(self.head_label2, 1, ali.AlignLeft | ali.AlignBottom)
        layout0.addWidget(self.head_label1, 0, ali.AlignCenter)
        layout0.addWidget(self.head_label3, 1, ali.AlignRight | ali.AlignBottom)
        # layout0.addStretch(1)

        layout1 = QHBoxLayout()
        layout1.addStretch(1)
        # layout.addWidget(self.tree, 0, ali.AlignCenter)
        layout1.addWidget(self.label, 0, ali.AlignCenter)
        layout1.addStretch(1)

        layout2 = QHBoxLayout()
        # layout2.addStretch(1)
        layout2.addWidget(self.bottom_label1, 1, ali.AlignLeft | ali.AlignTop)

        layout2.addWidget(self.page_button1, 0, ali.AlignCenter)
        for widget, button in self.widgets_button.items():
            layout2.addWidget(button, 0, ali.AlignCenter)

        layout2.addWidget(self.button12, 0, ali.AlignCenter)
        layout2.addWidget(self.page_button2, 0, ali.AlignCenter)

        layout2.addWidget(self.bottom_label2, 1, ali.AlignRight | ali.AlignTop)
        # layout2.addStretch(1)
        # layout2.addWidget(button1, 0, Qt.AlignCenter)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.bottom_label1, 1, ali.AlignLeft | ali.AlignTop)
        layout3.addWidget(self.bottom_label2, 1, ali.AlignRight | ali.AlignTop)
        # layout0.addStretch(1)

        layout = QVBoxLayout()
        layout.addStretch(1)
        # layout.addWidget(self.stock_label, 0, Qt.AlignCenter)
        layout.addLayout(layout0, 0)
        layout.addLayout(layout1, 0)
        layout.addLayout(layout2, 0)
        # layout.addLayout(layout3, 0)
        layout.addStretch(1)

        layout_l = QVBoxLayout()
        layout_l.addStretch(1)
        layout_l.addWidget(self.pad_l, 0, ali.AlignCenter)
        layout_l.addStretch(1)

        layout_r = QVBoxLayout()
        layout_r.addStretch(1)
        layout_r.addWidget(self.pad_r, 0, ali.AlignCenter)
        layout_r.addStretch(1)

        m_layout = QHBoxLayout()
        m_layout.addStretch(1)
        m_layout.addLayout(layout_l, 0)
        m_layout.addLayout(layout, 0)
        m_layout.addLayout(layout_r, 0)
        m_layout.addStretch(1)

        self.setLayout(m_layout)
        # self.setCentralWidget(layout)

        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.center()

        self.pad_l.setPixmap(self.pad_l_pix)
        self.pad_r.setPixmap(self.pad_r_pix)

        for widget, button in self.widgets_button.items():
            button.setCheckable(True)
            button.clicked.connect(self.get_show_func(widget))
            widget.close_signal.connect(self.sub_widget_close)

        self.page_button1.clicked.connect(self.code_widget.table_view.backward)
        self.page_button2.clicked.connect(self.code_widget.table_view.forward)
        # self.button1.clicked.connect(self.export_style)
        # self.button2.clicked.connect(self.save_codes)
        # self.button3.clicked.connect(self.compare_codes)

        self.button12.setCheckable(True)
        self.button12.clicked.connect(self.relocate)

        self.editor1.textChanged.connect(self.editor1_changed)

        palette1 = QPalette()
        palette1.setColor(self.backgroundRole(), QColor(40, 40, 40, 255))
        self.setPalette(palette1)
        self.setAutoFillBackground(True)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)  # 开放右键策略

    def show_menu(self, _):  # 添加右键菜单
        menu = QMenu(self)

        name_list = [
            '选择',
            '加载',
            '添加列表',
            '删除列表',
            '添加自选',
            '删除自选',
            '添加白名单',
            '删除白名单',
            '添加灰名单',
            '删除灰名单',
            '添加Src',
            '删除Src',
            '添加Toc',
            '删除Toc',
            '添加国有',
            '删除国有',
            '上移',
            '下移',
        ]

        actions = {}
        for name in name_list:
            actions[name] = QAction(name, menu)

        menu.addAction(actions['选择'])
        menu.addAction(actions['加载'])

        menu.addSeparator()
        sub_menu1 = menu.addMenu('评级')

        menu.addSeparator()
        sub_menu2 = menu.addMenu('功能')

        menu.addSeparator()
        # sub_menu3 = menu.addMenu('添加备注')

        menu.addSeparator()
        menu.addAction(actions['添加列表'])
        menu.addAction(actions['删除列表'])

        menu.addSeparator()
        menu.addAction(actions['添加自选'])
        menu.addAction(actions['删除自选'])

        menu.addSeparator()
        menu.addAction(actions['添加白名单'])
        menu.addAction(actions['删除白名单'])

        menu.addSeparator()
        menu.addAction(actions['添加灰名单'])
        menu.addAction(actions['删除灰名单'])

        menu.addSeparator()
        menu.addAction(actions['添加Src'])
        menu.addAction(actions['删除Src'])

        menu.addSeparator()
        menu.addAction(actions['添加Toc'])
        menu.addAction(actions['删除Toc'])

        menu.addSeparator()
        menu.addAction(actions['添加国有'])
        menu.addAction(actions['删除国有'])

        menu.addSeparator()
        menu.addAction(actions['上移'])
        menu.addAction(actions['下移'])

        actions['选择'].triggered.connect(self.code_widget.button4.clicked)
        actions['加载'].triggered.connect(self.code_widget.button3.clicked)

        actions['上移'].triggered.connect(lambda x: self.scale_change(0.5))
        actions['下移'].triggered.connect(lambda x: self.scale_change(2))

        actions['添加列表'].triggered.connect(lambda x: self.code_operate('add'))
        actions['删除列表'].triggered.connect(lambda x: self.code_operate('del'))

        actions['添加自选'].triggered.connect(lambda x: self.code_operate('add', '自选'))
        actions['删除自选'].triggered.connect(lambda x: self.code_operate('del', '自选'))

        actions['添加白名单'].triggered.connect(lambda x: self.code_operate('add', '白名单'))
        actions['删除白名单'].triggered.connect(lambda x: self.code_operate('del', '白名单'))

        actions['添加灰名单'].triggered.connect(lambda x: self.code_operate('add', '灰名单'))
        actions['删除灰名单'].triggered.connect(lambda x: self.code_operate('del', '灰名单'))

        actions['添加Src'].triggered.connect(lambda x: self.code_operate('add', 'Src'))
        actions['删除Src'].triggered.connect(lambda x: self.code_operate('del', 'Src'))

        actions['添加Toc'].triggered.connect(lambda x: self.code_operate('add', 'Toc'))
        actions['删除Toc'].triggered.connect(lambda x: self.code_operate('del', 'Toc'))

        actions['添加国有'].triggered.connect(lambda x: self.code_operate('add', '国有'))
        actions['删除国有'].triggered.connect(lambda x: self.code_operate('del', '国有'))

        ################################################

        action_mark0 = QAction('取消评级', menu)
        action_mark1 = QAction('AAA', menu)
        action_mark2 = QAction('AA', menu)
        action_mark3 = QAction('A', menu)
        action_mark4 = QAction('BBB', menu)
        action_mark5 = QAction('BB', menu)
        action_mark6 = QAction('B', menu)
        action_mark7 = QAction('CCC', menu)
        action_mark8 = QAction('CC', menu)
        action_mark9 = QAction('C', menu)

        sub_menu1.addAction(action_mark1)
        sub_menu1.addAction(action_mark2)
        sub_menu1.addAction(action_mark3)
        sub_menu1.addSeparator()
        sub_menu1.addAction(action_mark4)
        sub_menu1.addAction(action_mark5)
        sub_menu1.addAction(action_mark6)
        sub_menu1.addSeparator()
        sub_menu1.addAction(action_mark7)
        sub_menu1.addAction(action_mark8)
        sub_menu1.addAction(action_mark9)
        sub_menu1.addSeparator()
        sub_menu1.addAction(action_mark0)

        action_mark0.triggered.connect(lambda x: self.add_mark(None))
        action_mark1.triggered.connect(lambda x: self.add_mark('AAA'))
        action_mark2.triggered.connect(lambda x: self.add_mark('AA'))
        action_mark3.triggered.connect(lambda x: self.add_mark('A'))
        action_mark4.triggered.connect(lambda x: self.add_mark('BBB'))
        action_mark5.triggered.connect(lambda x: self.add_mark('BB'))
        action_mark6.triggered.connect(lambda x: self.add_mark('B'))
        action_mark7.triggered.connect(lambda x: self.add_mark('CCC'))
        action_mark8.triggered.connect(lambda x: self.add_mark('CC'))
        action_mark9.triggered.connect(lambda x: self.add_mark('C'))

        ################################################

        sub_menu2_action1 = QAction('保存代码组', menu)
        sub_menu2_action2 = QAction('显示图像', menu)

        sub_menu2_action3 = QAction('更新数据', menu)
        sub_menu2_action4 = QAction('快速更新', menu)

        sub_menu2.addAction(sub_menu2_action3)
        sub_menu2.addAction(sub_menu2_action4)
        sub_menu2.addSeparator()
        sub_menu2.addAction(sub_menu2_action1)
        sub_menu2.addAction(sub_menu2_action2)

        sub_menu2_action1.triggered.connect(self.save_codes)
        sub_menu2_action2.triggered.connect(self.show_plot)
        sub_menu2_action3.triggered.connect(self.request_data)
        sub_menu2_action4.triggered.connect(self.request_data_quick)

        ################################################

        menu.exec_(QCursor.pos())

    def save_codes(self):
        code_list = self.codes_df.df['code'].tolist()
        file = 'code_list_%s' % time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        write_json_txt('..\\basicData\\tmp\\%s' % file, code_list)

    @deco_show_stock_name
    def add_mark(self, mark):
        path = "../basicData/self_selected/gui_mark.txt"
        mark_dict = load_json_txt(path, log=False)

        row = self.codes_df.df.iloc[self.code_index]
        code = row['code']

        if mark is None:
            if code in mark_dict:
                mark_dict.pop(code)
        else:
            mark_dict[code] = mark

        write_json_txt(path, mark_dict, log=False)

    @deco_show_stock_name
    def code_operate(self, func, tag=None):
        if tag is None:
            items = [
                '忽略',
                '电池',
                '光伏',
            ]
            tag, _ = QInputDialog.getItem(self, '获取列表中的选项', '列表', items, editable=False)

        row = self.codes_df.df.iloc[self.code_index]
        code = row['code']
        tags_operate([code], tag, func)

    def request_data(self):
        code = self.stock_code

        request2mysql(
            stock_code=code,
            data_type='fs',
            start_date="1970-01-01",
        )

        request2mysql(
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

        request2mysql(
            stock_code=code,
            data_type='fs',
            start_date="2021-01-01",
        )

        request_eq2mysql([code])

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

    def change_style_all(self, style_df):
        flag = style_df.equals(self.style_df)
        if not flag:
            self.style_df = style_df.copy()
            self.pix_dict.clear()
            self.style_dict.clear()
            self.run_buffer()

    def change_style_current(self, style_df):
        code = self.stock_code
        self.style_dict[code] = style_df.copy()

        if code in self.pix_dict:
            self.pix_dict.pop(code)

        ratio = self.ratio_dict.get(code)
        ratio = 16 if ratio is None else ratio

        df = self.df_dict_copy(code)
        message = [code, style_df, df, ratio, True]
        self.send_message(message)

        if style_df.equals(self.style_df):
            self.style_dict.pop(code)

    def scale_change(self, val):
        code = self.stock_code

        ratio = self.ratio_dict.get(code)
        ratio = 16 if ratio is None else ratio
        ratio = ratio * val
        self.ratio_dict[code] = ratio

        if ratio == 16:
            self.ratio_dict.pop(code)

        style = self.style_df.copy()
        df = self.df_dict_copy(code)
        message = [code, style, df, ratio, True]
        self.send_message(message)

    def run_buffer(self):
        message_list = list()
        codes = self.codes_df.generate_buffer_list(20, 2)
        for code in codes:
            if code not in self.pix_dict.keys():
                style = self.style_df.copy()
                df = self.df_dict_copy(code)
                ratio = self.ratio_dict.get(code)
                message = [code, style, df, ratio, False]
                message_list.append(message)

        self.buffer.extend(message_list)
        self.buffer.start()

    def send_message(self, message):
        self.buffer.extend([message])
        self.buffer.start()

    def update_data_pix(self, data_pix):
        df_dict = self.df_dict
        pix_dict = self.pix_dict

        flag1 = len(df_dict) > 35
        flag2 = len(pix_dict) > 35

        if flag1 or flag2:
            buffer = self.codes_df.generate_buffer_list(23, 5)
            show = self.show_list
            codes = buffer + show

            if flag1:
                for key in df_dict.keys():
                    if key not in codes:
                        df_dict.pop(key)
                        # GuiLog.add_log('release df_dict --> ' + key)
                        break

            if flag2:
                for key in pix_dict.keys():
                    if key not in codes:
                        pix_dict.pop(key)
                        # GuiLog.add_log('release px_dict --> ' + key)
                        break

        code = data_pix.code
        pix_dict[code] = data_pix
        df_dict[code] = data_pix.df

        if code == self.stock_code:
            self.data_pix = data_pix
            self.update_window()
            # self.show_pix()

    def show_pix(self):
        self.label.setPixmap(self.data_pix.pix_show[self.window_flag])

    def update_window(self):
        code = self.stock_code
        self.update_counter(code)
        self.show_pix()
        self.show_stock_name()
        self.remark_widget.download()
        self.check_widget.download()

        self.web_widget.load_code(code)
        self.equity_change_widget.load_code(code)
        self.fs_view.load_df(code)

        self.style_widget.refresh_style(self.current_style)

        if plt.fignum_exists(1):
            self.show_plot()

    def generate_sql_data_dict(self, code, sql_df):
        data = dict()

        # 处理sql_df数据
        data['real_pe'] = get_recent_val(sql_df, 's_034_real_pe', np.inf)
        data['market_value'] = get_recent_val(sql_df, 's_028_market_value', np.nan)
        data['market_value2'] = get_recent_val(sql_df, 's_028_market_value', np.nan, 2)
        data['listing_date'] = get_recent_index(sql_df, 's_028_market_value', None, 0, False)
        data['yesterday_rise'] = (data['market_value'] / data['market_value2']) - 1
        data['liquidation_asset'] = get_recent_val(sql_df, 's_026_liquidation_asset', np.nan)
        data['real_cost'] = get_recent_val(sql_df, 's_025_real_cost', np.nan)
        data['turnover'] = get_recent_val(sql_df, 's_043_turnover_volume_ttm', 0)
        data['equity'] = get_recent_val(sql_df, 's_002_equity', np.nan)
        data['equity_ratio'] = get_recent_val(sql_df, 's_067_equity_ratio', np.nan)

        data['salary_cost'] = get_recent_val(sql_df, 's_053_core_profit_salary', np.nan)
        data['profit_salary_min'] = get_recent_val(sql_df, 's_063_profit_salary2', np.nan)
        tmp_date = get_recent_index(sql_df, 's_063_profit_salary2', np.nan)
        # data['profit_salary_date'] = tmp_date
        data['predict_delta'] = 0
        if not pd.isna(tmp_date):
            date1 = dt.datetime.strptime(tmp_date, "%Y-%m-%d").date()
            date2 = dt.date.today()
            data['predict_delta'] = (date2 - date1).days

        data['dividend_return'] = get_recent_val(sql_df, 's_069_dividend_rate', 0)
        data['dividend_return'] = data['dividend_return'] * 100
        data['dilution_rate'] = get_recent_val(sql_df, 'eq_012_dilution_rate', 0)

        # 处理actual_controller
        path = "..\\basicData\\actual_controller.txt"
        tmp_res = load_json_txt(path, False).get(code)
        data['actual_controller'] = tmp_res if tmp_res is not None else ''

        # 处理counter_data
        path = "../basicData/self_selected/gui_counter.txt"
        counter_dict = load_json_txt(path, False)
        counter_data = counter_dict.get(code)

        present_date = self.date_ini if sql_df.columns.size > 0 else None
        last_date = counter_data[1] if isinstance(counter_data, list) else None

        if present_date is None:
            data['counter_data'] = counter_data
        elif last_date is None:
            data['counter_data'] = ["", present_date, 1, data['real_pe'], np.nan]
            counter_dict[code] = data['counter_data']
            write_json_txt(path, counter_dict, False)
        elif present_date > last_date:
            number = counter_data[2] + 1
            last_real_pe = counter_data[3]
            delta = (1/data['real_pe'] - 1/last_real_pe) * abs(last_real_pe)
            data['counter_data'] = [last_date, present_date, number, data['real_pe'], delta]
            counter_dict[code] = data['counter_data']
            write_json_txt(path, counter_dict, False)
        else:
            data['counter_data'] = counter_data

        # 处理标题颜色
        path = "..\\basicData\\dailyUpdate\\latest\\a003_report_date_dict.txt"
        report_date = load_json_txt(path, False).get(code)

        color = Qt.GlobalColor.red
        color_white = Qt.GlobalColor.white
        if report_date is not None:
            if counter_data is None:
                color = color_white
            elif counter_data[1] < report_date:
                color = color_white
            elif self.date_ini == counter_data[1]:
                if counter_data[0] < report_date:
                    color = Qt.GlobalColor.white
        data['name_color'] = color

        # 处理时间戳
        path = "../basicData/self_selected/gui_timestamp.txt"
        timestamps = load_json_txt(path, False)
        timestamps[code] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        write_json_txt(path, timestamps, False)

        self.data = data

    def generate_gui_data_dict(self, code):
        data = self.data

        path = "..\\basicData\\self_selected\\gui_tags.txt"
        data['gui_tags'] = gui_tags = load_json_txt(path, False).get(code)
        path = "..\\basicData\\self_selected\\gui_rate.txt"
        data['gui_rate'] = gui_rate = load_json_txt(path, False).get(code)
        path = "..\\basicData\\self_selected\\gui_assessment.txt"
        data['gui_ass'] = gui_ass = load_json_txt(path, False).get(code)
        path = "..\\basicData\\self_selected\\gui_mark.txt"
        data['gui_mark'] = load_json_txt(path, False).get(code)

        # gui_export
        path = "..\\basicData\\self_selected\\gui_export.txt"
        gui_export = load_json_txt(path, False).get(code)
        gui_export = int(gui_export) if gui_export is not None else np.nan
        data['gui_export'] = gui_export

        # gui_tags
        if gui_tags is not None:
            tags_list = gui_tags.split('#')
            tags_list.pop(tags_list.index(''))
        else:
            tags_list = []
        data['gui_tags_list'] = sort_tags(tags_list)

        # gui_rate
        gui_rate = int(gui_rate) if gui_rate is not None else np.nan
        rate_adj = 0 if pd.isna(gui_rate) else gui_rate
        rate_adj = 25 if rate_adj > 25 else rate_adj
        data['predict_rate'] = rate_adj * data['predict_delta'] / 36500 + 1
        data['predict_profit'] = data['predict_rate'] * data['profit_salary_min']
        data['predict_discount'] = data['predict_profit'] / data['real_cost'] / 0.1
        data['discount_date'] = discount_to_date(data['predict_discount'] / 9, 1.2)

        # gui_ass
        gui_ass = int(gui_ass) if gui_ass is not None else np.nan
        data['liq_cost'] = data['equity'] - data['liquidation_asset']
        data['predict_ass'] = gui_ass * data['predict_rate'] * 1e8

        data['ass_rate1'] = data['market_value'] / (data['predict_ass'] - data['liq_cost'] / 2)
        data['ass_rate1_convert'] = (1 / ((data['ass_rate1'] / 2) ** 0.1) - 1) * 100

        data['ass_rate2'] = data['market_value'] / (data['predict_ass'] + data['liquidation_asset'] / 2)
        data['ass_rate2_convert'] = (1 / ((data['ass_rate2'] / 2) ** 0.1) - 1) * 100

        data['ass_rate3'] = gui_ass / data['equity'] * 1e8

        data['liq_cost_rate'] = data['liq_cost'] / data['profit_salary_min']
        data['salary_cost_rate'] = data['salary_cost'] / data['profit_salary_min'] / 0.1

        data['gui_rate_dv'] = np.nan
        try:
            data['gui_rate_dv'] = gui_rate + data['dividend_return']
        finally:
            pass
        self.data = data
        self.generate_pad_data()

    def generate_pad_data(self):
        data = self.data
        left_pad_list = []
        except_list = get_except_list(self.stock_code, self.codes_df.df_all, log=False)
        for val, color, condition in except_list:
            flag = False
            if isinstance(condition, bool):
                flag = condition
            elif isinstance(condition, str):
                try:
                    flag = eval("bool(%s)" % condition)
                finally:
                    pass

            if flag is True:
                show_color = color
            else:
                show_color = 'gray'
            left_pad_list.append([val, show_color, flag])

        data['left_pad_list'] = left_pad_list

        tmp_dict = dict()
        for val, _, flag in left_pad_list:
            tmp_dict[val] = flag

        color1 = {True: 'yellow', False: 'red'}
        color2 = {True: 'yellow', False: 'gray'}

        right_pad_list = list()

        flag = tmp_dict['清算差值大']
        right_pad_list.append(['清算差值比：', color1[flag]])
        right_pad_list.append(['  %.2f%%' % (self.data['liq_cost_rate']*100), color2[flag]])
        flag = tmp_dict['人力成本高']
        right_pad_list.append(['薪酬支出占比：', color1[flag]])
        right_pad_list.append(['  %.2f%%' % (self.data['salary_cost_rate']*100), color2[flag]])
        flag = tmp_dict['股权稀释']
        right_pad_list.append(['股权稀释率：', color1[flag]])
        right_pad_list.append(['  %.2f%%' % (self.data['dilution_rate']), color2[flag]])
        flag = tmp_dict['股权占比低']
        right_pad_list.append(['股权占比：', color1[flag]])
        right_pad_list.append(['  %.2f%%' % (self.data['equity_ratio']*100), color2[flag]])
        flag = tmp_dict['出口外汇风险']
        right_pad_list.append(['境外占比：', color1[flag]])
        right_pad_list.append(['  %s%%' % (self.data['gui_export']), color2[flag]])
        flag = tmp_dict['国有']
        right_pad_list.append(['企业性质：', color1[flag]])
        right_pad_list.append(['  %s' % (self.data['actual_controller']), color2[flag]])

        right_pad_list.extend(self.data['gui_tags_list'][1])
        data['right_pad_list'] = right_pad_list

    def update_counter(self, code):
        self.generate_sql_data_dict(code, self.data_pix.df)

        p = QPalette()
        p.setColor(QPalette.WindowText, self.data['name_color'])
        self.head_label1.setPalette(p)

    @try_decorator
    def show_stock_name(self):

        row = self.codes_df.df.iloc[self.code_index]
        total = self.codes_df.df.shape[0]

        code = row['code']
        name = row['name']

        self.generate_gui_data_dict(code)
        data = self.data

        # 标题
        txt1 = '%s: %s(%s/%s)' % (code, name, self.code_index + 1, total)

        # 左上
        txt2 = '行业: %s-%s-%s' % (row['level1'], row['level2'], row['level3'])

        if data['gui_mark'] is not None:
            txt2 = '-'.join([txt2, data['gui_mark']])
        txt2 = '-'.join([txt2, '%.2f' % data['predict_discount']])

        if data['discount_date'] is not None:
            txt2 = '%s(%s)' % (txt2, data['discount_date'])

        # 右上
        tmp_txt1 = '%s%%+%.1f' % (data['gui_rate'], data['dividend_return'])
        tmp_txt2 = '%.2f/%.2f/%.2f' % (data['ass_rate1'], data['ass_rate2'], data['ass_rate3'])
        txt3 = '/'.join([*data['gui_tags_list'][0], tmp_txt1, tmp_txt2])

        # 左下
        if data['gui_ass'] is not None:
            txt_bottom1 = '%.0f/%.0f%+.0f%+.0f[%+.1f%%]/[%+.1f%%]' % (
                data['market_value'] / 1e8,
                data['predict_ass'] / 1e8,
                data['liquidation_asset'] / 2e8,
                -data['equity'] / 2e8,
                data['ass_rate2_convert'],
                data['ass_rate1_convert'],
            )
        else:
            txt_bottom1 = 'cost: %.2f亿' % (data['real_cost'] / 1e8)

        # 右下
        counter = data['counter_data']
        txt_bottom2 = '%s次/%.2f%%[%s]' % (counter[2], counter[4] * 100, counter[0])
        txt_bottom2 = '%s/%.2f' % (txt_bottom2, data['yesterday_rise'] * 100)

        if data['listing_date'] is not None:
            txt_bottom2 = '/'.join([data['listing_date'], txt_bottom2])

        GuiLog.add_log('show stock --> ' + txt1)
        self.head_label1.setText(txt1)
        self.head_label2.setText(txt2)
        self.head_label3.setText(txt3)

        self.bottom_label1.setText(txt_bottom1)
        self.bottom_label2.setText(txt_bottom2)

        if code not in self.show_list:
            self.show_list.insert(0, code)
            self.show_list = self.show_list[:5]

        self.draw_left_pad()
        self.draw_right_pad()
        self.pad_l.setPixmap(self.pad_l_pix)
        self.pad_r.setPixmap(self.pad_r_pix)

    def draw_left_pad(self):
        pix = self.pad_l_pix
        pix.fill(QColor(40, 40, 40, 255))
        # pix.fill(QColor(40, 255, 40, 255))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 13))
        metrics = pix_painter.fontMetrics()

        blank = 4
        y = 20
        row_height = metrics.height() + blank * 2

        pen_dict = {
            'red': QPen(Qt.GlobalColor.red),
            'gray': QPen(Qt.GlobalColor.gray),
            'yellow': QPen(Qt.GlobalColor.yellow),
        }

        for val, color, _ in self.data['left_pad_list']:
            pen = pen_dict[color]
            pix_painter.setPen(pen)

            rect = QRect(10, y, 110, row_height)
            pix_painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, '%s' % val)

            y += row_height
        pix_painter.end()

    def draw_right_pad(self):
        pix = self.pad_r_pix
        pix.fill(QColor(40, 40, 40, 255))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 13))
        metrics = pix_painter.fontMetrics()

        blank = 4
        y = 20
        row_height = metrics.height() + blank * 2

        pen_dict = {
            'red': QPen(Qt.GlobalColor.red),
            'green': QPen(Qt.GlobalColor.green),
            'yellow': QPen(Qt.GlobalColor.yellow),
            'gray': QPen(Qt.GlobalColor.gray),
        }

        for val, color in self.data['right_pad_list']:
            pen = pen_dict[color]
            pix_painter.setPen(pen)

            rect = QRect(10, y, 110, row_height)
            pix_painter.drawText(rect, Qt.AlignmentFlag.AlignLeft, '%s' % val)

            y += row_height
        pix_painter.end()

    @staticmethod
    def init_code_list():
        # sort_hold()
        code_list = sift_codes(source='hold')
        # code_list = sift_codes(source='old')
        code_index = 0

        # if len(code_list) == 0:
        #     raise KeyboardInterrupt('len(code_list) == 0')

        path = '..\\basicData\\tmp\\code_list_latest.txt'
        write_json_txt(path, code_list)

        return code_list, code_index

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
        self.draw_flag = False
        self.draw_pos = None

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
        self.data_pix.draw_cross(x, y, self.cross, self.box, self.window_flag, self.draw_pos)
        self.label.setPixmap(self.data_pix.pix_show[self.window_flag])

    def mouseDoubleClickEvent(self, event):
        self.draw_flag = not self.draw_flag
        if self.draw_flag is True:
            pos = event.pos() - self.label.pos()
            self.set_draw_pos(pos.x(), pos.y())
        else:
            self.draw_pos = None

    def set_draw_pos(self, x, y):
        x, y, d0, _, _, _ = self.data_pix.get_d1_d2(x, y)
        self.draw_pos = (x, y, d0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # self.cross = not self.cross

            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())
            # GuiLog.write(self.log_path)
            self.label.setFocus()

            self.widgets_layer.pop(self.widgets_layer.index(self))
            self.widgets_layer.insert(0, self)
            self.activate_by_layer()
            # self.widgets_layer = [self]
            # self.close_all()
            # self.activate_by_layer()
        # elif event.button() == Qt.RightButton:
        #     self.close()

    def mouseMoveEvent(self, event):
        # if self.cross:
        pos = event.pos() - self.label.pos()
        self.draw_cross(pos.x(), pos.y())
        self.mouse_pos = [pos.x(), pos.y()]

    def wheelEvent(self, event):
        a = event.angleDelta().y() / 120
        if a < 0:
            new_index = (self.code_index + 1) % self.len_list
            self.change_stock(new_index)

        elif a > 0:
            new_index = (self.code_index - 1) % self.len_list
            self.change_stock(new_index)

    def editor1_changed(self, txt):
        code_list = self.codes_df.df['code'].tolist()
        if txt in code_list:
            new_index = code_list.index(txt)
            self.change_stock(new_index)
            self.editor1.setText('')
            self.label.setFocus()

    @staticmethod
    def compare_codes():
        pass
        # widget = ComparisonWidget()
        # widget.show()

    def show_plot(self):
        df = self.data_pix.df
        if df.columns.size == 0:
            return

        columns = ['id_041_mvs_mc', 's_043_turnover_volume_ttm']
        df = df[columns].copy()
        df = df.dropna(axis=0, how='all')

        show_plt(self.stock_code, df, *self.plt_rect)

    def relocate(self):

        if self.button12.isChecked():
            self.showMaximized()

            self.web_widget.resize(960, 1008)
            self.web_widget.move(-971, -10)

            self.equity_change_widget.resize(940, 1008)
            self.equity_change_widget.move(-1916, -10)

            # self.window2.move(-1906, 10)

            # self.fs_view.move(152-1920, 60)
            self.fs_view.resize(1600, 860)
            self.fs_view.move(159 - 1920, 88)

            if plt.fignum_exists(1):
                plt.figure(1, figsize=(16, 9), dpi=100)
                rect = [-1916, 32, 1600, 900]
                plt.get_current_fig_manager().window.setGeometry(*rect)

        else:
            self.showMaximized()

            self.web_widget.setGeometry(480, 120, 960, 860)
            self.equity_change_widget.setGeometry(460, 120, 1000, 860)
            self.fs_view.setGeometry(160, 120, 1600, 860)

            if plt.fignum_exists(1):
                plt.figure(1, figsize=(16, 9), dpi=100)
                rect = [10, 32, 1600, 900]
                plt.get_current_fig_manager().window.setGeometry(*rect)

        self.activate_by_layer()

    def activate_by_layer(self):
        layers = self.widgets_layer
        for widget in layers[::-1]:
            widget.activateWindow()

        for widget, button in self.widgets_button.items():
            if widget in layers:
                button.setChecked(True)
            else:
                button.setChecked(False)

    def get_show_func(self, widget):
        return lambda: self.show_sub_widget(widget)

    def show_sub_widget(self, widget):
        code = self.stock_code
        refresh_dict = {
            self.web_widget: [self.web_widget.load_code, code],
            self.equity_change_widget: [self.equity_change_widget.load_code, code],
            self.fs_view: [self.fs_view.load_df, code],
            self.style_widget: [self.style_widget.refresh_style, self.current_style],
            self.remark_widget: [self.remark_widget.download],
            self.check_widget: [self.check_widget.download],
            self.code_widget: [None]
        }

        arg = refresh_dict[widget].copy()
        func = arg.pop(0)

        if widget.isMinimized():
            widget.showNormal()
            widget.close()
        if widget.isHidden():
            self.widgets_layer.insert(0, widget)
            self.activate_by_layer()
            widget.show()
            if func is not None:
                func(*arg)
        else:
            # self.widgets_layer.pop(self.widgets_layer.index(widget))
            widget.close()

    def sub_widget_close(self, widget):
        if widget in self.widgets_layer:
            self.widgets_layer.pop(self.widgets_layer.index(widget))
        self.activate_by_layer()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_1:
            self.window_flag = 0
        elif e.key() == Qt.Key.Key_2:
            self.window_flag = 1
        elif e.key() == Qt.Key.Key_3:
            self.window_flag = 2
        elif e.key() == Qt.Key.Key_4:
            self.window_flag = 3
        elif e.key() == Qt.Key.Key_Space:
            self.cross = not self.cross
        elif e.key() == Qt.Key.Key_B:
            self.box = (self.box + 1) % 3
        elif e.key() == Qt.Key.Key_S:
            GuiLog.write(self.log_path)
            return
        elif e.key() == Qt.Key.Key_R:
            button = self.widgets_button[self.remark_widget]
            button.click()
            return
        elif e.key() == Qt.Key.Key_C:
            button = self.widgets_button[self.code_widget]
            button.click()
            return
        elif e.key() == Qt.Key.Key_W:
            button = self.widgets_button[self.web_widget]
            button.click()
            return
        elif e.key() == Qt.Key.Key_Down:
            new_index = (self.code_index + 1) % self.len_list
            self.change_stock(new_index)
            return
        elif e.key() == Qt.Key.Key_Up:
            new_index = (self.code_index - 1) % self.len_list
            self.change_stock(new_index)
            return
        else:
            return
        # self.update_window()

        x, y = self.mouse_pos
        self.data_pix.draw_cross(x, y, self.cross, self.box, self.window_flag, self.draw_pos)
        self.show_pix()

    def close_all(self):
        self.style_widget.close()
        self.code_widget.close()
        self.remark_widget.close()
        self.check_widget.close()
        self.web_widget.close()
        self.equity_change_widget.close()
        self.fs_view.close()
        plt.close()

    def closeEvent(self, event):
        self.close_all()

    @staticmethod
    def backup_data():
        MainLog.add_log('backup_data start...')
        today = dt.date.today()
        for file in os.listdir("..\\gui\\backup"):
            date = dt.datetime.strptime(file, "%Y%m%d%H%M%S").date()
            if (today - date).days > 7:
                shutil.rmtree("..\\gui\\backup\\%s" % file)
                # print(date)
                MainLog.add_log('remove file %s complete.' % file)

        dir1 = "..\\basicData\\self_selected"

        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        dir2 = "..\\gui\\backup\\%s" % timestamp
        if not os.path.exists(dir2):
            os.makedirs(dir2)
        copy_dir(dir1, dir2)
        MainLog.add_log('backup_data complete.')


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
