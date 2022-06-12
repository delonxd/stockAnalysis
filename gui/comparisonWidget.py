from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.fileMethod import *
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class ComparisonWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.pix_label = QLabel()

        self.dateTimeEdit1 = QDateTimeEdit(QDate.currentDate())
        self.dateTimeEdit2 = QDateTimeEdit(QDate.currentDate())

        self.button1 = QPushButton('加载列表')
        self.button2 = QPushButton('加载列表')
        self.compare_button = QPushButton('比较')

        self.editor1 = QLineEdit()
        self.editor2 = QLineEdit()

        self.range1 = QLineEdit()
        self.range2 = QLineEdit()

        self.precision_edit = QLineEdit()

        self.cache = dict()
        self.data = pd.DataFrame()

        self.init_gui()
        self.init_data()

        self.show()

    def init_gui(self):
        self.setWindowTitle('ComparisonWidget')
        self.resize(500, 200)
        self.move(20, 20)

        self.editor1.setEnabled(False)
        self.editor2.setEnabled(False)

        self.range1.setFixedWidth(60)
        self.range2.setFixedWidth(60)

        self.dateTimeEdit1.setCalendarPopup(True)
        self.dateTimeEdit2.setCalendarPopup(True)

        self.dateTimeEdit1.setDisplayFormat('yyyy-MM-dd')
        self.dateTimeEdit2.setDisplayFormat('yyyy-MM-dd')

        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel('数据1:'))
        layout1.addWidget(self.editor1)
        layout1.addWidget(self.range1)
        layout1.addWidget(self.button1)

        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel('数据2:'))
        layout2.addWidget(self.editor2)
        layout2.addWidget(self.range2)
        layout2.addWidget(self.button2)

        layout3 = QHBoxLayout()
        layout3.addWidget(QLabel('起始日期:'))
        layout3.addWidget(self.dateTimeEdit1)
        layout3.addWidget(QLabel('终止日期:'))
        layout3.addWidget(self.dateTimeEdit2)
        layout3.addWidget(QLabel('精度:'))
        layout3.addWidget(self.precision_edit)
        layout3.addStretch(1)
        layout3.addWidget(self.compare_button)

        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        layout.addLayout(layout3)
        layout.addWidget(self.pix_label)
        layout.addStretch(1)

        self.setLayout(layout)
        self.button1.clicked.connect(lambda: self.load_text(self.editor1))
        self.button2.clicked.connect(lambda: self.load_text(self.editor2))
        self.compare_button.clicked.connect(self.show_distribution)

    def init_data(self):
        root = '..\\basicData\\dailyUpdate\\latest\\res_daily\\'
        res = list()
        for file in os.listdir(root):
            res.extend(load_pkl('%s\\%s' % (root, file)))

        self.data = res

        cache = load_json_txt('tmp\\comparison_cache.txt')
        self.editor1.setText(cache['path1'])
        self.editor2.setText(cache['path2'])
        self.precision_edit.setText(str(cache['precision']))

        self.dateTimeEdit1.setDate(QDate.fromString(cache['date1'], 'yyyy-MM-dd'))
        self.dateTimeEdit2.setDate(QDate.fromString(cache['date2'], 'yyyy-MM-dd'))

        self.range1.setText(cache['range1'])
        self.range2.setText(cache['range2'])

        try:
            self.pix_label.setPixmap(QPixmap('tmp\\comparison_plot.png'))
        except:
            pass

    def save_cfg(self):
        self.cache['date1'] = self.dateTimeEdit1.date().toString('yyyy-MM-dd')
        self.cache['date2'] = self.dateTimeEdit2.date().toString('yyyy-MM-dd')
        self.cache['path1'] = self.editor1.text()
        self.cache['path2'] = self.editor2.text()
        self.cache['precision'] = float(self.precision_edit.text())
        self.cache['range1'] = self.range1.text()
        self.cache['range2'] = self.range2.text()
        write_json_txt('tmp\\comparison_cache.txt', self.cache)

    @staticmethod
    def convert2int(txt):
        ret = 0
        try:
            ret = int(txt)
        except:
            pass
        return ret

    def show_distribution(self):
        try:
            precision = float(self.precision_edit.text())

        except Exception as e:
            print(e)
            return

        date1 = self.dateTimeEdit2.date().toString('yyyy-MM-dd')
        date2 = self.dateTimeEdit1.date().toString('yyyy-MM-dd')

        list1 = load_json_txt(self.editor1.text())
        list2 = load_json_txt(self.editor2.text())

        range1 = self.convert2int(self.range1.text())
        range2 = self.convert2int(self.range2.text())

        if range1 != 0:
            list1 = list1[:range1]
        if range2 != 0:
            list2 = list2[:range2]

        df = self.data

        ret = pd.DataFrame(dtype='int64')

        for tmp in df:
            code = tmp[0]
            src = tmp[1]

            try:
                val1 = src.loc[date1, 's_028_market_value']
                val2 = src.loc[date2, 's_028_market_value']
            except Exception as e:
                val1 = np.inf
                val2 = np.inf

            r = val1 / val2 - 1

            if val1 == np.inf or val2 == np.inf:
                r = np.nan

            if not np.isnan(r):
                index = round(r / precision) * precision

                if code in list1:
                    ret = self.add_counter(ret, index, 'list1')

                if code in list2:
                    ret = self.add_counter(ret, index, 'list2')

        if ret.size == 0:
            print('warning: ret.size == 0')
            return

        start = min(ret.index)
        end = max(ret.index) + 1e-10

        new_index = np.arange(start, end, precision)
        new_index = map(lambda x: round(x / precision) * precision, new_index)
        ret = ret.reindex(new_index).fillna(0)

        print('ret: pd.DataFrame')
        print(ret.sum())

        g_figure(ret, 'tmp\\comparison_plot.png')
        self.pix_label.setPixmap(QPixmap('tmp\\comparison_plot.png'))
        self.save_cfg()

    @staticmethod
    def load_text(editor):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)
        dialog.setDirectoryUrl(QUrl('D:\\PycharmProjects\\stockAnalysis\\basicData'))

        if dialog.exec():
            file_paths = dialog.selectedFiles()
            try:
                path = file_paths[0]
                editor.setText(path)
            except Exception as e:
                print(e)

    @staticmethod
    def add_counter(df: pd.DataFrame, row, column):
        if row in df.index and column in df.columns:
            df.loc[row, column] = df.loc[row, column] + 1
        else:
            df.loc[row, column] = 1
        ret = df.fillna(0)
        return ret


def g_figure(df: pd.DataFrame, path):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    xx = df.index
    fig = plt.figure(figsize=(16, 9), dpi=90)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    ax1.yaxis.grid(True, which='both')
    ax1.xaxis.grid(True, which='both')
    # ax1.set_ylim([0, 0.5])

    colors = ['b', 'r', 'g']
    for index, column in enumerate(df.columns):
        yy = df.loc[:, column]
        yy = yy / yy.sum()
        color = colors[index % 3]
        ax1.plot(xx, yy, linestyle='-', alpha=0.8, color=color, label=column)

    ax1.legend()
    for label in ax1.xaxis.get_ticklabels():
        # label is a Text instance
        label.set_color('blue')
        # label.set_rotation(50)

    plt.savefig(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ComparisonWidget()
    main.show()
    sys.exit(app.exec_())


