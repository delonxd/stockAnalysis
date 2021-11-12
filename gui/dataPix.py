from method.dataMethod import get_value_from_ratio
from method.mainMethod import get_units_dict
from gui.dataSource import DataSource
from gui.dataSource import DefaultDataSource
from gui.informationBox import InformationBox
from method.dataMethod import get_month_delta
from method.dataMethod import get_month_data

from dateutil.rrule import *
from collections import defaultdict

import datetime as dt
import numpy as np
import pandas as pd


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
        self.pix2 = QPixmap()
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
        # self.px_list, self.px_dict = self.get_px_list()
        # self.px_list, self.px_dict = self.get_px_dict()

        # data_source
        self.data_dict = None
        self.default_ds = None

        # self.report_dict = dict()
        # self.report_date = list()

        self.dt_fs = pd.Series()
        self.dt_mvs = pd.Series()

        self.scale_ratio = 4

        self.update_pix()

    @property
    def df(self):
        return self.parent.df

    def update_pix(self):
        self.dt_fs = self.df['dt_fs'].copy().dropna()
        self.dt_mvs = self.df['dt_mvs'].copy().dropna()

        self.data_dict = dict()
        self.default_ds = DefaultDataSource(parent=self)

        if len(self.df.index) == 0:
            self.init_pix()
            self.draw_struct()
            self.pix_show = self.pix
            return

        self.reset_scale_all()

        style_df = self.style_df[self.style_df['selected'].values]
        for index, row in style_df.iterrows():
            if not row['index_name'] in self.df.columns:
                continue
            data = self.df.loc[:, [row['index_name']]].copy()
            data.dropna(inplace=True)

            if len(data.index) == 0:
                continue
            data = self.config_data(data, row)

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
            self.data_dict[ds.index_name] = ds

            if ds.default_ds is True:
                self.default_ds = ds

        self.draw_pix()

    def config_data(self, data, row):
        index_name = row['index_name']
        if index_name == 'id_141_bs_mc':
            return np.trim_zeros(data.iloc[:, 0]).to_frame()

        if index_name == 'id_145_bs_shbt1sh_tsc_r' or index_name == 'id_146_bs_shbt10sh_tsc_r':
            data = data.loc[data.iloc[:, 0].values != 0, :]
            return data

        if index_name == 'id_211_ps_np':
            data = self.df.loc[:, ['s_003_profit']].copy()
            data.dropna(inplace=True)
            data.columns = [index_name]
            return data

        if index_name == 'id_200_ps_op':
            data = self.df.loc[:, ['s_010_main_profit']].copy()
            data.dropna(inplace=True)
            data.columns = [index_name]
            return data

        if index_name == 'id_157_ps_toi':
            data = self.df.loc[:, ['s_008_revenue']].copy()
            data.dropna(inplace=True)
            data.columns = [index_name]
            return data

        if row['ds_type'] == 'digit':
            if row['frequency'] == 'DAILY':
                return data

            if row['delta_mode'] is True:
                data = get_month_delta(df=data, new_name=index_name)
            else:
                data = get_month_data(df=data, new_name=index_name)

            ma_mode = row['ma_mode']
            if ma_mode > 1:
                data = data.rolling(ma_mode, min_periods=1).mean()

        data.columns = [index_name]
        return data

    def reset_scale_all(self):
        style_df = self.style_df[self.style_df['selected'].values]

        default_row = style_df[style_df['default_ds'].values].iloc[0]
        ratio = get_units_dict()[default_row['units']]

        max0 = self.df[default_row['index_name']].max()

        if np.isnan(max0):
            max0 = self.default_ds.data_max

        scale_max = max0 * self.scale_ratio / ratio
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
        self.pix2 = QPixmap(self.pix)
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
        self.draw_percentage(self.pix2, 'assets')
        self.draw_percentage(self.pix, 'equity')
        for ds in self.data_dict.values():
            if ds.ds_type == 'digit' and ds.data_type is None:
                self.draw_data(ds, self.pix)

    def draw_percentage(self, pix, data_type):
        ds = self.data_dict['id_001_bs_ta']
        df_assets = ds.df.iloc[:, 0].copy()
        df0 = pd.DataFrame(index=df_assets.index)
        p_dict = dict()
        for ds in self.data_dict.values():
            if ds.ds_type == 'digit' and ds.frequency == 'QUARTERLY' and ds.data_type == data_type:
                data = ds.df.iloc[:, 0].copy() / df_assets
                data.name = ds.info_priority
                p_dict[ds.info_priority] = ds
                df0 = pd.concat([df0, data], axis=1)
        df0 = df0.reindex(df_assets.index)
        df0.fillna(0, inplace=True)
        # print(df0)

        val_x = self.x_date_str2value_vector(df_assets.index.values)
        px_x = self.x_value2px_vector(val_x)

        top = self.data_rect.top()
        p_list1 = [QPoint(x, top) for x in px_x]
        percent = np.zeros(df0.index.size)

        c_list = df0.columns.to_list()
        c_list.sort()
        for column in c_list:
            percent = percent + df0[column].values.copy()

            df_point = pd.DataFrame()
            df_point['px_x'] = px_x
            df_point['px_y'] = percent * self.data_rect.height() + self.data_rect.top()

            p_list2 = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]

            p_list1.reverse()
            p_list = p_list1 + p_list2

            # pix = self.pix
            pix_painter = QPainter(pix)

            ds = p_dict[column]
            brush = QBrush(Qt.SolidPattern)
            brush.setColor(ds.color)
            pen = QPen(Qt.red, 0, Qt.NoPen)

            pix_painter.setBrush(brush)
            pix_painter.setPen(pen)

            polygon = QPolygon(p_list)
            pix_painter.drawPolygon(polygon)
            pix_painter.end()
            p_list1 = p_list2

    def draw_data(self, ds: DataSource, pix):
        if ds.df.index.size == 0:
            return
        val_x = self.x_date_str2value_vector(ds.df.index.values)
        px_x = self.x_value2px_vector(val_x)

        # val_x = self.indexes_2_val_x(data.df.index.values)
        # px_x = self.val_x_2_px_x(val_x)

        if ds.ds_type == 'digit':
            data_y = ds.df.iloc[:, 0].values.copy()

            if ds.logarithmic is False:
                # data_y[data_y == 0] = np.nan
                pass
            else:
                px_x[np.isnan(data_y)] = np.nan
                data_y[np.isnan(data_y)] = 0
                data_y[data_y <= 0] = 1e-10

            df_point = pd.DataFrame()
            df_point['px_x'] = px_x
            df_point['px_y'] = self.y_data2px_vector(data_y, ds)
            df_point.dropna(inplace=True)

            point_list = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]

            # draw line
            pix_painter = QPainter(pix)
            pen = QPen(ds.color, ds.line_thick, ds.pen_type)
            pix_painter.setPen(pen)

            if ds.delta_mode is False:
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

        if not self.data_dict:
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

        val = self.y_px2data(y, self.default_ds)
        val_str = self.default_ds.format(val)

        d0 = self.x_px2data(x).strftime("%Y-%m-%d")

        d1 = self.get_last_date(d0, self.dt_mvs.values)
        d_report = self.get_last_date(d0, self.dt_fs.index.values)
        d2 = None if d_report is None else self.dt_fs[d_report]

        px_x0 = x
        px_x2 = x if d2 is None else self.x_data2px(dt.datetime.strptime(d2, "%Y-%m-%d").date())

        if state is True:
            self.draw_mask(px_x0, px_x2)

        # draw cross
        pix_painter = QPainter(self.pix_show)
        pen = QPen(Qt.gray, 1, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))
        pix_painter.end()

        self.draw_tooltip(px_x0, self.data_rect.bottom() + 1, d0)
        self.draw_tooltip(px_x2, self.data_rect.top(), d2)
        self.draw_tooltip(self.data_rect.right() + 1, y, val_str)

        self.draw_information(d1, d2)

    @staticmethod
    def get_last_date(d0, arr):
        res = None
        for date in arr[::-1]:
            if date <= d0:
                res = date
                break

        return res

    def draw_mask(self, px_x0, px_x2):
        if px_x2:
            self.draw_mask_pix(
                pix=self.pix_show,
                x=px_x2,
            )

        for ds in self.data_dict.values():
            if ds.frequency == 'DAILY':
                self.draw_data(ds, self.pix_show)

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

    def draw_information(self, *args):
        box = InformationBox(parent=self)
        pix = box.draw_pix(*args)

        pix_painter = QPainter(self.pix_show)
        pix_painter.drawPixmap(10, 10, pix)
        pix_painter.end()

    # @staticmethod
    # def get_last_value(x, x_list):
    #     if not x_list:
    #         return x
    #
    #     last = None
    #     for px in x_list:
    #         if x < px:
    #             return last
    #         last = px
    #     return last

    # @staticmethod
    # def get_nearest_value(x, x_list):
    #     nearest = None
    #
    #     if len(x_list) > 0:
    #         if x <= x_list[0]:
    #             return x_list[0]
    #         elif x >= x_list[-1]:
    #             return x_list[-1]
    #
    #     px1 = np.inf
    #     for px in x_list:
    #         px2 = px
    #         if px1 <= x < px2:
    #             if (x - px1) <= (px2 - x):
    #                 nearest = px1
    #             else:
    #                 nearest = px2
    #             break
    #         px1 = px
    #     return nearest

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

    ###############################################################################################

    def x_date_str2value_vector(self, array):
        res = np.vectorize(lambda x1: (dt.datetime.strptime(x1, "%Y-%m-%d").date() - self.date_min).days)(array)
        return res

    def x_value2px_vector(self, array):
        res = self.data_rect.x() + array * (self.data_rect.width() - 1) / self.d_date
        return res

    def y_data2px_vector(self, array, data):
        if data.logarithmic is False:
            res = (data.val_max - array) * self.data_rect.height() / data.val_delta + self.data_rect.top()
        else:
            res = (data.val_max - np.log2(array / data.scale_min) / np.log2(
                data.scale_max / data.scale_min)) * self.data_rect.height() / data.val_delta + self.data_rect.top()
        return res

