def daily_update():
    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from request.requestBasicData import request_basic, request_industry_sample
    from method.mainMethod import sift_codes
    from method.dataMethod import load_df_from_mysql
    from method.dataMethod import DataAnalysis
    from method.sql_update import update_latest_data
    from method.sql_update import update_all_data
    from method.logMethod import MainLog
    from method.sortCode import sort_daily_code
    from method.sortCode import save_latest_list
    from method.showTable import generate_daily_table
    from method.fileMethod import dump_pkl, write_json_txt
    from sql.load_data_infile import output_databases
    from request.requestMirData import request_mir_y10
    from request.requestData import request_data2mysql

    import json
    import time
    import pickle
    import datetime as dt
    import numpy as np

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dir_name = 'update_%s' % timestamp
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    all_codes, name_dict, ipo_dates = request_basic()

    MainLog.add_split('#')
    write_json_txt('%s\\name_dict.txt' % res_dir, name_dict)
    write_json_txt('..\\basicData\\code_names_dict.txt', name_dict)
    write_json_txt('%s\\code_list.txt' % res_dir, all_codes)
    MainLog.add_split('#')

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

    ret1 = update_all_data(new_codes, start_date='1970-01-01')
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
            start_date='2021-01-01',
        )

    sub_dir = '%s\\res_daily' % res_dir
    os.makedirs(sub_dir)

    MainLog.write('%s\\logs1.txt' % res_dir)
    MainLog.init_log()

    ################################################################################################################

    columns = [
        # 's_001_roe',
        # 's_002_equity',
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
    real_cost_dict = dict()

    MainLog.add_split('#')
    MainLog.add_log('columns: %s' % columns)

    while index < end:
        try:
            code = all_codes[index]
            MainLog.add_log('Analysis: %s/%s --> %s' % (index, end, code))

            df1 = load_df_from_mysql(code, 'fs')
            df2 = load_df_from_mysql(code, 'mvs')

            data = DataAnalysis(df1, df2)
            # data.config_widget_data()
            data.config_daily_data()

            df = data.df[columns].copy()

            s1 = data.df['dt_fs'].copy().dropna()
            report_date = s1.index[-1] if s1.size > 0 else ''
            report_date_dict[code] = report_date

            s2 = data.df['s_025_real_cost'].copy().dropna()
            real_cost = s2[-1] if s2.size > 0 else np.inf
            real_cost_dict[code] = real_cost

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
    MainLog.add_log('data analysis complete')

    ################################################################################################################

    MainLog.add_split('#')
    write_json_txt('%s\\report_date_dict.txt' % res_dir, report_date_dict)
    write_json_txt('%s\\real_cost_dict.txt' % res_dir, real_cost_dict)

    MainLog.add_split('#')
    sort_daily_code(dir_name)
    MainLog.add_log('sort_daily_code complete')

    MainLog.add_split('#')
    generate_daily_table(dir_name)
    MainLog.add_log('generate_daily_table complete')

    MainLog.add_split('#')
    save_latest_list(dir_name)
    MainLog.add_log('save_latest_list complete')

    MainLog.add_split('#')
    output_databases()
    MainLog.add_log('output_databases complete')

    MainLog.add_split('#')
    request_mir_y10()
    MainLog.add_log('request_mir_y10 complete')

    MainLog.add_split('#')
    request_industry_sample()
    MainLog.add_log('request_industry_sample complete')

    MainLog.write('%s\\logs2.txt' % res_dir)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    daily_update()
