from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import json


class RemarkWidget(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self, main_widget):
        super().__init__()

        self.setWindowTitle('备注')

        self.resize(600, 500)
        self.main_widget = main_widget

        self.label = QLabel('000000: 测试')
        self.label1 = QLabel('  复合增长率：')
        self.label2 = QLabel('%     估值：')
        self.label3 = QLabel('亿')

        self.editor0 = QLineEdit()
        self.editor1 = QLineEdit()
        self.editor2 = QTextEdit()
        self.editor3 = QLineEdit()
        self.button1 = QPushButton('上传备注')
        self.button2 = QPushButton('下载备注')

        self.label.setFont(QFont('Consolas', 18))
        self.label1.setFont(QFont('Consolas', 15))
        self.label2.setFont(QFont('Consolas', 15))
        self.label3.setFont(QFont('Consolas', 15))

        self.editor0.setFont(QFont('Consolas', 15))
        self.editor1.setFont(QFont('Consolas', 18))
        self.editor2.setFont(QFont('Consolas', 18))
        self.editor3.setFont(QFont('Consolas', 15))

        self.editor0.setAlignment(Qt.AlignRight)
        self.editor3.setAlignment(Qt.AlignRight)

        validator = QIntValidator(self)
        validator.setRange(1, 1000000)
        self.editor0.setValidator(validator)

        validator = QIntValidator(self)
        validator.setRange(0, 200)
        self.editor3.setValidator(validator)

        self.code = None
        self.name = None

        layout = QVBoxLayout()

        layout1 = QHBoxLayout()
        layout1.addStretch(0)
        layout1.addWidget(self.label1)
        layout1.addWidget(self.editor3, 1)
        layout1.addWidget(self.label2)
        layout1.addWidget(self.editor0, 1)
        layout1.addWidget(self.label3)
        layout1.addStretch(0)

        layout.addWidget(self.label)
        layout.addLayout(layout1)
        layout.addWidget(self.editor1)
        layout.addWidget(self.editor2)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        self.setLayout(layout)

        self.button1.clicked.connect(self.upload)
        self.button2.clicked.connect(self.download)

    def upload(self):
        txt1 = self.editor1.text()
        txt2 = self.editor2.toPlainText()

        path = "../basicData/self_selected/gui_remark.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            remark_dict = json.loads(f.read())
        remark_dict[self.code] = (self.name, txt1, txt2)

        res = json.dumps(remark_dict, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

        value = self.editor0.text()
        path = "../basicData/self_selected/gui_assessment.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
        value_dict[self.code] = value
        if value == '':
            value_dict.pop(self.code)

        res = json.dumps(value_dict, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

        value = self.editor3.text()
        path = "../basicData/self_selected/gui_rate.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
        value_dict[self.code] = value
        if value == '':
            value_dict.pop(self.code)

        res = json.dumps(value_dict, indent=4, ensure_ascii=False)
        with open(path, "w", encoding='utf-8') as f:
            f.write(res)

        self.main_widget.show_stock_name()

    def download(self):
        self.code = code = self.main_widget.stock_code
        self.name = name = self.main_widget.stock_name
        txt1 = '%s: %s' % (code, name)

        path = "../basicData/self_selected/gui_remark.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            remark_dict = json.loads(f.read())
        if code in remark_dict:
            _, txt2, txt3 = remark_dict[self.code]
        else:
            txt2, txt3 = '', ''

        path = "../basicData/self_selected/gui_assessment.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
        if code in value_dict:
            value = str(value_dict[self.code])
        else:
            value = ''

        path = "../basicData/self_selected/gui_rate.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            value_dict = json.loads(f.read())
        if code in value_dict:
            value1 = str(value_dict[self.code])
        else:
            value1 = ''

        self.label.setText(txt1)
        self.editor1.setText(txt2)
        self.editor2.setText(txt3)
        self.editor0.setText(value)
        self.editor3.setText(value1)

        # print(self.textEdit.toHtml())

    def closeEvent(self, event):
        self.close_signal.emit(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = RemarkWidget(1)
    main.show()
    sys.exit(app.exec_())
