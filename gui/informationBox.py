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

    def load_value(self, d1, d2):
        box_df = pd.DataFrame(columns=['priority', 'data_source', 'show_name', 'value', 'real_date'])

        for ds in self.parent.data_dict.values():
            if ds.data_type == 'assets':
                continue
            if ds.frequency == 'DAILY':
                date = d1
            else:
                date = d2

            index_name = ds.index_name

            if date in ds.df.index:
                box_df.loc[index_name, 'value'] = ds.df.loc[date][0]
            else:
                box_df.loc[index_name, 'value'] = None

            box_df.loc[index_name, 'priority'] = ds.info_priority
            box_df.loc[index_name, 'data_source'] = ds
            box_df.loc[index_name, 'show_name'] = ds.show_name

            if ds.frequency == 'DAILY':
                box_df.loc[index_name, 'real_date'] = d1
            else:
                box_df.loc[index_name, 'real_date'] = None

        box_df.sort_values('priority', inplace=True)

        res = list()
        res.append(('报告日期1: %s' % d1, QPen(Qt.white, 1, Qt.SolidLine)))
        res.append(('报告日期2: %s' % d2, QPen(Qt.white, 1, Qt.SolidLine)))

        for _, row in box_df.iterrows():
            name, value, ds = row['show_name'], row['value'], row['data_source']
            txt = ds.format(value)
            if row['real_date'] is not None:
                txt = '%s (%s)' % (txt, row['real_date'])

            row_txt = '%s: %s' % (name, txt)
            pen = QPen(ds.color, ds.line_thick, ds.pen_type)
            res.append((row_txt, pen))

        return res

    def draw_pix(self, *args):
        text_list = self.load_value(*args)

        pix = QPixmap(900, 1000)
        pix.fill(QColor(0, 0, 0, 255))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 9))

        metrics = pix_painter.fontMetrics()

        x = y = blank = 1
        max_width = 0
        row_height = metrics.height() + blank * 2

        for row_txt, pen in text_list:
            pix_painter.setPen(pen)

            width = metrics.width(row_txt)
            rect = QRect(x, y, width, row_height)
            pix_painter.drawText(rect, Qt.AlignCenter, row_txt)

            if width > max_width:
                max_width = width
            y += row_height
        pix_painter.end()

        max_width += blank * 2
        max_height = y + blank

        res = pix.copy(0, 0, max_width, max_height)
        return res
