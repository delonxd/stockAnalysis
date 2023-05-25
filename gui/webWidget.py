from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
import sys


class WebWidget(QMainWindow):
    close_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('WebWidget ')
        self.resize(960, 500)

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.code = None

    def load_code(self, code):
        if self.isHidden():
            return
        if code == self.code:
            return
        self.code = code
        url = 'http://basic.10jqka.com.cn/%s/operate.html###' % code
        self.browser.load(QUrl(url))

    # def load_url(self, url):
    #     # self.browser.load(QUrl(url))
    #
    #     # import os
    #     # path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    #     # os.system(path, url)
    #     import webbrowser
    #     webbrowser.open(url)

    def closeEvent(self, event):
        self.close_signal.emit(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = WebWidget()
    # main.load_code('600004')
    main.load_url('http://stockpage.10jqka.com.cn/600000/')
    main.show()

    sys.exit(app.exec_())
