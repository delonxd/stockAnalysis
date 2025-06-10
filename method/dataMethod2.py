from discount.discountModel import ValueModel
from method.fileMethod import load_pkl, load_json_txt, write_json_txt
from method.sqlMethod import mysql2df
from method.mainMethod import get_database_table, get_code_type, get_code_country
# from method.logMethod import MainLog
from method.mainMethod import quick_search

import pandas as pd
import numpy as np
import re

import datetime as dt
from dateutil.relativedelta import relativedelta


def load_df_from_mysql(stock_code, data_type, fields=None, code_type=None):
    database, table = get_database_table(stock_code, data_type, code_type)
    ret = mysql2df(database=database, table=table, fields=fields)

    if database in [
        'fsData',
        'fsData_cn_bank',
        'eqData',
        'dvData',
        'marketData',
    ]:
        if 'Invalid date' in ret.index:
            ret.drop('Invalid date', inplace=True)
        ret.index = ret.index.str[:10]

    return ret


class StandardData:
    def __init__(self, code, analysis_type):
        self.code = code
        self.country = get_code_country(code)
        self.code_type = get_code_type(code)
        self.analysis_type = analysis_type

        self.df_fs = pd.DataFrame()
        self.df_fs_rp = pd.DataFrame()
        self.df_mvs = pd.DataFrame()

        self.item_mapping_table = dict()
        self.asset_dict = dict()
        self.equity_dict = dict()

        self.dt_fs = pd.Series()
        self.dt_mvs = pd.Series()
        self.split_date = list()
        self.fs_data_list = list()

    def copy(self):
        ret = StandardData(self.code, self.analysis_type)
        ret.code = self.code
        ret.country = self.country
        ret.code_type = self.code_type
        ret.analysis_type = self.analysis_type

        ret.df_fs = self.df_fs.copy()
        ret.df_fs_rp = self.df_fs_rp.copy()
        ret.df_mvs = self.df_mvs.copy()

        ret.item_mapping_table = self.item_mapping_table.copy()
        ret.asset_dict = self.asset_dict.copy()
        ret.equity_dict = self.equity_dict.copy()

        ret.dt_fs = self.dt_fs.copy()
        ret.dt_mvs = self.dt_mvs.copy()
        ret.split_date = self.split_date.copy()

        tmp = list()
        for fs_data in self.fs_data_list:
            tmp.append(fs_data.copy(parent=ret))
        ret.fs_data_list = tmp

        return ret

    def is_empty(self):

        if self.df_fs.size == 0 and self.dt_mvs.size == 0:
            return True
        else:
            return False

    def config_standard_data(self):
        self.get_code_data()
        self.config_fs_data()
        self.config_mvs_data()
        self.merge_df()

    def get_code_data(self):
        if self.country == 'cn':
            if self.analysis_type == 'widget':
                self.get_item_mapping_table()
                self.df_fs = load_df_from_mysql(self.code, 'fs', code_type=self.code_type)
                self.regular_fs_data()
                self.add_dv_data()
                self.df_mvs = load_df_from_mysql(self.code, 'mvs', code_type=self.code_type)
                self.regular_mvs_data()
                self.add_eq_data()
                # self.get_basic_data()

            elif self.analysis_type == 'daily':
                self.get_item_mapping_table()
                self.df_fs = load_df_from_mysql(self.code, 'fs', code_type=self.code_type)
                self.regular_fs_data()
                self.add_dv_data()
                fields = [
                    "date",
                    "id_041_mvs_mc",
                ]
                self.df_mvs = load_df_from_mysql(self.code, 'mvs',
                                                 fields=fields, code_type=self.code_type)
                self.df_mvs.columns = ['mvs-日期', 'mvs-市值']

        elif self.country == 'hk':
            if self.analysis_type == 'widget':
                self.get_item_mapping_table()
                self.df_fs = load_df_from_mysql(self.code, 'fs', code_type=self.code_type)
                self.regular_fs_data()
                # self.add_dv_data()
                # self.df_mvs = load_df_from_mysql(self.code, 'mvs', code_type=self.code_type)
                # self.regular_mvs_data()
                # self.add_eq_data()

                columns = [
                    'mvs-日期',
                    'mvs-市值',
                    'mvs-流通市值',
                    'mvs-股价',
                    'mvs-成交量',
                    'mvs-成交金额',
                    'eq_002_rate',
                    'eq_012_dilution_rate',
                ]
                self.df_mvs = pd.DataFrame([], columns=columns)

    def get_item_mapping_table(self):
        if self.country == 'cn':
            if self.code_type == 'non_financial':
                path = '../basicData/mappingTable/item_m_table_cn_non_financial.txt'
                self.item_mapping_table = load_json_txt(path, log=False)
            elif self.code_type == 'bank':
                path = '../basicData/mappingTable/item_m_table_cn_bank.txt'
                self.item_mapping_table = load_json_txt(path, log=False)
        elif self.country == 'hk':
            path = '../basicData/mappingTable/item_m_table_%s.txt' % self.code_type
            self.item_mapping_table = load_json_txt(path, log=False)

    @staticmethod
    def change_columns_header(df, cmp_table, m_table):
        org_columns = list()
        new_columns = list()
        for key, value in m_table.items():
            new_columns.append(key)
            if value is None:
                org_columns.append(cmp_table[key])
            else:
                org_columns.append(cmp_table[value])

        df = df.reindex(org_columns, axis="columns")
        df.columns = new_columns
        return df

    def regular_fs_data(self):
        if self.country == 'cn':
            if self.code_type == 'non_financial':
                path = '../basicData/chineseComparison/zh_cmp_table_fs_cn_org.txt'
                cmp_table = load_json_txt(path, log=False)
                path = '../basicData/mappingTable/fs_m_table_cn_non_financial.txt'
                m_table = load_json_txt(path, log=False)
                self.df_fs = self.change_columns_header(self.df_fs, cmp_table, m_table)
                self.df_fs = self.fs_fill_na(self.df_fs)

            elif self.code_type == 'bank':
                path = '../basicData/chineseComparison/zh_cmp_table_fs_cn_bank.txt'
                cmp_table = load_json_txt(path, log=False)
                path = '../basicData/mappingTable/fs_m_table_cn_bank.txt'
                m_table = load_json_txt(path, log=False)
                self.df_fs = self.change_columns_header(self.df_fs, cmp_table, m_table)
                indexes = self.df_fs["bs-持有至到期投资"] == self.df_fs["bs-以摊余成本计量的金融投资"]
                self.df_fs.loc[indexes, 'bs-持有至到期投资'] = np.nan
                self.df_fs = self.fs_fill_na(self.df_fs)

        elif self.country == 'hk':
            path = '../basicData/chineseComparison/zh_cmp_table_fs_%s.txt' % self.code_type
            cmp_table = load_json_txt(path, log=False)
            path = '../basicData/mappingTable/fs_m_table_%s.txt' % self.code_type
            m_table = load_json_txt(path, log=False)
            self.df_fs = self.change_columns_header(self.df_fs, cmp_table, m_table)
            self.df_fs = self.fs_fill_na(self.df_fs)

    def regular_mvs_data(self):
        if self.country == 'cn':
            path = '../basicData/chineseComparison/zh_cmp_table_mvs_cn.txt'
            cmp_table = load_json_txt(path, log=False)
            path = '../basicData/mappingTable/mvs_m_table_cn.txt'
            m_table = load_json_txt(path, log=False)
            self.df_mvs = self.change_columns_header(self.df_mvs, cmp_table, m_table)

    def fs_fill_na(self, df):
        table = self.item_mapping_table
        if self.country == 'cn':
            note_list = table['附注项目']
            ignore_list = table['处理空值排除项目'] + note_list
            df0 = df.filter(items=[x for x in df.columns if x not in ignore_list])
            df1 = df0.filter(regex='^bs-')
            df2 = df0.filter(regex='^cfs-')
            df3 = df0.filter(regex='^ps-')
            df4 = df.filter(items=[x for x in df.columns if x in note_list])
            df = self.fill_na_by_sub_df(df, df1)
            df = self.fill_na_by_sub_df(df, df2)
            df = self.fill_na_by_sub_df(df, df3)
            df = self.fill_na_by_sub_df(df, df4)

        elif self.country == 'hk':
            note_list = table['附注项目']
            ignore_list = table['处理空值排除项目'] + note_list
            df0 = df.filter(items=[x for x in df.columns if x not in ignore_list])
            df1 = df0.filter(regex='^bs-')
            # df2 = df0.filter(regex='^cfs-')
            # df3 = df0.filter(regex='^ps-')
            df4 = df.filter(items=[x for x in df.columns if x in note_list])
            df = self.fill_na_by_sub_df(df, df1)
            # df = self.fill_na_by_sub_df(df, df2)
            # df = self.fill_na_by_sub_df(df, df3)
            df = self.fill_na_by_sub_df(df, df4)
        return df

    @staticmethod
    def fill_na_by_sub_df(df, sub_df):
        df = df.copy()
        sub_df = sub_df.fillna(0)
        sub_df = sub_df[sub_df.ne(0).any(axis=1)]
        df[sub_df.columns] = sub_df
        return df

    def add_dv_data(self):
        code = self.code
        if self.country == 'cn':
            df = load_df_from_mysql(code, 'dv', fields=[
                'id', 'dividend', 'originalValue', 'status'
            ], code_type=self.code_type)
            df = df[df['dividend'] != 0]
            s0 = self.df_fs['bs-总股本'].copy().ffill()
            dv_dict = dict()
            for date, row in df.iterrows():
                st_date = self.report_date2standard([date]).iloc[0]
                if pd.isna(row['originalValue']):
                    if st_date != 'None' and st_date in s0.index:
                        dv_value = s0[st_date] * row['dividend']
                    else:
                        continue
                else:
                    dv_value = row['originalValue']

                if st_date in dv_dict:
                    dv_value = dv_value + dv_dict[st_date]
                dv_dict[st_date] = dv_value
            s1 = pd.Series(dv_dict, name='dv-分红金额')
            self.df_fs = pd.concat([self.df_fs, pd.DataFrame(s1)], axis=1, sort=True)

    def report_date2standard(self, s1):
        # 设置reportDate
        report_date = self.df_fs['报告日期'].copy().dropna()
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

    def add_eq_data(self):
        if self.country == 'cn':
            df = load_df_from_mysql(self.code, 'eq', code_type=self.code_type)
            ret = df.reindex(['id_002_rate', 'id_012_dilution_rate'], axis="columns")
            ret.columns = ['eq_002_rate', 'eq_012_dilution_rate']
            if ret.size > 0:
                ret['eq_002_rate'] = ret['eq_002_rate'] / ret.iloc[-1, 0]

        else:
            ret = pd.DataFrame()
        self.df_mvs = pd.concat([self.df_mvs, ret], axis=1, sort=True)
        return ret

    def get_basic_data(self):
        df1 = self.get_daily_data()
        df2 = self.get_mir_data()
        df3 = self.get_crypto_data()
        df4 = self.get_futures_data()
        ret = pd.concat([df1, df2, df3, df4], axis=1, sort=True)
        return ret

    @staticmethod
    def get_daily_data():
        path1 = "../basicData/daily_position.txt"
        path2 = "../basicData/dailyUpdate/latest/a007_change_rate.txt"
        res1 = load_json_txt(path1, log=False)
        res2 = load_json_txt(path2, log=False)

        s1 = pd.Series(res1, name='daily_position').dropna().astype('float64')
        s2 = pd.Series(res2, name='market_change_rate').dropna().astype('float64')
        return pd.concat([s1, s2], axis=1)

    @staticmethod
    def get_mir_data():
        # path = "..\\basicData\\nationalDebt\\mir_y10.txt"
        path1 = "../basicData/nationalDebt/mir_y10_akshare.txt"
        path2 = "../basicData/nationalDebt/mir_y10_us_akshare.txt"
        res1 = load_json_txt(path1, log=False)
        res2 = load_json_txt(path2, log=False)
        s1 = pd.Series(res1, name='mir_y10').dropna().astype('float64')
        s2 = pd.Series(res2, name='mir_y10_us').dropna().astype('float64')
        s3 = s1.values[0] / s1 * 128
        s3.name = 'mir_y10_ratio'
        s4 = s1.values[0] / s2 * 128
        s4.name = 'mir_y10_us_ratio'
        return pd.concat([s1, s2, s3, s4], axis=1)

    @staticmethod
    def get_crypto_data():
        path = "../basicData/crypto/crypto_btc_sz.txt"
        res = load_json_txt(path, log=False)
        s1 = pd.Series(res, name='cpt_btc').dropna().astype('float64')
        return pd.DataFrame(s1)

    @staticmethod
    def get_futures_data():
        path = "../basicData/futures/futures_prices_history.pkl"
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
        return df

    def merge_df(self):
        if self.country == 'cn':
            if self.analysis_type == 'widget':

                self.df_mvs = self.df_mvs.replace({
                    'mvs-市值': {0: np.nan},
                })
                self.df_fs = self.df_fs.replace({
                    'bs-第一大股东持仓占总股本比例': {0: np.nan},
                    'bs-前十大股东持仓占总股本比例': {0: np.nan},
                })

                self.df_fs_rp = pd.DataFrame()
                # print(self.df_fs_rp.shape)

            elif self.analysis_type == 'daily':
                columns = [
                    'dv_001_dividend_value',
                    's_002_equity',
                    's_016_roe_parent',
                    's_026_liquidation_asset',
                    's_063_profit_salary2',
                    's_067_equity_ratio',
                    's_079_capital_retention_ratio',
                    's_081_total_retention_ratio',
                ]
                self.df_fs = self.df_fs[columns]
                self.df_mvs = self.df_mvs[['s_028_market_value']]

                # df_list = [
                #     self.df_fs,
                #     self.df_mvs,
                # ]
                # self.df_total = pd.concat(df_list, axis=1, sort=True)
                # self.df_fs = pd.DataFrame()
                # self.df_mvs = pd.DataFrame()
                self.df_fs_rp = pd.DataFrame()

        elif self.country == 'hk':
            if self.analysis_type == 'widget':

                # print(self.df_fs)

                self.df_fs_rp = pd.DataFrame()

    @staticmethod
    def get_df_val(df: pd.DataFrame, column, default, shift=1, reverse=True):
        if column in df.columns:
            series = df.loc[:, column].copy().dropna()
            if reverse is True:
                if series.size >= shift:
                    return series.iloc[-shift]
            elif reverse is False:
                if series.size > shift:
                    return series.iloc[shift]
        return default

    @staticmethod
    def get_df_idx(df: pd.DataFrame, column, default, shift=1, reverse=True):
        if column in df.columns:
            series = df.loc[:, column].copy().dropna()
            series = series.index
            if reverse is True:
                if series.size >= shift:
                    return series[-shift]
            elif reverse is False:
                if series.size > shift:
                    return series[shift]
        return default

    def get_data_dict(self):
        df_fs = self.df_fs
        df_mvs = self.df_mvs
        data = dict()

        # todo 获取profile

        # 处理sql_df数据
        data['stock_price'] = self.get_df_val(df_mvs, 'mvs-股价', np.nan)
        data['real_pe'] = self.get_df_val(df_mvs, 's_034_real_pe', np.inf)
        data['market_value'] = self.get_df_val(df_mvs, 's_028_market_value', np.nan)
        data['market_value2'] = self.get_df_val(df_mvs, 's_028_market_value', np.nan, 2)
        data['turnover'] = self.get_df_val(df_mvs, 's_043_turnover_volume_ttm', 0)
        # data['real_cost'] = self.get_df_val(df_mvs, 's_025_real_cost', np.nan)
        data['dilution_rate'] = self.get_df_val(df_mvs, 'eq_012_dilution_rate', 0)

        data['listing_date'] = self.get_df_idx(df_mvs, 's_028_market_value', None, 0, False)
        data['yesterday_rise'] = data['market_value'] / data['market_value2'] - 1

        data['liquidation_asset'] = self.get_df_val(df_fs, 's_026_liquidation_asset', np.nan)
        data['equity'] = self.get_df_val(df_fs, 's_002_equity', np.nan)
        data['equity_ratio'] = self.get_df_val(df_fs, 's_067_equity_ratio', np.nan)
        data['liq_cost'] = self.get_df_val(df_fs, 's_071_additional_cost', np.nan)
        data['salary_cost'] = self.get_df_val(df_fs, 's_053_core_profit_salary', np.nan)
        data['profit_salary_min'] = self.get_df_val(df_fs, 's_063_profit_salary2', np.nan)
        data['cap_retention_ratio'] = self.get_df_val(df_fs, 's_081_total_retention_ratio', np.nan)

        data['last_fs_date'] = self.get_df_idx(df_fs, 's_063_profit_salary2', np.nan)
        data['last_fs_date2'] = self.get_df_idx(df_fs, 's_002_equity', np.nan)

        date2 = dt.date.today()
        data['predict_delta'] = 0
        if not pd.isna(data['last_fs_date']):
            date1 = dt.datetime.strptime(data['last_fs_date'], "%Y-%m-%d").date()
            data['predict_delta'] = (date2 - date1).days

        data['predict_delta2'] = 0
        if not pd.isna(data['last_fs_date2']):
            date1 = dt.datetime.strptime(data['last_fs_date2'], "%Y-%m-%d").date()
            data['predict_delta2'] = (date2 - date1).days

        data['dividend_return'] = self.get_df_val(df_mvs, 's_069_dividend_rate', 0)
        data['dividend_return'] = data['dividend_return'] * 100

        data['dividend_value'] = self.get_df_val(df_fs, 'dv_001_dividend_value', 0)
        data['dv_per_ps'] = data['dividend_value'] / data['profit_salary_min'] * 10

        tmp_ratio = 1 - data['cap_retention_ratio']
        tmp_ratio = 0 if tmp_ratio < 0 else tmp_ratio
        data['dv_value_safety'] = tmp_ratio * data['profit_salary_min'] / 10
        data['dv_return_safety'] = data['dv_value_safety'] / data['market_value'] * 100

        return data

    def config_fs_data(self):
        self.df_fs = self.df_fs.dropna(subset='bs-资产合计').copy()
        self.fs_data_list = self.split_df_fs()
        last_date = ''
        df_list = list()

        for fs_df in self.fs_data_list:
            fs_df.config_fs_data()
            df = fs_df.df
            sub_df = df.loc[df.index.values > last_date, :].copy()
            if sub_df.size > 0:
                df_list.append(sub_df)
                last_date = sub_df.index.values[-1]

        if len(df_list) == 0:
            fs_df = FsDataFrame(self, self.df_fs.copy(), '12-31')
            fs_df.config_fs_data()
            ret = fs_df.df
            self.fs_data_list = [fs_df]
        else:
            ret = pd.concat(df_list)
        ret = ret.sort_index()

        self.df_fs = ret

        if self.analysis_type == 'widget':
            # 预先config资产类、负债类
            columns = list()
            columns.extend(self.item_mapping_table['资产类'])
            columns.extend(self.item_mapping_table['负债类'])

            df_cfg = pd.DataFrame()
            for column in columns:
                s0 = self.get_month_data(column, 'config_%s' % column)
                df_cfg = pd.concat([df_cfg, s0], axis=1)
            df_cfg = df_cfg.sort_index()
            self.df_fs = pd.concat([self.df_fs, df_cfg], axis=1, sort=True)

        # print(self.df_fs)

    def split_df_fs(self):
        s0 = self.df_fs['bs-资产合计'].copy()

        sp_date_fiscal = list()
        sp_date_asset = list()
        ret = list()

        for lst in self.split_fs_by_fiscal():

            # todo split_date
            sp_date_fiscal.append(lst[-1][:10])
            fiscal_year = lst[1]

            index_list = list()
            val0 = np.inf

            for index in lst[2:]:
                val = s0[index]
                if val > 2 * val0:
                    sp_date_asset.append(index_list[-1][:10])

                    df_tmp = self.df_fs.loc[index_list, :].copy()
                    df_tmp.index = df_tmp.index.str[:10]
                    ret.append(FsDataFrame(self, df_tmp, fiscal_year))
                    index_list = list()

                index_list.append(index)
                val0 = val

            if len(index_list) > 0:
                df_tmp = self.df_fs.loc[index_list, :].copy()
                df_tmp.index = df_tmp.index.str[:10]
                ret.append(FsDataFrame(self, df_tmp, fiscal_year))

        return ret

    def split_fs_by_fiscal(self):
        if self.country == 'cn':
            ret = self.df_fs.index.tolist()
            if len(ret) > 0:
                ret.insert(0, '12-31')
                ret.insert(0, ret[-1])
                ret = [ret]
        else:
            df = self.df_fs
            table = dict()
            for index in df.index:
                res = re.findall(r'\((.*)\)$', index)
                fiscal_year = res[0]
                fiscal_year = fiscal_year.rjust(5, '0')

                tmp = table.get(fiscal_year)
                if tmp is None:
                    table[fiscal_year] = [index]
                else:
                    tmp.append(index)
                    table[fiscal_year] = tmp

            ret = list()
            for fiscal_year, lst in table.items():
                year0 = 0
                for index in lst:
                    year = int(index[:4])
                    if (year-year0) >= 4:
                        sub = [index[:10], fiscal_year, index]
                        ret.append(sub)
                    else:
                        sub = ret[-1]
                        sub.append(index)
                        ret[-1] = sub
                    year0 = year
            ret.sort()
        return ret

    def get_month_data(self, column: str, name):
        if column not in self.df_fs.columns:
            return pd.Series()
        s1 = self.df_fs.loc[:, column].copy().dropna()
        fs_data = self.fs_data_list[0]
        ret = fs_data.get_month_data(s1, name, fs_index=self.df_fs.index)
        return ret

    def get_month_delta(self, column: str, name):
        last_date = ''
        s_list = []
        for fs_data in self.fs_data_list:
            if column not in fs_data.df.columns:
                continue
            s1 = fs_data.df.loc[:, column].copy().dropna()
            s2 = fs_data.get_month_delta(s1, name)
            s2 = s2.loc[s2.index.values > last_date].copy()
            if s2.size > 0:
                last_date = s2.index.values[-1]
                s_list.append(s2)
        if len(s_list) == 0:
            ret = pd.Series()
        else:
            ret = pd.concat(s_list, sort=True)
        ret.name = name
        return ret

    def config_dt_fs_mvs(self):
        # fs日期
        df = self.df_fs.copy().dropna(subset='报告日期')
        df.sort_index(inplace=True)
        df['报告日期'] = df['报告日期'].apply(lambda x: x[:10])
        df['标准日期'] = df['标准日期'].apply(lambda x: x[:10])

        df = df.set_index('报告日期', drop=False)
        df = df[~df.index.duplicated(keep='last')]

        self.dt_fs = df['标准日期'].copy().dropna()

        # mvs日期
        mvs_dates = self.df_mvs['mvs-日期'].copy().dropna()
        self.dt_mvs = mvs_dates.copy().apply(lambda x: x[:10])

        # 合并报表
        self.df_fs_rp = pd.concat([df, mvs_dates], axis=1, sort=True)

    def config_mvs_data(self):
        self.config_dt_fs_mvs()

        if self.analysis_type == 'widget':
            columns = [
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
                # 'market_change_rate',

                's_069_dividend_rate',
                's_070_turnover_rate',
            ]
        elif self.analysis_type == 'daily':
            columns = [
                # 's_004_pe',
                # 's_025_real_cost',
                # 's_026_holder_return_rate',
                # 's_027_pe_return_rate',
                's_028_market_value',
                # 's_037_real_pe_return_rate',
                # 's_044_turnover_volume',
            ]
        else:
            raise KeyboardInterrupt('config_mvs_data类型错误: %s' % self.analysis_type)

        for column in columns:
            self.get_column(column)

    def get_column(self, column):
        df = self.df_mvs
        if column in df.columns:
            return df[column].copy().dropna()

        if column == 's_004_pe':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column('mvs-市值')
            ret = self.regular_series(column, s2 / s1)

        elif column == 's_025_real_cost':
            s1 = self.fs_to_mvs('s_026_liquidation_asset')
            s3 = self.fs_to_mvs('s_002_equity')
            s2 = self.get_column('s_068_market_value_adj')
            ret = self.regular_series(column, s2 - s1 + s3)

        elif column == 's_027_pe_return_rate':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column('mvs-市值')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_028_market_value':
            s1 = self.get_column('mvs-市值')
            ret = self.regular_series(column, s1)

        elif column == 's_034_real_pe':
            # s1 = self.fs_to_mvs('s_018_profit_parent')
            s1 = self.fs_to_mvs('s_051_core_profit')
            s2 = self.get_column('s_025_real_cost')
            ret = self.regular_series(column, s2 / s1)

        elif column == 's_035_pe2rate':
            # s1 = self.get_column(df, 's_004_pe')
            s1 = self.get_column('s_034_real_pe')
            s2 = self.transform_pe(s1)
            ret = self.regular_series(column, s2)

        elif column == 's_036_real_pe2rate':
            s1 = self.get_column('s_034_real_pe')
            s2 = self.transform_pe(s1/2)
            ret = self.regular_series(column, s2)

        elif column == 's_037_real_pe_return_rate':
            s1 = self.fs_to_mvs('s_018_profit_parent')
            s2 = self.get_column('s_025_real_cost')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_043_turnover_volume_ttm':
            s1 = self.get_column('mvs-市值')
            s2 = self.get_column('mvs-流通市值')
            s3 = self.get_column('mvs-成交金额')
            s4 = s1 / s2 * s3 * 10
            s4 = self.get_ttm(s4, 20)
            ret = self.regular_series(column, s4)

        elif column == 's_044_turnover_volume':
            s1 = self.get_column('mvs-市值')
            s2 = self.get_column('mvs-流通市值')
            s3 = self.get_column('mvs-成交金额')
            ret = self.regular_series(column, s1 / s2 * s3)

        elif column == 's_068_market_value_adj':
            s1 = self.get_column('mvs-市值')
            s2 = self.fs_to_mvs('s_067_equity_ratio')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_069_dividend_rate':
            s1 = self.get_column('mvs-市值')
            s2 = self.fs_to_mvs('dv_001_dividend_value')
            ret = self.regular_series(column, s2 / s1)

        elif column == 's_070_turnover_rate':
            s1 = self.get_column('s_043_turnover_volume_ttm')
            s2 = self.fs_to_mvs('s_063_profit_salary2')
            s3 = self.fs_to_mvs('s_067_equity_ratio')
            ret = self.regular_series(column, s1 / s2 / s3)

        else:
            raise KeyboardInterrupt(column)

        self.df_mvs = pd.concat([self.df_mvs, pd.DataFrame(ret)], axis=1, sort=True)
        return self.df_mvs[column].copy().dropna()

    def fs_to_mvs(self, column, name='tmp'):
        # todo对比原始代码，确认结果是否一致
        s1 = self.df_fs_rp[column].copy().ffill()
        s1.name = name
        return s1

    @staticmethod
    def transform_pe(s1):
        start = -10
        end = 50
        v_list = []
        for r1 in np.arange(start, end + 0.01, 0.01):
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

        s2 = s1.apply(lambda x: quick_search(x, v_list))
        s2 = (s2 * 0.01 - 10) / 100
        return s2

    @staticmethod
    def get_ttm(series: pd.Series, ttm):
        ret = series.dropna()
        ret = ret.rolling(ttm, min_periods=1).mean()
        return ret

    @staticmethod
    def regular_series(name, series):
        ret = series.dropna()
        ret.name = name
        ret = ret.astype('float64')
        return ret


class FsDataFrame:
    def __init__(self, parent: StandardData, df, fiscal_year):
        self.parent = parent
        self.df = df
        self.fiscal_year = fiscal_year
        self.fs_index = []

    def copy(self, parent):
        ret = FsDataFrame(parent, self.df.copy(), self.fiscal_year)
        ret.fs_index = self.fs_index.copy()
        return ret

    def init_index(self):
        if self.df.size == 0:
            return

        index_start = self.df.index.values[0]
        index_end = self.df.index.values[-1]
        month0 = int(self.fiscal_year.split('-')[0])

        date0 = dt.datetime.strptime(index_start, "%Y-%m-%d")
        delta = (month0 - date0.month) % 12 - 9 + 1
        date = dt.date(date0.year, date0.month, 1)
        date = date + relativedelta(months=delta)

        fs_index = []
        while True:
            tmp = date + relativedelta(days=-1)
            index = tmp.strftime("%Y-%m-%d")
            fs_index.append(index)
            if index >= index_end:
                break
            date = date + relativedelta(months=3)
        self.fs_index = fs_index

    @property
    def country(self):
        return self.parent.country

    @property
    def code_type(self):
        return self.parent.code_type

    @property
    def item_mapping_table(self):
        return self.parent.item_mapping_table

    def get_month_data(self, src: pd.Series, name, fs_index=None):
        if fs_index is None:
            fs_index = self.fs_index
        s0 = src.reindex(fs_index).copy()
        values = []
        val0 = np.nan
        counter = 0
        for val in s0.values:
            if pd.isna(val):
                counter += 1
            else:
                delta = (val - val0) / (counter + 1)
                values.extend([(val0 + x * delta) for x in range(counter)])
                values.append(val)
                val0 = val
                counter = 0
        values.extend([np.nan for _ in range(counter)])
        ret = pd.Series(values, index=fs_index, name=name)
        ret = ret.dropna()
        return ret

    def get_month_delta(self, src: pd.Series, name):
        if src.size == 0:
            return pd.Series([], index=[], name=name)

        fs_index = self.fs_index
        month0 = int(self.fiscal_year[:2])

        s0 = src.reindex(fs_index).copy()
        s0 = s0[::-1]

        values = []
        val0 = np.nan
        counter = 1
        for idx, val in s0.items():
            if int(idx[5:7]) == month0:
                delta = val0 / counter * 4
                values.extend([delta for _ in range(counter)])
                counter = 1
                val0 = val

            elif pd.isna(val):
                counter += 1
            else:
                delta = (val0 - val) / counter * 4
                values.extend([delta for _ in range(counter)])
                counter = 1
                val0 = val

        delta = val0 / counter * 4
        values.extend([delta for _ in range(counter)])
        values.pop(0)
        values = values[::-1]

        ret = pd.Series(values, index=fs_index, name=name)

        id1 = ret.first_valid_index()
        id2 = ret.last_valid_index()
        if id1 is None or id2 is None:
            return pd.Series([], index=[], name=name)

        pos1 = ret.index.get_loc(id1)
        pos2 = ret.index.get_loc(id2)
        ret = ret.iloc[pos1:pos2 + 1].bfill()

        return ret

    def regular_series(self, *args, **kwargs):
        return self.parent.regular_series(*args, **kwargs)

    def get_ttm(self, *args, **kwargs):
        return self.parent.get_ttm(*args, **kwargs)

    def config_fs_data(self):
        self.init_index()
        analysis_type = self.parent.analysis_type
        if analysis_type == 'widget':
            columns = [
                'dv_001_dividend_value',
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

                # todo s_009_revenue_rate
                # 's_009_revenue_rate',

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
                's_071_additional_cost',

                # 's_038_pay_for_long_term_asset',
                # 's_039_profit_adjust',
                # 's_040_profit_adjust2',
                # 's_041_profit_adjust_ttm',
                # 's_045_main_cost_adjust',
                # 's_046_profit_adjust3',

                's_086_rental_expense',
                's_051_core_profit',

                's_048_profit_tax',
                's_049_pf_tx_invest',
                's_050_pf_tx_iv_outer',

                's_052_core_profit_asset',
                's_053_core_profit_salary',
                's_054_gross_profit_rate',
                's_055_gross_cost',
                's_056_inventory_turnaround',
                's_057_core_roe',
                's_058_equity_adj',
                's_059_total_expend',

                # todo s_060_total_expend_rate
                # 's_060_total_expend_rate',

                's_061_total_return_rate',

                's_063_profit_salary2',
                's_064_profit_salary3',
                's_065_profit_salary_adj',
                's_066_profit_salary_min',

                's_072_core_profit_adj_inventory',
                's_073_dividend_payout_ratio',
                's_075_capital_dividend_ratio',
                's_074_profit_growth_rate',

                's_076_financing_cash_inflows',
                's_077_financing_cash_outflows',
                's_078_total_cash_inflows',
                's_080_capital_retention',
                's_079_capital_retention_ratio',
                's_081_total_retention_ratio',

                's_082_net_capital_delta',
                's_083_sum_dv_net_cap_delta',
                's_084_capital_reinvestment',
                's_085_total_retention_ratio2',

                's_087_liabilities_ratio',
                's_088_other_income',
                's_089_income_tax_expense',
                's_090_invest_income',
            ]

        elif analysis_type == 'daily':
            columns = [
                'dv_001_dividend_value',

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

                's_067_equity_ratio',

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

                's_080_capital_retention',
                's_079_capital_retention_ratio',
                's_081_total_retention_ratio',
            ]
        else:
            raise KeyboardInterrupt('config_fs_data类型错误: %s' % analysis_type)

        for column in columns:
            self.get_column(column)

    def get_column(self, column):
        df = self.df
        if column in df.columns:
            return df[column].copy().dropna()

        ret = self.regular_series(column, pd.Series())
        if column == 'dv_001_dividend_value':
            if self.country == 'cn':
                s1 = self.get_column('dv-分红金额')
                s2 = self.get_column('s_003_profit')
                s2 = s1.reindex_like(s2)

                s_tmp = s2.loc[s2.last_valid_index():]
                if s_tmp.size > 4:
                    index_tmp = 4 - s_tmp.size
                    s2 = s2.iloc[:index_tmp]
                s3 = s2.fillna(0)
                s3 = self.get_ttm(s3, 4) * 4
                ret = self.regular_series(column, s3)

        elif column == 's_001_roe':
            s1 = self.get_column('s_003_profit')
            s2 = self.get_column('s_002_equity')
            s3 = self.get_roe(s1, s2)
            ret = self.regular_series(column, s3)

        elif column == 's_002_equity':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'bs-所有者权益合计')
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'bs-总权益')

        elif column == 's_003_profit':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'ps-净利润', delta=True, ttm=True)
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'ps-除税后溢利', delta=True, ttm=True)

        elif column == 's_005_receivables_surplus':
            if self.country == 'cn':
                if self.code_type == 'non_financial':
                    s1 = self.get_column('bs-应收票据及应收账款')
                    s2 = self.get_column('bs-应收票据及应收账款-(其中)应收票据')
                    s3 = self.get_column('bs-应收票据及应收账款-(其中)应收账款')
                    s4 = s1 - (s2 + s3)
                    s5 = self.get_month_data(s4, column)
                    ret = self.regular_series(column, s5)

        elif column == 's_007_asset':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'bs-资产合计')
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'bs-总资产')

        elif column == 's_008_revenue':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'ps-营业总收入', delta=True, ttm=True)
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'ps-营运收入', delta=True, ttm=True)

        # elif column == 's_009_revenue_rate':
        #     s1 = self.get_column(df, 's_008_revenue')
        #     s2 = StandardFitModel.get_growth_rate(s1, column, 12)
        #     return self.regular_series(column, s2)

        elif column == 's_010_cash_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['现金资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_011_insurance_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['保险资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_012_financial_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['流动性金融资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_013_invest_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['非流动性投资资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_014_turnover_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['经营资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_015_inventory_asset':
            # todo 重新对资产分类
            s1 = self.sum_columns(df, self.item_mapping_table['存货资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_016_roe_parent':
            s1 = self.get_column('s_018_profit_parent')
            s2 = self.get_column('s_017_equity_parent')
            s3 = self.get_roe(s1, s2)
            ret = self.regular_series(column, s3)

        elif column == 's_017_equity_parent':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'bs-归属于母公司普通股股东权益合计')
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'bs-股东权益')

        elif column == 's_018_profit_parent':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'ps-归属于母公司普通股股东的净利润', delta=True, ttm=True)
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'ps-股东应占溢利', delta=True, ttm=True)

        elif column == 's_021_fixed_asset':
            s1 = self.sum_columns(df, self.item_mapping_table['固定资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_022_capitalized_asset':
            # todo 重新对资产分类
            s1 = self.sum_columns(df, self.item_mapping_table['资本化资产'])
            s2 = self.get_month_data(s1, column)
            ret = self.regular_series(column, s2)

        elif column == 's_023_liabilities':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'bs-负债合计')
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'bs-总负债')

        elif column == 's_024_real_liabilities':
            tmp = list()
            tmp.append(self.get_column('s_010_cash_asset') * -1)
            tmp.append(self.get_column('s_011_insurance_asset') * -1)
            tmp.append(self.get_column('s_012_financial_asset') * -1)
            tmp.append(self.get_column('s_023_liabilities'))

            df1 = pd.concat(tmp, axis=1, sort=True)
            s1 = df1.apply(lambda x: x.sum(), axis=1)
            ret = self.regular_series(column, s1)

        elif column == 's_026_liquidation_asset':
            tmp = list()
            # 净营运资本（net working capital）
            if self.country == 'cn':
                if self.code_type == 'non_financial':
                    s0 = self.smooth_data(column, 'bs-应收票据及应收账款')
                    tmp.append(s0 * 0.6)
                elif self.code_type == 'bank':
                    s0 = self.smooth_data(column, 'bs-应收利息')
                    tmp.append(s0 * 0.6)
                tmp.append(self.smooth_data(column, 'bs-租赁负债'))

            tmp.append(self.get_column('s_010_cash_asset'))
            tmp.append(self.get_column('s_011_insurance_asset'))
            tmp.append(self.get_column('s_012_financial_asset'))
            tmp.append(self.get_column('s_013_invest_asset') * 0.5)
            tmp.append(self.get_column('s_014_turnover_asset') * 0.2)
            tmp.append(self.get_column('s_015_inventory_asset') * 0.2)
            tmp.append(self.get_column('s_021_fixed_asset') * 0.1)
            tmp.append(self.get_column('s_023_liabilities') * -1)

            df1 = pd.concat(tmp, axis=1, sort=True)
            s1 = df1.apply(lambda x: x.sum(), axis=1)
            ret = self.regular_series(column, s1)

        elif column == 's_047_gross_cost':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'ps-营业成本', delta=True, ttm=True)
            elif self.country == 'hk':
                s1 = self.smooth_data(column, 'ps-营运收入', delta=True, ttm=True)
                s2 = self.smooth_data(column, 'ps-毛利', delta=True, ttm=True)
                ret = self.regular_series(column, s1 - s2)

        elif column == 's_048_profit_tax':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_089_income_tax_expense')
            ret = self.regular_series(column, s1 + s2)

        elif column == 's_049_pf_tx_invest':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_090_invest_income')
            ret = self.regular_series(column, s1 + s2)

        elif column == 's_050_pf_tx_iv_outer':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_088_other_income')
            ret = self.regular_series(column, s1 + s2)

        elif column == 's_051_core_profit':
            if self.country == 'cn':
                if self.code_type == 'non_financial':
                    columns = [
                        'cfs-财务费用',
                        'cfs-递延所得税资产减少',
                        'cfs-递延所得税负债增加',
                        'cfs-存货的减少',
                        'cfs-经营性应收项目的减少',
                        'cfs-经营性应付项目的增加',
                        'cfs-其他',
                    ]
                    s1 = self.get_column('cfs-经营活动产生的现金流量净额')
                    s2 = self.get_column('s_088_other_income')
                    s3 = self.sum_columns(df, columns)
                    s4 = self.get_column('s_086_rental_expense')
                    s5 = (s1 - s2 - s3 - s4).dropna()
                    ttm = self.get_ttm(self.get_month_delta(s5, column), 4)
                    ret = self.regular_series(column, ttm)

                elif self.code_type == 'bank':
                    columns1 = [
                        'ps-净利息收入',
                        'ps-手续费及佣金净收入',
                    ]
                    columns2 = [
                        'ps-税金及附加',
                        'ps-减：所得税费用',
                    ]
                    s1 = self.sum_columns(df, columns1)
                    s2 = self.sum_columns(df, columns2)
                    s3 = (s1 - s2).dropna()
                    s4 = self.get_ttm(self.get_month_delta(s3, column), 4)
                    s5 = self.get_column('s_053_core_profit_salary')
                    ret = self.regular_series(column, s4 - s5)

        elif column == 's_052_core_profit_asset':
            if self.country == 'cn':
                s1 = self.get_column('cfs-吸收投资收到的现金')
                s2 = self.get_column('cfs-购建固定资产、无形资产及其他长期资产所支付的现金')
                s3 = self.get_ttm(self.get_month_delta(s1 - s2, 's2'), 4)
                s4 = self.get_column('s_051_core_profit')
                ret = self.regular_series(column, s3 + s4)

        elif column == 's_053_core_profit_salary':
            if self.country == 'cn':
                s1 = self.sum_columns(df, self.item_mapping_table['应付薪酬类'])
                s1 = self.get_month_data(s1, column)
                s1 = self.get_ttm((s1 - s1.shift(1)) * 4, 4)
                s2 = self.smooth_data(column, 'cfs-支付给职工及为职工支付的现金', delta=True, ttm=True)

                df1 = pd.DataFrame([s1, s2])
                s3 = df1.apply(lambda x: x.sum(), axis=0)
                ret = self.regular_series(column, s3)

        elif column == 's_054_gross_profit_rate':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_008_revenue')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_055_gross_cost':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_008_revenue')
            ret = self.regular_series(column, s2 - s1)

        elif column == 's_056_inventory_turnaround':
            if self.country == 'cn':
                if self.code_type == 'non_financial':
                    s1 = self.get_column('bs-存货')
                    s1 = self.get_ttm(self.get_month_data(s1, 's1'), 4)
                    s2 = self.get_column('s_055_gross_cost')
                    ret = self.regular_series(column, s1 / s2)

        elif column == 's_057_core_roe':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_002_equity')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_058_equity_adj':
            # todo 重做
            if self.country == 'cn':
                columns = [
                    'cfs-加：资产减值准备',
                    'cfs-信用减值损失',
                    'cfs-固定资产折旧、油气资产折耗、生产性生物资产折旧',
                    'cfs-投资性房地产的折旧及摊销',
                    'cfs-无形资产摊销',
                    'cfs-长期待摊费用摊销',
                    'cfs-固定资产报废损失',
                ]
                s1 = self.sum_columns(df, columns)
                s2 = self.get_month_delta(s1, 's2')
                s3 = s2.cumsum()
                s4 = self.get_column('s_002_equity')
                ret = self.regular_series(column, s3 / 4 + s4)

        elif column == 's_059_total_expend':
            s1 = self.get_column('s_058_equity_adj')
            s2 = self.get_column('s_026_liquidation_asset')
            ret = self.regular_series(column, s1 - s2)

        # todo 重做
        # elif column == 's_060_total_expend_rate':
        #     s1 = self.get_column(df, 's_058_equity_adj')
        #     s2 = StandardFitModel.get_growth_rate(s1, column, 12)
        #     return self.regular_series(column, s2)

        elif column == 's_061_total_return_rate':
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_058_equity_adj')
            ret = self.regular_series(column, s1 / s2)

        # todo 删除
        # elif column == 's_062_equity_ratio':
        #     s1 = self.get_column('s_051_core_profit')
        #     s2 = self.get_column('s_058_equity_adj')
        #     return self.regular_series(column, s1 / s2)

        elif column == 's_063_profit_salary2':
            # todo 调整比例
            s1 = self.get_column('s_051_core_profit')
            s2 = self.get_column('s_053_core_profit_salary')
            s3 = s1 + s2
            s3 = s3 / 0.1
            ret = self.regular_series(column, s3)

        elif column == 's_064_profit_salary3':
            s1 = self.get_column('s_052_core_profit_asset')
            s2 = self.get_column('s_053_core_profit_salary')
            s3 = s1 + s2
            s3 = s3 / 0.1
            ret = self.regular_series(column, s3)

        elif column == 's_065_profit_salary_adj':
            s1 = self.get_column('s_063_profit_salary2')
            s2 = self.get_column('s_003_profit')
            s3 = self.get_column('s_018_profit_parent')
            s4 = s1 / s2 * s3
            ret = self.regular_series(column, s4)

        elif column == 's_066_profit_salary_min':
            s1 = self.get_column('s_063_profit_salary2')
            s2 = self.get_column('s_065_profit_salary_adj')
            s3 = pd.DataFrame([s1, s2]).min(axis=0)
            ret = self.regular_series(column, s3)

        elif column == 's_067_equity_ratio':
            s1 = self.get_column('s_003_profit')
            s1 = s1.replace(0, np.inf)

            s2 = self.get_column('s_018_profit_parent')
            s3 = s2 / s1
            s3[s3 > 1] = 1
            s3[s3 < 0.25] = 0.25
            ret = self.regular_series(column, s3)

        elif column == 's_071_additional_cost':
            s1 = self.get_column('s_026_liquidation_asset')
            s2 = self.get_column('s_002_equity')
            ret = self.regular_series(column, s2 - s1)

        elif column == 's_072_core_profit_adj_inventory':
            if self.country == 'cn':
                columns = [
                    'cfs-财务费用',
                    'cfs-递延所得税资产减少',
                    'cfs-递延所得税负债增加',
                    'cfs-存货的减少',
                    'cfs-经营性应收项目的减少',
                    'cfs-经营性应付项目的增加',
                    'cfs-其他',
                ]
                s1 = self.get_column('cfs-经营活动产生的现金流量净额')
                s2 = self.get_column('s_088_other_income')
                s3 = self.sum_columns(df, columns)
                s4 = self.get_column('s_086_rental_expense')
                s5 = (s1 - s2 - s3 - s4).dropna()
                ttm = self.get_ttm(self.get_month_delta(s5, column), 4)

                s1 = self.regular_series(column, ttm)
                s2 = self.get_column('s_053_core_profit_salary')
                s3 = s1 + s2
                s3 = s3 / 0.1
                ret = self.regular_series(column, s3)

        elif column == 's_073_dividend_payout_ratio':
            s1 = self.get_column('dv_001_dividend_value')
            s2 = self.get_column('s_018_profit_parent')
            s3 = s1 / s2
            s3[s3 > 2] = 2
            s3[s3 < 0] = 0
            ret = self.regular_series(column, s3)

        elif column == 's_074_profit_growth_rate':
            s1 = self.get_column('s_075_capital_dividend_ratio')
            s1[s1 > 1] = 1
            s1 = (1 - s1)/5
            ret = self.regular_series(column, s1)

        elif column == 's_075_capital_dividend_ratio':
            s1 = self.get_column('dv_001_dividend_value')
            s2 = self.get_column('s_063_profit_salary2')
            # s3 = self.get_column(df, 's_067_equity_ratio')
            s4 = s1 / s2 / 0.1
            ret = self.regular_series(column, s4)

        elif column == 's_076_financing_cash_inflows':
            # todo 检查 s_026_liquidation_asset 算法
            if self.country == 'cn':
                self.get_column('s_026_liquidation_asset')
                df1 = df.dropna(subset='s_026_liquidation_asset').copy()
                s1 = df1['cfs-吸收投资收到的现金'].copy().fillna(0)
                ttm = self.get_ttm(self.get_month_delta(s1, column), 4)
                s1 = ttm / 0.1
                ret = self.regular_series(column, s1)

        elif column == 's_077_financing_cash_outflows':
            self.get_column('s_026_liquidation_asset')
            df1 = df.dropna(subset='s_026_liquidation_asset').copy()
            s1 = df1['dv_001_dividend_value'].copy().fillna(0)
            s1 = s1 / 0.1
            ret = self.regular_series(column, s1)

        elif column == 's_078_total_cash_inflows':
            s1 = self.get_column('s_076_financing_cash_inflows')
            s2 = self.get_column('s_063_profit_salary2')
            s3 = s1 + s2
            ret = self.regular_series(column, s3)

        elif column == 's_079_capital_retention_ratio':
            s1 = self.get_column('s_080_capital_retention')
            s2 = self.get_column('s_063_profit_salary2')
            s2[s2 < 0] = np.nan
            s3 = s1 / s2
            s3[s3 < 0] = 0
            ret = self.regular_series(column, s3)

        elif column == 's_080_capital_retention':
            s1 = self.get_column('s_078_total_cash_inflows')
            s2 = self.get_column('s_077_financing_cash_outflows')
            s3 = s1 - s2
            ret = self.regular_series(column, s3)

        elif column == 's_081_total_retention_ratio':
            s1 = self.get_column('s_080_capital_retention').cumsum()
            s2 = self.get_column('s_063_profit_salary2').cumsum()
            s2[s2 < 0] = np.nan
            s3 = s1 / s2
            s3[s3 < 0] = 0
            s3 = s3.fillna(np.inf)
            ret = self.regular_series(column, s3)

        elif column == 's_082_net_capital_delta':
            # s1 = self.get_column('s_026_liquidation_asset')
            s1 = self.get_column('s_091_net_working_capital')
            s2 = self.get_ttm((s1 - s1.shift(1)) * 4, 4)
            ret = self.regular_series(column, s2)

        elif column == 's_083_sum_dv_net_cap_delta':
            self.get_column('s_082_net_capital_delta')
            df1 = df.dropna(subset='s_082_net_capital_delta').copy()
            s1 = df1['dv_001_dividend_value'].copy().fillna(0)
            s2 = df1['s_082_net_capital_delta'].copy()
            s3 = df1['s_076_financing_cash_inflows'].copy()
            s4 = df1['s_067_equity_ratio'].copy().ffill()

            s5 = s1 + (s2 - s3/10)*s4
            ret = self.regular_series(column, s5)

        elif column == 's_084_capital_reinvestment':
            self.get_column('s_082_net_capital_delta')
            df1 = df.dropna(subset='s_082_net_capital_delta').copy()
            s1 = df1['s_076_financing_cash_inflows'].copy()
            s2 = df1['s_063_profit_salary2'].copy().ffill()
            s3 = df1['s_077_financing_cash_outflows'].copy()
            s4 = df1['s_082_net_capital_delta'].copy()

            s5 = s1 + s2 - s3 - s4 / 0.1
            ret = self.regular_series(column, s5)

        elif column == 's_085_total_retention_ratio2':
            self.get_column('s_082_net_capital_delta')
            df1 = df.dropna(subset='s_082_net_capital_delta').copy()
            s1 = df1['s_084_capital_reinvestment'].copy().cumsum()
            s2 = df1['s_063_profit_salary2'].copy().ffill().cumsum()
            s2[s2 < 0] = np.nan
            s3 = s1 / s2
            s3[s3 < 0] = 0
            s3 = s3.fillna(np.inf)
            ret = self.regular_series(column, s3)

        elif column == 's_086_rental_expense':
            if self.country == 'cn':
                df1 = df.dropna(subset='cfs-净利润').copy()
                s1 = df1['bs-使用权资产'].copy().fillna(0)
                s2 = df1['bs-租赁负债'].copy().fillna(0)
                s3 = df1['cfs-使用权资产摊销'].copy().fillna(0)

                s1 = (s1 - s1.shift(1)).fillna(0)
                s2 = (s2 - s2.shift(1)).fillna(0)
                s4 = self.get_month_data(s1 + s3 - s2, 's4')
                ret = self.regular_series(column, s4)

        elif column == 's_087_liabilities_ratio':
            s1 = self.get_column('s_023_liabilities')
            s2 = self.get_column('s_007_asset')
            ret = self.regular_series(column, s1 / s2)

        elif column == 's_088_other_income':
            s1 = self.sum_columns(df, self.item_mapping_table['其他收入类'])
            s2 = self.sum_columns(df, self.item_mapping_table['其他支出类'])
            ret = self.regular_series(column, s1 - s2)

        elif column == 's_089_income_tax_expense':
            if self.country == 'cn':
                ret = self.smooth_data(column, 'ps-减：所得税费用', delta=True, ttm=True)
            elif self.country == 'hk':
                ret = self.smooth_data(column, 'ps-税项', delta=True, ttm=True)

        elif column == 's_090_invest_income':
            s1 = self.sum_columns(df, self.item_mapping_table['投资收益类'])
            ret = self.regular_series(column, s1)

        elif column == 's_091_net_working_capital':
            tmp = list()
            # 净营运资本（net working capital）
            if self.country == 'cn':
                if self.code_type == 'non_financial':
                    tmp.append(self.smooth_data(column, 'bs-租赁负债'))
                    tmp.append(self.get_column('s_010_cash_asset'))
                    tmp.append(self.get_column('s_011_insurance_asset'))
                    tmp.append(self.get_column('s_012_financial_asset'))
                    tmp.append(self.get_column('s_014_turnover_asset') * 0.8)
                    tmp.append(self.get_column('s_015_inventory_asset') * 0.2)
                    tmp.append(self.get_column('s_023_liabilities') * -1)

                    df1 = pd.concat(tmp, axis=1, sort=True)
                    s1 = df1.apply(lambda x: x.sum(), axis=1)
                    ret = self.regular_series(column, s1)

        else:
            raise KeyboardInterrupt(column)
            # ret = self.regular_series(column, pd.Series())

        self.df = pd.concat([self.df, pd.DataFrame(ret)], axis=1, sort=True)
        return self.df[column].copy().dropna()

    @staticmethod
    def sum_columns(df, columns):
        df = df.loc[:, columns].copy().dropna(how='all')
        # res_df = res_df.replace(0, np.nan)
        # res_df = res_df.dropna(axis=0, how='all')
        s1 = df.apply(lambda x: x.sum(), axis=1)
        return s1

    @staticmethod
    def get_roe(s1, s2):
        s3 = s2 - s1
        s3[s3 <= 0] = np.nan
        s4 = s1 / s3
        s4.dropna(inplace=True)
        s4[s4 <= -50] = np.nan
        return s4.dropna()

    def smooth_data(self, name, column, delta=False, ttm=False):
        s1 = self.df.loc[:, column].copy().dropna()
        if delta is False:
            res = self.get_month_data(s1, name)
        else:
            res = self.get_month_delta(s1, name)
        if ttm is True:
            res = self.get_ttm(res, 4)
        return self.regular_series(name, res)


def creat_mapping_table():
    src = load_json_txt('../basicData/header_df/header_df_fs.txt')
    ret = dict()
    tmp = ''
    for key, value in src.items():
        sheet_name = value['sheet_name']
        if sheet_name is None:
            continue
        txt = value['txt_CN']
        if txt[:4] == '(其中)':
            ret_key = '-'.join([sheet_name, tmp, txt])
        else:
            ret_key = '-'.join([sheet_name, txt])
            tmp = value['txt_CN']

        if ret_key in ret.keys():
            raise KeyboardInterrupt(ret_key)
        else:
            ret[ret_key] = key

    write_json_txt('../basicData/chineseComparison/zh_cmp_table_fs_cn_org.txt', ret)
    print(ret)


def test_mapping_table():
    path = '../basicData/mappingTable/mvs_m_table_cn.txt'
    table1 = load_json_txt(path)

    path = '../basicData/chineseComparison/zh_cmp_table_mvs_cn.txt'
    table2 = load_json_txt(path)

    ret = dict()
    for key in table1.keys():
        ret[key] = None

    df = pd.DataFrame(columns=table2.values())
    df = StandardData.change_columns_header(df=df, cmp_table=table2, m_table=table1)
    print(df.columns)


def create_zh_cmp_table_cn_bank():
    import re
    path = '../basicData/src_text/fs_src_table_bank.txt'
    with open(path, "r", encoding='utf-8') as f:
        text = f.read()

    sheet = ''
    parent = ''
    ret = dict()
    counter = 1
    for rowText in re.findall(r'^.*$', text, re.MULTILINE):
        if rowText == '':
            continue

        if rowText == '资产合计 :bs.ta':
            sheet = 'bs'
        elif rowText == '营业收入 :ps.oi':
            sheet = 'ps'
        elif rowText == '经营活动产生的现金流量':
            sheet = 'cfs'

        # print(repr(rowText))
        tmp = re.findall(r'^(.*) :(.*)\.(.*)$', rowText)
        if len(tmp) == 0:
            key = rowText
            value = ''
        else:
            key = tmp[0][0]
            value = '_'.join(tmp[0][1:])

        txt = key
        if txt[:4] == '(其中)':
            ret_key = '-'.join([sheet, parent, txt])
        else:
            ret_key = '-'.join([sheet, txt])
            parent = key

        if ret_key in ret.keys():
            raise KeyboardInterrupt(ret_key)
        else:
            if value == '':
                ret_value = 'id_{:0>3}'.format(counter)
            else:
                ret_value = 'id_{:0>3}_{}'.format(counter, value)

            ret[ret_key] = ret_value
            counter += 1

        print(ret_key, ret_value)

    write_json_txt('../basicData/chineseComparison/zh_cmp_table_fs_cn_bank.txt', ret)


def creat_mapping_table_cn_bank():
    src = load_json_txt('../basicData/chineseComparison/zh_cmp_table_fs_cn_bank.txt')
    ret = dict()
    for key in src.keys():
        ret_key = key

        if ret_key in ret.keys():
            raise KeyboardInterrupt(ret_key)
        else:
            ret[ret_key] = None

    write_json_txt('../basicData/mappingTable/fs_m_table_cn_bank.txt', ret)
    print(ret)


def creat_mapping_table_hk():
    for suffix in ['001', '002', '003', '004']:

        src = load_json_txt('../basicData/chineseComparison/zh_cmp_table_fs_hk_%s.txt' % suffix)
        ret = dict()
        for key in src.keys():
            ret_key = key

            if ret_key in ret.keys():
                raise KeyboardInterrupt(ret_key)
            else:
                ret[ret_key] = None
        print(ret)

        write_json_txt('../basicData/mappingTable/fs_m_table_hk_%s.txt' % suffix, ret)


# def create_zh_cmp_table_hk():
#     path = '../basicData/foreignCodes/hk_header_mapping_table2.txt'
#     table = load_json_txt(path)
#
#     for suffix in ['001', '002', '003', '004']:
#         ret = dict()
#         for key, val in table.items():
#             if key[:4] == 'cfs_' \
#                     or key[:6] == 'bs_%s' % suffix \
#                     or key[:6] == 'ps_%s' % suffix:
#                 sheet = key.split('_')[0]
#                 ret['%s-%s' % (sheet, val)] = key
#         path = '../basicData/chineseComparison/zh_cmp_table_fs_hk_%s.txt' % suffix
#         write_json_txt(path, ret)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # sd1 = StandardData('601398', 'widget')
    # sd1 = StandardData('002594', 'widget')
    # sd1 = StandardData('600750', 'daily')
    # sd1.config_standard_data()
    #
    # sd2 = sd1.copy()
    # sd2.get_data_dict()
    # sd1 = StandardData('002594', 'widget')
    # sd1.config_standard_data()

    # sd1 = StandardData('hk-00700', 'widget')
    sd1 = StandardData('hk-01810', 'widget')
    sd1.config_standard_data()

    pass
