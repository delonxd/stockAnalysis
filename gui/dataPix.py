from method.dataMethod import *
from method.mainMethod import get_units_dict
from gui.dataSource import DataSource
from gui.dataSource import DefaultDataSource
from gui.informationBox import InformationBox

from dateutil.rrule import *

import datetime as dt
import numpy as np
from collections import defaultdict

import time


from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DataPix(QObject):
    update_tree = pyqtSignal()

    def __init__(self, parent, m_width, m_height, style_df: pd.DataFrame):
        super().__init__()

        self.parent = parent
        self.style_df = style_df

        # structure
        self.m_width = m_width
        self.m_height = m_height

        self.d_width = d_width = 1400
        self.d_height = d_height = 700

        left_blank = 130
        right_blank = 80
        bottom_blank = 50

        self.main_rect = QRect(0, 0, m_width, m_height)
        self.data_rect = QRect(left_blank, 100, d_width, d_height)

        # pix
        self.pix = QPixmap()
        self.pix_show = QPixmap()
        self.struct_pix = QPixmap()

        # date metrics
        self.date_max = dt.date(2022, 7, 20)
        self.date_min = dt.date(1996, 7, 20)
        self.d_date = (self.date_max - self.date_min).days

        self.date_metrics1 = self.get_date_list('INTERIM')
        self.date_metrics2 = self.get_date_list('YEARLY')

        # px_list
        # self.date_list = self.get_date_list('MONTHLY')
        self.date_list = self.get_date_list('QUARTERLY')
        self.px_list, self.px_dict = self.get_px_list()
        # self.px_list, self.px_dict = self.get_px_dict()

        # data_source
        self.data_dict = None
        self.default_ds = None

        self.report_dict = dict()
        self.report_date = list()

        self.scale_ratio = 4

        self.update_pix()

    @property
    def df(self):
        return self.parent.df

    def update_pix(self):
        if len(self.df.index) == 0:
            self.init_pix()
            self.draw_struct()
            self.pix_show = self.pix
            return

        self.reset_scale_all()

        ds_dict = dict()

        style_df = self.style_df[self.style_df['selected'].values]

        self.default_ds = DefaultDataSource(parent=self)

        for index, row in style_df.iterrows():
            data = self.df.loc[:, [row['index_name']]]
            data.dropna(inplace=True)

            if len(data.index) == 0:
                continue
            # print(data)
            ds = DataSource(
                parent=self,
                df=data,
                index_name=row['index_name'],
                show_name=row['show_name'],
                color=row['color'],
                line_thick=row['line_thick'],
                pen_type=row['pen_style'],
                scale_min=row['scale_min'],
                scale_max=row['scale_max'],
                scale_div=row['scale_div'],
                logarithmic=row['logarithmic'],
                info_priority=row['info_priority'],
                units=row['units'],
                ds_type=row['ds_type'],
                delta_mode=row['delta_mode'],
                default_ds=row['default_ds'],
                ma_mode=row['ma_mode'],
                frequency=row['frequency'],
            )
            ds_dict[ds.index_name] = ds

            if ds.default_ds is True:
                self.default_ds = ds

        self.data_dict = ds_dict
        self.draw_pix()
        self.config_report_date()

    def config_report_date(self):
        if 'reportDate' in self.data_dict.keys():
            df = self.data_dict['reportDate'].df
            dates1 = np.vectorize(lambda x: x[:10])(df.iloc[:, 0].values)
            val_x1 = np.vectorize(lambda x: (dt.datetime.strptime(x, "%Y-%m-%d").date() - self.date_min).days)(dates1)

            dates2 = df.index.values
            val_x2 = np.vectorize(lambda x: (dt.datetime.strptime(x, "%Y-%m-%d").date() - self.date_min).days)(dates2)

            dict0 = defaultdict(int)
            for index in range(val_x1.shape[0]):
                dict0[val_x1[index]] = val_x2[index]

            self.report_dict = dict0
            list0 = list(dict0.keys())
            list0.sort()
            self.report_date = list0

    def reset_scale_all(self):
        style_df = self.style_df[self.style_df['selected'].values]

        default_row = style_df[style_df['default_ds'].values].iloc[0]
        ratio = get_units_dict()[default_row['units']]

        scale_max = self.df[default_row['index_name']].max() * self.scale_ratio / ratio
        scale_min = scale_max / 1024

        self.style_df.loc[
            self.style_df['selected'].values &
            self.style_df['logarithmic'].values &
            (self.style_df['units'].values == '亿'),
            ['scale_max', 'scale_min']
            ] = [scale_max, scale_min]

        self.update_tree.emit()

    def get_date_list(self, mode):
        if mode == 'WEEKLY':
            return list(rrule(WEEKLY, wkst=SU, byweekday=FR, dtstart=self.date_min, until=self.date_max))
        elif mode == 'MONTHLY':
            return list(rrule(MONTHLY, bymonthday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'YEARLY':
            return list(rrule(YEARLY, byyearday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'INTERIM':
            return list(rrule(YEARLY, bymonthday=-1, bymonth=6, dtstart=self.date_min, until=self.date_max))
        elif mode == 'QUARTERLY':
            return list(rrule(YEARLY, bymonthday=-1, bymonth=[3, 6, 9, 12], dtstart=self.date_min, until=self.date_max))
        return None

    def get_px_list(self):
        px_dict = dict()
        px_list = list()
        for datetime in self.date_list:
            date = datetime.date()
            px = self.x_data2px(date)
            px_dict[px] = date
            px_list.append(px)

        # px_list.sort()

        return px_list, px_dict

    def get_px_dict(self):
        res_dict = defaultdict(str)

        val_x = np.arange(0, self.d_date + 1)
        px_x = self.data_rect.x() + val_x * (self.data_rect.width() - 1) / self.d_date
        px_x = np.floor(px_x)
        res_list = np.unique(px_x).tolist()
        # res_list.sort()
        date0 = self.date_min
        for i in val_x:
            px = px_x[i]
            index = date0.strftime("%Y-%m-%d")
            res_dict[px] = index
            date0 = date0 + dt.timedelta(days=1)

        return res_list, res_dict

    # @staticmethod
    # def iter_delta_date(date_min, date_iter):
    #     return map(lambda x: (x - date_min).days, date_iter)
    #
    # def indexes_2_val_x(self, indexes):
    #     return np.vectorize(lambda x1: (dt.datetime.strptime(x1, "%Y-%m-%d").date() - self.date_min).days)(indexes)
    #
    # def val_x_2_px_x(self, val_x):
    #     return self.data_rect.x() + val_x * (self.data_rect.width() - 1) / self.d_date

    ###############################################################################################

    def init_pix(self):
        self.pix = QPixmap(self.main_rect.width(), self.main_rect.height())
        color = QColor(40, 40, 40, 255)
        self.pix.fill(color)
        # self.pix.fill(Qt.black)

    def draw_pix(self):
        self.init_pix()
        self.draw_struct()
        self.draw_metrics(self.default_ds)

        self.draw_auxiliary_line(self.default_ds)

        self.struct_pix = QPixmap(self.pix)
        self.draw_data_dict()
        self.pix_show = self.pix

    def draw_struct(self):
        pix_painter = QPainter(self.pix)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawRect(
            self.main_rect.x(),
            self.main_rect.y(),
            self.main_rect.width() - 1,
            self.main_rect.height() - 1)

        pix_painter.drawRect(
            self.data_rect.x() - 1,
            self.data_rect.y(),
            self.data_rect.width() + 1,
            self.data_rect.height())

        pix_painter.end()

    def draw_metrics(self, data: DataSource):
        self.draw_x_metrics()
        self.draw_y_metrics(data)
        # self.draw_y_metrics2(data)

    def draw_x_metrics(self):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        # pen2 = QPen(Qt.gray, 1, Qt.DotLine)
        pen2 = QPen(QColor(80, 80, 80, 255), 1, Qt.DotLine)

        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom() + 1

        for datetime in self.date_metrics1:
            x = self.x_data2px(datetime.date())
            txt = str(datetime.year)

            width = pix_painter.fontMetrics().width(txt) + 2
            height = pix_painter.fontMetrics().height() + 2
            rect = QRect(
                x - width / 2, self.data_rect.bottom() + 1,
                width, height)

            pix_painter.setPen(pen1)
            pix_painter.drawText(rect, Qt.AlignCenter, txt)

        for datetime in self.date_metrics2:
            x = self.x_data2px(datetime.date())

            pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))

        pix_painter.end()

    def draw_y_metrics(self, data: DataSource):
        pix_painter = QPainter(self.pix)

        pix_painter.setFont(QFont('Consolas', 10))
        pen1 = QPen(Qt.red, 1, Qt.SolidLine)
        pen2 = QPen(Qt.red, 1, Qt.DotLine)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()

        val_list = [x / 10 for x in range(1, 10)]

        for val_y in val_list:
            y = self.y_value2px(val_y, data)
            data_y = self.y_value2data(val_y, data)
            txt = data.format(data_y)

            width = pix_painter.fontMetrics().width(txt) + 2
            height = pix_painter.fontMetrics().height() + 2
            rect = QRect(
                self.data_rect.right() + 1, y - height / 2,
                width, height)

            pix_painter.setPen(pen1)
            pix_painter.drawText(rect, Qt.AlignCenter, txt)

            pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        pix_painter.end()

    # def draw_y_metrics2(self, data: DataSource):
    #     pix_painter = QPainter(self.pix)
    #
    #     pix_painter.setFont(QFont('Consolas', 10))
    #     pen1 = QPen(Qt.red, 1, Qt.SolidLine)
    #     pen2 = QPen(Qt.red, 1, Qt.DotLine)
    #
    #     d_left = self.data_rect.left()
    #     d_right = self.data_rect.right()
    #     d_top = self.data_rect.top()
    #     d_bottom = self.data_rect.bottom()
    #
    #     ratio = data.ratio
    #     data_list = [(2 ** x) * ratio for x in range(-10, 20)]
    #
    #     for data_y in data_list:
    #         y = self.y_data2px(data_y, data)
    #         txt = data.format(data_y)
    #
    #         width = pix_painter.fontMetrics().width(txt) + 2
    #         height = pix_painter.fontMetrics().height() + 2
    #         rect = QRect(
    #             self.data_rect.right() + 1, y - height / 2,
    #             width, height)
    #
    #         if rect.top() < d_top or rect.bottom() > d_bottom:
    #             continue
    #
    #         pix_painter.setPen(pen1)
    #         pix_painter.drawText(rect, Qt.AlignCenter, txt)
    #
    #         pix_painter.setPen(pen2)
    #         pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))
    #
    #     # val_list = [x / 10 for x in range(1, 10)]
    #     # for val_y in val_list:
    #     #     y = self.y_value2px(val_y, data)
    #     #     pix_painter.setPen(pen2)
    #     #     pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))
    #
    #     pix_painter.end()

    def draw_auxiliary_line(self, data: DataSource):
        pix_painter = QPainter(self.pix)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()

        date0 = dt.datetime.strptime(data.df.index.values[-1], "%Y-%m-%d").date()
        value0 = data.df.values[-1, -1]

        if value0 <= 0:
            value0 = data.scale_max / 4

        # 30% 辅助线
        ratio_year = 1.3
        value1 = get_value_from_ratio(date0, value0, self.date_min, ratio_year)
        value2 = get_value_from_ratio(date0, value0, self.date_max, ratio_year)
        y1 = self.y_data2px(value1, self.default_ds)
        y2 = self.y_data2px(value2, self.default_ds)

        pen = QPen(Qt.red, 1, Qt.DotLine)
        pix_painter.setPen(pen)
        pix_painter.drawLine(QPoint(d_left, y1), QPoint(d_right, y2))

        # 10% 辅助线
        ratio_year = 1.1
        value1 = get_value_from_ratio(date0, value0, self.date_min, ratio_year)
        value2 = get_value_from_ratio(date0, value0, self.date_max, ratio_year)
        y1 = self.y_data2px(value1, self.default_ds)
        y2 = self.y_data2px(value2, self.default_ds)

        pen = QPen(Qt.blue, 1, Qt.DotLine)
        pix_painter.setPen(pen)
        pix_painter.drawLine(QPoint(d_left, y1), QPoint(d_right, y2))

        pix_painter.end()

    def draw_data_dict(self):
        for data in self.data_dict.values():
            self.draw_data(data, self.pix)

    def draw_data(self, data: DataSource, pix):
        dates = data.df.index.values
        val_x = np.vectorize(lambda x1: (dt.datetime.strptime(x1, "%Y-%m-%d").date() - self.date_min).days)(dates)
        px_x = self.data_rect.x() + val_x * (self.data_rect.width() - 1) / self.d_date

        # val_x = self.indexes_2_val_x(data.df.index.values)
        # px_x = self.val_x_2_px_x(val_x)

        if data.ds_type == 'digit':

            pix_painter = QPainter(pix)
            pen = QPen(data.color, data.line_thick, data.pen_type)
            pix_painter.setPen(pen)

            data_y = data.df.iloc[:, 0].values.copy()

            # print(data.show_name)
            # print(data_y)

            if data.logarithmic is False:
                data_y[data_y == 0] = np.nan

                df_point = pd.DataFrame()
                df_point['px_x'] = px_x
                df_point['px_y'] = (data.val_max - data_y) * self.data_rect.height() / data.val_delta + self.data_rect.top()

                df_point.dropna(inplace=True)
                point_list = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]

            else:
                # print(data.index_name, data.show_name)
                px_x[np.isnan(data_y)] = np.nan
                data_y[np.isnan(data_y)] = 0
                data_y[data_y <= 0] = 1e-10

                df_point = pd.DataFrame()
                df_point['px_x'] = px_x
                px_y = (data.val_max - np.log2(data_y / data.scale_min) / np.log2(data.scale_max / data.scale_min)) * self.data_rect.height() / data.val_delta + self.data_rect.top()
                df_point['px_y'] = px_y

                df_point.dropna(inplace=True)
                point_list = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]

            if data.delta_mode is False:
                if point_list:
                    pix_painter.drawPolyline(*point_list)
            else:
                point1 = None
                for point in point_list:
                    point2 = point
                    if point1:
                        point3 = QPoint(point1.x(), point2.y())
                        pix_painter.drawLine(point1, point3)
                        pix_painter.drawLine(point3, point2)
                    point1 = point2

            pix_painter.end()

    ###############################################################################################

    def draw_cross(self, x, y, state):

        self.pix_show = QPixmap(self.pix)

        if x is None and y is None:
            return

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()
        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom() + 1

        if x < d_left:
            x = d_left
        elif x > d_right:
            x = d_right
        if y < d_top:
            y = d_top
        elif y > d_bottom:
            y = d_bottom

        # date, val = self.px2data(x, y, self.default_ds)
        # date_str = date.strftime("%Y-%m-%d")

        val = self.y_px2data(y, self.default_ds)
        val_str = self.default_ds.format(val)

        val_x0 = self.x_px2value(x)

        val_x1 = self.get_last_value(val_x0, self.report_date)

        if not val_x1:
            val_x1 = self.report_date[0]

        val_x2 = self.report_dict.get(val_x1)
        val_x2 = val_x2 if val_x2 else val_x1

        px_x0 = x
        px_x2 = self.x_value2px(val_x2)

        if state is True:
            self.draw_mask(px_x0, px_x2)

        pix_painter = QPainter(self.pix_show)
        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))
        pix_painter.end()

        date0 = self.x_value2data(int(val_x0))
        date2 = self.x_value2data(int(val_x2))
        date_str0 = date0.strftime("%Y-%m-%d")
        date_str2 = date2.strftime("%Y-%m-%d")

        self.draw_tooltip(px_x0, self.data_rect.bottom() + 1, date_str0)
        self.draw_tooltip(px_x2, self.data_rect.top(), date_str2)

        self.draw_tooltip(self.data_rect.right() + 1, y, val_str)
        # self.draw_information(date)

        self.draw_information(px_x2)

    def draw_mask(self, px_x0, px_x2):
        if px_x2:
            self.draw_mask_pix(
                pix=self.pix_show,
                x=px_x2,
            )

        self.draw_data(self.data_dict['id_041_mvs_mc'], self.pix_show)

        self.draw_mask_pix(
            pix=self.pix_show,
            x=px_x0,
        )

    def draw_mask_pix(self, pix, x):
        y = self.main_rect.top()
        width = self.main_rect.right() - x
        height = self.main_rect.height()

        pix_painter = QPainter(pix)
        mask = self.struct_pix.copy(x, y, width, height)
        # mask = QPixmap(xwidth, height)
        # mask.fill(QColor(40, 40, 40, 255))
        pix_painter.drawPixmap(x, y, mask)
        pix_painter.end()

    def draw_tooltip(self, x, y, text):
        pix_painter = QPainter(self.pix_show)
        pix_painter.setFont(QFont('Consolas', 10))

        metrics = pix_painter.fontMetrics()
        rect = QRect(x, y, metrics.width(text) + 2, metrics.height() + 2)

        # draw_rect
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(Qt.blue)

        pen = QPen(Qt.red, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.setBrush(brush)
        pix_painter.drawRect(rect)

        # draw_text
        pix_painter.setPen(QColor(Qt.red))
        pix_painter.drawText(rect, Qt.AlignCenter, text)

        pix_painter.end()

    def draw_information(self, px_x):
        box = InformationBox(parent=self)
        pix = box.draw_pix(px_x)

        pix_painter = QPainter(self.pix_show)
        pix_painter.drawPixmap(10, 10, pix)
        pix_painter.end()

    @staticmethod
    def get_last_value(x, x_list):
        if not x_list:
            return x

        last = None
        for px in x_list:
            if x < px:
                return last
            last = px
        return last

    @staticmethod
    def get_nearest_value(x, x_list):
        nearest = None

        if len(x_list) > 0:
            if x <= x_list[0]:
                return x_list[0]
            elif x >= x_list[-1]:
                return x_list[-1]

        px1 = np.inf
        for px in x_list:
            px2 = px
            if px1 <= x < px2:
                if (x - px1) <= (px2 - x):
                    nearest = px1
                else:
                    nearest = px2
                break
            px1 = px
        return nearest

    # def get_nearest_date(self, x):
    #     px = self.get_nearest_px(x)
    #     if px is not None:
    #         return self.px_dict[px]
    #     else:
    #         return None

    ###############################################################################################

    def x_data2value(self, date):
        val_x = None
        if date is not None:
            val_x = (date - self.date_min).days
        return val_x

    def x_value2data(self, val_x):
        date = None
        if val_x is not None:
            date = self.date_min + dt.timedelta(days=val_x)
        return date

    def x_value2px(self, val_x):
        px_x = None
        if val_x is not None:
            px_x = self.data_rect.x() + val_x * (self.data_rect.width() - 1) / self.d_date
        return px_x

    def x_px2value(self, px_x):
        val_x = None
        if px_x is not None:
            val_x = (px_x - self.data_rect.x()) * self.d_date / (self.data_rect.width() - 1)
        return val_x

    def x_data2px(self, date):
        val_x = self.x_data2value(date)
        px_x = self.x_value2px(val_x)
        return px_x

    def x_px2data(self, px_x):
        val_x = self.x_px2value(px_x)
        date = self.x_value2data(val_x)
        return date

    ###############################################################################################

    @staticmethod
    def y_data2value(value, data: DataSource):
        val_y = None
        if value is not None:
            if data.logarithmic is True:
                val_y = np.log2(value / data.scale_min) / np.log2(data.scale_max / data.scale_min)
            else:
                val_y = value
        return val_y

    @staticmethod
    def y_value2data(val_y, data: DataSource):
        value = None
        if val_y is not None:
            if data.logarithmic is True:
                value = 2 ** (val_y * np.log2(data.scale_max / data.scale_min)) * data.scale_min
            else:
                value = val_y
        return value

    def y_value2px(self, val_y, data: DataSource):
        y = None
        if val_y is not None:
            y = (data.val_max - val_y) * self.data_rect.height() / data.val_delta + self.data_rect.top()
        return y

    def y_px2value(self, px_y, data: DataSource):
        val_y = None
        if px_y is not None:
            val_y = data.val_max - (px_y - self.data_rect.top()) * data.val_delta / self.data_rect.height()
        return val_y

    def y_data2px(self, value, data):
        val_y = self.y_data2value(value, data)
        y = self.y_value2px(val_y, data)
        return y

    def y_px2data(self, px_y, data):
        val_y = self.y_px2value(px_y, data)
        value = self.y_value2data(val_y, data)
        return value

    ###############################################################################################

    def data2value(self, date, value, data: DataSource):
        val_x = self.x_data2value(date)
        val_y = self.y_data2value(value, data)
        return val_x, val_y

    def value2data(self, val_x, val_y, data: DataSource):
        date = self.x_value2data(val_x)
        value = self.y_value2data(val_y, data)
        return date, value

    def value2px(self, val_x, val_y, data: DataSource):
        x = self.x_value2px(val_x)
        y = self.y_value2px(val_y, data)
        return x, y

    def px2value(self, px_x, px_y, data: DataSource):
        val_x = self.x_px2value(px_x)
        val_y = self.y_px2value(px_y, data)
        return val_x, val_y

    def data2px(self, date, value, data):
        x = self.x_data2px(date)
        y = self.y_data2px(value, data)
        return x, y

    def px2data(self, px_x, px_y, data):
        date = self.x_px2data(px_x)
        value = self.y_px2data(px_y, data)
        return date, value

