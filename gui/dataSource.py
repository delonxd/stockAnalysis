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

            ma_mode,
    ):

        # self.parent = parent

        self.default_ds = default_ds

        self.index_name = index_name
        self.show_name = show_name

        self.df = df
        self.ds_type = ds_type
        self.delta_mode = delta_mode
        self.ma_mode = ma_mode

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

    def format(self, value):
        if value is None:
            return 'None'
        else:
            try:
                return self.format_fun(value)
            except Exception:
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
        if self.ds_type == 'digit':
            if self.delta_mode is True:
                self.df = get_month_delta(df=self.df, new_name=self.index_name)
            else:
                self.df = get_month_data(df=self.df, new_name=self.index_name)

            if self.ma_mode > 1:
                array0 = self.df.iloc[:, 0].values.copy()

                first = self.ma_mode - 1
                array1 = array0[first:]

                last = 0
                while first:
                    first -= 1
                    last -= 1
                    array1 = array1 + array0[first:last].copy()

                array1 = array1 / self.ma_mode
                # print('array1', array1)
                indexes = self.df.index.values[(self.ma_mode - 1):]

                self.df = pd.DataFrame(array1, index=indexes, columns=[self.index_name])

    @staticmethod
    def copy(data):
        # todo: copy dataSource

        pass
