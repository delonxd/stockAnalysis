from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.fileMethod import *

import sys
import json


class CheckWidget(QWidget):
    close_signal = pyqtSignal(object)

    def __init__(self, main_widget=None, code=None):
        super().__init__()

        self.setWindowTitle('检查事项')

        self.resize(600, 850)
        self.main_widget = main_widget
        self._code = code

        self.label = QLabel('000000: 测试')
        self.button1 = QPushButton('上传')
        self.button2 = QPushButton('下载')

        self.button3 = QPushButton('添加')
        self.button4 = QPushButton('删除')
        self.button5 = QPushButton('选择')

        self.label.setFont(QFont('Consolas', 18))

        layout = QVBoxLayout()
        self.tab = QTabWidget()
        self.tab.setMovable(True)
        self.tab.setFont(QFont('Consolas', 14))

        layout1 = QHBoxLayout()
        layout1.addStretch(0)
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)
        layout1.addWidget(self.button3)
        layout1.addWidget(self.button4)
        layout1.addWidget(self.button5)
        layout1.addStretch(0)

        layout.addWidget(self.label)
        layout.addWidget(self.tab)
        layout.addLayout(layout1)
        self.setLayout(layout)

        self.button1.clicked.connect(self.upload)
        self.button2.clicked.connect(self.download)
        self.button3.clicked.connect(self.tab_add)
        self.button4.clicked.connect(self.tab_del)
        self.button5.clicked.connect(self.select)
        self.tab.tabBarDoubleClicked.connect(self.tab_double_clicked)

        path = "..\\basicData\\checkList3.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            self.txt_ini = str(f.read())

        self.tab_ini = 'New'

        self.download()

    @property
    def code(self):
        if self.main_widget is None:
            ret = self._code
        else:
            ret = self.main_widget.stock_code
        return ret

    @property
    def code_name(self):
        if self.main_widget is None:
            code = self._code
            name_dict = load_json_txt('..\\basicData\\code_names_dict.txt', log=False)
            ret = name_dict.get(code)
        else:
            ret = self.main_widget.stock_name
        return ret

    def upload(self):

        code = self.code
        res = self.read_tab()

        path = "..\\basicData\\self_selected\\gui_check.txt"
        remark_dict = load_json_txt(path, log=False)
        remark_dict[code] = res

        if len(res) == 0:
            remark_dict.pop(code)

        write_json_txt(path, remark_dict, log=False)

        if self.main_widget is not None:
            self.main_widget.show_stock_name()

    def download(self):
        code = self.code
        name = self.code_name
        txt1 = '%s: %s' % (code, name)

        path = "..\\basicData\\self_selected\\gui_check.txt"
        remark_dict = load_json_txt(path, log=False)

        if code in remark_dict:
            res = remark_dict[code]
        else:
            res = dict()

        self.label.setText(txt1)
        self.show_tab(res)

    def show_tab(self, src):
        self.tab.clear()

        if len(src) == 0:
            src[self.tab_ini] = self.txt_ini

        for key, value in src.items():
            txt = self.txt_ini if value is None else value
            editor = QTextEdit()
            editor.setText(txt)
            editor.setFont(QFont('Consolas', 14))
            self.tab.addTab(editor, key)

    def read_tab(self):
        res = dict()
        for index in range(self.tab.count()):
            key = self.tab.tabText(index)
            editor = self.tab.widget(index)
            txt = editor.toPlainText()

            value = None if txt == self.txt_ini else txt
            if key == self.tab_ini and value is None:
                continue
            else:
                res[key] = value
        return res

    def get_tab_text(self):
        ret = []
        for index in range(self.tab.count()):
            ret.append(self.tab.tabText(index))
        return ret

    def tab_double_clicked(self, index):
        ini = self.tab.tabText(index)
        txt, _ = QInputDialog.getText(self, '业务', '请输入:', text=ini)
        if txt == '':
            return
        self.tab.setTabText(index, txt)

    def tab_add(self):
        txt, _ = QInputDialog.getText(self, '业务', '请输入:')
        if txt == '':
            return
        if txt in self.get_tab_text():
            return
        editor = QTextEdit()
        editor.setText(self.txt_ini)
        editor.setFont(QFont('Consolas', 14))
        self.tab.addTab(editor, txt)

    def tab_del(self):
        txt, _ = QInputDialog.getText(self, '业务', '请输入:')
        tab_list = self.get_tab_text()
        if txt not in tab_list:
            return
        self.tab.removeTab(tab_list.index(txt))

    def select(self):
        if self.main_widget is None:
            txt, _ = QInputDialog.getText(self, '选择', '请输入:')

            name_dict = load_json_txt('..\\basicData\\code_names_dict.txt', log=False)

            if txt in name_dict.keys():
                self._code = txt

            if txt in name_dict.values():
                for key, value in name_dict.items():
                    if value == txt:
                        self._code = key

            if self._code is not None:
                self.download()

    def closeEvent(self, event):
        self.close_signal.emit(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CheckWidget(code='600438')
    main.show()
    sys.exit(app.exec_())
