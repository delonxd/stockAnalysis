from method.dataMethod import *
from method.mainMethod import get_units_dict
from gui.dataSource import DataSource
from gui.informationBox import InformationBox

import datetime as dt
import numpy as np
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
        self.data_rect = QRect(left_blank, 0, d_width, d_height)

        # pix
        self.pix = QPixmap()
        self.pix_show = QPixmap()

        # date metrics
        self.date_max = dt.date(2022, 7, 20)
        self.date_min = dt.date(1996, 7, 20)
        self.d_date = (self.date_max - self.date_min).days

        self.date_metrics1 = self.get_date_list('INTERIM')
        self.date_metrics2 = self.get_date_list('YEARLY')

        # px_list
        # self.date_list = self.get_date_list('MONTHLY')
        self.date_list = self.get_date_list('SEASON')
        self.px_list, self.px_dict = self.get_px_list()

        # data_source
        self.data_dict = None
        self.default_ds = None

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

        for index, row in style_df.iterrows():
            data = self.df.loc[:, [row['index_name']]]
            data.dropna(inplace=True)
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
            )
            ds_dict[ds.index_name] = ds

            if ds.default_ds is True:
                self.default_ds = ds

        self.data_dict = ds_dict
        self.draw_pix()

    def reset_scale_all(self):
        style_df = self.style_df[self.style_df['selected'].values]

        default_row = style_df[style_df['default_ds'].values].iloc[0]
        ratio = get_units_dict()[default_row['units']]

        scale_max = self.df[default_row['index_name']].max() * 4 / ratio
        scale_min = scale_max / 1024

        self.style_df.loc[
            self.style_df['selected'].values &
            self.style_df['logarithmic'].values &
            (self.style_df['units'].values == '亿'),
            ['scale_max', 'scale_min']
            ] = [scale_max, scale_min]

        self.update_tree.emit()

    def get_date_list(self, mode):
        res = None
        if mode == 'WEEKLY':
            res = list(rrule(WEEKLY, wkst=SU, byweekday=FR, dtstart=self.date_min, until=self.date_max))
        elif mode == 'MONTHLY':
            res = list(rrule(MONTHLY, bymonthday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'YEARLY':
            res = list(rrule(YEARLY, byyearday=-1, dtstart=self.date_min, until=self.date_max))
        elif mode == 'INTERIM':
            res = list(rrule(YEARLY, bymonthday=-1, bymonth=6, dtstart=self.date_min, until=self.date_max))
        elif mode == 'SEASON':
            res = list(rrule(YEARLY, bymonthday=-1, bymonth=[3, 6, 9, 12], dtstart=self.date_min, until=self.date_max))
        return res

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
            self.draw_data(data)

    def draw_data(self, data: DataSource):
        dates = data.df.index.values
        val_x = np.vectorize(lambda x1: (dt.datetime.strptime(x1, "%Y-%m-%d").date() - self.date_min).days)(dates)
        px_x = self.data_rect.x() + val_x * (self.data_rect.width() - 1) / self.d_date

        if data.ds_type == 'digit':

            pix_painter = QPainter(self.pix)
            pen = QPen(data.color, data.line_thick, data.pen_type)
            pix_painter.setPen(pen)

            data_y = data.df.iloc[:, 0].values.copy()

            # print(data.show_name)
            # print(data_y)

            if data.logarithmic is False:
                data_y[data_y == 0] = np.nan

                df_point = pd.DataFrame()
                df_point['px_x'] = px_x
                df_point['px_y'] = (data.val_max - data_y) * self.data_rect.height() / data.val_delta

                df_point.dropna(inplace=True)
                point_list = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]

            else:
                # print(data.index_name, data.show_name)
                px_x[np.isnan(data_y)] = np.nan
                data_y[np.isnan(data_y)] = 0
                data_y[data_y <= 0] = 1e-10

                df_point = pd.DataFrame()
                df_point['px_x'] = px_x
                px_y = (data.val_max - np.log2(data_y / data.scale_min) / np.log2(data.scale_max / data.scale_min)) * self.data_rect.height() / data.val_delta
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

    def draw_cross(self, x, y):

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

        pix_painter = QPainter(self.pix_show)

        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        x = self.get_nearest_px(x)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

        pix_painter.end()

        date, val = self.px2data(x, y, self.default_ds)
        date_str = date.strftime("%Y-%m-%d")
        val_str = self.default_ds.format(val)

        self.draw_tooltip(x, self.data_rect.bottom() + 1, date_str)
        self.draw_tooltip(self.data_rect.right() + 1, y, val_str)
        self.draw_information(date)

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

    def draw_information(self, date):
        box = InformationBox(parent=self)
        pix = box.draw_pix(date)

        pix_painter = QPainter(self.pix_show)
        pix_painter.drawPixmap(10, 10, pix)
        pix_painter.end()

    def get_nearest_px(self, x):
        nearest = None

        if len(self.px_list) > 0:
            if x <= self.px_list[0]:
                return self.px_list[0]
            elif x >= self.px_list[-1]:
                return self.px_list[-1]

        px1 = np.inf
        for px in self.px_list:
            px2 = px
            if px1 <= x < px2:
                if (x - px1) <= (px2 - x):
                    nearest = px1
                else:
                    nearest = px2
                break
            px1 = px
        return nearest

    def get_nearest_date(self, x):
        px = self.get_nearest_px(x)
        if px is not None:
            return self.px_dict[px]
        else:
            return None

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
            y = (data.val_max - val_y) * self.data_rect.height() / data.val_delta
        return y

    def y_px2value(self, px_y, data: DataSource):
        val_y = None
        if px_y is not None:
            val_y = data.val_max - px_y * data.val_delta / self.data_rect.height()
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

