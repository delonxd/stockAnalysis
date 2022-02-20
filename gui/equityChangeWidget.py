from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from method.urlMethod import data_request

import sys
import datetime as dt
import json


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
        if code == self.code:
            return
        self.code = code

        data = request_equity_change(code)
        list0 = config_equity_change_data(data)

        self.table_widget.setRowCount(len(list0))
        self.table_widget.setColumnCount(12)
        header = [
            '日期',
            '原因',
            '稀释',
            '变动',
            '总股本',
            '流通',
            '限售',
            '其他',
            'Δ总股本',
            'Δ流通',
            'Δ限售',
            'Δ其他',
        ]
        self.table_widget.setHorizontalHeaderLabels(header)
        for i, row in enumerate(list0):
            if abs(row[11]-1) > 0.03:
                brush = QBrush(Qt.red)
            else:
                brush = QBrush(Qt.black)

            show = [
                row[0], row[5], row[10], row[11],
                row[1], row[2], row[3], row[4],
                row[6],  row[7], row[8], row[9],
            ]
            for j, value in enumerate(show):
                item = QTableWidgetItem(str(value))
                # item.setBackground(brush)
                item.setForeground(brush)
                self.table_widget.setItem(i, j, item)

        self.table_widget.resizeColumnsToContents()
        self.table_widget.setColumnWidth(0, 100)
        self.table_widget.setColumnWidth(2, 55)
        self.table_widget.setColumnWidth(3, 55)


def request_equity_change(code):
    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    today = dt.date.today().strftime("%Y-%m-%d")
    url = 'https://open.lixinger.com/api/cn/company/equity-change'
    api = {
        "token": token,
        "startDate": "1970-01-01",
        "endDate": today,
        "stockCode": code,
    }

    res = data_request(url=url, api_dict=api)
    data = json.loads(res.decode())['data']

    # print(config_equity_change_data(data))
    return data


def config_equity_change_data(data):
    res = []

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
    for row in data:
        date = row['date'][:10]

        cap0 = row.get('capitalization')
        cap1 = row.get('outstandingSharesA')
        cap2 = row.get('limitedSharesA')

        cap0 = 0 if cap0 is None else cap0
        cap1 = 0 if cap1 is None else cap1
        cap2 = 0 if cap2 is None else cap2
        cap3 = cap0 - cap1 - cap2

        reason = row.get('changeReason')
        res.append([date, cap0, cap1, cap2, cap3, dict0.get(reason)])

    res.reverse()
    last = None
    res2 = []

    func = lambda x: '-' if x == 0 else x

    ipo_rate = 1
    for row in res:
        if last:
            d1 = row[1] - last[1]
            d2 = row[2] - last[2]
            d3 = row[3] - last[3]
            d4 = row[4] - last[4]

            if d1 == d2 == d3 == d4 == 0 and row[5] == '定期报告':
                pass
            else:
                rate = row[1] / last[1]
                if row[5] == '送、转股' or row[5] == '拆细':
                    # if abs(row[2] - last[2] * rate) <= 50:
                    #     if abs(row[3] - last[3] * rate) <= 50:
                    #         if abs(row[4] - last[4] * rate) <= 50:
                    rate = 1.0

                tmp = last[10]*rate
                if row[5] == 'IPO':
                    ipo_rate = tmp
                new = [*row, func(d1), func(d2), func(d3), func(d4), tmp, round(rate, 4)]
                res2.append(new)
        else:
            d1 = row[1]
            d2 = row[2]
            d3 = row[3]
            d4 = row[4]

            new = [*row, func(d1), func(d2), func(d3), func(d4), 1, 1]
            res2.append(new)
        last = res2[-1]

    for row in res2:
        row[10] = round(row[10] / ipo_rate, 4)

    return res2


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = EquityChangeWidget()
    main.load_code('000820')
    main.show()
    sys.exit(app.exec_())

    # a = request_equity_change('600004')
    # print(a)