from method.sqlMethod import get_data_frame, sql_if_table_exists
from request.requestData import get_cursor
from request.requestData import get_header_df
from request.requestData import request_data2mysql

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime as dt
from dateutil.relativedelta import relativedelta

from scipy.optimize import curve_fit
from functools import wraps


def load_df_from_mysql(stock_code, data_type):
    db, cursor = get_cursor(data_type)

    if data_type == 'fs':
        table = 'fs_%s' % stock_code
        check_field = 'standardDate'
    elif data_type == 'mvs':
        table = 'mvs_%s' % stock_code
        check_field = 'date'
    else:
        return

    flag = sql_if_table_exists(cursor=cursor, table=table)
    if flag:
        sql_df = get_data_frame(cursor=cursor, table=table)
        sql_df = sql_df.set_index(check_field, drop=False)
        # sql_df = sql_df.where(sql_df.notnull(), None)
        sql_df.sort_index(inplace=True)
        sql_df.index = sql_df.index.map(lambda x: x[:10])

        return sql_df
    else:
        header_df = get_header_df(data_type)
        return pd.DataFrame(columns=header_df.columns)


def data_by_dates(df: pd.DataFrame, dates: list):
    res_df = pd.DataFrame(columns=df.columns.tolist())
    date0 = dates[0]

    ps_src = list()
    for tup in df.itertuples():
        if tup[1]:
            if isinstance(tup[1], (int, float)):
                date = dt.datetime.strptime(tup[0], "%Y-%m-%d")
                offset = (date - date0).days
                ps_src.append((offset, tup[1]))

    if len(ps_src) < 2:
        return res_df

    it = iter(ps_src)
    p1 = it.__next__()
    p2 = it.__next__()

    for date in dates:
        x = (date - date0).days
        index = date.strftime("%Y-%m-%d")
        while x > p2[0]:
            try:
                p_tmp = it.__next__()
                p1 = p2
                p2 = p_tmp
            except StopIteration:
                break

        if p1[0] <= x <= p2[0]:
            y = get_y_from_points(x, p1, p2)
            # ps_res.append((x, y))

            res_df.loc[index] = y

    return res_df


def get_y_from_points(x: int, point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    res = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    return res


def get_value_from_ratio(date0, value0, date, ratio_year):
    x = (date - date0).days
    res = value0 * (ratio_year ** (x / 365))
    return res


def get_month_data(df: pd.DataFrame, new_name):
    df = df.dropna()

    date0 = None
    year0 = None
    month0 = None
    index0 = None
    value0 = None

    indexes = list()
    values = list()

    for tup in df.itertuples():
        date = dt.datetime.strptime(tup[0], "%Y-%m-%d")

        if date0:
            year1 = date.year
            month1 = date.month
            value1 = tup[1]

            d_month = (year1 - year0) * 12 + month1 - month0
            d_value = (value1 - value0) / d_month

            indexes.append(index0)
            values.append(value0)

            for m in range(3, d_month, 3):
                date1 = date0 + dt.timedelta(days=1)
                date_tmp = date1 + relativedelta(months=m, days=-1)

                index = date_tmp.strftime("%Y-%m-%d")

                indexes.append(index)
                values.append(value0 + d_value * m)

        date0 = date
        year0 = date.year
        month0 = date.month
        value0 = tup[1]
        index0 = tup[0]

    if index0:
        indexes.append(index0)
        values.append(value0)

    res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    # print(res_df)
    # raise KeyboardInterrupt

    return res_df


def get_month_delta(df: pd.DataFrame, new_name, mode='QUARTERLY'):

    if mode == 'MONTHLY':
        step = 1
    elif mode == 'QUARTERLY':
        step = 3
    else:
        step = 1
    year = None
    month0 = 0
    value0 = 0

    indexes = list()
    values = list()

    for tup in df.itertuples():
        date = dt.datetime.strptime(tup[0], "%Y-%m-%d")
        if not year == date.year:
            month0 = 0
            value0 = 0
        month1 = date.month
        value1 = tup[1]
        year = date.year

        d_value = (value1 - value0) / (month1 - month0)

        for m in range((month0 + step), (month1 + 1), step):
            date1 = dt.date(date.year, m, 1)
            date_tmp = date1 + relativedelta(months=1, days=-1)

            index = date_tmp.strftime("%Y-%m-%d")
            # res_df.loc[index] = d_value * 12

            indexes.append(index)
            values.append(d_value * 12)

        month0 = month1
        value0 = value1

    res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    return res_df


def sql2df(code):
    today = dt.date.today().strftime("%Y-%m-%d")

    df1 = load_df_from_mysql(code, 'fs')
    d0 = '' if df1.shape[0] == 0 else df1.iloc[-1, :]['last_update'][:10]

    # if not d0 == today:
    #     request_data2mysql(
    #         stock_code=code,
    #         data_type='fs',
    #         start_date="2021-04-01",
    #     )
    #     df1 = load_df_from_mysql(code, 'fs')

    df2 = load_df_from_mysql(code, 'mvs')
    d0 = '' if df2.shape[0] == 0 else df2.iloc[-1, :]['last_update'][:10]

    # if not d0 == today:
    #     request_data2mysql(
    #         stock_code=code,
    #         data_type='mvs',
    #         start_date="2021-04-01",
    #         # start_date="1970-01-01",
    #     )
    #     df2 = load_df_from_mysql(code, 'mvs')

    # print(df1)
    # print(df2)
    data = DataAnalysis(df1, df2)
    data.config_widget_data()
    # print(data.df['s_012_return_year'])

    return data.df


def if_column_exist(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        self = args[0]
        df = kwargs.pop('df') if 'df' in kwargs.keys() else args[1]
        column = kwargs.pop('column') if 'column' in kwargs.keys() else args[2]
        if column in df.columns:
            return df[column].copy().dropna()
        else:
            return func(self, df, column)
    return wrapped_function


class DataAnalysis:
    def __init__(self, df_fs: pd.DataFrame, df_mvs: pd.DataFrame):
        self.df_fs = df_fs
        self.df_mvs = df_mvs
        self.df = pd.DataFrame()

    def get_sub_date(self):
        df = self.df_fs
        dt_fs = df['id_001_bs_ta'].copy().dropna()

        res = list()
        sub = list()
        val = np.inf
        for index, value in dt_fs.iteritems():
            if value > 2 * val:
                res.append(sub)
                sub = list()

            sub.append(index)
            val = value

        if len(sub) > 0:
            res.append(sub)

        return res

    def config_sub_fs(self):
        df = self.df_fs.copy()
        sub_list = self.get_sub_date()
        last_date = ''
        df_list = list()
        for sub in sub_list:
            sub_df = df.loc[sub, :].copy()
            sub_data = DataAnalysis(sub_df, None)
            sub_data.config_fs_data()

            sub_data.df_fs = self.get_df_after_date(sub_data.df_fs, last_date)
            df_list.append(sub_data.df_fs)
            last_date = sub_data.df_fs.index.values[-1]

        length = len(df_list)
        if length == 0:
            self.config_fs_data()
        elif length == 1:
            self.df_fs = df_list[0]
        else:
            self.df_fs = pd.concat(df_list)

        return self.df_fs

    def config_fs_data(self):
        df = self.df_fs
        self.fs_add(self.get_column(df, 's_007_asset'))
        self.fs_add(self.get_column(df, 's_002_equity'))
        self.fs_add(self.get_column(df, 's_005_stocks'))

        self.fs_add(self.get_column(df, 's_003_profit'))
        self.fs_add(self.get_column(df, 's_010_main_profit'))
        self.fs_add(self.get_column(df, 's_011_main_profit_rate'))

        self.fs_add(self.get_column(df, 's_001_roe'))
        self.fs_add(self.get_column(df, 's_006_stocks_rate'))

        self.fs_add(self.get_column(df, 's_008_revenue'))
        self.fs_add(self.get_column(df, 's_009_revenue_rate'))

    def config_widget_data(self):
        self.config_sub_fs()
        self.fs_add(self.get_column(self.df_fs, 'dt_fs'))
        self.mvs_add(self.get_column(self.df_mvs, 'dt_mvs'))
        self.mvs_add(self.get_column(self.df_mvs, 's_004_pe'))
        self.mvs_add(self.get_column(self.df_mvs, 's_012_return_year'))
        self.mvs_add(self.get_column(self.df_mvs, 's_014_pe2'))
        self.mvs_add(self.get_column(self.df_mvs, 's_015_return_year2'))
        self.set_df()

    def fs_add(self, new_df):
        self.df_fs = pd.concat([self.df_fs, new_df], axis=1, sort=True)

    def mvs_add(self, new_df):
        self.df_mvs = pd.concat([self.df_mvs, new_df], axis=1, sort=True)

    def set_df(self):
        self.df = pd.merge(
            self.df_fs,
            self.df_mvs,
            how='outer',
            left_index=True,
            right_index=True,
            sort=True,
            suffixes=('_fs', '_mvs'),
            copy=True,
        )

    @staticmethod
    def get_df_after_date(df, date):
        return df.loc[df.index.values > date, :].copy()

    @if_column_exist
    def get_column(self, df, column):
        if column == 'dt_fs':
            dt_fs = df['reportDate'].copy().dropna()
            dict0 = dict()
            for index, value in dt_fs.iteritems():
                dict0[value[:10]] = index

            dt_fs = pd.Series(dict0, name=column)
            dt_fs.sort_index(inplace=True)
            return dt_fs

        elif column == 'dt_mvs':
            index = df['date'].copy().dropna().index.values
            dt_mvs = pd.Series(index, index=index, name=column)
            return dt_mvs

        elif column == 's_001_roe':
            s1 = self.get_column(df, 's_003_profit')
            s2 = self.get_column(df, 's_002_equity')
            s3 = s2 - s1
            s3[s3 <= 0] = np.nan
            s4 = s1 / s3
            s4.dropna(inplace=True)
            s4[s4 <= -50] = np.nan
            s4.name = column
            return s4.dropna(inplace=True)

        elif column == 's_002_equity':
            return self.smooth_data(column, 'id_110_bs_toe')

        elif column == 's_003_profit':
            return self.smooth_data(column, 'id_211_ps_np', delta=True, ttm=True)

        elif column == 's_004_pe':
            s1 = self.fs_to_mvs('tmp', 's_003_profit')
            s2 = self.df_mvs['id_041_mvs_mc'].copy().dropna()
            s3 = s2 / s1
            s3.name = column
            return s3.dropna()

        elif column == 's_005_stocks':
            return self.smooth_data(column, 'id_023_bs_i')

        elif column == 's_006_stocks_rate':
            s1 = self.get_column(df, 's_005_stocks')
            s2 = self.get_column(df, 's_007_asset')
            s3 = s1 / s2
            s3.name = column
            return s3.dropna()

        elif column == 's_007_asset':
            return self.smooth_data(column, 'id_001_bs_ta')

        elif column == 's_008_revenue':
            return self.smooth_data(column, 'id_157_ps_toi', delta=True, ttm=True)

        elif column == 's_009_revenue_rate':
            s1 = self.get_column(df, 's_008_revenue')
            return StandardFitModel.get_growth_rate(s1, column)

        elif column == 's_010_main_profit':
            return self.smooth_data(column, 'id_200_ps_op', delta=True, ttm=True)

        elif column == 's_011_main_profit_rate':
            s1 = self.get_column(df, 's_010_main_profit')
            return StandardFitModel.get_growth_rate(s1, column)

        elif column == 's_012_return_year':
            s1 = self.fs_to_mvs('tmp', 's_009_revenue_rate')
            s2 = self.get_column(df, 's_004_pe')
            s3 = self.get_return_year(s2, s1)
            s3.name = column
            return s3

        elif column == 's_013_noc_asset':
            s1 = self.fs_to_mvs('tmp', 's_003_profit')
            s2 = self.df_mvs['id_041_mvs_mc'].copy().dropna()
            s3 = s2 / s1
            s3.name = column
            return s3.dropna()

        elif column == 's_014_pe2':
            s1 = self.fs_to_mvs('tmp', 's_003_profit')
            s2 = self.df_mvs['id_041_mvs_mc'].copy().dropna()
            s3 = self.fs_to_mvs('tmp', 's_005_stocks')
            s4 = (s2 + s3) / s1
            s4.name = column
            return s4.dropna()

        elif column == 's_015_return_year2':
            s1 = self.fs_to_mvs('tmp', 's_009_revenue_rate')
            s2 = self.get_column(df, 's_014_pe2')
            s3 = self.get_return_year(s2, s1)
            s3.name = column
            return s3

    @staticmethod
    def get_return_year(pe, rate):
        a = 1 + rate
        b = (rate / (1 + rate) * pe + 1)

        a[a <= 0] = np.nan
        b.dropna(inplace=True)
        b[b <= 0] = np.nan

        y = np.log(b) / np.log(a)
        return y.dropna()

    def fs_to_mvs(self, name, src):
        dt_fs = self.get_column(self.df_fs, 'dt_fs')
        dt_mvs = self.get_column(self.df_mvs, 'dt_mvs')

        data = self.get_column(self.df_fs, src)
        data = data.reindex_like(pd.Series(index=dt_fs.values))
        data.fillna(np.inf, inplace=True)
        data.index = dt_fs.index

        index = pd.concat([dt_mvs, data], axis=1, sort=True).index
        data = data.reindex_like(pd.Series(index=index))

        data.fillna(method='ffill', inplace=True)
        data[data == np.inf] = np.nan
        data = data[dt_mvs.values]
        data.name = name
        return data

    def smooth_data(self, name, src, delta=False, ttm=False, df=None):
        if df is None:
            df = self.df_fs

        src_df = df.loc[:, [src]].copy().dropna()
        if delta is False:
            new_df = get_month_data(src_df, name)
        else:
            new_df = get_month_delta(src_df, name)
            if ttm is True:
                new_df = new_df.rolling(4, min_periods=1).mean()
        return new_df[name]

    @staticmethod
    def return_df(df, new_df, add=False):
        if add is False:
            return new_df
        else:
            return pd.concat([df, new_df], axis=1, sort=True)


class StandardFitModel:
    @classmethod
    def get_growth_rate(cls, series, name):
        data = series
        data[data <= 0] = np.nan
        data3 = data.rolling(12, min_periods=1).apply(cls.window_method, raw=True)
        data4 = np.exp(data3) - 1
        data4.name = name
        return data4

    @classmethod
    def window_method(cls, arr_y):
        arr_y = cls.config_window_array(arr_y)
        if arr_y is None:
            return 0
        delta = cls.curve_fit(arr_y) * 4
        return delta

    @classmethod
    def config_window_array(cls, arr_y):
        tmp = np.where(np.isnan(arr_y))[0]
        if tmp.size > 0:
            index = tmp[-1] + 1
            arr_y = arr_y[index:]

        if arr_y.size == 0:
            return None

        size = 12
        pre = np.ones(size - arr_y.size) * arr_y[0]
        arr_y = np.append(pre, arr_y)

        return arr_y

    @classmethod
    def curve_fit(cls, arr_y):
        arr_x = np.arange(0, arr_y.size, 1)
        popt, pcov = curve_fit(cls.curve_func, arr_x, arr_y)
        return popt[0]

    @staticmethod
    def curve_func(x, a, b):
        return np.exp(a * x + b)


if __name__ == '__main__':
    # # sql2df('000002')
    # str2 = "from __main__ import sql2df_mvs"
    # t0 = timeit.Timer("sql2df_mvs('000004')", str2)
    # print(t0.timeit(10))

    # combine_style_df()
    #
    # res = sql2df('600006')
    # print(res)
    pass
