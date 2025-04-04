from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import numpy as np
from method.mainMethod import predict_cap_return


class PrintWidget(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self, main_widget):
        super().__init__()

        self.setWindowTitle('信息显示')

        self.resize(420, 860)
        self.move(20, 90)
        self.main_widget = main_widget

        self.label = QLabel('000000: 测试')
        self.editor = QTextEdit()

        self.button1 = QPushButton('窗口置顶')
        self.is_top = False

        self.label.setFont(QFont('Consolas', 18))
        self.editor.setFont(QFont('Consolas', 15))

        self.code = None
        self.name = None

        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.button1)
        self.setLayout(layout)

        self.button1.clicked.connect(self.toggle_top)

        # self.editor.setText("<span style='color:green;'>%s</span>" % 'ww')

        txt = predict_cap_return(None)
        self.editor.setText(txt)
        self.toggle_top()
        self.editor.setReadOnly(True)

    def toggle_top(self):
        t1 = Qt.WindowType.WindowStaysOnTopHint
        if self.is_top:
            self.setWindowFlags(t1)
            self.setWindowFlags(self.windowFlags() & ~t1)
            self.button1.setText("窗口置顶")
        else:
            self.setWindowFlags(t1)
            self.setWindowFlags(self.windowFlags() | t1)
            self.button1.setText("取消置顶")

        self.is_top = not self.is_top
        self.show()

    def download(self):
        self.code = code = self.main_widget.stock_code
        self.name = name = self.main_widget.stock_name
        txt1 = '%s: %s' % (code, name)
        txt2 = self.main_widget.print_txt

        self.label.setText(txt1)
        self.editor.setText(txt2)

    def show_widget(self):
        self.download()
        self.show()

    def closeEvent(self, event):
        self.close_signal.emit(self)


def calculate_test():
    import re
    import json

    src = 'ps-(100)[5,20/5,15/inf,10];dv-(15)[5,20/5,15/inf,10]'
    src = 'ps-(100)[5,20/5,15/inf,10]'
    # str1, str2 = src.split(';')
    m1 = re.search(r"^ps-(.*)(\[.*\])$", src)
    print(m1.group(1))
    print(m1.group(2))

    src = "123 abc 4567 def"
    print(re.findall(r"[a-z]*", src))
    src = [(np.inf, 10), (1, 4)]
    res = json.dumps(src, ensure_ascii=False)

    # m2 = re.search(r'.*{', symbol[:end])

    print(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = PrintWidget(1)
    main.show()
    sys.exit(app.exec_())
    # calculate_test()
