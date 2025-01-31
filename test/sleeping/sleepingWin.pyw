from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import datetime as dt


class AbnormalWin(QMainWindow):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.slot1)

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close)

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
        self.status = -1
        self.timer.start(1000)
        # self.close_timer.start(8*3600000)

    def paintEvent(self, event):
        print('painting...')
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix.width(), self.pix.height(), self.pix)

    def refresh_status0(self):
        if self.status != 0:
            pix_path = 'D:\\PycharmProjects\\stockAnalysis\\test\\sleeping\\测试112.png'
            self.pix = QPixmap(pix_path)
            self.resize(self.pix.size())
            self.move(0, 0)
            self.setMask(self.pix.mask())

            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.SubWindow
            )
            self.status = 0
            if not self.isHidden():
                self.hide()

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
            if self.isHidden():
                self.show()

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
            if self.isHidden():
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
            self.close_timer.start(7*3600*1000)
            self.status = 3
            if self.isHidden():
                self.show()

    def slot1(self):
        self.timer.stop()

        time0 = '22:30:00'
        time1 = '22:45:00'
        time2 = '23:00:00'
        time3 = '07:00:00'

        val = dt.datetime.now().strftime("%H:%M:%S")
        print(val)
        if self.is_in_duration(val, time0, time1):
            self.refresh_status1()
        elif self.is_in_duration(val, time1, time2):
            self.refresh_status2()
        elif self.is_in_duration(val, time2, time3):
            self.refresh_status3()
        else:
            self.refresh_status0()
        print(self.status)

        self.timer.start(1000)

    @staticmethod
    def is_in_duration(val, start, end):
        if start <= end:
            if start <= val < end:
                return True
            else:
                return False
        else:
            if start <= val or val < end:
                return True
            else:
                return False

    def closeEvent(self, event):
        self.timer.stop()
        self.close_timer.stop()
        super().closeEvent(event)
        QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = AbnormalWin()
    sys.exit(app.exec_())


