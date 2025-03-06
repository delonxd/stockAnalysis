from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from method.fileMethod import *
from method.mainMethod import value2credit_rating, credit_rating2value
import sys


class RemarkWidget(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self, main_widget):
        super().__init__()

        self.setWindowTitle('备注')

        self.resize(600, 500)
        self.main_widget = main_widget

        self.label = QLabel('000000: 测试')
        self.label11 = QLabel('  复合增长率：')
        self.label12 = QLabel('%     估值：')
        self.label13 = QLabel('亿')
        self.label21 = QLabel('  业务了解度：')
        self.label22 = QLabel('境外占比：')
        self.label23 = QLabel('% ')
        self.label31 = QLabel('  盈利长期性：')
        self.label32 = QLabel('管理层信用：')
        self.label33 = QLabel('')

        self.editor0 = QLineEdit()
        self.editor1 = QLineEdit()
        self.editor2 = QTextEdit()
        self.editor3 = QLineEdit()
        self.editor4 = QLineEdit()
        self.editor5 = QLineEdit()
        self.editor6 = QLineEdit()
        self.editor7 = QLineEdit()
        self.button1 = QPushButton('上传备注')
        self.button2 = QPushButton('下载备注')

        self.label.setFont(QFont('Consolas', 18))
        self.label11.setFont(QFont('Consolas', 15))
        self.label12.setFont(QFont('Consolas', 15))
        self.label13.setFont(QFont('Consolas', 15))
        self.label21.setFont(QFont('Consolas', 15))
        self.label22.setFont(QFont('Consolas', 15))
        self.label23.setFont(QFont('Consolas', 15))
        self.label31.setFont(QFont('Consolas', 15))
        self.label32.setFont(QFont('Consolas', 15))
        self.label33.setFont(QFont('Consolas', 15))

        self.editor0.setFont(QFont('Consolas', 15))
        self.editor1.setFont(QFont('Consolas', 18))
        self.editor2.setFont(QFont('Consolas', 18))
        self.editor3.setFont(QFont('Consolas', 15))
        self.editor4.setFont(QFont('Consolas', 15))
        self.editor5.setFont(QFont('Consolas', 15))
        self.editor6.setFont(QFont('Consolas', 15))
        self.editor7.setFont(QFont('Consolas', 15))

        self.editor0.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editor3.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editor4.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editor5.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editor6.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.editor7.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label12.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label22.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label32.setAlignment(Qt.AlignmentFlag.AlignRight)

        validator = QIntValidator(self)
        validator.setRange(1, 1000000)
        self.editor0.setValidator(validator)

        validator = QIntValidator(self)
        validator.setRange(0, 200)
        self.editor3.setValidator(validator)

        validator = QIntValidator(self)
        validator.setRange(0, 100)
        self.editor4.setValidator(validator)

        self.code = None
        self.name = None

        layout = QVBoxLayout()

        layout1 = QGridLayout()
        layout1.addWidget(self.label11, 0, 0)
        layout1.addWidget(self.editor3, 0, 1)
        layout1.addWidget(self.label12, 0, 2)
        layout1.addWidget(self.editor0, 0, 3)
        layout1.addWidget(self.label13, 0, 4)
        layout1.addWidget(self.label21, 1, 0)
        layout1.addWidget(self.editor5, 1, 1)
        layout1.addWidget(self.label22, 1, 2)
        layout1.addWidget(self.editor4, 1, 3)
        layout1.addWidget(self.label23, 1, 4)
        layout1.addWidget(self.label31, 2, 0)
        layout1.addWidget(self.editor6, 2, 1)
        layout1.addWidget(self.label32, 2, 2)
        layout1.addWidget(self.editor7, 2, 3)
        layout1.addWidget(self.label33, 2, 4)

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
        self.write_content(self.editor1.text(), "gui_tags.txt")
        self.write_content(self.editor2.toPlainText(), "gui_remark.txt")
        self.write_content(self.editor0.text(), "gui_assessment.txt")
        self.write_content(self.editor3.text(), "gui_rate.txt")
        self.write_content(self.editor4.text(), "gui_export.txt")

        val1 = self.editor5.text()
        val2 = self.editor6.text()
        val3 = self.editor7.text()
        val = list(map(lambda x: credit_rating2value(x), [val1, val2, val3]))
        self.write_content(val, "gui_ud.txt", non=[None, None, None])

        self.main_widget.show_stock_name()

    def load_tags(self):
        code = self.main_widget.stock_code
        path = "../basicData/self_selected/gui_tags.txt"
        res = load_json_txt(path, log=False)
        txt = res[code] if code in res else ''
        self.editor1.setText(txt)

    def write_content(self, val, file, non: object = ''):
        path = "../basicData/self_selected/%s" % file
        code = self.code
        res = load_json_txt(path, log=False)
        res[code] = val
        if val == non:
            res.pop(code)
        write_json_txt(path, res, log=False)

    def download(self):
        self.code = code = self.main_widget.stock_code
        self.name = name = self.main_widget.stock_name
        txt1 = '%s: %s' % (code, name)

        path = "../basicData/self_selected/gui_remark.txt"
        res = load_json_txt(path, log=False)
        txt3 = res[code] if code in res else ''

        path = "../basicData/self_selected/gui_tags.txt"
        res = load_json_txt(path, log=False)
        txt2 = res[code] if code in res else ''

        path = "../basicData/self_selected/gui_ud.txt"
        res = load_json_txt(path, log=False)

        value3 = res.get(code)
        value3 = [None] * 3 if value3 is None else value3
        value3 = list(map(lambda x: value2credit_rating(x), value3))

        path = "../basicData/self_selected/gui_assessment.txt"
        res = load_json_txt(path, log=False)
        value = str(res[code]) if code in res else ''

        path = "../basicData/self_selected/gui_rate.txt"
        res = load_json_txt(path, log=False)
        value1 = str(res[code]) if code in res else ''

        path = "../basicData/self_selected/gui_export.txt"
        res = load_json_txt(path, log=False)
        value2 = str(res[code]) if code in res else ''

        self.label.setText(txt1)
        self.editor1.setText(txt2)
        self.editor2.setText(txt3)
        self.editor0.setText(value)
        self.editor3.setText(value1)
        self.editor4.setText(value2)
        self.editor5.setText(value3[0])
        self.editor6.setText(value3[1])
        self.editor7.setText(value3[2])

        # print(self.textEdit.toHtml())

    def closeEvent(self, event):
        self.close_signal.emit(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = RemarkWidget(1)
    main.show()
    sys.exit(app.exec_())
