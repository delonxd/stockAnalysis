from request.requestBasicData import request_security_profile_cn
from request.requestBasicData import request_company_profile_cn

from method.logMethod import MainLog, log_it
from method.fileMethod import load_json_txt, write_json_txt
from method.fileMethod import dump_pkl, load_pkl
from method.fileMethod import copy_file, copy_dir, clear_dir

from method.sql_update import update_latest_data_cn
from method.sql_update import update_all_data_cn

from method.dataMethod2 import StandardData
from method.siftMethod import SiftCode

from method.showTable import add_bool_column, get_recent_val, get_recent_index
from method.showTable import generate_show_table

from method.profileMethod import generate_all_code_info
from method.profileMethod import get_code_profile_df

import numpy as np
import os
import pandas as pd
import datetime as dt


@log_it(None)
def update_code_profile_combine():
    generate_all_code_info()


def update_security_profile_cn(dir_name):
    all_codes, name_dict, ipo_dates, type_dict = request_security_profile_cn()
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    MainLog.add_split('#')
    write_json_txt('%s\\a002_name_dict.txt' % res_dir, name_dict)
    write_json_txt('..\\basicData\\code_names_dict.txt', name_dict)
    write_json_txt('..\\basicData\\code_types_dict.txt', type_dict)
    write_json_txt('%s\\a001_code_list.txt' % res_dir, all_codes)
    write_json_txt('..\\basicData\\ipo_date.txt', ipo_dates)
    write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, [])

    return all_codes, name_dict, ipo_dates


def update_company_profile_cn():
    MainLog.add_split('#')
    request_company_profile_cn()


def update_mysql_data_daily_cn(dir_name):
    MainLog.add_split('#')

    df = get_code_profile_df()
    df = df[df['area'] == 'cn']

    all_codes = df.index.to_list()
    ipo_dates = df['ipo_date'].dropna().to_dict()

    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    # ret1 = []
    # ret2 = []

    timestamp = dir_name.split('_')[1]
    dir_date = dt.datetime.strptime(timestamp, "%Y%m%d%H%M%S").date()

    date1 = dir_date - dt.timedelta(days=365)
    date2 = dt.date(dt.date.today().year - 9, 1, 1)

    date1_str = date1.strftime("%Y-%m-%d")
    date2_str = date2.strftime("%Y-%m-%d")

    ################################################################################################################

    new_codes = []
    for code, date in ipo_dates.items():
        if not date:
            new_codes.append(code)
        elif date > date1_str:
            new_codes.append(code)

    MainLog.add_log('Length of all codes: %s' % len(all_codes))
    MainLog.add_log('Length of new codes: %s' % len(new_codes))

    ret1 = update_latest_data_cn(all_codes, fs_flag=True)
    MainLog.write('%s\\logs1.txt' % res_dir, init=False)
    MainLog.add_log('update latest data complete')

    ################################################################################################################

    refresh = list(set(new_codes + ret1))
    refresh.sort()

    MainLog.add_split('#')
    MainLog.add_log('refresh codes: %s' % len(refresh))
    write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, refresh)

    ret2 = update_all_data_cn(refresh, start_date=date2_str, fs_flag=True)
    MainLog.write('%s\\logs1.txt' % res_dir, init=False)

    ret = list(set(ret1 + ret2))
    MainLog.add_log('refresh complete')

    ################################################################################################################

    write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, ret)
    MainLog.add_log('fs data complete')
    MainLog.add_split('#')

    ################################################################################################################

    weekday = dir_date.weekday()
    if weekday not in [5, 6]:
        update_latest_data_cn(all_codes, mvs_flag=True)
        MainLog.write('%s\\logs1.txt' % res_dir, init=False)
        update_all_data_cn(new_codes, start_date=date2_str, mvs_flag=True)
        MainLog.write('%s\\logs1.txt' % res_dir, init=False)

        MainLog.add_log('mvs data complete')
        MainLog.add_split('#')

    ################################################################################################################

    MainLog.add_log('mysql_daily_update complete')
    MainLog.add_split('#')


def daily_analysis_cn(dir_name):
    MainLog.add_split('#')

    df = get_code_profile_df()
    df = df[df['area'] == 'cn']
    all_codes = df.index.to_list()

    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    sub_dir = '..\\basicData\\dailyUpdate\\%s\\res_daily' % dir_name

    if not os.path.exists(sub_dir):
        os.makedirs(sub_dir)

    MainLog.add_split('#')

    index = 0
    end = len(all_codes)

    timestamp = dir_name[-14:]
    counter = 1
    tmp_list = []
    report_date_dict = dict()
    while index < end:
        try:
            code = all_codes[index]
            MainLog.add_log_accurate('Analysis: %s/%s --> %s' % (index, end, code))

            st_data = StandardData(code, 'daily')
            st_data.config_standard_data()

            df1 = st_data.df_fs.copy()
            df2 = st_data.df_mvs.copy()

            s1 = st_data.dt_fs.copy()
            report_date = s1.index[-1] if s1.size > 0 else ''
            report_date_dict[code] = report_date

        except Exception as e:
            MainLog.add_log(e)
            continue

        tmp_list.append((code, df1, df2))
        # print(df.columns)
        if len(tmp_list) == 1000:
            dump_pkl('%s\\%s_%s.pkl' % (sub_dir, timestamp, counter), tmp_list)
            MainLog.add_split('-')

            tmp_list = []
            counter += 1

        index += 1

    if len(tmp_list) > 0:
        dump_pkl('%s\\%s_%s.pkl' % (sub_dir, timestamp, counter), tmp_list)

    MainLog.add_split('-')

    write_json_txt('%s\\a003_report_date_dict.txt' % res_dir, report_date_dict)

    MainLog.add_split('-')
    MainLog.add_log('data analysis complete')
    MainLog.add_split('#')


def generate_daily_table(dir_name):
    MainLog.add_split('#')
    df = pd.DataFrame()

    daily_dir = "..\\basicData\\dailyUpdate\\%s" % dir_name
    ################################################################################################################

    res = load_json_txt("%s\\a002_name_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'cn_name'] = value

    ################################################################################################################

    res = load_json_txt("%s\\a003_report_date_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'report_date'] = value

    ################################################################################################################

    path = "%s\\s004_code_latest_update.txt" % daily_dir
    df = add_bool_column(df, path, 'update_recently')

    ################################################################################################################

    sub_dir = '%s\\res_daily\\' % daily_dir

    res = list()
    for file in os.listdir(sub_dir):
        res.extend(load_pkl('%s\\%s' % (sub_dir, file)))

    # s1 = sum_value(res, ['s_028_market_value'])
    # s2 = sum_value(res, ['s_044_turnover_volume'])
    # s2 = s2.rolling(20, min_periods=1).mean()
    #
    # s3 = (s2 / s1).dropna().to_dict()
    # write_json_txt('%s\\a007_change_rate.txt' % daily_dir, s3)

    end = len(res)
    for index, tmp in enumerate(res):
        code = tmp[0]
        src = tmp[1]
        src_mvs = tmp[2]

        MainLog.add_log_accurate('Reading: %s/%s --> %s' % (index, end, code))

        val = get_recent_val(src_mvs, 's_028_market_value', np.inf)
        df.loc[code, 'market_value_1'] = val

        val = get_recent_val(src_mvs, 's_028_market_value', np.inf, 2)
        df.loc[code, 'market_value_2'] = val

        s0 = src_mvs.loc[:, 's_028_market_value'].copy().dropna()
        df.loc[code, 'ipo_date'] = s0.index[0] if s0.size > 0 else np.nan

        # val = get_recent_val(src, 's_037_real_pe_return_rate', -np.inf)
        # df.loc[code, 'real_pe_return_rate'] = val

        val = get_recent_val(src, 's_016_roe_parent', -np.inf)
        df.loc[code, 'roe_parent'] = val

        # val = get_recent_val(src, 's_027_pe_return_rate', -np.inf)
        # df.loc[code, 'pe_return_rate'] = val

        # val = get_recent_val(src, 's_025_real_cost', np.inf)
        # df.loc[code, 'real_cost'] = val

        # val = get_recent_val(src, 's_061_total_return_rate', -np.inf)
        # df.loc[code, 'total_return_rate'] = val

        val = get_recent_val(src, 's_002_equity', np.nan)
        df.loc[code, 'equity'] = val

        val = get_recent_val(src, 's_026_liquidation_asset', np.nan)
        df.loc[code, 'liquidation'] = val

        val = get_recent_val(src, 's_067_equity_ratio', np.nan)
        df.loc[code, 'equity_ratio'] = val

        val = get_recent_val(src, 's_079_capital_retention_ratio', np.nan)
        df.loc[code, 'cap_retention_ratio'] = val

        val = get_recent_val(src, 's_081_total_retention_ratio', np.nan)
        df.loc[code, 'total_retention_ratio'] = val

        # s1 = src.loc[:, 's_044_turnover_volume'].copy().dropna()
        # s1 = s1.rolling(20, min_periods=1).mean().dropna()
        # df.loc[code, 'turnover_ttm20'] = s1[-1] if s1.size >= 1 else np.nan

        val = get_recent_index(src, 's_063_profit_salary2', np.nan)
        df.loc[code, 'recent_date'] = val

        date2 = dt.date.today()
        delta = 0
        if not pd.isna(val):
            date1 = dt.datetime.strptime(val, "%Y-%m-%d").date()
            delta = (date2 - date1).days
        df.loc[code, 'predict_delta'] = delta

        val = get_recent_index(src, 's_002_equity', np.nan)
        df.loc[code, 'recent_date2'] = val

        delta = 0
        if not pd.isna(val):
            date1 = dt.datetime.strptime(val, "%Y-%m-%d").date()
            delta = (date2 - date1).days
        df.loc[code, 'predict_delta2'] = delta

        val = get_recent_val(src, 's_063_profit_salary2', np.nan)
        df.loc[code, 'profit_salary_adj'] = val

        val = get_recent_val(src, 'dv_001_dividend_value', 0)
        df.loc[code, 'dividend_value'] = val

    # tmp = df.loc[:, 'real_cost'].copy().dropna().to_dict()
    # write_json_txt('%s\\a004_real_cost_dict.txt' % daily_dir, tmp)

    # tmp = df.loc[:, 'equity'].copy().dropna().to_dict()
    # write_json_txt('%s\\a005_equity_dict.txt' % daily_dir, tmp)

    # tmp = df.loc[:, 'turnover_ttm20'].copy().dropna().to_dict()
    # write_json_txt('%s\\a006_turnover_dict.txt' % daily_dir, tmp)

    # tmp = df.sort_values('pe_return_rate', ascending=False).index.to_list()
    # write_json_txt('%s\\s001_code_sorted_pe.txt' % daily_dir, tmp)

    # tmp = df.sort_values('real_pe_return_rate', ascending=False).index.to_list()
    # write_json_txt('%s\\s002_code_sorted_real_pe.txt' % daily_dir, tmp)

    # tmp = df.sort_values('roe_parent', ascending=False).index.to_list()
    # write_json_txt('%s\\s003_code_sorted_roe_parent.txt' % daily_dir, tmp)

    dump_pkl('%s\\z001_daily_table.pkl' % daily_dir, df)

    MainLog.add_log('generate_daily_table complete')
    MainLog.add_split('#')

    return df


def save_latest_list(dir_name):
    MainLog.add_split('#')

    src_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    target_dir = '..\\basicData\\dailyUpdate\\latest'

    files = [
        'a000_log_data.txt',
        'a001_code_list.txt',
        'a002_name_dict.txt',
        'a003_report_date_dict.txt',
        'a004_real_cost_dict.txt',
        'a005_equity_dict.txt',
        'a006_turnover_dict.txt',
        'a007_change_rate.txt',
        's001_code_sorted_pe.txt',
        's002_code_sorted_real_pe.txt',
        's003_code_sorted_roe_parent.txt',
        's004_code_latest_update.txt',
        'z001_daily_table.pkl',
    ]

    for file in files:
        # path1 = '%s\\%s' % (src_dir, file[5:])
        path1 = '%s\\%s' % (src_dir, file)
        path2 = '%s\\%s' % (target_dir, file)

        if os.path.exists(path1):
            copy_file(path1, path2)

    dir1 = '..\\basicData\\dailyUpdate\\%s\\res_daily' % dir_name
    dir2 = '..\\basicData\\dailyUpdate\\latest\\res_daily'
    clear_dir(dir2)
    copy_dir(dir1, dir2)

    MainLog.add_log('save_latest_list complete')
    MainLog.add_split('#')


def generate_log_data(dir_name):
    MainLog.add_split('#')

    daily_dir = "..\\basicData\\dailyUpdate\\%s" % dir_name

    # path = "%s\\logs1.txt" % daily_dir
    # with open(path, 'r') as f:
    #     for num, line in enumerate(f):
    #         if num == 1:
    #             date = line[:10]
    #             break

    timestamp = dir_name.split('_')[1]
    dt_date = dt.datetime.strptime(timestamp, "%Y%m%d%H%M%S").date()
    date = dt_date.strftime("%Y-%m-%d")

    ret = dict()
    ret['update_date'] = date

    path = "%s\\a000_log_data.txt" % daily_dir
    write_json_txt(path, ret)

    MainLog.add_log('generate_log_data complete')
    MainLog.add_split('#')


# def eq_daily_update():
#     MainLog.add_split('#')
#
#     list1 = code_list_from_tags("白名单")
#     list2 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")
#     list3 = list(set(list1 + list2))
#     list4 = sorted(list3)
#     request_eq2mysql(list4)
#
#     MainLog.add_log('eq_daily_update complete')
#     MainLog.add_split('#')


def backup_daily_update():
    MainLog.add_split('#')

    src = '白名单&mkt:main&cnd:gui_rate>=13' \
          '&cnd:predict_discount>7' \
          '-光伏-电池-新上市'

    generate_show_table()
    df_all = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")
    timestamp = load_json_txt('..\\basicData\\dailyUpdate\\latest\\a000_log_data.txt')["update_date"]
    key = timestamp.replace('-', '')

    path = "..\\basicData\\backups\\df_all\\df_all_%s.pkl" % key
    dump_pkl(path, df_all)

    codes = SiftCode(
        source=src,
        sort=["gui_rate", "code"],
        ascending=[False, True],
        sort_ids=True,
        df_all=df_all,
    ).code_list

    path = "..\\basicData\\self_selected\\backup_daily_codes.txt"
    source = load_json_txt(path)
    source[key] = codes
    write_json_txt(path, source)

    MainLog.add_log('backup_daily_codes complete')
    MainLog.add_split('#')


if __name__ == '__main__':

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # update_latest_data(['600438'], mvs_flag=False)
    # manual_daily_update()
    # eq_daily_update()

    # test_daily_analysis()
