import pandas as pd

from method.mainMethod import *
from method.sqlMethod import *
from method.dataMethod import data_by_dates, sql2df
import mysql.connector
import datetime as dt
import numpy as np

from dateutil.rrule import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class DataSource:
    def __init__(
            self,
            df,
            name=None,
            units='None',
            color=Qt.red,
            line_thick=2,
            pen_type=Qt.SolidLine,
            scale_min=2e8,
            scale_max=2048*1e8,
            scale_div=10,
            logarithmic=True,
    ):
        self.df = df
        if name is None:
            self.name = df.columns.tolist()[0]
        else:
            self.name = name

        self.units = units

        self.color = color
        self.line_thick = line_thick
        self.pen_type = pen_type

        self.scale_min = scale_min
        self.scale_max = scale_max

        self.scale_div = scale_div
        self.logarithmic = logarithmic

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        self.format_fun = lambda x: '%i亿' % (x / 1e8)

        self.set_val_scale()

    def format(self, value):
        if value is None:
            return 'None'
        else:
            try:
                return self.format_fun(value)
            except Exception as e:
                return e

    def set_val_scale(self):
        if self.logarithmic is True:
            self.val_max = 1
            self.val_min = 0
        else:
            self.val_max = self.scale_max
            self.val_min = self.scale_min

        self.val_delta = self.val_max - self.val_min
        self.metrics = list(np.linspace(self.val_min, self.val_max, self.scale_div+1))
        self.metrics = self.metrics[1:-1]

    @staticmethod
    def copy(data):
        res = DataSource(data.name, data.df)

        res.name = data.name
        res.df = data.df

        res.units = data.units

        res.color = data.color
        res.line_thick = data.line_thick
        res.pen_type = data.pen_type

        res.scale_min = data.scale_min
        res.scale_max = data.scale_max

        res.scale_div = data.scale_div
        res.logarithmic = data.logarithmic

        res.val_max = data.val_max
        res.val_min = data.val_min
        res.val_delta = data.val_delta
        res.metrics = data.metrics

        res.format_fun = data.format_fun

        return res


class InformationBox:
    def __init__(self):
        self.date = None
        self.info = pd.DataFrame(columns=['name', 'value', 'data_source'])
        self.font = None
        self.background = None

    def add_info(self, value, data: DataSource):
        self.info.loc[data.name] = [data.name, value, data]

    def load_data_sources(self, data_dict: dict):
        for ds in data_dict.values():
            self.add_info(0, ds)

    def load_value(self, date):
        date_index = date.strftime("%Y-%m-%d")
        for _, row in self.info.iterrows():
            pass
        info = self.info
        for i in range(0, len(info)):
            ds = info.iloc[i]['data_source']
            index_list = ds.df.index.tolist()

            if date_index in index_list:
                info.iloc[i]['value'] = ds.df.loc[date_index][0]
            else:
                info.iloc[i]['value'] = None
        self.date = date

    def read_values(self):
        res = list()
        txt = self.date.strftime("%Y-%m-%d")
        res.append(('日期: %s' % txt, QPen(Qt.white, 1, Qt.SolidLine)))
        for _, row in self.info.iterrows():
            name, value, ds = row['name'], row['value'], row['data_source']
            txt = ds.format(value)

            row_txt = '%s: %s' % (name, txt)
            pen = QPen(ds.color, ds.line_thick, ds.pen_type)
            res.append((row_txt, pen))
        return res

    def draw_pix(self):
        text_list = self.read_values()

        pix = QPixmap(400, 400)
        pix.fill(QColor(0, 0, 0, 30))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 10))

        metrics = pix_painter.fontMetrics()

        x = y = blank = 1
        max_width = 0
        row_height = metrics.height() + blank * 2

        for row_txt, pen in text_list:
            pix_painter.setPen(pen)

            width = metrics.width(row_txt)
            rect = QRect(x, y, width, row_height)
            pix_painter.drawText(rect, Qt.AlignCenter, row_txt)

            if width > max_width:
                max_width = width
            y += row_height
        pix_painter.end()

        max_width += blank * 2
        max_height = y + blank

        res = pix.copy(0, 0, max_width, max_height)
        return res


class DataPix:
    def __init__(self, m_width, m_height):
        self.data_dict = get_data_source()
        self.default_ds = self.data_dict['所有者权益']

        # date metrics
        self.date_max = dt.date(2022, 7, 20)
        self.date_min = dt.date(1996, 7, 20)
        self.d_date = (self.date_max - self.date_min).days

        self.date_metrics1 = self.get_date_list('INTERIM')
        self.date_metrics2 = self.get_date_list('YEARLY')

        # structure
        self.m_width = m_width
        self.m_height = m_height

        self.d_width = d_width = 800
        self.d_height = d_height = 600

        left_blank = 130
        right_blank = 80
        bottom_blank = 50

        self.main_rect = QRect(0, 0, m_width, m_height)
        self.data_rect = QRect(left_blank, 0, d_width, d_height)

        # px_list
        self.date_list = self.get_date_list('MONTHLY')
        self.px_list, self.px_dict = self.get_px_list()
        # print(len(self.date_list))

        self.format_data_source()

        # pix
        self.pix = QPixmap(self.main_rect.width(), self.main_rect.height())
        self.pix.fill(Qt.black)
        # self.pix.fill(Qt.white)
        # self.pix.fill(QColor(80, 80, 80))
        self.pix_show = QPixmap()
        self.draw_pix()

        # '2012-09-30T00:00:00+08:00'

    def format_data_source(self):
        for ds in self.data_dict.values():
            ds.df = data_by_dates(ds.df, self.date_list)

    def draw_pix(self):
        self.draw_struct()
        self.draw_metrics(self.default_ds)
        self.draw_data_dict()
        self.pix_show = self.pix

    def get_date_list(self, mode):
        res = None
        if mode == 'WEEKLY':
            res = list(rrule(WEEKLY, wkst=SU, byweekday=FR, dtstart=self.date_min, until=self.date_max))
        elif mode == 'MONTHLY':
            res = list(rrule(MONTHLY, bymonthday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'YEARLY':
            res = list(rrule(YEARLY, byyearday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'INTERIM':
            res = list(rrule(YEARLY, bymonthday=-1, bymonth=6, dtstart=self.date_min, until=self.date_max))
        return res

    def get_px_list(self):
        px_dict = dict()
        for datetime in self.date_list:
            date = datetime.date()
            px, _ = self.data2px(date, None, self.default_ds)
            px_dict[px] = date
        px_list = list(px_dict.keys())
        px_list.sort()

        return px_list, px_dict

    def get_nearest_px(self, x):
        nearest = None

        if len(self.px_list) > 0:
            if x <= self.px_list[0]:
                return self.px_list[0]
            elif x >= self.px_list[-1]:
                return self.px_list[-1]

        px1 = np.inf
        for px in self.px_list:
            px2 = px
            if px1 <= x < px2:
                if (x-px1) <= (px2-x):
                    nearest = px1
                else:
                    nearest = px2
                break
            px1 = px
        return nearest

    def get_nearest_date(self, x):
        px = self.get_nearest_px(x)
        if px is not None:
            return self.px_dict[px]
        else:
            return None

    def draw_struct(self):
        pix_painter = QPainter(self.pix)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawRect(
            self.main_rect.x(),
            self.main_rect.y(),
            self.main_rect.width()-1,
            self.main_rect.height()-1)

        pix_painter.drawRect(
            self.data_rect.x()-1,
            self.data_rect.y(),
            self.data_rect.width()+1,
            self.data_rect.height())

        pix_painter.end()

    def draw_metrics(self, data: DataSource):
        self.draw_x_metrics(data)
        self.draw_y_metrics(data)

    def draw_x_metrics(self, data: DataSource):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        pen2 = QPen(Qt.gray, 1, Qt.DotLine)

        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom() + 1

        for datetime in self.date_metrics1:
            x, _ = self.data2px(datetime.date(), None, data)
            txt = str(datetime.year)

            width = pix_painter.fontMetrics().width(txt) + 2
            height = pix_painter.fontMetrics().height() + 2
            rect = QRect(
                x - width / 2, self.data_rect.bottom() + 1,
                width, height)

            pix_painter.setPen(pen1)
            pix_painter.drawText(rect, Qt.AlignCenter, txt)

        for datetime in self.date_metrics2:
            x, _ = self.data2px(datetime.date(), None, data)

            pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))

        pix_painter.end()

    def draw_y_metrics(self, data: DataSource):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        pen2 = QPen(Qt.red, 1, Qt.DotLine)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()
        
        for val_y in data.metrics:
            _, y = self.value2px(None, val_y, data)
            _, val_src = self.value2data(None, val_y, data)
            txt = data.format(val_src)

            width = pix_painter.fontMetrics().width(txt) + 2
            height = pix_painter.fontMetrics().height() + 2
            rect = QRect(
                self.data_rect.right() + 1, y - height / 2,
                width, height)

            pix_painter.setPen(pen1)
            pix_painter.drawText(rect, Qt.AlignCenter, txt)

            pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        pix_painter.end()

    def draw_data_dict(self):
        for data in self.data_dict.values():
            self.draw_data(data)

    def draw_data(self, data: DataSource):
        pix_painter = QPainter(self.pix)

        pen = QPen(data.color, data.line_thick, data.pen_type)
        pix_painter.setPen(pen)

        point1 = None
        for tup in data.df.itertuples():
            if tup[1]:
                date = dt.datetime.strptime(tup[0], "%Y-%m-%d").date()
                value = tup[1]
                x, y = self.data2px(date, value, data)
                point2 = QPoint(x, y)
                if point1:
                    pix_painter.drawLine(point1, point2)
                point1 = point2
        pix_painter.end()

    def data2value(self, date, value, data: DataSource):
        x, y = None, None
        if date is not None:
            x = (date - self.date_min).days
        if value is not None:
            if data.logarithmic is True:
                y = np.log2(value / data.scale_min) / np.log2(data.scale_max / data.scale_min)
            else:
                y = value
        return x, y

    def value2data(self, x, y, data: DataSource):
        date, value = None, None
        if x is not None:
            date = self.date_min + dt.timedelta(days=x)
        if y is not None:
            if data.logarithmic is True:
                value = 2 ** (y * np.log2(data.scale_max / data.scale_min)) * data.scale_min
            else:
                value = y
        return date, value

    def value2px(self, val_x, val_y, data: DataSource):
        x, y = None, None
        if val_x is not None:
            x = self.data_rect.x() + val_x * (self.data_rect.width()-1) / self.d_date
        if val_y is not None:
            y = (data.val_max - val_y) * self.data_rect.height() / data.val_delta
        return x, y

    def px2value(self, px_x, px_y, data: DataSource):
        x, y = None, None
        if px_x is not None:
            x = (px_x - self.data_rect.x()) * self.d_date / (self.data_rect.width() - 1)
        if px_y is not None:
            y = data.val_max - px_y * data.val_delta / self.data_rect.height()
        return x, y

    def data2px(self, date, value, data):
        val_x, val_y = self.data2value(date, value, data)
        x, y = self.value2px(val_x, val_y, data)
        return x, y

    def px2data(self, px_x, px_y, data):
        val_x, val_y = self.px2value(px_x, px_y, data)
        date, value = self.value2data(val_x, val_y, data)
        return date, value

    def draw_cross(self, x, y):

        self.pix_show = QPixmap(self.pix)

        if x is None and y is None:
            return

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()
        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom()+1

        if x < d_left:
            x = d_left
        elif x > d_right:
            x = d_right
        if y < d_top:
            y = d_top
        elif y > d_bottom:
            y = d_bottom

        pix_painter = QPainter(self.pix_show)

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        x = self.get_nearest_px(x)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        pix_painter.end()

        date, val = self.px2data(x, y, self.default_ds)
        date_str = date.strftime("%Y-%m-%d")
        val_str = self.default_ds.format(val)

        self.draw_tooltip(x, self.data_rect.bottom() + 1, date_str)
        self.draw_tooltip(self.data_rect.right() + 1, y, val_str)
        self.draw_information(date)

    def draw_tooltip(self, x, y, text):
        pix_painter = QPainter(self.pix_show)
        pix_painter.setFont(QFont('Consolas', 10))

        metrics = pix_painter.fontMetrics()
        rect = QRect(x, y, metrics.width(text) + 2, metrics.height() + 2)

        # draw_rect
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(Qt.blue)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.setBrush(brush)
        pix_painter.drawRect(rect)

        # draw_text
        pix_painter.setPen(QColor(Qt.red))
        pix_painter.drawText(rect, Qt.AlignCenter, text)

        pix_painter.end()

    def draw_information(self, date):
        box = InformationBox()
        box.load_data_sources(self.data_dict)
        # print(type(date), '-->', date)
        box.load_value(date)
        pix = box.draw_pix()
        # pix = QPixmap(200, 200)
        # pix.fill(Qt.black)

        pix_painter = QPainter(self.pix_show)
        pix_painter.drawPixmap(10, 10, pix)
        pix_painter.end()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('绘制图形')

        self.resize(1600, 800)
        self.label = QLabel(self)
        self.label_right = QLabel(self)
        pix = QPixmap(200, 800)
        pix.fill(Qt.white)
        self.label_right.setPixmap(pix)

        self.label_left = QLabel(self)
        pix = QPixmap(200, 800)
        pix.fill(Qt.white)
        self.label_left.setPixmap(pix)

        layout = QHBoxLayout()
        layout.addWidget(self.label_left, 0, Qt.AlignCenter)
        layout.addWidget(self.label, 0, Qt.AlignCenter)
        layout.addWidget(self.label_right, 0, Qt.AlignCenter)
        self.setLayout(layout)

        self.data_pix = DataPix(1000, 800)

        self.cross = False
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)

        self.update()

        self.center()

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


def get_data_source():
    df = sql2df()
    res = dict()

    sss = df.loc[:, 'id_115']

    ds = DataSource(
        df.loc[:, ['id_115']],
        name='所有者权益',
        color=Qt.yellow
    )
    res[ds.name] = ds

    ds = DataSource(
        df.loc[:, ['id_6']],
        name='资产合计',
        color=Qt.white
    )
    res[ds.name] = ds

    ds = DataSource(
        df.loc[:, ['id_67']],
        name='负债合计',
        color=Qt.red
    )
    res[ds.name] = ds

    return res


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

    # a = [1, 2, 3, 4]
    # it = iter(a)
    #
    # for _ in range(8):
    #     try:
    #         v = it.__next__()
    #     except StopIteration:
    #         v = 'None'
    #
    #     print(v)
