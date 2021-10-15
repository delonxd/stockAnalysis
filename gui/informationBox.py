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

    def load_value(self, px_x):
        date = self.parent.px_dict.get(px_x)
        date_index = date.strftime("%Y-%m-%d")
        box_df = pd.DataFrame(columns=['priority', 'data_source', 'show_name', 'value', 'real_date'])

        for ds in self.parent.data_dict.values():
            index_name = ds.index_name
            index_list = ds.df.index.tolist()

            if ds.frequency == 'DAILY':
                # date0 = self.parent.date_min
                # val_x = (date - date0).days
                # val_x = self.parent.get_nearest_value(val_x, ds.offsets)
                # # print(type(val_x), '-->', val_x)
                # date1 = date0 + relativedelta(days=int(val_x))
                # date_index1 = date1.strftime("%Y-%m-%d")
                #
                # box_df.loc[index_name, 'value'] = ds.df.loc[date_index1][0]
                # box_df.loc[index_name, 'real_date'] = date_index1

                box_df.loc[index_name, 'value'] = ds.df.iloc[-1, 0]
                box_df.loc[index_name, 'real_date'] = ds.df.index[-1]

                # box_df.loc[index_name, 'value'] = None
                # box_df.loc[index_name, 'real_date'] = None

            else:
                if date_index in index_list:
                    box_df.loc[index_name, 'value'] = ds.df.loc[date_index][0]
                else:
                    box_df.loc[index_name, 'value'] = None

                box_df.loc[index_name, 'real_date'] = None

            box_df.loc[index_name, 'priority'] = ds.info_priority
            box_df.loc[index_name, 'data_source'] = ds
            box_df.loc[index_name, 'show_name'] = ds.show_name

        box_df.sort_values('priority', inplace=True)

        res = list()
        txt = date.strftime("%Y-%m-%d")
        res.append(('日期: %s' % txt, QPen(Qt.white, 1, Qt.SolidLine)))

        for _, row in box_df.iterrows():
            name, value, ds = row['show_name'], row['value'], row['data_source']
            txt = ds.format(value)
            if row['real_date'] is not None:
                txt = '%s (%s)' % (txt, row['real_date'])

            row_txt = '%s: %s' % (name, txt)
            pen = QPen(ds.color, ds.line_thick, ds.pen_type)
            res.append((row_txt, pen))

        return res

    def draw_pix(self, px_x):
        text_list = self.load_value(px_x)

        pix = QPixmap(400, 800)
        pix.fill(QColor(0, 0, 0, 30))

        pix_painter = QPainter(pix)
        pix_painter.setFont(QFont('Consolas', 14))

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
