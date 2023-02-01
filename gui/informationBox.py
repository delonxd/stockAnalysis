from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

from gui.dataSource import DataSource


class InformationBox:
    def __init__(self, parent):
        self.parent = parent
        self.background = None

    def load_value(self, d1, d2, d_report, window_flag):
        df = self.parent.ds_df
        s1 = df.loc[d1, :].copy() if d1 in df.index else pd.Series()
        s2 = df.loc[d2, :].copy() if d2 in df.index else pd.Series()

        box = list()
        for ds in self.parent.data_dict.values():
            if ds.info_show[window_flag] is False:
                continue

            index_name = ds.index_name

            row = [ds.info_priority, ds, ds.show_name, None, None]

            if ds.frequency == 'DAILY':
                row[4] = d1
                value = s1[index_name] if index_name in s1.index else None
                if pd.isna(value):
                    sub = ds.df.iloc[:, 0].copy().dropna()
                    value = sub[-1] if sub.size > 0 else None
                row[3] = value
            else:
                value = s2[index_name] if index_name in s2.index else None
                if pd.isna(value):
                    sub = ds.df.iloc[:, 0].copy().dropna()
                    if sub.size > 0:
                        value = sub[-1]
                        row[4] = sub.index[-1]
                row[3] = value

            box.append(row)

        box.sort(key=lambda x: x[0])

        res = list()
        res.append(('公布日期: %s' % d_report, QPen(Qt.red, 1, Qt.SolidLine)))
        res.append(('报告日期: %s' % d2, QPen(Qt.white, 1, Qt.SolidLine)))
        res.append(('当前日期: %s' % d1, QPen(Qt.white, 1, Qt.SolidLine)))

        for _, ds, name, value, real_date in box:
            txt = ds.format(value)
            if real_date is not None:
                name = '%s (%s)' % (name, real_date)

            # num = self.chinese_num(txt)
            # txt = '{0:>{width}}'.format(txt, width=7-num)
            row_txt = '%s: %s' % (txt, name)
            pen = QPen(ds.color)
            res.append((row_txt, pen, ds))

        return res

    def draw_pix(self, *args):
        text_list = self.load_value(*args)
        window_flag = args[3]

        res_list = []
        for row in text_list:

            if len(row) == 2:
                res_list.append((row[0], row[1]))
                continue
            ds = row[2]

            if ds.info_show[window_flag] is True:
                res_list.append((row[0], row[1]))

        pix = self.draw_text(res_list)
        return pix

    @staticmethod
    def draw_text(text_list):

        pix = QPixmap(900, 1000)
        pix.fill(QColor(0, 0, 0, 255))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 9))

        metrics = pix_painter.fontMetrics()

        max_width1 = max_width2 = 0
        for row_txt, _ in text_list:
            txt1, txt2 = row_txt.split(":")
            max_width1 = max(metrics.width(txt1), max_width1)
            max_width2 = max(metrics.width(txt2), max_width2)

        x = y = blank = 1
        max_width = max_width1 + max_width2
        row_height = metrics.height() + blank * 2

        for row_txt, pen in text_list:
            pix_painter.setPen(pen)

            txt1, txt2 = row_txt.split(":")

            width1 = metrics.width(txt1)
            rect = QRect(x + max_width1 - width1, y, width1, row_height)
            pix_painter.drawText(rect, Qt.AlignCenter, txt1)

            width2 = metrics.width(txt2)
            rect = QRect(x + max_width1, y, width2, row_height)
            pix_painter.drawText(rect, Qt.AlignCenter, txt2)

            y += row_height
        pix_painter.end()

        max_width += blank * 2
        max_height = y + blank

        res = pix.copy(0, 0, max_width, max_height)
        return res

    @staticmethod
    def draw_box(box, pix):
        pix_painter = QPainter(pix)
        pix_painter.drawPixmap(10, 10, box)
        pix_painter.end()

    @staticmethod
    def chinese_num(data):
        ret = 0
        for s in data:
            if ord(s) > 127:
                ret += 1
        return ret
