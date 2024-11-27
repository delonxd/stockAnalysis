from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import datetime as dt
import time


class BgThread(QThread):
    signal1 = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(1)
        self.signal1.emit()


class AbnormalWin(QWidget):
    def __init__(self):
        super().__init__()
        self.bg = BgThread()
        self.bg.signal1.connect(self.slot1)

        # self.label1 = QLabel(self)
        # p = QPalette()
        # p.setColor(QPalette.WindowText, Qt.GlobalColor.red)
        # self.label1.setFont(QFont('Consolas', 20))
        # self.label1.setPalette(p)
        # self.label1.setText('测试')
        #
        # m_layout = QHBoxLayout()
        # m_layout.addStretch(1)
        # m_layout.addWidget(self.label1, 0)
        # m_layout.addStretch(1)
        # self.setLayout(m_layout)

        self.pix = QPixmap()
        self.status = 0
        self.refresh_status1()

        self.bg.start()

    def paintEvent(self, event):
        print('painting...')
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)

        # painter = QPainter(self)
        # painter.drawPixmap(0, 0, self.pix.width(), self.pix.height(),
        #                    QPixmap('D:\\PycharmProjects\\stockAnalysis\\test\\sleeping\\welcome.jpg'))

    def refresh_status1(self):
        if self.status != 1:
            pix_path = 'D:\\PycharmProjects\\stockAnalysis\\test\\sleeping\\测试112.png'
            self.pix = QPixmap(pix_path)
            self.resize(self.pix.size())
            self.move(0, 0)
            self.setMask(self.pix.mask())

            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.SubWindow
            )
            self.status = 1

    def refresh_status2(self):
        if self.status != 2:
            pix_path = 'D:\\PycharmProjects\\stockAnalysis\\test\\sleeping\\测试112.png'
            self.pix = QPixmap(pix_path)
            self.resize(self.pix.size())
            self.move(0, 0)
            self.setMask(self.pix.mask())

            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.SubWindow
            )
            self.status = 2
            self.show()

    def refresh_status3(self):
        if self.status != 3:
            pix_path = 'D:\\PycharmProjects\\stockAnalysis\\test\\sleeping\\测试113.png'
            self.pix = QPixmap(pix_path)
            self.setFixedWidth(self.pix.width())
            self.setFixedHeight(self.pix.height())
            self.move(-1140, -660)
            self.setMask(self.pix.mask())

            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.SubWindow
            )
            self.status = 3
            self.show()

    def slot1(self):
        dt_now = dt.datetime.now()
        hour = dt_now.hour
        minute = dt_now.minute
        second = dt_now.second

        val = hour * 60 + minute
        print(dt_now)
        print(val)

        # if 420 < val < 1410:

        time1 = 420
        time2 = 1390
        time3 = 1410

        if time1 < val < time2:
            self.refresh_status1()
        elif time2 <= time3:
            self.refresh_status2()
        else:
            self.refresh_status3()

        self.bg.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = AbnormalWin()
    main.show()
    sys.exit(app.exec_())


