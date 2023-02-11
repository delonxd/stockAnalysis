from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys
import json


class CheckWidget(QWidget):
    def __init__(self, main_widget):
        super().__init__()

        self.setWindowTitle('检查事项')

        self.resize(600, 750)
        self.main_widget = main_widget

        self.label = QLabel('000000: 测试')
        self.editor1 = QTextEdit()
        self.button1 = QPushButton('上传')
        self.button2 = QPushButton('下载')

        self.label.setFont(QFont('Consolas', 18))
        self.editor1.setFont(QFont('Consolas', 14))

        self.code = None
        self.name = None

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.editor1)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.setLayout(layout)

        self.button1.clicked.connect(self.upload)
        self.button2.clicked.connect(self.download)

        path = "..\\basicData\\checkList3.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            self.txt_ini = f.read()
        self.editor1.setText(self.txt_ini)

    def upload(self):
        txt1 = self.editor1.toPlainText()

        path = "..\\basicData\\self_selected\\gui_check.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            remark_dict = json.loads(f.read())
        remark_dict[self.code] = (self.name, txt1)

        if txt1 == self.txt_ini:
            remark_dict.pop(self.code)

        res = json.dumps(remark_dict, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

        self.main_widget.show_stock_name()

    def download(self):
        self.code = code = self.main_widget.stock_code
        self.name = name = self.main_widget.stock_name
        txt1 = '%s: %s' % (code, name)

        path = "..\\basicData\\self_selected\\gui_check.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            remark_dict = json.loads(f.read())
        if code in remark_dict:
            _, txt2 = remark_dict[self.code]
        else:
            txt2 = self.txt_ini

        self.label.setText(txt1)
        self.editor1.setText(txt2)

        # print(self.textEdit.toHtml())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CheckWidget(1)
    main.show()
    sys.exit(app.exec_())
