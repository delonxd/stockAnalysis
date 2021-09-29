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


def get_px(df, width, height, date_start, date_end):
    date_width = (date_end - date_start).days
    df_px = pd.DataFrame(columns=['x', 'y'], dtype=int)

    for tup in df.itertuples():
        time_str = tup[0]
        datetime = dt.datetime.strptime(time_str, "%Y-%m-%dT00:00:00+08:00")
        date = datetime.date()
        delta = (date - date_start).days

        if tup[1]:
            x = int(width * delta / date_width)
            y = int(height - 60 * np.log2(tup[1] / 1e8))
            df_px.loc[date] = [x,  y]
    return df_px


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('绘制图形')
        self.resize(800, 600)

        layout = QVBoxLayout()
        sp1 = QSplitter(Qt.Vertical)
        self.label = QLabel(self)
        # self.label = PixWidget()
        self.label.setFixedWidth(800)
        self.label.setFixedHeight(600)

        self.button = QPushButton('button')
        self.button.setObjectName('button')

        sp1.addWidget(self.label)
        # sp1.addStretch()
        sp1.addWidget(self.button)
        sp1.addWidget(QPushButton('button2'))

        layout.addWidget(sp1)
        self.setLayout(layout)

        self.df = sql2df(['id_115'])
        self.df.sort_index(inplace=True)

        self.pix = QPixmap(800, 600)
        self.pix.fill(Qt.black)

        self.draw_pix()

        self.pix_show = QPixmap(self.pix)

        self.cross = False
        self.setMouseTracking(True)
        self.label.setMouseTracking(True)
        sp1.setMouseTracking(True)
        sp1.setObjectName('sp1')

        self.button.clicked.connect(self.on_button_clicked)

        self.setObjectName('MainWindow')

        style = '''
        #MainWindow{
            background-color:black;
        }
        #sp1{
            background-color:black;
        }
        # #button{
        #     border-width:2px;
        #     border-color:red;
        #     border-style: solid;
        #     background-color: white;
        # }
        '''
        # # #边框     !!边框长度与label控件一致（如果要修改长度，只需要修改上方的setGeometry的第三个参数
        # # 设置边框样式
        # self.button.setFrameShape(QFrame.Box)
        # # 设置阴影 据说只有加了这步才能设置边框颜色。 可选样式有Raised、Sunken、Plain（这个无法设置颜色）等
        # self.button.setFrameShadow(QFrame.Raised)
        # # 设置背景颜色，包括边框颜色

        self.setStyleSheet(style)

    def draw_pix(self):
        pix_painter = QPainter(self.pix)

        # pix_painter.setPen(QColor(Qt.blue))
        # pix_painter.setFont(QFont('SimSun', 25))

        pen = QPen(Qt.red, 2, Qt.SolidLine)
        pix_painter.setPen(pen)

        df_px = get_px(
            df=self.df,
            date_start=dt.date(1996, 7, 20),
            date_end=dt.date(2022, 7, 20),
            width=800,
            height=600,
        )

        point1 = None
        point2 = None
        for tup in df_px.itertuples():

            point2 = QPoint(tup[1], tup[2])
            if point1:
                pix_painter.drawLine(point1, point2)
            point1 = point2

        pen = QPen(Qt.red, 1, Qt.DotLine)
        pix_painter.setPen(pen)

        for y in range(60, 600, 60):
            point1 = QPoint(0, y)
            point2 = QPoint(800, y)
            pix_painter.drawLine(point1, point2)

    def draw_cross(self, x, y):

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        pix = QPixmap(self.pix)
        pix_painter = QPainter(pix)

        # pix_painter.setPen(QColor(Qt.blue))
        # pix_painter.setFont(QFont('SimSun', 25))

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        point1 = QPoint(x, 0)
        point2 = QPoint(x, pix.height())
        pix_painter.drawLine(point1, point2)

        point1 = QPoint(0, y)
        point2 = QPoint(pix.width(), y)
        pix_painter.drawLine(point1, point2)
        self.pix_show = pix
        self.update()

    def paintEvent(self, e):
        self.label.setPixmap(self.pix_show)

    def on_button_clicked(self):
        self.cross = not self.cross

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.cross:
                self.draw_cross(0, 0)
                self.cross = False
            else:
                pos = event.pos() - self.label.pos()
                self.draw_cross(pos.x(), pos.y())
                self.cross = True

        if event.button() == Qt.RightButton:
            self.close()

    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.m_drag = False
    #         self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseMoveEvent(self, event):
        if self.cross:
            pos = event.pos() - self.label.pos()
            self.draw_cross(pos.x(), pos.y())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

