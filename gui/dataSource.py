from PyQt5.QtCore import *
import numpy as np


class DataSource:
    def __init__(
            self,
            df,
            name=None,
            show_name=None,
            units='None',
            color=Qt.red,
            line_thick=2,
            pen_type=Qt.SolidLine,
            scale_min=2e8,
            scale_max=2048*1e8,
            scale_div=10,
            logarithmic=True,
            info_priority=0,
    ):
        self.df = df
        if name is None:
            self.name = df.columns.tolist()[0]
        else:
            self.name = name

        self.index_name = name
        self.show_name = show_name

        self.units = units

        self.color = color
        self.line_thick = line_thick
        self.pen_type = pen_type

        self.scale_min = scale_min
        self.scale_max = scale_max

        self.scale_div = scale_div
        self.logarithmic = logarithmic
        self.info_priority = info_priority

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        self.format_fun = lambda x: '%i亿' % (x / 1e8)

        self.set_val_scale()

        self.check_logarithmic()

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

    def check_logarithmic(self):
        df = self.df
        column = self.df.columns.tolist()[0]
        print(column)
        if self.logarithmic is True:
            df.loc[df[column] <= 0, column] = None

    @staticmethod
    def copy(data):
        res = DataSource(data.name, data.df)

        res.name = data.name
        res.df = data.df

        res.units = data.units

        res.color = data.color
        res.line_thick = data.line_thick
        res.pen_type = data.pen_type

        res.scale_min = data.scale_min
        res.scale_max = data.scale_max

        res.scale_div = data.scale_div
        res.logarithmic = data.logarithmic

        res.val_max = data.val_max
        res.val_min = data.val_min
        res.val_delta = data.val_delta
        res.metrics = data.metrics

        res.format_fun = data.format_fun

        return res
