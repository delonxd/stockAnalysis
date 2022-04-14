from method.dataMethod import get_value_from_ratio
from method.mainMethod import get_units_dict
from gui.dataSource import DataSource
from gui.dataSource import DefaultDataSource
from gui.informationBox import InformationBox
from method.dataMethod import get_month_delta
from method.dataMethod import get_month_data

from method.dataMethod import sql2df
from gui.styleDataFrame import load_default_style

from dateutil.rrule import *
from collections import defaultdict

import datetime as dt
import numpy as np
import pandas as pd


from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DataPix:
    def __init__(self, code, style_df: pd.DataFrame, df=None, ratio=None):
        self.code = code

        self.df = pd.DataFrame()
        self.load_df(df)

        # structure
        self.m_width = 1600
        self.m_height = 900

        self.d_width = d_width = 1400
        self.d_height = d_height = 700

        left_blank = 130
        right_blank = 80
        bottom_blank = 50

        self.main_rect = QRect(0, 0, self.m_width, self.m_height)
        self.data_rect = QRect(left_blank, 100, d_width, d_height)

        # pix
        self.pix = QPixmap(self.m_width, self.m_height)
        self.pix2 = QPixmap(self.pix)
        self.pix3 = QPixmap(self.pix)
        self.pix4 = QPixmap(self.pix)
        self.pix_show = QPixmap(self.pix)
        self.struct_pix = QPixmap(self.pix)
        self.pix_list = [self.pix, self.pix2, self.pix3, self.pix4]

        # date metrics
        self.date_max = dt.date(2023, 7, 20)
        self.date_min = dt.date(1997, 7, 20)
        self.d_date = (self.date_max - self.date_min).days

        self.date_metrics1 = self.get_date_list('INTERIM')
        self.date_metrics2 = self.get_date_list('YEARLY')

        # self.date_list = self.get_date_list('MONTHLY')
        self.date_list = self.get_date_list('QUARTERLY')

        self.data_dict = None
        self.default_ds = None

        self.dt_fs = pd.Series()
        self.dt_mvs = pd.Series()

        # self.scale_ratio = 4
        self.scale_ratio = 16 if ratio is None else ratio

        self.update_pix(style_df)

    def load_df(self, df):
        if df is None:
            self.df = sql2df(self.code)
        else:
            self.df = df

    def update_pix(self, style_df):
        if style_df.shape[0] == 0:
            return

        self.dt_fs = self.df['dt_fs'].copy().dropna()
        self.dt_mvs = self.df['dt_mvs'].copy().dropna()

        self.data_dict = dict()
        self.default_ds = DefaultDataSource(parent=self)

        if len(self.df.index) == 0:
            self.init_pix()
            self.draw_struct()
            self.pix_show = self.pix
            return

        style_df = style_df[style_df['selected'].values]
        d_min, d_max = self.reset_scale_all(style_df)

        for index, row in style_df.iterrows():
            if not row['index_name'] in self.df.columns:
                continue
            data = self.df.loc[:, [row['index_name']]].copy()
            data.dropna(inplace=True)

            if len(data.index) == 0:
                continue
            data = self.config_data(data, row)

            scale_min, scale_max = row[['scale_min', 'scale_max']]
            scale_min = d_min if scale_min == 'auto' else scale_min
            scale_max = d_max if scale_max == 'auto' else scale_max

            ds = DataSource(
                parent=self,
                df=data,
                index_name=row['index_name'],
                show_name=row['show_name'],
                color=row['color'],
                line_thick=row['line_thick'],
                pen_type=row['pen_style'],
                scale_min=scale_min,
                scale_max=scale_max,
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

        config_name = 'config_' + index_name

        if config_name in self.df.columns:
            data = self.df.loc[:, [config_name]].copy()
            data.dropna(inplace=True)
            data.columns = [index_name]
            return data

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

        if index_name == 'id_217_ps_npatoshopc':
            data = self.df.loc[:, ['s_018_profit_parent']].copy()
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

        tmp_list = [
            's_022_profit_no_expenditure',
            's_038_pay_for_long_term_asset',
            's_039_profit_adjust',
            's_040_profit_adjust2',
            's_041_profit_adjust_ttm',
        ]

        if index_name in tmp_list:
            data = self.df.loc[:, [index_name]].copy()
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

    def reset_scale_all(self, style_df):
        # style_df = self.style_df[self.style_df['selected'].values]

        default_row = style_df[style_df['default_ds'].values].iloc[0]
        ratio = get_units_dict()[default_row['units']]

        max0 = self.df[default_row['index_name']].max()

        if np.isnan(max0):
            max0 = self.default_ds.data_max

        scale_max = max0 * self.scale_ratio / ratio
        scale_min = scale_max / 1024

        return scale_min, scale_max

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
        self.pix3 = QPixmap(self.pix)
        self.pix4 = QPixmap(self.pix)

        self.draw_data_dict()

        self.pix_show = self.pix
        self.pix_list = [self.pix, self.pix2, self.pix3, self.pix4]

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
        pen3 = QPen(Qt.yellow, 1, Qt.DotLine)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()

        val_list = [x / 10 for x in range(1, 10)]

        counter = 1
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

            if counter == 3:
                pix_painter.setPen(pen3)
            else:
                pix_painter.setPen(pen2)
            pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))

            counter += 1

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

        # 20% 辅助线
        ratio_year = 1.2
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
        tmp_dict = {
            's_022_profit_no_expenditure': '股东盈余',
            's_025_real_cost': '真实成本',
            'id_041_mvs_mc': '市值',
            'id_217_ps_npatoshopc': '归母净利润',
            's_018_profit_parent': '归母净利润',
            'id_124_bs_tetoshopc': '归母股东权益',
            's_017_equity_parent': '归母股东权益',
            'id_001_bs_ta': '资产合计',
            's_020_cap_asset': '资本化资产',
            'id_261_cfs_ncffoa': '经营现金流净额',
            's_026_holder_return_rate': '股东回报率',
            's_027_pe_return_rate': 'pe回报率',
            'id_341_m_gp_m': '毛利率',
            'id_157_ps_toi': '主营收入',
            's_009_revenue_rate': '主营收入增速',
            's_029_return_predict': '预测回报率',
            's_016_roe_parent': 'roe',
            's_032_remain_rate': '资金留存率',
            'mir_y10': '十年期国债利率',
            's_004_pe': 'pe',
            's_034_real_pe': 'real_pe',
            's_035_pe2rate': 's_035_pe2rate',
            's_036_real_pe2rate': 's_036_real_pe2rate',

            's_038_pay_for_long_term_asset': 's_038_pay_for_long_term_asset',
            's_039_profit_adjust': 's_039_profit_adjust',
            's_040_profit_adjust2': 's_040_profit_adjust2',
            's_041_profit_adjust_ttm': 's_041_profit_adjust_ttm',
        }

        tmp_list = list(tmp_dict.keys())

        self.draw_percentage(self.pix2, 'assets')
        self.draw_percentage(self.pix, 'equity')

        for ds in self.data_dict.values():
            if ds.ds_type == 'digit' and ds.data_type is None:
                self.draw_data(ds, self.pix)
                self.draw_data(ds, self.pix3)

            if ds.index_name in tmp_list:
                self.draw_data(ds, self.pix4)

    def draw_percentage(self, pix, data_type):
        if 'id_001_bs_ta' not in self.data_dict.keys():
            return
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

            try:
                point_list = [QPoint(tup[1], tup[2]) for tup in df_point.itertuples()]
            except Exception as e:
                print(df_point)
                print(e)

            if ds.frequency == 'DAILY':
                if point_list:
                    x = point_list[-1].x() + 30
                    y = point_list[-1].y()
                    point_list.append(QPoint(x, y))

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
        if x is None and y is None:
            return

        if not self.data_dict:
            return

        if self.df.shape[0] == 0:
            return

        x, y, d0, d1, d2, d_report = self.get_d1_d2(x, y)
        box = InformationBox(parent=self)
        box = box.draw_pix(d1, d2, d_report)

        thick = 3 if state is True else 1
        show1 = self.draw_sub_cross(x, y, d0, d1, d2, state, thick, box[0], self.pix)
        show2 = self.draw_sub_cross(x, y, d0, d1, d2, False, thick, box[1], self.pix2)
        show3 = self.draw_sub_cross(x, y, d0, d1, d2, False, thick, box[2], self.pix3)
        show4 = self.draw_sub_cross(x, y, d0, d1, d2, False, thick, box[2], self.pix4)

        self.pix_list = [show1, show2, show3, show4]

    def get_d1_d2(self, x, y):

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

        d0 = self.x_px2data(x).strftime("%Y-%m-%d")

        d1 = self.get_last_date(d0, self.dt_mvs.values)
        d_report = self.get_last_date(d0, self.dt_fs.index.values)
        d2 = None if d_report is None else self.dt_fs[d_report]

        return x, y, d0, d1, d2, d_report

    def draw_sub_cross(self, x, y, d0, d1, d2, state, thick, box, pix):

        pix_show = QPixmap(pix)

        d_left = self.data_rect.left()
        d_right = self.data_rect.right()
        d_top = self.data_rect.top()
        d_bottom = self.data_rect.bottom() + 1

        val = self.y_px2data(y, self.default_ds)
        val_str = self.default_ds.format(val)

        px_x0 = x
        px_x2 = x if d2 is None else self.x_data2px(dt.datetime.strptime(d2, "%Y-%m-%d").date())

        if state is True:
            self.draw_mask(px_x0, px_x2, pix_show)

        # draw cross
        pix_painter = QPainter(pix_show)
        pen = QPen(Qt.gray, thick, Qt.SolidLine)
        pix_painter.setPen(pen)

        pix_painter.drawLine(QPoint(x, d_top), QPoint(x, d_bottom))
        pix_painter.drawLine(QPoint(d_left, y), QPoint(d_right, y))
        pix_painter.end()

        self.draw_tooltip(px_x0, self.data_rect.bottom() + 1, d0, pix_show)
        self.draw_tooltip(px_x2, self.data_rect.top(), d2, pix_show)
        self.draw_tooltip(self.data_rect.right() + 1, y, val_str, pix_show)

        # self.draw_information(d1, d2, pix_show)

        pix_painter = QPainter(pix_show)
        pix_painter.drawPixmap(10, 10, box)
        pix_painter.end()

        return pix_show

    @staticmethod
    def get_last_date(d0, arr):
        res = None
        for date in arr[::-1]:
            if date <= d0:
                res = date
                break

        return res

    def draw_mask(self, px_x0, px_x2, pix):
        if px_x2:
            self.draw_mask_pix(
                pix=pix,
                x=px_x2,
            )

        for ds in self.data_dict.values():
            if ds.frequency == 'DAILY':
                self.draw_data(ds, pix)

        self.draw_mask_pix(
            pix=pix,
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

    @staticmethod
    def draw_tooltip(x, y, text, pix):
        pix_painter = QPainter(pix)
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

    # def draw_information(self, *args):
    #     box = InformationBox(parent=self)
    #     pix = box.draw_pix(*args)
    #
    #     pix_painter = QPainter(self.pix_show)
    #     pix_painter.drawPixmap(10, 10, pix)
    #     pix_painter.end()

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

