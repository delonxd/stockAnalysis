from method.mainMethod import get_units_dict
from method.dataMethod import get_month_delta
from method.dataMethod import get_month_data

import pandas as pd
import numpy as np
import datetime as dt


class DataSource:
    def __init__(
            self,
            parent,
            df,

            index_name,
            show_name,

            color,
            line_thick,
            pen_type,

            scale_min,
            scale_max,
            scale_div,
            logarithmic,
            units,

            info_priority,

            ds_type,
            delta_mode,
            default_ds,

            ma_mode,
            frequency,
    ):

        self.parent = parent

        self.default_ds = default_ds

        self.index_name = index_name
        self.show_name = show_name

        # if index_name == 'id_141_bs_mc':
        #     df = np.trim_zeros(df.iloc[:, 0]).to_frame()

        self.df = df

        self.ds_type = ds_type
        self.delta_mode = delta_mode
        self.ma_mode = ma_mode
        self.frequency = frequency

        # self.format_data_source()

        self.color = color
        self.line_thick = line_thick
        self.pen_type = pen_type

        # if self.ds_type == 'digit':
        #     series = self.df.iloc[:, 0]
        #     d_max = series.max()
        #     d_min = series.min()
        #     if 0 <= d_min <= 1 and 0 <= d_max <= 1:
        #         scale_max = 100
        #         scale_min = 0
        #         units = '%'
        #         logarithmic = False
        #
        #         self.parent.style_df.loc[index_name, 'scale_min'] = scale_min
        #         self.parent.style_df.loc[index_name, 'scale_max'] = scale_max
        #         self.parent.style_df.loc[index_name, 'units'] = units
        #         self.parent.style_df.loc[index_name, 'logarithmic'] = logarithmic
        #

        self.units = units
        self.ratio = get_units_dict()[units]
        self.scale_min = scale_min * self.ratio
        self.scale_max = scale_max * self.ratio

        self.scale_div = scale_div
        self.logarithmic = logarithmic

        self.info_priority = info_priority

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        if self.ds_type == 'digit':
            self.format_fun = lambda x: '%.2f%s' % (x / self.ratio, units)
        else:
            self.format_fun = lambda x: '%s' % x

        self.set_val_scale()
        self.df.columns = [index_name]

        # self.offsets = None
        # self.init_offsets()

    def format(self, value):
        if value is None:
            return 'None'
        else:
            try:
                return self.format_fun(value)
            except Exception as e:
                print(e)
                return repr(value)

    def set_val_scale(self):
        if self.logarithmic is True:
            self.val_max = 1
            self.val_min = 0
        else:
            self.val_max = self.scale_max
            self.val_min = self.scale_min

        self.val_delta = self.val_max - self.val_min
        self.metrics = list(np.linspace(self.val_min, self.val_max, self.scale_div+1))
        self.metrics = self.metrics[1:-1]

    def format_data_source(self):
        pass
        # if self.ds_type == 'digit':
        #     if self.frequency == 'DAILY':
        #         return
        #
        #     if self.delta_mode is True:
        #         self.df = get_month_delta(df=self.df, new_name=self.index_name)
        #     else:
        #         self.df = get_month_data(df=self.df, new_name=self.index_name)
        #
        #     if self.ma_mode > 1:
        #         # array0 = self.df.iloc[:, 0].values.copy()
        #         #
        #         # first = self.ma_mode - 1
        #         # array1 = array0[first:]
        #         #
        #         # last = 0
        #         # while first:
        #         #     first -= 1
        #         #     last -= 1
        #         #     array1 = array1 + array0[first:last].copy()
        #         #
        #         # array1 = array1 / self.ma_mode
        #         # # print('array1', array1)
        #         # indexes = self.df.index.values[(self.ma_mode - 1):]
        #         #
        #         # self.df = pd.DataFrame(array1, index=indexes, columns=[self.index_name])
        #
        #         # self.df = self.df.rolling(self.ma_mode, min_periods=1).sum()
        #         self.df = self.df.rolling(self.ma_mode, min_periods=1).mean()

    def init_offsets(self):
        if self.frequency == 'DAILY':
            self.offsets = np.zeros(self.df.index.values.shape[0], dtype='int32')
            date0 = self.parent.date_min
            for i, index in enumerate(self.df.index.values):
                date = dt.datetime.strptime(index, "%Y-%m-%d").date()
                offset = (date - date0).days
                self.offsets[i] = offset

    @staticmethod
    def index2date(index):
        return dt.datetime.strptime(index, "%Y-%m-%d").date()

    def map_indexes2date(self):
        return map(self.index2date, self.df.index)
        # date_list = list()
        # for index in self.df.index:
        #     date = dt.datetime.strptime(index, "%Y-%m-%d").date()
        #     date_list.append(date)
        #
        # self.date_list = date_list

    @staticmethod
    def copy(data):
        pass


class DefaultDataSource(DataSource):
    def __init__(self, parent):
        self.parent = parent

        self.default_ds = True

        self.index_name = 'DefaultDataSource'
        self.show_name = 'DefaultDataSource'

        self.df = pd.DataFrame(columns=[self.index_name])

        index = dt.datetime.now().date().strftime("%Y-%m-%d")

        self.data_max = 256 * 1e8
        self.df.loc[index] = [self.data_max]

        self.ds_type = 'digit'
        self.delta_mode = False
        self.ma_mode = 0
        self.frequency = None

        self.format_data_source()

        self.color = None
        self.line_thick = None
        self.pen_type = None

        self.units = '亿'
        self.ratio = get_units_dict()[self.units]

        self.scale_max = self.data_max * parent.scale_ratio
        self.scale_min = self.scale_max / 1024

        self.scale_div = 10
        self.logarithmic = True

        self.info_priority = 0

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        self.set_val_scale()

        self.format_fun = lambda x: '%.2f%s' % (x / self.ratio, self.units)

        self.df.columns = [self.index_name]
        self.offsets = None
