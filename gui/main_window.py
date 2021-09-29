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
    df1 = get_data_frame(cursor=cursor, table='bs_600008')

    df1 = df1.set_index('standardDate', drop=False)
    df1 = df1.loc[:, columns]
    df1 = df1.where(df1.notnull(), None)
    return df1


class DataPix:
    def __init__(self):
        # self.parent = parent

        self.df = sql2df(['id_115'])
        self.df.sort_index(inplace=True)

        self.value_y_max = 10
        self.value_y_min = 0

        self.date_max = dt.date(2022, 7, 20)
        self.date_min = dt.date(1996, 7, 20)

        d_width = 800
        d_height = 600
        side_blank = 50
        bottom_blank = 50

        self.main_rect = QRect(0, 0, d_width + 2 * side_blank, d_height + bottom_blank)
        self.data_rect = QRect(side_blank, 0, d_width, d_height)

        self.pix = QPixmap(self.main_rect.width(), self.main_rect.height())
        self.pix.fill(Qt.black)

        self.draw_struct()
        self.draw_pix()

    def get_px(self, df, start_date, end_date):
        date_width = (end_date - start_date).days + 1
        df_px = pd.DataFrame(columns=['x', 'y'], dtype=int)

        for tup in df.itertuples():
            time_str = tup[0]
            date = dt.datetime.strptime(time_str, "%Y-%m-%dT00:00:00+08:00").date()
            delta = (date - start_date).days + 1

            if tup[1]:
                x = self.data_rect.width() * delta / date_width - 1 + self.data_rect.x()
                y = self.data_rect.height() - 60 * np.log2(tup[1] / 1e8) + self.data_rect.y()
                df_px.loc[date] = [int(x), int(y)]
        return df_px

    def draw_pix(self):
        pix_painter = QPainter(self.pix)

        pen = QPen(Qt.red, 2, Qt.SolidLine)
        pix_painter.setPen(pen)

        df_px = self.get_px(
            df=self.df,
            start_date=self.date_min,
            end_date=self.date_max,
        )

        point1 = None
        point2 = None
        for tup in df_px.itertuples():

            point2 = QPoint(tup[1], tup[2])
            if point1:
                pix_painter.drawLine(point1, point2)
            point1 = point2

    def draw_struct(self):
        pix_painter = QPainter(self.pix)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawRect(
            self.main_rect.x(),
            self.main_rect.y(),
            self.main_rect.width()-1,
            self.main_rect.height()-1)
        # pix_painter.drawRect(QRect(0, 0, 999, 799))
        pix_painter.drawRect(
            self.data_rect.x()-1,
            self.data_rect.y(),
            self.data_rect.width()+1,
            self.data_rect.height())

        pen = QPen(Qt.red, 1, Qt.DotLine)
        pix_painter.setPen(pen)

        x1 = self.data_rect.x()
        x2 = self.data_rect.right()
        for y in range(60, 600, 60):
            point1 = QPoint(x1, y)
            point2 = QPoint(x2, y)
            pix_painter.drawLine(point1, point2)

    def px2value_x(self, x):
        px_max = self.data_rect.right()
        px_min = self.data_rect.left()
        val_max = (self.date_max - self.date_min).days
        val_min = 0

        val = (x - px_min) * (val_max - val_min) / (px_max - px_min) + val_min
        return val

    def px2value_y(self, y):
        px_max = 0
        px_min = self.data_rect.height()
        val_max = self.value_y_max
        val_min = self.value_y_min

        val = (y - px_max) * (val_max - val_min) / (px_max - px_min) + val_max
        return val


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
        pix_painter = QPainter(pix)

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        x_val = self.data_pix.px2value_x(x)
        date_tmp = self.data_pix.date_min + dt.timedelta(days=x_val)
        y_val = self.data_pix.px2value_y(y)
        print(date_tmp, x_val, y_val)

        self.pix_show = pix
        self.update()

    def paintEvent(self, e):
        self.label.setPixmap(self.pix_show)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cross:
                self.draw_cross(None, None)
                self.cross = False
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

