from request.requestBasicData import request_basic, request_company_profile
from request.requestEquityData import request_eq2mysql
from request.requestDividendData import request_dv2mysql
from request.requestMirData import request_mir_y10
from method.fileMethod import *
from method.sql_update import update_latest_data
from method.sql_update import update_all_data
from request.requestData import request2mysql
from request.requestSwData import update_sw_2021
from method.dataMethod import load_df_from_mysql
from method.dataMethod import DataAnalysis, DailyDataAnalysis
from method.showTable import add_bool_column, get_recent_val, sum_value, get_recent_index
from method.sortCode import sift_codes
from method.showTable import generate_show_table
import numpy as np
import os
import pandas as pd
import datetime as dt
import time


def basic_daily_update(dir_name):
    all_codes, name_dict, ipo_dates = request_basic()
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    MainLog.add_split('#')
    actual_controller = request_company_profile(all_codes)
    write_json_txt("..\\basicData\\actual_controller.txt", actual_controller)

    MainLog.add_split('#')
    write_json_txt('%s\\a002_name_dict.txt' % res_dir, name_dict)
    write_json_txt('..\\basicData\\code_names_dict.txt', name_dict)
    write_json_txt('%s\\a001_code_list.txt' % res_dir, all_codes)
    write_json_txt('..\\basicData\\ipo_date.txt', ipo_dates)
    write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, [])
    return all_codes, name_dict, ipo_dates


# def mysql_daily_update(dir_name, all_codes, ipo_dates):
#     MainLog.add_split('#')
#
#     res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
#     ret1 = []
#     ret2 = []
#
#     # industry_dict = request_industry_sample()
#     # res = json.dumps(industry_dict, indent=4, ensure_ascii=False)
#     # file = '%s\\industry_dict.txt' % res_dir
#     # with open(file, "w", encoding='utf-8') as f:
#     #     f.write(res)
#
#     # code_list = get_part_codes(code_list)
#
#     ################################################################################################################
#     new_codes = []
#     for code, date in ipo_dates.items():
#         if not date:
#             new_codes.append(code)
#         elif date > '2023-01-01':
#             new_codes.append(code)
#
#     MainLog.add_log('Length of all codes: %s' % len(all_codes))
#     MainLog.add_log('Length of new codes: %s' % len(new_codes))
#
#     weekday = dt.date.today().weekday()
#     mvs_flag = True
#     if weekday in [5, 6]:
#         mvs_flag = False
#
#     ret1 = update_all_data(new_codes, start_date='2014-01-01', mvs_flag=mvs_flag)
#     ret2 = update_latest_data(all_codes, mvs_flag=mvs_flag)
#     updated_code = list(set(ret1 + ret2))
#     updated_code.sort()
#
#     ################################################################################################################
#
#     MainLog.add_split('#')
#     MainLog.add_log('new updated: %s' % len(updated_code))
#     MainLog.add_log('generate code_latest_update.txt')
#
#     # res = json.dumps(updated_code, indent=4, ensure_ascii=False)
#     # file = '%s\\code_latest_update.txt' % res_dir
#     # with open(file, "w", encoding='utf-8') as f:
#     #     f.write(res)
#
#     write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, updated_code)
#
#     ################################################################################################################
#
#     for code in updated_code:
#         MainLog.add_split('#')
#         request2mysql(
#             stock_code=code,
#             data_type='fs',
#             start_date='2014-01-01',
#         )
#
#     MainLog.add_log('mysql_daily_update complete')
#     MainLog.add_split('#')


def mysql_daily_update2(dir_name, all_codes, ipo_dates):
    MainLog.add_split('#')

    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    ret1 = []
    ret2 = []

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

    ret1 = update_latest_data(all_codes, mvs_flag=False)
    MainLog.add_log('update latest data complete')

    ################################################################################################################

    refresh = list(set(new_codes + ret1))
    refresh.sort()

    MainLog.add_split('#')
    MainLog.add_log('refresh codes: %s' % len(refresh))

    ret2 = update_all_data(refresh, start_date=date2_str, mvs_flag=False)
    ret = list(set(ret1 + ret2))

    MainLog.add_log('refresh complete')

    ################################################################################################################

    write_json_txt('%s\\s004_code_latest_update.txt' % res_dir, ret)
    MainLog.add_log('fs data complete')
    MainLog.add_split('#')

    ################################################################################################################

    weekday = dir_date.weekday()
    if weekday not in [5, 6]:
        update_latest_data(all_codes, fs_flag=False)
        update_all_data(new_codes, start_date=date2_str, fs_flag=False)

        MainLog.add_log('mvs data complete')
        MainLog.add_split('#')

    ################################################################################################################

    MainLog.add_log('mysql_daily_update complete')
    MainLog.add_split('#')


def daily_analysis(dir_name, all_codes):
    MainLog.add_split('#')

    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    sub_dir = '..\\basicData\\dailyUpdate\\%s\\res_daily' % dir_name
    os.makedirs(sub_dir)

    timestamp = dir_name[-14:]

    columns = [
        # 's_001_roe',
        's_002_equity',
        # 's_003_profit',
        # 's_004_pe',
        # 's_005_stocks',
        # 's_006_stocks_rate',
        # 's_007_asset',
        # 's_008_revenue',
        # 's_009_revenue_rate',
        # 's_010_main_profit',
        # 's_011_main_profit_rate',
        # 's_012_return_year',
        # 's_013_noc_asset',
        # 's_014_pe2',
        # 's_015_return_year2',
        's_016_roe_parent',
        # 's_017_equity_parent',
        # 's_018_profit_parent',
        # 's_019_monetary_asset',
        # 's_020_cap_asset',
        # 's_021_cap_expenditure',
        # 's_022_profit_no_expenditure',
        # 's_023_liabilities',
        # 's_024_real_liabilities',
        's_025_real_cost',
        's_026_liquidation_asset',
        # 's_026_holder_return_rate',
        # 's_027_pe_return_rate',
        's_028_market_value',
        # 's_037_real_pe_return_rate',
        # 'id_048_mvs_ta',
        # 's_044_turnover_volume',
        # 's_061_total_return_rate',
        's_063_profit_salary2',
        # 's_066_profit_salary_min',
        'dv_001_dividend_value',
    ]

    index = 0
    end = len(all_codes)
    tmp_list = []
    counter = 1

    report_date_dict = dict()
    # real_cost_dict = dict()

    MainLog.add_split('#')
    MainLog.add_log('columns: %s' % columns)

    while index < end:
        try:
            code = all_codes[index]
            # MainLog.add_log('Analysis: %s/%s --> %s' % (index, end, code))
            MainLog.add_log_accurate('Analysis: %s/%s --> %s' % (index, end, code))

            df1 = load_df_from_mysql(code, 'fs')

            fields = [
                'date',
                'id_041_mvs_mc',
                'id_042_mvs_cmc',
                'id_048_mvs_ta',
            ]

            df2 = load_df_from_mysql(code, 'mvs', fields=fields)

            data = DailyDataAnalysis(df1, df2)
            data.add_dv_data(code)
            data.config_daily_data()

            df = data.df[columns].copy()

            s1 = data.df['dt_fs'].copy().dropna()
            report_date = s1.index[-1] if s1.size > 0 else ''
            report_date_dict[code] = report_date

        except Exception as e:
            MainLog.add_log(e)
            continue

        tmp_list.append((code, df))
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

        MainLog.add_log_accurate('Reading: %s/%s --> %s' % (index, end, code))

        # val = get_recent_val(src, 's_037_real_pe_return_rate', -np.inf)
        # df.loc[code, 'real_pe_return_rate'] = val

        val = get_recent_val(src, 's_016_roe_parent', -np.inf)
        df.loc[code, 'roe_parent'] = val

        # val = get_recent_val(src, 's_027_pe_return_rate', -np.inf)
        # df.loc[code, 'pe_return_rate'] = val

        val = get_recent_val(src, 's_025_real_cost', np.inf)
        df.loc[code, 'real_cost'] = val

        # val = get_recent_val(src, 's_061_total_return_rate', -np.inf)
        # df.loc[code, 'total_return_rate'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf)
        df.loc[code, 'market_value_1'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf, 2)
        df.loc[code, 'market_value_2'] = val

        val = get_recent_val(src, 's_002_equity', np.nan)
        df.loc[code, 'equity'] = val

        val = get_recent_val(src, 's_026_liquidation_asset', np.nan)
        df.loc[code, 'liquidation'] = val

        s0 = src.loc[:, 's_028_market_value'].copy().dropna()
        df.loc[code, 'ipo_date'] = s0.index[0] if s0.size > 0 else np.nan

        # s1 = src.loc[:, 's_044_turnover_volume'].copy().dropna()
        # s1 = s1.rolling(20, min_periods=1).mean().dropna()
        # df.loc[code, 'turnover_ttm20'] = s1[-1] if s1.size >= 1 else np.nan

        val = get_recent_index(src, 's_063_profit_salary2', np.nan)
        df.loc[code, 'recent_date'] = val

        delta = 0
        if not pd.isna(val):
            date1 = dt.datetime.strptime(val, "%Y-%m-%d").date()
            date2 = dt.date.today()
            delta = (date2 - date1).days
        df.loc[code, 'predict_delta'] = delta

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


def test_daily_analysis():
    import time
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dir_name = 'test_%s' % timestamp
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    codes = load_json_txt('..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt')
    daily_analysis(dir_name, codes)


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


def eq_daily_update():
    MainLog.add_split('#')

    list1 = code_list_from_tags("白名单")
    list2 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")
    list3 = list(set(list1 + list2))
    list4 = sorted(list3)
    request_eq2mysql(list4)

    MainLog.add_log('eq_daily_update complete')
    MainLog.add_split('#')


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

    codes = sift_codes(
        source=src,
        sort=["gui_rate", "code"],
        ascending=[False, True],
        sort_ids=True,
        df_all=df_all,
    )

    path = "..\\basicData\\self_selected\\backup_daily_codes.txt"
    source = load_json_txt(path)
    source[key] = codes
    write_json_txt(path, source)

    MainLog.add_log('backup_daily_codes complete')
    MainLog.add_split('#')


def manual_daily_update():
    # timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    # dir_name = 'update_%s' % timestamp
    # res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    #
    # if not os.path.exists(res_dir):
    #     os.makedirs(res_dir)

    dir_name = 'update_20231031155003'
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    # all_codes, name_dict, ipo_dates = basic_daily_update(dir_name)
    all_codes = load_json_txt('%s\\a001_code_list.txt' % res_dir)

    # ################################################################################################################
    #
    # MainLog.write('%s\\logs1.txt' % res_dir, init=True)
    #
    # tmp_path = '%s\\logs1.txt' % res_dir
    # if os.path.exists(res_dir):
    #     print('adadsadsad')
    #
    # generate_log_data(dir_name)
    # daily_analysis(dir_name, all_codes)
    # MainLog.write('%s\\logs2.txt' % res_dir, init=True)
    #
    generate_daily_table(dir_name)
    save_latest_list(dir_name)
    # request_mir_y10()
    MainLog.write('%s\\logs3.txt' % res_dir, init=True)

    # eq_daily_update()
    # MainLog.write('%s\\logs4.txt' % res_dir, init=True)

    backup_daily_update()
    MainLog.write('%s\\logs5.txt' % res_dir, init=True)


if __name__ == '__main__':

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    update_latest_data(['600000'], fs_flag=False)
    # manual_daily_update()
    # eq_daily_update()

    # test_daily_analysis()
