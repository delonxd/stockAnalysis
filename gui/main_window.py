from method.mainMethod import *
from method.sqlMethod import *
import mysql.connector
import datetime as dt
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


def sql2df(columns):
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'bsdata',
    }
    db = mysql.connector.connect(**config)

    cursor = db.cursor()
    sql_df = get_data_frame(cursor=cursor, table='bs_600008')

    sql_df = sql_df.set_index('standardDate', drop=False)
    sql_df = sql_df.loc[:, columns]
    sql_df = sql_df.where(sql_df.notnull(), None)
    return sql_df


class DataPix:
    def __init__(self):
        # get df
        self.df = sql2df(['id_115'])
        self.df.sort_index(inplace=True)

        # date metrics
        self.date_max = dt.date(2022, 7, 20)
        self.date_min = dt.date(1996, 7, 20)
        self.d_date = (self.date_max - self.date_min).days

        years = list(range(self.date_min.year+1, self.date_max.year+1, 1))
        self.date_metrics = [dt.date(x, 1, 1) for x in years]

        self.y_value_metrics = list(range(1, 10))

        # data metrics
        self.data_max = (2 ** 10) * 1e8
        self.data_min = 1e8

        _, self.val_max = self.data2value(None, self.data_max)
        _, self.val_min = self.data2value(None, self.data_min)
        self.d_val = self.val_max - self.val_min

        # self.data_metrics = []

        # structure
        d_width = 800
        d_height = 600
        side_blank = 80
        bottom_blank = 50

        self.main_rect = QRect(0, 0, d_width + 2 * side_blank, d_height + bottom_blank)
        self.data_rect = QRect(side_blank, 0, d_width, d_height)

        # pix
        self.pix = QPixmap(self.main_rect.width(), self.main_rect.height())
        # self.pix.fill(Qt.black)
        self.pix.fill(Qt.white)
        # self.pix.fill(QColor(80, 80, 80))

        # draw
        self.draw_struct()
        self.draw_metrics()
        self.draw_data()

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

    def draw_metrics(self):
        self.draw_x_metrics()
        self.draw_y_metrics()

    def draw_x_metrics(self):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        pen2 = QPen(Qt.gray, 1, Qt.DotLine)

        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom() + 1

        for date in self.date_metrics:
            x, _ = self.data2px(date, None)
            txt = str(date.year)

            width = pix_painter.fontMetrics().width(txt) + 2
            height = pix_painter.fontMetrics().height() + 2
            rect = QRect(
                x - width / 2, self.data_rect.bottom() + 1,
                width, height)

            pix_painter.setPen(pen1)
            pix_painter.drawText(rect, Qt.AlignCenter, txt)

            pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))

        pix_painter.end()

    def draw_y_metrics(self):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        pen2 = QPen(Qt.red, 1, Qt.DotLine)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()
        
        for value in self.y_value_metrics:
            _, y = self.value2px(None, value)
            _, data = self.value2data(None, value)
            txt = '%i亿' % (data / 1e8)

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

    def draw_data(self):
        pix_painter = QPainter(self.pix)

        pen = QPen(Qt.red, 2, Qt.SolidLine)
        pix_painter.setPen(pen)

        point1 = None
        point2 = None
        for tup in self.df.itertuples():
            if tup[1]:
                date = dt.datetime.strptime(tup[0], "%Y-%m-%dT00:00:00+08:00").date()
                value = tup[1]
                x, y = self.data2px(date, value)
                point2 = QPoint(x, y)
                if point1:
                    pix_painter.drawLine(point1, point2)
                point1 = point2
        pix_painter.end()

    def data2value(self, date, value):
        x, y = None, None
        if date is not None:
            x = (date - self.date_min).days
        if value is not None:
            y = np.log2(value / 1e8)
        return x, y

    def value2data(self, x, y):
        date, value = None, None
        if x is not None:
            date = self.date_min + dt.timedelta(days=x)
        if y is not None:
            value = (2 ** y) * 1e8
        return date, value

    def value2px(self, val_x, val_y):
        x, y = None, None
        if val_x is not None:
            x = self.data_rect.x() + val_x * (self.data_rect.width()-1) / self.d_date
        if val_y is not None:
            y = (self.val_max - val_y) * self.data_rect.height() / self.d_val
        return x, y

    def px2value(self, px_x, px_y):
        x, y = None, None
        if px_x is not None:
            x = (px_x - self.data_rect.x()) * self.d_date / (self.data_rect.width() - 1)
        if px_y is not None:
            y = self.val_max - px_y * self.d_val / self.data_rect.height()
        return x, y

    def data2px(self, date, value):
        val_x, val_y = self.data2value(date, value)
        x, y = self.value2px(val_x, val_y)
        return x, y

    def px2data(self, px_x, px_y):
        val_x, val_y = self.px2value(px_x, px_y)
        date, value = self.value2data(val_x, val_y)
        return date, value


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('绘制图形')

        self.label = QLabel(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label, 0, Qt.AlignCenter)
        self.setLayout(layout)

        # self.df = sql2df(['id_115'])
        # self.df.sort_index(inplace=True)

        self.data_pix = DataPix()

        self.cross = False
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)

        self.painter = QPainter()
        self.metrics = self.painter.fontMetrics()

        self.pix_show = QPixmap(self.data_pix.pix)

    def draw_cross(self, x, y):
        if x is None and y is None:
            self.pix_show = QPixmap(self.data_pix.pix)
            self.update()
            return

        d_left = self.data_pix.data_rect.left()
        d_right = self.data_pix.data_rect.right()
        d_top = self.data_pix.data_rect.top()
        d_bottom = self.data_pix.data_rect.bottom()+1

        if x < d_left:
            x = d_left
        elif x > d_right:
            x = d_right
        if y < d_top:
            y = d_top
        elif y > d_bottom:
            y = d_bottom

        pix = QPixmap(self.data_pix.pix)
        self.painter.begin(pix)

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        self.painter.setPen(pen)

        self.painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        self.painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        self.painter.end()
        self.pix_show = pix

        date, val = self.data_pix.px2data(x, y)

        date_str = date.strftime("%Y-%m-%d")
        self.draw_tooltip(x, self.data_pix.data_rect.bottom() + 1, date_str)

        val_str = '%.2e' % val
        self.draw_tooltip(self.data_pix.data_rect.right() + 1, y, val_str)

        self.update()

    def draw_tooltip(self, x, y, text):
        self.painter.setFont(QFont('Consolas', 10))

        rect = QRect(x, y, self.metrics.width(text) + 2, self.metrics.height() + 2)

        self.painter.begin(self.pix_show)

        # draw_rect
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(Qt.blue)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        self.painter.setPen(pen)

        self.painter.setBrush(brush)
        self.painter.drawRect(rect)

        # draw_text
        self.painter.setPen(QColor(Qt.red))
        self.painter.drawText(rect, Qt.AlignCenter, text)

        self.painter.end()

    def paintEvent(self, e):
        self.label.setPixmap(self.pix_show)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

