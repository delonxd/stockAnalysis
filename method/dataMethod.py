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

    data = DataAnalysis(df1, df2)
    data.config_widget_data()
    return data.df


class DataAnalysis:
    def __init__(self, df_fs: pd.DataFrame, df_mvs: pd.DataFrame):
        self.df_fs = df_fs

        # self.get_df_after_date(self.df_fs, '2010-01-01')
        self.df_mvs = df_mvs
        self.df = pd.DataFrame()

    def config_widget_data(self):
        self.config_sub_fs()

        self.df_fs = self.get_dt_fs(add=True)
        self.df_mvs = self.get_dt_mvs(add=True)
        self.df_mvs = self.get_last_report(add=True)

        # self.df_fs = self.get_asset(add=True)
        # self.df_fs = self.get_equity(add=True)
        # self.df_fs = self.get_stocks(add=True)
        # self.df_fs = self.get_profit(add=True)
        #
        # self.df_fs = self.get_roe(add=True)
        # self.df_fs = self.get_stocks_rate(add=True)
        #
        # self.df_fs = self.get_revenue(add=True)
        # self.df_fs = self.get_revenue_rate(add=True)

        # self.config_fs_data()

        self.df_mvs = self.get_pe(add=True)
        self.set_df()

    def config_sub_fs(self, inplace=True):
        df = self.df_fs.copy()
        sub_list = self.get_sub_date()
        last_date = ''
        df_list = list()
        for sub in sub_list:
            sub_df = df.loc[sub, :].copy()
            sub_data = SubDataAnalysis(sub_df)
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
        self.df_fs = self.get_asset(add=True)
        self.df_fs = self.get_equity(add=True)
        self.df_fs = self.get_stocks(add=True)
        self.df_fs = self.get_profit(add=True)
        self.df_fs = self.get_main_profit(add=True)

        self.df_fs = self.get_roe(add=True)
        self.df_fs = self.get_stocks_rate(add=True)

        self.df_fs = self.get_revenue(add=True)
        self.df_fs = self.get_revenue_rate(add=True)

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

    @staticmethod
    def get_df_after_date(df, date):
        df = df.copy()
        new_df = df.loc[df.index.values > date, :]
        return new_df

    def get_dt_fs(self, add=False):
        df = self.df_fs
        name = 'dt_fs'

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            dt_fs = df['reportDate'].copy().dropna()
            dict0 = dict()
            for index, value in dt_fs.iteritems():
                dict0[value[:10]] = index

            dt_fs = pd.Series(dict0, name=name)
            dt_fs.sort_index(inplace=True)
            new_df = pd.DataFrame(dt_fs)
            return self.return_df(df, new_df, add=add)

    def get_dt_mvs(self, add=False):
        df = self.df_mvs
        name = 'dt_mvs'

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            dt_mvs = df['date'].copy().dropna()
            new_df = pd.DataFrame(dt_mvs.index.values, index=dt_mvs.index, columns=[name])
            return self.return_df(df, new_df, add=add)

    def get_last_report(self, add=False):
        df = self.df_mvs
        name = 'last_report'

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            dt_mvs = self.get_dt_mvs()
            dt_fs = self.get_dt_fs()

            dict0 = dt_fs.iloc[:, 0].to_dict()
            it = iter(dt_fs.index.values[::-1])

            last_report = pd.Series(index=dt_mvs.index, name=name)

            d0 = 'a'
            dates = dt_mvs.index.values[::-1]
            index = dates.size
            for date in dates:
                index -= 1
                while date < d0:
                    try:
                        d0 = it.__next__()
                    except StopIteration:
                        break
                if d0 == 'a':
                    break
                last_report.iloc[index] = dict0[d0]

            new_df = pd.DataFrame(last_report)
            return self.return_df(df, new_df, add=add)

    def get_equity(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_110_bs_toe',
            name='s_002_equity',
            add=add,
            delta=False,
        )
        return res

    def get_profit(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_211_ps_np',
            name='s_003_profit',
            add=add,
            delta=True,
            ttm=True,
        )
        return res

    def get_main_profit(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_200_ps_op',
            name='s_010_main_profit',
            add=add,
            delta=True,
            ttm=True,
        )
        return res

    def get_stocks(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_023_bs_i',
            name='s_005_stocks',
            add=add,
            delta=False,
        )
        return res

    def get_asset(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_001_bs_ta',
            name='s_007_asset',
            add=add,
            delta=False,
        )
        return res

    def get_revenue(self, add=False):
        res = self.get_smooth_data(
            df=self.df_fs,
            src='id_157_ps_toi',
            name='s_008_revenue',
            add=add,
            delta=True,
            ttm=True,
        )
        return res

    def get_revenue_rate(self, add=False):
        name = 's_009_revenue_rate'
        df = self.df_fs
        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            df1 = self.get_revenue()
            new_df = StandardFitModel.get_growth_rate(df1, name)
            return self.return_df(df, new_df, add=add)

    def get_roe(self, add=False):
        name = 's_001_roe'
        df = self.df_fs

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            df1 = self.get_profit()
            df2 = self.get_equity()

            con = pd.concat([df1, df2], axis=1, sort=True, join='inner')

            a = con[df1.columns[0]].values
            b = con[df2.columns[0]].values
            c = b - a
            c[c <= 0] = np.nan
            d = a / c

            if d.size > 0:
                d[np.isnan(d)] = -np.inf
                d[d <= -50] = -np.inf
                d[d == -np.inf] = np.nan

            con[name] = np.around(d, decimals=2)
            new_df = con.loc[:, [name]].copy()
            return self.return_df(df, new_df, add=add)

    def get_pe(self, add=False):
        name = 's_004_pe'
        df = self.df_mvs

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            s1 = df['id_041_mvs_mc'].copy().dropna()
            s2 = self.get_profit().iloc[:, 0]
            last_report = self.get_last_report().iloc[:, 0]

            new = pd.Series(index=last_report.index, name=name)
            counter = 0
            for index, value in last_report.iteritems():
                try:
                    a = s1[index]
                except Exception as e:
                    # print(e)
                    a = np.nan
                try:
                    b = s2[value]
                except Exception as e:
                    # print(e)
                    b = np.nan

                new[counter] = a / b
                counter += 1
            new_df = pd.DataFrame(new)

            return self.return_df(df, new_df, add=add)

    def get_stocks_rate(self, add=False):
        name = 's_006_stocks_rate'
        df = self.df_fs

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            df1 = self.get_stocks()
            df2 = self.get_asset()

            con = pd.concat([df1, df2], axis=1, sort=True, join='inner')

            a = con[df1.columns[0]].values
            b = con[df2.columns[0]].values

            con[name] = a / b
            new_df = con.loc[:, [name]].copy()

            return self.return_df(df, new_df, add=add)

    def get_smooth_data(self, df, src, name, add=False, delta=False, ttm=False):
        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            new_df = df.loc[:, [src]].copy().dropna()
            if delta is False:
                new_df = get_month_data(new_df, name)
            else:
                new_df = get_month_delta(new_df, name)
                if ttm is True:
                    new_df = new_df.rolling(4, min_periods=1).mean()
            return self.return_df(df, new_df, add=add)

    @staticmethod
    def return_df(df, new_df, add=False):
        if add is False:
            return new_df
        else:
            return pd.concat([df, new_df], axis=1, sort=True)

    # def get_growth_rate(self, df, name):
    #     data = df
    #     data[data <= 0] = np.nan
    #     data3 = data.rolling(12, min_periods=1).apply(self.window_method, raw=True)
    #     data4 = np.exp(data3) - 1
    #
    #     data4.columns = [name]
    #
    #     # arr_y = data2.iloc[:, 0].values
    #     # arr_y2 = data4.iloc[:, 0].values
    #     # arr_x = np.arange(0, arr_y.size, 1)
    #     #
    #     # plt.plot(arr_x, arr_y, 'b-', label='data2')
    #     # plt.plot(arr_x, arr_y2, 'r', label='data4')
    #     #
    #     # plt.xlabel('x axis')
    #     # plt.ylabel('y axis')
    #     #
    #     # plt.title('curve_fit')
    #     # plt.show()
    #
    #     return data4
    #
    # def window_method(self, arr_y):
    #     # arr_y[arr_y <= 0] = np.nan
    #     tmp = np.where(np.isnan(arr_y))[0]
    #     if tmp.size > 0:
    #         index = tmp[-1] + 1
    #         arr_y = arr_y[index:]
    #
    #     if arr_y.size == 0:
    #         return 0
    #
    #     size = 12
    #     pre = np.ones(size - arr_y.size) * arr_y[0]
    #     arr_y = np.append(pre, arr_y)
    #
    #     # delta = self.potential_rate(arr_y) * 4
    #     delta = self.curve_fit1(arr_y) * 4
    #     return delta
    #
    # # @staticmethod
    # # def potential_rate(arr_y):
    # #     arr_x = np.arange(0, arr_y.size, 1)
    # #     p = np.polyfit(arr_x, arr_y, 1)
    # #     rate = p[0]
    # #
    # #     return rate
    #
    # def curve_fit1(self, arr_y):
    #     arr_x = np.arange(0, arr_y.size, 1)
    #     popt, pcov = curve_fit(self.curve_func, arr_x, arr_y)
    #     return popt[0]
    #
    # @staticmethod
    # def curve_func(x, a, b):
    #     return np.exp(a * x + b)


class DataAnalysis2:
    def __init__(self, df_fs: pd.DataFrame, df_mvs: pd.DataFrame):
        self.df_fs = df_fs

        # self.get_df_after_date(self.df_fs, '2010-01-01')
        self.df_mvs = df_mvs
        self.df = pd.DataFrame()

    def config_widget_data(self):
        self.config_sub_fs()

        self.df_fs = self.get_dt_fs(add=True)
        self.df_mvs = self.get_dt_mvs(add=True)
        self.df_mvs = self.get_last_report(add=True)

        # self.df_fs = self.get_asset(add=True)
        # self.df_fs = self.get_equity(add=True)
        # self.df_fs = self.get_stocks(add=True)
        # self.df_fs = self.get_profit(add=True)
        #
        # self.df_fs = self.get_roe(add=True)
        # self.df_fs = self.get_stocks_rate(add=True)
        #
        # self.df_fs = self.get_revenue(add=True)
        # self.df_fs = self.get_revenue_rate(add=True)

        # self.config_fs_data()

        self.df_mvs = self.get_pe(add=True)
        self.set_df()

    def config_sub_fs(self, inplace=True):
        df = self.df_fs.copy()
        sub_list = self.get_sub_date()
        last_date = ''
        df_list = list()
        for sub in sub_list:
            sub_df = df.loc[sub, :].copy()
            sub_data = SubDataAnalysis(sub_df)
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
        self.df_fs = self.get_asset(add=True)
        self.df_fs = self.get_equity(add=True)
        self.df_fs = self.get_stocks(add=True)
        self.df_fs = self.get_profit(add=True)
        self.df_fs = self.get_main_profit(add=True)

        self.df_fs = self.get_roe(add=True)
        self.df_fs = self.get_stocks_rate(add=True)

        self.df_fs = self.get_revenue(add=True)
        self.df_fs = self.get_revenue_rate(add=True)

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

    @staticmethod
    def get_df_after_date(df, date):
        return df.loc[df.index.values > date, :].copy()

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
            dt_mvs = df['date'].copy().dropna()
            dt_mvs.name = column
            return dt_mvs

        elif column == 'last_report':
            dt_fs = self.get_column(self.df_fs, 'dt_fs')
            dt_mvs = self.get_column(self.df_mvs, 'dt_mvs')

            dict0 = dt_fs.to_dict()
            it = iter(dt_fs.index.values[::-1])

            last_report = pd.Series(index=dt_mvs.index, name=column)

            d0 = 'a'
            dates = dt_mvs.index.values[::-1]
            index = dates.size
            for date in dates:
                index -= 1
                while date < d0:
                    try:
                        d0 = it.__next__()
                    except StopIteration:
                        break
                if d0 == 'a':
                    break
                last_report.iloc[index] = dict0[d0]

            return last_report

        elif column == 's_001_roe':
            s1 = self.get_column(self.df_fs, 's_003_profit')
            s2 = self.get_column(self.df_fs, 's_002_equity')
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
            return 0

        elif column == 's_005_stocks':
            return self.smooth_data(column, 'id_023_bs_i')

        elif column == 's_006_stocks_rate':
            s1 = self.get_column(self.df_fs, 's_005_stocks')
            s2 = self.get_column(self.df_fs, 's_007_asset')
            s3 = s1 / s2
            s3.name = column
            return s3.dropna()

        elif column == 's_007_asset':
            return self.smooth_data(column, 'id_001_bs_ta')

        elif column == 's_008_revenue':
            return self.smooth_data(column, 'id_157_ps_toi', delta=True, ttm=True)

        elif column == 's_009_revenue_rate':
            revenue = self.get_column(self.df_fs, 's_008_revenue')
            return StandardFitModel.get_growth_rate(revenue, column)

        elif column == 's_010_main_profit':
            return self.smooth_data(column, 'id_200_ps_op', delta=True, ttm=True)

    @staticmethod
    def if_column_exist(func):
        @wraps(func)
        def wrapped_function(df, column):
            if column in df.columns:
                return df[column].copy().dropna()
            else:
                return func(df, column)
        return wrapped_function

    def get_revenue_rate(self, add=False):
        name = 's_009_revenue_rate'
        df = self.df_fs
        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            df1 = self.get_revenue()
            new_df = StandardFitModel.get_growth_rate(df1, name)
            return self.return_df(df, new_df, add=add)

    def get_pe(self, add=False):
        name = 's_004_pe'
        df = self.df_mvs

        if name in df.columns:
            new_df = df.loc[:, [name]].copy().dropna()
            return new_df if add is False else df
        else:
            s1 = df['id_041_mvs_mc'].copy().dropna()
            s2 = self.get_profit().iloc[:, 0]
            last_report = self.get_last_report().iloc[:, 0]

            new = pd.Series(index=last_report.index, name=name)
            counter = 0
            for index, value in last_report.iteritems():
                try:
                    a = s1[index]
                except Exception as e:
                    # print(e)
                    a = np.nan
                try:
                    b = s2[value]
                except Exception as e:
                    # print(e)
                    b = np.nan

                new[counter] = a / b
                counter += 1
            new_df = pd.DataFrame(new)

            return self.return_df(df, new_df, add=add)

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
        data4.columns = [name]
        return data4

    @classmethod
    def config_window_array(cls, arr_y):
        # arr_y[arr_y <= 0] = np.nan
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
    def window_method(cls, arr_y):
        arr_y = cls.config_window_array(arr_y)
        if arr_y is None:
            return 0
        delta = cls.curve_fit(arr_y) * 4
        return delta

    @classmethod
    def curve_fit(cls, arr_y):
        arr_x = np.arange(0, arr_y.size, 1)
        popt, pcov = curve_fit(cls.curve_func, arr_x, arr_y)
        return popt[0]

    @staticmethod
    def curve_func(x, a, b):
        return np.exp(a * x + b)


class SubDataAnalysis(DataAnalysis):
    def __init__(self, df_fs: pd.DataFrame):
        self.df_fs = df_fs.copy()
        self.df_mvs = None

        # self.config_fs_data()
        # self.df_fs = self.get_profit(add=True)
        # self.df_fs = self.get_revenue(add=True)
        # self.df_fs = self.get_revenue_rate(add=True)


if __name__ == '__main__':
    # # sql2df('000002')
    # str2 = "from __main__ import sql2df_mvs"
    # t0 = timeit.Timer("sql2df_mvs('000004')", str2)
    # print(t0.timeit(10))

    # combine_style_df()
    #
    res = sql2df('600006')
    print(res)
    pass
