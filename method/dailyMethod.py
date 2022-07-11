from request.requestBasicData import request_basic
from method.fileMethod import *
from method.sql_update import update_latest_data
from method.sql_update import update_all_data
from request.requestData import request_data2mysql
from method.dataMethod import load_df_from_mysql
from method.dataMethod import DataAnalysis
from method.showTable import add_bool_column, get_recent_val
import numpy as np
import os
import pandas as pd


def basic_daily_update(dir_name):
    all_codes, name_dict, ipo_dates = request_basic()
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    MainLog.add_split('#')
    write_json_txt('%s\\name_dict.txt' % res_dir, name_dict)
    write_json_txt('..\\basicData\\code_names_dict.txt', name_dict)
    write_json_txt('%s\\code_list.txt' % res_dir, all_codes)
    return all_codes, name_dict, ipo_dates


def mysql_daily_update(dir_name, all_codes, ipo_dates):
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    # industry_dict = request_industry_sample()
    # res = json.dumps(industry_dict, indent=4, ensure_ascii=False)
    # file = '%s\\industry_dict.txt' % res_dir
    # with open(file, "w", encoding='utf-8') as f:
    #     f.write(res)

    # code_list = get_part_codes(code_list)

    ################################################################################################################

    new_codes = []
    for code, date in ipo_dates.items():
        if not date:
            new_codes.append(code)
        elif date > '2021-11-01':
            new_codes.append(code)

    MainLog.add_log('Length of all codes: %s' % len(all_codes))
    MainLog.add_log('Length of new codes: %s' % len(new_codes))

    ret1 = update_all_data(new_codes, start_date='2013-01-01')
    ret2 = update_latest_data(all_codes)

    updated_code = list(set(ret1 + ret2))
    updated_code.sort()

    ################################################################################################################

    MainLog.add_split('#')
    MainLog.add_log('new updated: %s' % len(updated_code))
    MainLog.add_log('generate code_latest_update.txt')

    res = json.dumps(updated_code, indent=4, ensure_ascii=False)
    file = '%s\\code_latest_update.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    ################################################################################################################

    for code in updated_code:
        MainLog.add_split('#')
        request_data2mysql(
            stock_code=code,
            data_type='fs',
            start_date='2013-01-01',
        )


def daily_analysis(dir_name, all_codes):
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
        's_007_asset',
        # 's_008_revenue',
        # 's_009_revenue_rate',
        # 's_010_main_profit',
        # 's_011_main_profit_rate',
        # 's_012_return_year',
        # 's_013_noc_asset',
        # 's_014_pe2',
        # 's_015_return_year2',
        's_016_roe_parent',
        's_017_equity_parent',
        # 's_018_profit_parent',
        # 's_019_monetary_asset',
        # 's_020_cap_asset',
        # 's_021_cap_expenditure',
        's_022_profit_no_expenditure',
        # 's_023_liabilities',
        # 's_024_real_liabilities',
        's_025_real_cost',
        's_026_holder_return_rate',
        's_027_pe_return_rate',
        's_028_market_value',
        's_037_real_pe_return_rate',
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
            MainLog.add_log('Analysis: %s/%s --> %s' % (index, end, code))

            df1 = load_df_from_mysql(code, 'fs')
            df2 = load_df_from_mysql(code, 'mvs')

            data = DataAnalysis(df1, df2)
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

    write_json_txt('%s\\report_date_dict.txt' % res_dir, report_date_dict)

    MainLog.add_split('#')


def generate_daily_table(dir_name):
    df = pd.DataFrame()

    daily_dir = "..\\basicData\\dailyUpdate\\%s" % dir_name
    ################################################################################################################

    res = load_json_txt("%s\\name_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'cn_name'] = value

    ################################################################################################################

    res = load_json_txt("%s\\report_date_dict.txt" % daily_dir)
    for key, value in res.items():
        df.loc[key, 'report_date'] = value

    ################################################################################################################

    path = "%s\\code_latest_update.txt" % daily_dir
    df = add_bool_column(df, path, 'update_recently')

    ################################################################################################################

    sub_dir = '%s\\res_daily\\' % daily_dir

    res = list()
    for file in os.listdir(sub_dir):
        res.extend(load_pkl('%s\\%s' % (sub_dir, file)))

    for tmp in res:
        code = tmp[0]
        src = tmp[1]

        val = get_recent_val(src, 's_037_real_pe_return_rate', -np.inf)
        df.loc[code, 'real_pe_return_rate'] = val

        val = get_recent_val(src, 's_016_roe_parent', -np.inf)
        df.loc[code, 'roe_parent'] = val

        val = get_recent_val(src, 's_027_pe_return_rate', -np.inf)
        df.loc[code, 'pe_return_rate'] = val

        val = get_recent_val(src, 's_025_real_cost', np.inf)
        df.loc[code, 'real_cost'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf)
        df.loc[code, 'market_value_1'] = val

        val = get_recent_val(src, 's_028_market_value', np.inf, 2)
        df.loc[code, 'market_value_2'] = val

        val = get_recent_val(src, 's_002_equity', np.nan)
        df.loc[code, 'equity'] = val

    dict1 = df.loc[:, 'equity'].copy().dropna().to_dict()
    write_json_txt('%s\\equity_dict.txt' % daily_dir, dict1)

    dict2 = df.loc[:, 'real_cost'].copy().dropna().to_dict()
    write_json_txt('%s\\real_cost_dict.txt' % daily_dir, dict2)

    list1 = df.sort_values('real_pe_return_rate', ascending=False).index.to_list()
    write_json_txt('%s\\code_sorted_real_pe.txt' % daily_dir, list1)

    list2 = df.sort_values('roe_parent', ascending=False).index.to_list()
    write_json_txt('%s\\code_sorted_roe_parent.txt' % daily_dir, list2)

    list3 = df.sort_values('pe_return_rate', ascending=False).index.to_list()
    write_json_txt('%s\\code_sorted_pe.txt' % daily_dir, list3)

    dump_pkl('%s\\daily_table.pkl' % daily_dir, df)

    return df


def save_latest_list(dir_name):
    src_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    target_dir = '..\\basicData\\dailyUpdate\\latest'

    files = [
        'a001_code_list.txt',
        'a002_name_dict.txt',
        'a003_report_date_dict.txt',
        'a004_real_cost_dict.txt',
        'a005_equity_dict.txt',
        's001_code_sorted_pe.txt',
        's002_code_sorted_real_pe.txt',
        's003_code_sorted_roe_parent.txt',
        's004_code_latest_update.txt',
        'z001_daily_table.pkl',
    ]

    for file in files:
        path1 = '%s\\%s' % (src_dir, file[5:])
        path2 = '%s\\%s' % (target_dir, file)
        copy_file(path1, path2)

    dir1 = '..\\basicData\\dailyUpdate\\%s\\res_daily' % dir_name
    dir2 = '..\\basicData\\dailyUpdate\\latest\\res_daily'
    clear_dir(dir2)
    copy_dir(dir1, dir2)


def test_daily_analysis():
    import time
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dir_name = 'test_%s' % timestamp
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    codes = load_json_txt('..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt')
    daily_analysis(dir_name, codes)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # dir_daily = 'update_20220602153503'
    # generate_daily_table(dir_daily)
    # save_latest_list(dir_daily)

    test_daily_analysis()
