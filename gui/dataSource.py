from PyQt5.QtCore import *
from method.mainMethod import get_units_dict
from method.dataMethod import *
import numpy as np
import time


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
    ):

        self.parent = parent

        self.default_ds = default_ds

        self.index_name = index_name
        self.show_name = show_name

        # if index_name == 'id_145_bs_shbt1sh_tsc_r':
        #     print('>>>>>>>>>>>>>>>')
        #     print(df.values)

        self.df = df
        self.ds_type = ds_type
        self.delta_mode = delta_mode

        self.format_data_source()

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
        #         # todo: 优化遍历

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
            self.check_logarithmic()
        else:
            self.format_fun = lambda x: '%s' % x

        self.set_val_scale()

        self.df.columns = [index_name]

        # self.df.fillna(value=np.nan)
        # self.df.fillna(value=None)

        # try:
        #     self.df[self.df[index_name].values is None, index_name] = np.nan
        # except Exception as e:
        #     print(self.df)
        #     print(self.df.columns)
        #     raise KeyboardInterrupt(e)

    # def get_last_data_ratio(self):
    #     value = self.df.iloc[-1, 0]
    #     # print(value)
    #     return value

    def format(self, value):
        if value is None:
            return 'None'
        else:
            try:
                return self.format_fun(value)
            except Exception:
                return repr(value)

    def set_val_scale(self):
        # if self.scale_max == 0 or self.scale_min == 0:
        #     self.logarithmic = False
        #     self.parent.style_df.loc[self.index_name, 'logarithmic'] = self.logarithmic

        if self.logarithmic is True:
            self.val_max = 1
            self.val_min = 0
        else:
            self.val_max = self.scale_max
            self.val_min = self.scale_min

        self.val_delta = self.val_max - self.val_min
        self.metrics = list(np.linspace(self.val_min, self.val_max, self.scale_div+1))
        self.metrics = self.metrics[1:-1]

    def check_logarithmic(self):
        # df = self.df
        # column = self.df.columns.tolist()[0]
        if self.logarithmic is True:
            # self.df = df.where(df[column] > 0, None)
            # self.df = df.where(df > 0, None)
            # self.df = self.df.where(self.df > 0, None)
            # self.df = self.df.where(self.df > 0, np.inf)
            pass

            # todo：optimize check_logarithmic()

    def format_data_source(self):
        date_list = self.parent.date_list
        if self.ds_type == 'digit':
            # print(7, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

            if self.delta_mode is True:
                self.df = get_mouth_delta(df=self.df, new_name=self.index_name)
            else:
                # self.df = data_by_dates(self.df, date_list)
                pass
            # print(7, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    @staticmethod
    def copy(data):
        # todo: copy dataSource

        pass
