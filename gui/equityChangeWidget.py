from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from method.dataMethod import load_df_from_mysql
from request.requestData import get_header_df

import sys


class EquityChangeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('EquityChangeWidget')
        self.resize(940, 800)

        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.code = None

        layout = QHBoxLayout()
        layout.addWidget(self.table_widget)

        self.setLayout(layout)

    def load_code(self, code):
        if self.isHidden():
            return
        if code == self.code:
            return

        self.code = code

        df = load_df_from_mysql(code, 'eq')

        header_df = get_header_df('eq')

        df.columns = header_df.loc['txt_CN', :]
        df = df.drop(['首次上传日期', '最近上传日期'], axis=1)

        drop_index = []
        for index, series in df.iterrows():
            row = series.tolist()
            if row[8] == row[9] == row[10] == row[11] == 0 and row[1] == 'periodicReport':
                drop_index.append(index)
        df = df.drop(drop_index)

        self.table_widget.setRowCount(df.index.size)
        self.table_widget.setColumnCount(12)
        self.table_widget.setHorizontalHeaderLabels(df.columns)

        for i, tup in enumerate(df.iterrows()):
            row = tup[1].tolist()

            if abs(row[3]-1) > 0.03:
                brush = QBrush(Qt.red)
            else:
                brush = QBrush(Qt.black)

            row[1] = get_reason_cn(row[1])
            row[5] = row[5] / row[4]
            row[6] = row[6] / row[4]
            row[7] = row[7] / row[4]

            for j, value in enumerate(row):
                if j in [4, 8, 9, 10, 11]:
                    if value == 0:
                        txt = '-'
                    else:
                        txt = format(int(value), ',')
                elif j in [5, 6, 7]:
                    if value == 0:
                        txt = '-'
                    else:
                        txt = format(value*100, '.2f') + '%'
                elif j == 2:
                    txt = '  ' + str(value)
                elif j == 3:
                    if value == 1:
                        txt = '-'
                    else:
                        txt = format(value*100-100, '.2f') + '%'
                else:
                    txt = str(value)
                item = QTableWidgetItem(txt)
                item.setForeground(brush)

                # if j == 2:
                #     item.setBackground(Qt.gray)

                if j > 7:
                    font = item.font()
                    font.setPointSize(8)
                    item.setFont(font)

                if j > 2:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignCenter)
                self.table_widget.setItem(i, j, item)

        self.table_widget.resizeColumnsToContents()
        self.table_widget.setColumnWidth(0, 90)

        width = 60
        self.table_widget.setColumnWidth(2, width)
        self.table_widget.setColumnWidth(3, width)
        self.table_widget.setColumnWidth(5, width)
        self.table_widget.setColumnWidth(6, width)
        self.table_widget.setColumnWidth(7, width)


def get_reason_cn(reason):
    dict0 = {
        'dividend': '送、转股',
        'limitedToShare': '股份性质变动',
        'IPO': 'IPO',
        'beforeIPO': '发行前股本',
        'allotment': '配股',
        'periodicReport': '定期报告',
        'equityOption': '权证行权',
        'SPO': '增发',
        'SPO_H': 'H股上市',
        'SPO_B': 'B股上市',
        'otherSPO': '其它上市',
        'nonTradableSharesReform': '股权分置',
        'equityIncentive': '股权激励',
        'optionIncentive': '期权行权',
        'repurchase': '回购',
        'debtForEquity': '债转股',
        'sharesReformDividend': '股改追送',
        'historyReason': '历史遗留',
        'merger': '吸收合并',
        'reorganize': '资产重组',
        'overAllotment': '超额配售',
        'nonOperatingAssetStripping': '非经营资产剥离',
        'split': '拆细',
        'unknown': '未知',
    }
    return dict0.get(reason)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = EquityChangeWidget()
    main.show()
    main.load_code('000001')
    sys.exit(app.exec_())

    # a = request_equity_change('600004')
    # print(a)
