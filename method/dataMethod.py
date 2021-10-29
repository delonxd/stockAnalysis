from method.sqlMethod import get_data_frame, sql_if_table_exists
from request.requestData import get_cursor
from request.requestData import get_header_df
from request.requestData import request_data2mysql

import pandas as pd
import numpy as np

import datetime as dt
from dateutil.relativedelta import relativedelta


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


def get_roe_from_df(df: pd.DataFrame):
    profit0 = df.loc[:, ['id_211_ps_np']]
    profit0.dropna(inplace=True)

    profit = get_month_delta(profit0, 'profit')
    profit = profit.rolling(4, min_periods=1).mean()

    equity0 = df.loc[:, ['id_110_bs_toe']]
    equity0.dropna(inplace=True)
    equity = get_month_data(equity0, 'equity')

    res_df = pd.concat([profit, equity], axis=1, sort=True, join='inner')

    a = res_df['profit'].values
    b = res_df['equity'].values
    c = b - a
    c[c <= 0] = np.nan
    d = a / c

    if d.size == 0:
        return pd.DataFrame(columns=['roe'])

    d[np.isnan(d)] = -np.inf
    d[d <= -50] = -np.inf
    d[d == -np.inf] = np.nan
    res_df['roe'] = np.around(d, decimals=2)

    res = res_df.loc[:, ['roe']]
    return res


def sql2df(code):
    today = dt.date.today().strftime("%Y-%m-%d")

    df1 = load_df_from_mysql(code, 'fs')
    d0 = df1.iloc[-1, :]['last_update'][:10]

    if not d0 == today:
        request_data2mysql(
            stock_code=code,
            data_type='fs',
            start_date="2021-04-01",
        )
        df1 = load_df_from_mysql(code, 'fs')

    df2 = load_df_from_mysql(code, 'mvs')
    d0 = df2.iloc[-1, :]['last_update'][:10]

    if not d0 == today:
        request_data2mysql(
            stock_code=code,
            data_type='mvs',
            start_date="2021-04-01",
            # start_date="1970-01-01",
        )
        df2 = load_df_from_mysql(code, 'mvs')

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True,
                  sort=True, suffixes=('_mvs', '_fs'), copy=True)

    df_roe = get_roe_from_df(df)
    df_roe.columns = ['s_001_roe']
    df = pd.merge(df, df_roe, how='outer', left_index=True, right_index=True,
                  sort=True, suffixes=('_id', '_self'), copy=True)

    return df


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
