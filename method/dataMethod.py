from method.sqlMethod import get_data_frame, sql_if_table_exists
from request.requestData import get_cursor
from request.requestData import get_header_df
from discount.discountModel import ValueModel
from method.fileMethod import load_pkl

import pandas as pd
import numpy as np
import json

import datetime as dt
from dateutil.relativedelta import relativedelta

from scipy.optimize import curve_fit
from functools import wraps


def load_df_from_mysql(stock_code, data_type, fields=None):
    db, cursor = get_cursor(data_type)

    if data_type == 'fs':
        table = 'fs_%s' % stock_code
        check_field = 'standardDate'
    elif data_type == 'mvs':
        table = 'mvs_%s' % stock_code
        check_field = 'date'
    elif data_type == 'eq':
        table = 'eq_%s' % stock_code
        check_field = 'date'
    elif data_type == 'dv':
        table = 'dv_%s' % stock_code
        check_field = 'id'
    else:
        return

    flag = sql_if_table_exists(cursor=cursor, table=table)
    if flag:
        if fields is None:
            sql_df = get_data_frame(cursor=cursor, table=table)
        else:
            sql_df = get_data_frame(cursor=cursor, table=table, fields=fields)

        sql_df = sql_df.set_index(check_field, drop=False)
        # sql_df = sql_df.where(sql_df.notnull(), None)
        sql_df.sort_index(inplace=True)
        if 'Invalid date' in sql_df.index:
            sql_df.drop('Invalid date', inplace=True)
        sql_df.index = sql_df.index.map(lambda x: x[:10])
        return sql_df
    else:
        if fields is None:
            header_df = get_header_df(data_type)
            return pd.DataFrame(columns=header_df.columns)
        else:
            return pd.DataFrame(columns=fields)


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


def get_month_data(series: pd.Series, new_name):
    series = series.dropna()

    date0 = None
    year0 = None
    month0 = None
    index0 = None
    value0 = None

    indexes = list()
    values = list()

    for tup in series.items():
        date = dt.datetime.strptime(str(tup[0]), "%Y-%m-%d")

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

    res = pd.Series(values, index=indexes, name=new_name)
    # res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    # print(res_df)
    # raise KeyboardInterrupt

    return res


def get_month_delta(series: pd.Series, new_name, mode='QUARTERLY'):

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

    for tup in series.items():
        date = dt.datetime.strptime(str(tup[0]), "%Y-%m-%d")
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

    res = pd.Series(values, index=indexes, name=new_name)
    # res_df = pd.DataFrame(values, index=indexes, columns=[new_name])

    return res


def sql2df(code):
    df1 = load_df_from_mysql(code, 'fs')
    df2 = load_df_from_mysql(code, 'mvs')

    # print(df1)
    # print(df2)
    data = DataAnalysis(df1, df2, code=code)
    data.add_dv_data(code)
    data.config_widget_data()
    data.add_eq_data(code)
    data.add_mir_data()
    data.add_position_data()
    data.add_futures_data()
    # data.add_dv_data(code)

    # print(data.df.columns.values)
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
    def __init__(self, df_fs: pd.DataFrame, df_mvs: pd.DataFrame, code=''):
        self.df_fs = df_fs
        self.df_mvs = df_mvs
        self.df = pd.DataFrame()
        self.code = code

    def get_sub_date(self):
        df = self.df_fs
        dt_fs = df['id_001_bs_ta'].copy().dropna()

        res = list()
        sub = list()
        val = np.inf
        for index, value in dt_fs.items():
            if value > 2 * val:
                res.append(sub)
                sub = list()

            sub.append(index)
            val = value

        if len(sub) > 0:
            res.append(sub)

        return res

    def config_sub_fs(self, class_sub):
        df = self.df_fs.copy()
        s0 = pd.Series(name='split_date')

        sub_list = self.get_sub_date()

        last_date = ''
        df_list = list()
        for sub in sub_list:
            s0[sub[-1]] = sub[-1]

            sub_df = df.loc[sub, :].copy()
            sub_data = class_sub(sub_df, None, code=self.code)
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

        self.fs_add(s0)
        return self.df_fs

    def config_fs_data(self):
        index_list = [
            's_017_equity_parent',
            's_018_profit_parent',
            's_016_roe_parent',

            's_007_asset',
            's_002_equity',

            's_005_receivables_surplus',

            's_003_profit',
            # 's_010_main_profit',
            # 's_011_main_profit_rate',

            's_067_equity_ratio',

            's_001_roe',
            # 's_006_stocks_rate',

            's_008_revenue',
            's_047_gross_cost',
            's_009_revenue_rate',

            # 's_019_monetary_asset',
            # 's_020_cap_asset',
            # 's_021_cap_expenditure',
            # 's_022_profit_no_expenditure',

            's_010_cash_asset',
            's_011_insurance_asset',
            's_012_financial_asset',
            's_013_invest_asset',
            's_014_turnover_asset',
            's_015_inventory_asset',
            's_021_fixed_asset',
            's_022_capitalized_asset',

            's_023_liabilities',
            's_024_real_liabilities',
            's_026_liquidation_asset',

            # 's_038_pay_for_long_term_asset',
            # 's_039_profit_adjust',
            # 's_040_profit_adjust2',
            # 's_041_profit_adjust_ttm',
            # 's_045_main_cost_adjust',
            # 's_046_profit_adjust3',
            's_049_pf_tx_invest',
            's_050_pf_tx_iv_outer',
            's_051_core_profit',
            's_048_profit_tax',
            's_052_core_profit_asset',
            's_053_core_profit_salary',
            's_054_gross_profit_rate',
            's_055_gross_cost',
            's_056_inventory_turnaround',
            's_057_core_roe',
            's_058_equity_adj',
            's_059_total_expend',
            's_060_total_expend_rate',
            's_061_total_return_rate',

            's_063_profit_salary2',
            's_064_profit_salary3',
            's_065_profit_salary_adj',
            's_066_profit_salary_min',
        ]

        # df = self.df_fs

        for index in index_list:
            self.fs_add(self.get_column(self.df_fs, index))
            # self.fs_add(self.get_column(df, index))

    def config_widget_data(self):
        self.config_sub_fs(DataAnalysis)
        self.fs_add(self.get_column(self.df_fs, 'dt_fs'))
        self.mvs_add(self.get_column(self.df_mvs, 'dt_mvs'))

        df = self.df_mvs

        index_list1 = [
            # 's_030_parent_equity_delta',
            # 's_031_financing_outflow',
            # 's_032_remain_rate',
            # 's_033_profit_compound',
        ]
        for index in index_list1:
            self.fs_add(self.get_column(df, index))

        index_list2 = [
            's_004_pe',
            # 's_012_return_year',
            # 's_014_pe2',
            # 's_015_return_year2',
            's_068_market_value_adj',

            's_025_real_cost',
            # 's_026_holder_return_rate',
            's_027_pe_return_rate',
            's_028_market_value',
            # 's_029_return_predict',

            # 'mir_y10',
            's_034_real_pe',
            's_035_pe2rate',
            's_036_real_pe2rate',
            's_043_turnover_volume_ttm',
            'market_change_rate',

            's_069_dividend_rate',
            's_070_turnover_rate',

        ]
        for index in index_list2:
            self.mvs_add(self.get_column(df, index))

        self.config_balance_sheet()
        self.set_df()

    def config_balance_sheet(self):
        assets_dict = {
            'id_005_bs_cabb': '货币资金',
            'id_007_bs_sr': '结算备付金',
            'id_008_bs_pwbaofi': '拆出资金',
            'id_009_bs_tfa': '交易性金融资产',
            'id_010_bs_cdfa': '衍生金融资产(流动)',
            'id_012_bs_nr': '应收票据',
            'id_013_bs_ar': '应收账款',
            'id_014_bs_rf': '应收款项融资',
            'id_015_bs_ats': '预付款项',
            'id_016_bs_pr': '应收保费',
            'id_017_bs_rir': '应收分保账款',
            'id_018_bs_crorir': '应收分保合同准备金',
            'id_019_bs_or': '其他应收款',
            'id_022_bs_fahursa': '买入返售金融资产',
            'id_023_bs_i': '存货',
            'id_024_bs_ca': '合同资产',
            'id_025_bs_ahfs': '持有待售资产',
            'id_026_bs_claatc': '发放贷款及垫款(流动)',
            'id_027_bs_pe': '待摊费用',
            'id_028_bs_ncadwioy': '一年内到期的非流动资产',
            'id_029_bs_oca': '其他流动资产',

            'id_035_bs_nclaatc': '发放贷款及垫款(非流动)',
            'id_036_bs_cri': '债权投资',
            'id_037_bs_ocri': '其他债权投资',
            'id_038_bs_ncafsfa': '可供出售金融资产(非流动)',
            'id_039_bs_htmi': '持有至到期投资',
            'id_040_bs_ltar': '长期应收款',
            'id_041_bs_ltei': '长期股权投资',
            'id_042_bs_oeii': '其他权益工具投资',
            'id_043_bs_oncfa': '其他非流动金融资产',
            'id_044_bs_rei': '投资性房地产',
            'id_045_bs_fa': '固定资产',
            'id_048_bs_cip': '在建工程',
            'id_051_bs_pba': '生产性生物资产',
            'id_052_bs_oaga': '油气资产',
            'id_053_bs_pwba': '公益性生物资产',
            'id_054_bs_roua': '使用权资产',
            'id_055_bs_ia': '无形资产',
            'id_056_bs_rade': '开发支出',
            'id_057_bs_gw': '商誉',
            'id_059_bs_ltpe': '长期待摊费用',
            'id_060_bs_dita': '递延所得税资产',
            'id_061_bs_onca': '其他非流动资产',
        }

        equity_dict = {
            'id_068_bs_stl': '短期借款',
            'id_069_bs_bfcb': '向中央银行借款',
            'id_070_bs_pfbaofi': '拆入资金',
            'id_071_bs_dfl': '衍生金融负债',
            'id_072_bs_tfl': '交易性金融负债',
            'id_073_bs_npaap': '应付票据及应付账款',
            'id_074_bs_np': '(其中) 应付票据',
            'id_075_bs_ap': '(其中) 应付账款',
            'id_076_bs_afc': '预收账款',
            'id_077_bs_cl': '合同负债',
            'id_078_bs_fasurpa': '卖出回购金融资产',
            'id_079_bs_dfcab': '吸收存款及同业存放',
            'id_080_bs_stoa': '代理买卖证券款',
            'id_081_bs_ssoa': '代理承销证券款',
            'id_082_bs_sawp': '应付职工薪酬',
            'id_083_bs_tp': '应交税费',
            'id_084_bs_oap': '其他应付款',
            'id_087_bs_facp': '应付手续费及佣金',
            'id_088_bs_rip': '应付分保账款',
            'id_089_bs_lhfs': '持有待售负债',
            'id_090_bs_ncldwioy': '一年内到期的非流动负债',
            'id_091_bs_didwioy': '一年内到期的递延收益',
            'id_092_bs_cal': '预计负债(流动)',
            'id_093_bs_stbp': '短期应付债券',
            'id_094_bs_ocl': '其他流动负债',

            'id_097_bs_icr': '保险合同准备金',
            'id_098_bs_ltl': '长期借款',
            'id_099_bs_bp': '应付债券',
            'id_102_bs_ll': '租赁负债',
            'id_103_bs_ltap': '长期应付款',
            'id_105_bs_ltpoe': '长期应付职工薪酬',
            'id_106_bs_ncal': '预计负债(非流动)',
            'id_107_bs_ltdi': '长期递延收益',
            'id_108_bs_ditl': '递延所得税负债',
            'id_109_bs_oncl': '其他非流动负债',

            'id_112_bs_sc': '股本',
            'id_113_bs_oei': '其他权益工具',
            'id_116_bs_capr': '资本公积',
            'id_118_bs_oci': '其他综合收益',
            'id_119_bs_rr': '专项储备',
            'id_120_bs_surr': '盈余公积',
            'id_121_bs_pogr': '一般风险准备金',
            'id_122_bs_rtp': '未分配利润',
            'id_126_bs_etmsh': '少数股东权益',
        }

        index_list = list()
        index_list.extend(assets_dict.keys())
        index_list.extend(equity_dict.keys())

        res_df = pd.DataFrame()

        df = self.df_fs
        for index in index_list:
            # src_df = df.loc[:, [index]].copy().dropna()
            # name = 'config_' + index
            # new_df = get_month_data(src_df, name)
            s1 = df.loc[:, index].copy().dropna()
            s2 = get_month_data(s1, 'config_' + index)
            res_df = pd.concat([res_df, s2], axis=1, sort=True)

        self.df_fs = pd.concat([self.df_fs, res_df], axis=1, sort=True)

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

    def add_df(self, new_df):
        self.df = pd.concat([self.df, new_df], axis=1, sort=True)

    def add_eq_data(self, code):
        df_src = load_df_from_mysql(code, 'eq')
        df = df_src.loc[:, ['id_002_rate', 'id_012_dilution_rate']]
        df.columns = ['eq_002_rate', 'eq_012_dilution_rate']
        if df.size > 0:
            df['eq_002_rate'] = df['eq_002_rate'] / df.iloc[-1, 0]
        self.add_df(df)

    def add_dv_data(self, code):
        df = load_df_from_mysql(code, 'dv', fields=[
            'id', 'dividend', 'originalValue', 'status'
        ])

        df = df[df['dividend'] != 0]
        s0 = self.get_column(self.df_fs, 'id_142_bs_tsc')
        tmp_dict = dict()
        for date, row in df.iterrows():
            if pd.isna(row['originalValue']):
                date_r = self.report_date2standard([date]).iloc[0]
                if date_r != 'None':
                    if date_r in s0.index:
                        tmp_dict[date] = s0[date_r] * row['dividend']
        for date, value in tmp_dict.items():
            df.loc[date, 'originalValue'] = value

        s1 = df.loc[:, 'originalValue'].copy()
        s1 = s1.replace(0, np.nan).dropna()
        s1 = s1.sort_index(ascending=False)
        s1.index = self.report_date2standard(s1.index)
        s1 = s1.drop('None', errors='ignore').dropna()

        if s1.index.is_unique is False:
            d0 = dict()
            for index, value in s1.items():
                if index in d0:
                    d0[index] = d0[index] + value
                else:
                    d0[index] = value
            s1 = pd.Series(d0)

        s2 = self.get_column(self.df_fs, 's_003_profit')
        s2 = s1.reindex_like(s2)

        s_tmp = s2.loc[s2.last_valid_index():]
        if s_tmp.size > 4:
            index_tmp = 4 - s_tmp.size
            s2 = s2.iloc[:index_tmp]
        s3 = s2.fillna(0)
        s3 = self.get_ttm(s3, 4) * 4

        s3.name = 'dv_001_dividend_value'

        new_df = pd.DataFrame(s3)
        self.fs_add(new_df)
        # self.add_df(new_df)

    def add_mir_data(self):
        # path = "..\\basicData\\nationalDebt\\mir_y10.txt"
        path = "..\\basicData\\nationalDebt\\mir_y10_akshare.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            res = json.loads(f.read())

        s0 = self.regular_series('mir_y10', pd.Series(res))
        df = pd.DataFrame(s0)
        self.add_df(df)

    def add_position_data(self):
        # path = "..\\basicData\\nationalDebt\\mir_y10.txt"
        path = "..\\basicData\\daily_position.txt"
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            res = json.loads(f.read())

        s0 = self.regular_series('daily_position', pd.Series(res))
        df = pd.DataFrame(s0)
        self.add_df(df)

    def add_futures_data(self):
        path = "..\\basicData\\futures\\futures_prices_history.pkl"
        df = load_pkl(path, log=False)
        df = df.dropna(axis=0, how='all')
        columns = []

        df_columns = list(df.columns)
        for index, val in enumerate(df_columns):
            str1 = str(index+1).rjust(2, '0')
            str2 = val.split('_')[0]
            column = 'futures_%s_%s' % (str1, str2)
            columns.append(column)
        df.columns = columns
        self.add_df(df)

    def report_date2standard(self, s1):
        report_date = self.df_fs['reportDate'].copy().dropna()
        report_date = report_date.sort_index(ascending=False)

        res = list()
        for date1 in s1:
            tmp = 'None'
            for index, value in report_date.items():
                date2 = value[:10]
                if date1 > date2:
                    break
                if date1 <= date2:
                    tmp = index
            res.append(tmp)
        return pd.Series(res, dtype='str')

    @staticmethod
    def get_df_after_date(df, date):
        return df.loc[df.index.values > date, :].copy()

    @if_column_exist
    def get_column(self, df, column):
        if column == 'dt_fs':
            dt_fs = df['reportDate'].copy().dropna()
            dict0 = dict()
            for index, value in dt_fs.items():
                dict0[value[:10]] = index

            dt_fs = pd.Series(dict0, name=column)
            dt_fs.sort_index(inplace=True)
            return dt_fs

        elif column == 'dt_mvs':
            index = df['date'].copy().dropna().index.values
            dt_mvs = pd.Series(index, index=index, name=column)
            return dt_mvs

        # elif column == 'mir_y10':
        #     # path = "..\\basicData\\nationalDebt\\mir_y10.txt"
        #     path = "..\\basicData\\nationalDebt\\mir_y10_akshare.txt"
        #     with open(path, "r", encoding="utf-8", errors="ignore") as f:
        #         res = json.loads(f.read())
        #     return self.regular_series(column, pd.Series(res))

        elif column == 'market_change_rate':
            path = "..\\basicData\\dailyUpdate\\latest\\a007_change_rate.txt"
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                res = json.loads(f.read())
            return self.regular_series(column, pd.Series(res))

        elif column == 's_001_roe':
            s1 = self.get_column(df, 's_003_profit')
            s2 = self.get_column(df, 's_002_equity')
            s3 = self.get_delta_rate(s1, s2)
            return self.regular_series(column, s3)

        elif column == 's_002_equity':
            return self.smooth_data(column, 'id_110_bs_toe')

        elif column == 's_003_profit':
            return self.smooth_data(column, 'id_211_ps_np', delta=True, ttm=True)

        elif column == 's_004_pe':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            return self.regular_series(column, s2 / s1)

        elif column == 's_005_receivables_surplus':
            s1 = self.get_column(self.df_fs, 'id_011_bs_nraar')
            s2 = self.get_column(self.df_fs, 'id_012_bs_nr')
            s3 = self.get_column(self.df_fs, 'id_013_bs_ar')
            s4 = s1 - (s2 + s3)
            s5 = get_month_data(s4, column)
            return self.regular_series(column, s5)

        # 待删除
        # elif column == 's_006_stocks_rate':
        #     s1 = self.get_column(df, 's_005_stocks')
        #     s2 = self.get_column(df, 's_007_asset')
        #     return self.regular_series(column, s1 / s2)

        elif column == 's_007_asset':
            return self.smooth_data(column, 'id_001_bs_ta')

        elif column == 's_008_revenue':
            return self.smooth_data(column, 'id_157_ps_toi', delta=True, ttm=True)

        elif column == 's_009_revenue_rate':
            s1 = self.get_column(df, 's_008_revenue')
            s2 = StandardFitModel.get_growth_rate(s1, column, 12)
            return self.regular_series(column, s2)

        elif column == 's_010_cash_asset':
            d1 = {
                'id_005_bs_cabb': '货币资金',
                'id_007_bs_sr': '结算备付金',
                'id_008_bs_pwbaofi': '拆出资金',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_011_insurance_asset':
            d1 = {
                'id_016_bs_pr': '应收保费',
                'id_017_bs_rir': '应收分保账款',
                'id_018_bs_crorir': '应收分保合同准备金',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_012_financial_asset':
            d1 = {
                'id_036_bs_cri': '债权投资',
                'id_037_bs_ocri': '其他债权投资',
                'id_039_bs_htmi': '持有至到期投资',
                'id_009_bs_tfa': '交易性金融资产',
                'id_010_bs_cdfa': '衍生金融资产(流动)',
                'id_022_bs_fahursa': '买入返售金融资产',
                'id_042_bs_oeii': '其他权益工具投资',
                'id_038_bs_ncafsfa': '可供出售金融资产(非流动)',
                'id_043_bs_oncfa': '其他非流动金融资产',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_013_invest_asset':
            d1 = {
                'id_026_bs_claatc': '发放贷款及垫款(流动)',
                'id_035_bs_nclaatc': '发放贷款及垫款(非流动)',
                'id_029_bs_oca': '其他流动资产',
                'id_025_bs_ahfs': '持有待售资产',
                'id_041_bs_ltei': '长期股权投资',
                'id_044_bs_rei': '投资性房地产',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_014_turnover_asset':
            d1 = {
                'id_015_bs_ats': '预付款项',
                'id_060_bs_dita': '递延所得税资产',
                'id_024_bs_ca': '合同资产',
                'id_014_bs_rf': '应收款项融资',
                'id_011_bs_nraar': '应收票据及应收账款',
                'id_040_bs_ltar': '长期应收款',
                'id_019_bs_or': '其他应收款',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_015_inventory_asset':
            d1 = {
                'id_023_bs_i': '存货',
                'id_052_bs_oaga': '油气资产',
                'id_051_bs_pba': '生产性生物资产',
                'id_053_bs_pwba': '公益性生物资产',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_016_roe_parent':
            s1 = self.get_column(df, 's_018_profit_parent')
            s2 = self.get_column(df, 's_017_equity_parent')
            s3 = self.get_delta_rate(s1, s2)
            return self.regular_series(column, s3)

        elif column == 's_017_equity_parent':
            return self.smooth_data(column, 'id_124_bs_tetoshopc')

        elif column == 's_018_profit_parent':
            return self.smooth_data(column, 'id_217_ps_npatoshopc', delta=True, ttm=True)

        # elif column == 's_019_monetary_asset':
        #     d1 = {
        #         'id_005_bs_cabb': '货币资金',
        #         'id_007_bs_sr': '结算备付金',
        #         'id_008_bs_pwbaofi': '拆出资金',
        #         'id_009_bs_tfa': '交易性金融资产',
        #         'id_010_bs_cdfa': '衍生金融资产(流动)',
        #         'id_024_bs_ca': '合同资产',
        #     }
        #
        #     s1 = self.sum_columns(df, list(d1.keys()))
        #     s2 = get_month_data(s1, column)
        #     return self.regular_series(column, s2)

        # elif column == 's_020_cap_asset':
        #     s1 = self.get_column(df, 's_007_asset')
        #     s2 = self.get_column(df, 's_019_monetary_asset')
        #     return self.regular_series(column, s1 - s2)

        elif column == 's_021_fixed_asset':
            d1 = {
                'id_045_bs_fa': '固定资产',
                'id_048_bs_cip': '在建工程',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_022_capitalized_asset':
            d1 = {
                'id_061_bs_onca': '其他非流动资产',
                'id_028_bs_ncadwioy': '一年内到期的非流动资产',
                'id_054_bs_roua': '使用权资产',
                'id_055_bs_ia': '无形资产',
                'id_027_bs_pe': '待摊费用',
                'id_059_bs_ltpe': '长期待摊费用',
                'id_056_bs_rade': '开发支出',
                'id_057_bs_gw': '商誉',
            }

            s1 = self.sum_columns(df, list(d1.keys()))
            s2 = get_month_data(s1, column)
            return self.regular_series(column, s2)

        elif column == 's_023_liabilities':
            return self.smooth_data(column, 'id_062_bs_tl')

        elif column == 's_024_real_liabilities':
            tmp = list()
            tmp.append(self.get_column(df, 's_010_cash_asset') * -1)
            tmp.append(self.get_column(df, 's_011_insurance_asset') * -1)
            tmp.append(self.get_column(df, 's_012_financial_asset') * -1)
            tmp.append(self.get_column(df, 's_023_liabilities'))

            df1 = pd.concat(tmp, axis=1, sort=True)
            s1 = df1.apply(lambda x: x.sum(), axis=1)
            return self.regular_series(column, s1)

        elif column == 's_025_real_cost':
            s1 = self.fs_to_mvs('s_026_liquidation_asset')
            s3 = self.fs_to_mvs('s_002_equity')
            s2 = self.get_column(self.df_mvs, 's_068_market_value_adj')

            return self.regular_series(column, s2 - s1 + s3)

        elif column == 's_026_liquidation_asset':
            s0 = self.smooth_data(column, 'id_011_bs_nraar')  # 应收票据及应收账款

            tmp = list()
            tmp.append(self.get_column(df, 's_010_cash_asset'))
            tmp.append(self.get_column(df, 's_011_insurance_asset'))
            tmp.append(self.get_column(df, 's_012_financial_asset'))
            tmp.append(self.get_column(df, 's_013_invest_asset') * 0.5)
            tmp.append(self.get_column(df, 's_014_turnover_asset') * 0.2)
            tmp.append(self.get_column(df, 's_015_inventory_asset') * 0.2)
            tmp.append(self.get_column(df, 's_021_fixed_asset') * 0.1)
            tmp.append(self.get_column(df, 's_023_liabilities') * -1)
            tmp.append(s0 * 0.6)

            df1 = pd.concat(tmp, axis=1, sort=True)
            s1 = df1.apply(lambda x: x.sum(), axis=1)
            return self.regular_series(column, s1)

        elif column == 's_027_pe_return_rate':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            return self.regular_series(column, s1 / s2)

        elif column == 's_028_market_value':
            s1 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            return self.regular_series(column, s1)

        # elif column == 's_029_return_predict':
        #     s1 = self.fs_to_mvs('s_009_revenue_rate')
        #     s2 = self.get_column(df, 's_027_pe_return_rate')
        #     s3 = (s1 * 5 + 1) * s2
        #     return self.regular_series(column, s3)

        # elif column == 's_030_parent_equity_delta':
        #     s1 = self.smooth_data(column, 'id_124_bs_tetoshopc')
        #     s2 = s1 - s1.shift(1)
        #     s3 = s2.fillna(0)
        #     return self.regular_series(column, s3)

        # elif column == 's_031_financing_outflow':
        #     s1 = self.smooth_data('s1', 'id_217_ps_npatoshopc', delta=True)
        #     s2 = self.get_column(df, 's_030_parent_equity_delta')
        #     s3 = s2 - (s1 / 4)
        #     return self.regular_series(column, s3)

        # elif column == 's_032_remain_rate':
        #     s1 = self.get_column(df, 's_030_parent_equity_delta')
        #     s1 = self.get_ttm(s1 * 4, 4)
        #     s2 = self.get_column(df, 's_017_equity_parent')
        #     res = self.get_delta_rate(s1, s2)
        #     return self.regular_series(column, res)

        # elif column == 's_033_profit_compound':
        #     s1 = self.get_column(df, 's_032_remain_rate')
        #     s2 = (s1 + 1) ** 5
        #     s2[s2 > 1e8] = 1e8
        #     s2.name = column
        #     return self.regular_series(column, s2)

        elif column == 's_034_real_pe':
            # s1 = self.fs_to_mvs('s_018_profit_parent')
            s1 = self.fs_to_mvs('s_051_core_profit')
            s2 = self.get_column(df, 's_025_real_cost')
            return self.regular_series(column, s2 / s1)

        elif column == 's_035_pe2rate':
            # s1 = self.get_column(df, 's_004_pe')
            s1 = self.get_column(df, 's_034_real_pe')
            s2 = self.transform_pe(s1)
            return self.regular_series(column, s2)

        elif column == 's_036_real_pe2rate':
            s1 = self.get_column(df, 's_034_real_pe')
            s2 = self.transform_pe(s1/2)
            return self.regular_series(column, s2)

        elif column == 's_037_real_pe_return_rate':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column(df, 's_025_real_cost')
            return self.regular_series(column, s1 / s2)

        # elif column == 's_038_pay_for_long_term_asset':
        #     s1 = self.smooth_data('s1', 'id_271_cfs_cpfpfiaolta', delta=True)
        #     return self.regular_series(column, s1)

        # elif column == 's_039_profit_adjust':
        #     d1 = {
        #         'id_298_cfs_np': '净利润',
        #         'id_299_cfs_ioa': '加： 资产减值准备',
        #         'id_300_cfs_cilor': '信用减值损失',
        #         'id_301_cfs_dofx_dooaga_dopba': '固定资产折旧、油气资产折耗、生产性生物资产折旧',
        #         'id_302_cfs_daaorei': '投资性房地产的折旧及摊销',
        #         'id_303_cfs_aoia': '无形资产摊销',
        #         'id_304_cfs_aoltde': '长期待摊费用摊销',
        #         'id_305_cfs_lodofaiaaolta': '处置固定资产、无形资产和其他长期资产的损失',
        #         'id_306_cfs_lfsfa': '固定资产报废损失',
        #         # 'id_307_cfs_lfcifv': '公允价值变动损失',
        #         'id_312_cfs_dii': '存货的减少',
        #     }
        #
        #     s1 = self.sum_columns(df, list(d1.keys()))
        #     s2 = get_month_delta(s1, column)
        #     return self.regular_series(column, s2)

        # elif column == 's_040_profit_adjust2':
        #     s1 = self.get_column(df, 's_039_profit_adjust')
        #     s2 = self.get_column(df, 's_038_pay_for_long_term_asset')
        #     s3 = self.get_ttm(s1 - s2, 4)
        #     return self.regular_series(column, s3)

        # elif column == 's_041_profit_adjust_ttm':
        #     s1 = self.get_column(df, 's_039_profit_adjust')
        #     s2 = self.get_ttm(s1, 4)
        #     return self.regular_series(column, s2)

        # elif column == 's_042_roe_adjust':
        #     return self.regular_series(column, pd.Series())

        elif column == 's_043_turnover_volume_ttm':
            s1 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            s2 = self.get_column(self.df_mvs, 'id_042_mvs_cmc')
            s3 = self.get_column(self.df_mvs, 'id_048_mvs_ta')
            s4 = self.get_ttm(s1 / s2 * s3 * 10, 20)
            return self.regular_series(column, s4)

        elif column == 's_044_turnover_volume':
            s1 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            s2 = self.get_column(self.df_mvs, 'id_042_mvs_cmc')
            s3 = self.get_column(self.df_mvs, 'id_048_mvs_ta')
            s4 = s1 / s2 * s3
            return self.regular_series(column, s4)

        # elif column == 's_045_main_cost_adjust':
        #     d1 = {
        #         # 'id_299_cfs_ioa': '加： 资产减值准备',
        #         # 'id_300_cfs_cilor': '信用减值损失',
        #         'id_301_cfs_dofx_dooaga_dopba': '固定资产折旧、油气资产折耗、生产性生物资产折旧',
        #         'id_302_cfs_daaorei': '投资性房地产的折旧及摊销',
        #         'id_303_cfs_aoia': '无形资产摊销',
        #         'id_304_cfs_aoltde': '长期待摊费用摊销',
        #         'id_305_cfs_lodofaiaaolta': '处置固定资产、无形资产和其他长期资产的损失',
        #         'id_306_cfs_lfsfa': '固定资产报废损失',
        #         # 'id_307_cfs_lfcifv': '公允价值变动损失',
        #         'id_312_cfs_dii': '存货的减少',
        #     }
        #
        #     s1 = self.sum_columns(df, list(d1.keys()))
        #     s1 = get_month_delta(s1, 's1')
        #     s2 = self.smooth_data('s2', 'id_163_ps_toc', delta=True)
        #     s3 = self.get_ttm(s2 - s1, 4)
        #     return self.regular_series(column, s3)

        # elif column == 's_046_profit_adjust3':
        #     s1 = self.get_column(df, 's_039_profit_adjust')
        #     s2 = self.smooth_data('s2', 'id_271_cfs_cpfpfiaolta', delta=True)
        #     s3 = self.smooth_data('s3', 'id_265_cfs_crfdofiaolta', delta=True)
        #     s4 = self.smooth_data('s4', 'id_281_cfs_crfai', delta=True)
        #     s5 = self.get_ttm(s1 - (s2 - s3 - s4), 4)
        #     return self.regular_series(column, s5)

        elif column == 's_047_gross_cost':
            return self.smooth_data(column, 'id_164_ps_oc', delta=True, ttm=True)

        elif column == 's_048_profit_tax':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.smooth_data(column, 'id_209_ps_ite', delta=True, ttm=True)
            return self.regular_series(column, s1 + s2)

        elif column == 's_049_pf_tx_invest':
            d0 = {
                'id_211_ps_np': '净利润',
                'id_187_ps_ivi': '投资收益',
                'id_196_ps_adi': '资产处置收益',
                'id_192_ps_ciofv': '公允价值变动收益',
            }
            s = list()
            for index in d0.keys():
                s.append(self.get_column(df, index))
            res = s[0] - (s[1] + s[2] + s[3])
            ttm = self.get_ttm(get_month_delta(res, column), 4)
            return self.regular_series(column, ttm)

        elif column == 's_050_pf_tx_iv_outer':
            d0 = {
                'id_186_ps_oic': '加： 其他收益',
                'id_197_ps_ooe': '其他业务成本',
                'id_203_ps_noi': '加： 营业外收入',
                'id_205_ps_noe': '减： 营业外支出',
            }
            s = list()
            for index in d0.keys():
                s.append(self.get_column(df, index))
            res = s[0] - s[1] + s[2] - s[3]

            s1 = self.get_column(self.df_fs, 's_049_pf_tx_invest')
            s2 = self.get_ttm(get_month_delta(res, 's2'), 4)
            return self.regular_series(column, s1 - s2)

        elif column == 's_051_core_profit':
            d0 = {
                'id_299_cfs_ioa': '加： 资产减值准备',
                'id_300_cfs_cilor': '信用减值损失',
                'id_301_cfs_dofx_dooaga_dopba': '固定资产折旧、油气资产折耗、生产性生物资产折旧',
                'id_302_cfs_daaorei': '投资性房地产的折旧及摊销',
                'id_303_cfs_aoia': '无形资产摊销',
                'id_304_cfs_aoltde': '长期待摊费用摊销',
                'id_306_cfs_lfsfa': '固定资产报废损失',
            }
            s1 = self.sum_columns(self.df_fs, list(d0.keys()))
            s2 = self.get_ttm(get_month_delta(s1, 's2'), 4)
            s3 = self.get_column(df, 's_050_pf_tx_iv_outer')
            return self.regular_series(column, s2 + s3)

        elif column == 's_052_core_profit_asset':
            d0 = {
                'id_281_cfs_crfai': '吸收投资收到的现金',
                # 'id_265_cfs_crfdofiaolta': '处置固定资产、无形资产及其他长期资产收到的现金',
                'id_271_cfs_cpfpfiaolta': '购建固定资产、无形资产及其他长期资产所支付的现金',
            }
            s = list()
            for index in d0.keys():
                s.append(self.get_column(df, index))
            res = s[0] - s[1]

            s1 = self.get_column(self.df_fs, 's_051_core_profit')
            s2 = self.get_ttm(get_month_delta(res, 's2'), 4)
            return self.regular_series(column, s1 + s2)

        elif column == 's_053_core_profit_salary':
            d0 = {
                'id_082_bs_sawp': '应付职工薪酬',
                'id_105_bs_ltpoe': '长期应付职工薪酬',
            }

            s1 = self.sum_columns(df, list(d0.keys()))
            s1 = get_month_data(s1, column)

            # s01 = self.smooth_data('s01', 'id_082_bs_sawp')
            # s02 = self.smooth_data('s02', 'id_105_bs_ltpoe')
            # s1 = s01 + s02

            s1 = self.get_ttm((s1 - s1.shift(1))*4, 4)
            s2 = self.smooth_data(column, 'id_257_cfs_cptofe', delta=True, ttm=True)
            # s3 = self.get_column(df, 's_051_core_profit')

            res_df = pd.DataFrame([s1, s2])
            s3 = res_df.apply(lambda x: x.sum(), axis=0)

            return self.regular_series(column, s3)

        elif column == 's_054_gross_profit_rate':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_008_revenue')
            return self.regular_series(column, s1 / s2)

        elif column == 's_055_gross_cost':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_008_revenue')
            return self.regular_series(column, s2 - s1)

        elif column == 's_056_inventory_turnaround':
            s1 = self.get_column(df, 'id_023_bs_i')
            s1 = self.get_ttm(get_month_data(s1, 's1'), 4)
            s2 = self.get_column(df, 's_055_gross_cost')
            return self.regular_series(column, s1 / s2)

        elif column == 's_057_core_roe':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_002_equity')
            return self.regular_series(column, s1 / s2)

        elif column == 's_058_equity_adj':
            d0 = {
                'id_299_cfs_ioa': '加： 资产减值准备',
                'id_300_cfs_cilor': '信用减值损失',
                'id_301_cfs_dofx_dooaga_dopba': '固定资产折旧、油气资产折耗、生产性生物资产折旧',
                'id_302_cfs_daaorei': '投资性房地产的折旧及摊销',
                'id_303_cfs_aoia': '无形资产摊销',
                'id_304_cfs_aoltde': '长期待摊费用摊销',
                'id_306_cfs_lfsfa': '固定资产报废损失',
            }
            s1 = self.sum_columns(self.df_fs, list(d0.keys()))
            s2 = get_month_delta(s1, 's2')
            s3 = s2.cumsum()
            s4 = self.get_column(df, 's_002_equity')
            return self.regular_series(column, s3 / 4 + s4)

        elif column == 's_059_total_expend':
            s1 = self.get_column(df, 's_058_equity_adj')
            s2 = self.get_column(df, 's_026_liquidation_asset')
            return self.regular_series(column, s1 - s2)

        elif column == 's_060_total_expend_rate':
            s1 = self.get_column(df, 's_058_equity_adj')
            s2 = StandardFitModel.get_growth_rate(s1, column, 12)
            return self.regular_series(column, s2)

        elif column == 's_061_total_return_rate':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_058_equity_adj')
            return self.regular_series(column, s1 / s2)

        elif column == 's_062_equity_ratio':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_058_equity_adj')
            return self.regular_series(column, s1 / s2)

        elif column == 's_063_profit_salary2':
            s1 = self.get_column(df, 's_051_core_profit')
            s2 = self.get_column(df, 's_053_core_profit_salary')
            s3 = s1 + s2
            s3 = s3 / 0.1
            return self.regular_series(column, s3)

        elif column == 's_064_profit_salary3':
            s1 = self.get_column(df, 's_052_core_profit_asset')
            s2 = self.get_column(df, 's_053_core_profit_salary')
            s3 = s1 + s2
            s3 = s3 / 0.1
            return self.regular_series(column, s3)

        elif column == 's_065_profit_salary_adj':
            s1 = self.get_column(df, 's_063_profit_salary2')
            s2 = self.get_column(df, 's_003_profit')
            s3 = self.get_column(df, 's_018_profit_parent')
            s4 = s1 / s2 * s3
            return self.regular_series(column, s4)

        elif column == 's_066_profit_salary_min':
            s1 = self.get_column(df, 's_063_profit_salary2')
            s2 = self.get_column(df, 's_065_profit_salary_adj')
            s3 = pd.DataFrame([s1, s2]).min(axis=0)
            return self.regular_series(column, s3)

        elif column == 's_067_equity_ratio':
            s1 = self.get_column(df, 's_003_profit')
            s1 = s1.replace(0, np.inf)

            s2 = self.get_column(df, 's_018_profit_parent')
            s3 = s2 / s1
            s3[s3 > 1] = 1
            s3[s3 < 0.25] = 0.25
            return self.regular_series(column, s3)

        elif column == 's_068_market_value_adj':
            s1 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            s2 = self.fs_to_mvs('s_067_equity_ratio')
            s3 = s1 / s2
            return self.regular_series(column, s3)

        elif column == 's_069_dividend_rate':
            s1 = self.get_column(self.df_mvs, 'id_041_mvs_mc')
            s2 = self.fs_to_mvs('dv_001_dividend_value')
            # s2.fillna(method='ffill', inplace=True)
            s2.ffill(inplace=True)
            s3 = s2 / s1
            return self.regular_series(column, s3)

        elif column == 's_070_turnover_rate':
            s1 = self.get_column(self.df_mvs, 's_043_turnover_volume_ttm')
            s2 = self.fs_to_mvs('s_063_profit_salary2')
            s3 = self.fs_to_mvs('s_067_equity_ratio')
            s4 = s1 / s2 / s3
            return self.regular_series(column, s4)

    @staticmethod
    def get_return_year(pe, rate):
        a = 1 + rate
        b = (rate / (1 + rate) * pe + 1)

        a[a <= 0] = np.nan
        b.dropna(inplace=True)
        b[b <= 0] = np.nan

        y = np.log(b) / np.log(a)
        y.dropna(inplace=True)
        y[y <= 0] = np.nan
        return y.dropna()

    @staticmethod
    def get_delta_rate(s1, s2):
        s3 = s2 - s1
        s3[s3 <= 0] = np.nan
        s4 = s1 / s3
        s4.dropna(inplace=True)
        s4[s4 <= -50] = np.nan
        return s4.dropna()

    @staticmethod
    def sum_series(src_list):
        res_df = pd.concat(src_list, axis=1, sort=True)
        res_df = res_df.replace(0, np.nan)
        res_df = res_df.dropna(axis=0, how='all')
        s1 = res_df.apply(lambda x: x.sum(), axis=1)
        return s1

    @staticmethod
    def sum_columns(df, columns):
        res_df = df.loc[:, columns].copy()
        res_df = res_df.replace(0, np.nan)
        res_df = res_df.dropna(axis=0, how='all')
        s1 = res_df.apply(lambda x: x.sum(), axis=1)
        return s1

    @staticmethod
    def get_ttm(series: pd.Series, ttm):
        ret = series.dropna()
        ret = ret.rolling(ttm, min_periods=1).mean()
        return ret

    def fs_to_mvs(self, src, name='tmp'):
        dt_fs = self.get_column(self.df_fs, 'dt_fs')
        dt_mvs = self.get_column(self.df_mvs, 'dt_mvs')

        data = self.get_column(self.df_fs, src)
        data = data.reindex_like(pd.Series(index=dt_fs.values))

        if data.size > 1:
            if pd.isna(data.iloc[-1]):
                data.iloc[-1] = data.iloc[-2]

        data.fillna(np.inf, inplace=True)
        data.index = dt_fs.index

        index = pd.concat([dt_mvs, data], axis=1, sort=True).index
        data = data.reindex_like(pd.Series(index=index))

        # data.fillna(method='ffill', inplace=True)
        data.ffill(inplace=True)
        data[data == np.inf] = np.nan
        data = data[dt_mvs.values]
        data.name = name
        return data

    def smooth_data(self, name, src, delta=False, ttm=False, df=None):
        if df is None:
            df = self.df_fs

        # src_df = df.loc[:, [src]].copy().dropna()
        s1 = df.loc[:, src].copy().dropna()
        if delta is False:
            res = get_month_data(s1, name)
        else:
            res = get_month_delta(s1, name)
            if ttm is True:
                res = self.get_ttm(res, 4)
                # res = res.rolling(4, min_periods=1).mean()
        return self.regular_series(name, res)

    @staticmethod
    def regular_series(name, series):
        ret = series.dropna()
        ret.name = name
        ret = ret.astype('float64')
        return ret

    @staticmethod
    def return_df(df, new_df, add=False):
        if add is False:
            return new_df
        else:
            return pd.concat([df, new_df], axis=1, sort=True)

    @staticmethod
    def transform_pe(s1):
        v_list = []
        start = -10
        end = 50
        for r1 in np.arange(start, end+0.01, 0.01):
            if r1 <= 5:
                r2 = r1
            else:
                r2 = 5
            m = ValueModel(
                pe=10,
                rate=[r1, r2],
                year=[10, 10],
                rate0=-10,
            )

            v_list.append(m.value / 2)
            # m.show_value()

        res_list = []
        for val in s1.values:
            res = 0
            for index, x in enumerate(v_list):
                if val <= x:
                    res = index
                    break
            if val > v_list[-1]:
                res = len(v_list) - 1
            tmp = (res * 0.01 + start) / 100
            res_list.append(tmp)
        s2 = pd.Series(res_list, index=s1.index)

        # print(s2)
        return s2


class StandardFitModel:
    @classmethod
    def get_growth_rate2(cls, series, name, size):
        s1 = series.copy()
        s1[s1 <= 0] = np.nan
        s2 = np.log(s1)
        s3 = s2.rolling(size, min_periods=1).apply(
            lambda x: cls.window_method2(x, size),
            raw=True
        )
        s4 = np.exp(s3) ** 4 - 1
        s4.name = name
        # print(s1)
        # print(s4)

        return s4

    @classmethod
    def window_method2(cls, src, _):
        error = np.log(1.02) / 4
        arr_y = src
        val_nan = np.where(np.isnan(src))[0]
        if val_nan.size > 0:
            index = val_nan[-1] + 1
            arr_y = src[index:]

        error_min = np.inf
        res = np.nan
        while True:
            if arr_y.size <= 2:
                break
            arr_x = np.arange(arr_y.size)
            fit = np.polyfit(arr_x, arr_y, deg=1)
            arr_error = arr_y - (arr_x * fit[0] + fit[1])
            tmp_max = np.max(np.abs(arr_error))
            if tmp_max <= error_min:
                res = fit[0]
                error_min = tmp_max
                if error_min <= error:
                    break

            arr_y = arr_y[1:]

        return res

    @classmethod
    def get_growth_rate(cls, series, name, size):
        data = series
        data[data <= 0] = np.nan
        data3 = data.rolling(size, min_periods=1).apply(
            lambda x: cls.window_method(x, size),
            raw=True
        )
        data4 = np.exp(data3) - 1
        data4.name = name
        return data4

    @classmethod
    def window_method(cls, arr_y, size):
        arr_y = cls.config_window_array(arr_y, size)
        if arr_y is None:
            return 0
        delta = cls.curve_fit(arr_y) * 4
        return delta

    @classmethod
    def config_window_array(cls, arr_y, size):
        tmp = np.where(np.isnan(arr_y))[0]
        if tmp.size > 0:
            index = tmp[-1] + 1
            arr_y = arr_y[index:]

        if arr_y.size == 0:
            return None

        # size = 12
        pre = np.ones(size - arr_y.size) * arr_y[0]
        arr_y = np.append(pre, arr_y)

        return arr_y

    @classmethod
    def curve_fit(cls, arr_y):
        arr_x = np.arange(0, arr_y.size, 1)
        try:
            res = curve_fit(cls.curve_func, arr_x, arr_y)
        except Exception as e:
            print(e)
            return 0
        return res[0][0]

    @staticmethod
    def curve_func(x, a, b):
        return np.exp(a * x + b)


class DailyDataAnalysis(DataAnalysis):
    def __init__(self, df_fs: pd.DataFrame, df_mvs: pd.DataFrame, code=''):
        super().__init__(df_fs, df_mvs, code=code)

    def config_fs_data(self):

        index_list = [
            's_017_equity_parent',
            's_018_profit_parent',
            's_016_roe_parent',

            's_007_asset',
            's_002_equity',
            # 's_005_stocks',

            # 's_003_profit',
            # 's_010_main_profit',
            # 's_011_main_profit_rate',
            #
            # 's_001_roe',
            # 's_006_stocks_rate',
            #
            # 's_008_revenue',
            # 's_009_revenue_rate',

            # 's_019_monetary_asset',
            # 's_020_cap_asset',
            # 's_021_cap_expenditure',
            # 's_022_profit_no_expenditure',

            # 's_023_liabilities',
            # 's_024_real_liabilities',
            's_026_liquidation_asset',
            # 's_061_total_return_rate',
            's_063_profit_salary2',
            # 's_066_profit_salary_min',

            # 's_038_pay_for_long_term_asset',
            # 's_039_profit_adjust',
            # 's_040_profit_adjust2',
            # 's_041_profit_adjust_ttm',
            # 's_045_main_cost_adjust',
            # 's_046_profit_adjust3',

            # 'dv_001_dividend_value',
        ]

        df = self.df_fs
        for index in index_list:
            self.fs_add(self.get_column(df, index))

    def config_daily_data(self):

        self.config_sub_fs(DailyDataAnalysis)
        self.fs_add(self.get_column(self.df_fs, 'dt_fs'))
        self.mvs_add(self.get_column(self.df_mvs, 'dt_mvs'))

        df = self.df_mvs

        index_list1 = [
            # 's_004_pe',
            's_025_real_cost',
            # 's_026_holder_return_rate',
            # 's_027_pe_return_rate',
            's_028_market_value',
            # 's_037_real_pe_return_rate',
            # 's_044_turnover_volume',
        ]
        for index in index_list1:
            self.mvs_add(self.get_column(df, index))

        self.set_df()


# def test_analysis():
#     code = '603889'
#     # code = '600519'
#
#     df1 = load_df_from_mysql(code, 'fs')
#     df2 = load_df_from_mysql(code, 'mvs')
#
#     data = DataAnalysis(df1, df2)
#     # data.config_widget_data()
#     data.config_daily_data()
#     # s1 = data.df['s_028_market_value'].copy()
#     # print(s1)
#
#     # s2 = data.df['s_018_profit_parent'].copy().dropna()
#     # s2 = data.df['s_040_profit_adjust2'].copy().dropna()
#     # s2 = data.df['s_038_pay_for_long_term_asset'].copy().dropna()
#     # s2 = data.df['s_039_profit_adjust'].copy().dropna()
#     # print(s2)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    df_tmp = sql2df('600438')
    # a = pd.Series(range(100))
    # a = np.power(1.1, a)
    # a[3] = -1
    # a[6] = -1
    # print(a)
    # b = StandardFitModel.get_growth_rate(a, '', 20)
    # for i, v in b.iteritems():
    #     print(i, '%.2f' % v)
    # test_analysis()
    pass
