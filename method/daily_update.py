def daily_update():
    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from request.requestBasicData import request_basic, request_industry_sample

    from method.mainMethod import get_part_codes

    from method.dataMethod import load_df_from_mysql
    from method.dataMethod import DataAnalysis
    from method.sql_update import update_latest_data
    from method.sql_update import update_all_data
    from method.logMethod import MainLog

    import json
    import time
    import pickle
    import datetime as dt

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

    res_dir = '..\\basicData\\dailyUpdate\\update_%s' % timestamp

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    all_codes, name_dict, ipo_dates = request_basic()

    res = json.dumps(name_dict, indent=4, ensure_ascii=False)
    file = '%s\\name_dict.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(all_codes, indent=4, ensure_ascii=False)
    file = '%s\\code_list.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    # industry_dict = request_industry_sample()
    # res = json.dumps(industry_dict, indent=4, ensure_ascii=False)
    # file = '%s\\industry_dict.txt' % res_dir
    # with open(file, "w", encoding='utf-8') as f:
    #     f.write(res)

    # code_list = get_part_codes(code_list)

    new_codes = []
    for code, date in ipo_dates.items():
        if not date:
            new_codes.append(code)
        elif date > '2021-11-01':
            new_codes.append(code)

    print('Length of all codes: ', len(all_codes))
    print('Length of new codes: ', len(new_codes))

    # update_all_data(new_codes, start_date='1970-01-01')
    # update_latest_data(all_codes)

    sub_dir = '%s\\res_daily' % res_dir
    os.makedirs(sub_dir)

    MainLog.write('%s\\logs1.txt' % res_dir)
    MainLog.init_log()

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
        # 's_025_real_cost',
        's_026_holder_return_rate',
        's_027_pe_return_rate',
        's_028_market_value',
        's_037_real_pe_return_rate',
    ]

    index = 0
    end = len(all_codes)
    tmp_list = []
    counter = 1

    while index < end:
        try:
            code = all_codes[index]
            print('\n')
            print('############################################################################################')
            print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())))
            print('Analysis: %s/%s --> %s' % (index, end, code))

            df1 = load_df_from_mysql(code, 'fs')
            df2 = load_df_from_mysql(code, 'mvs')

            data = DataAnalysis(df1, df2)
            # data.config_widget_data()
            data.config_daily_data()

            df = data.df[columns].copy()
            df.name = code

        except Exception as e:
            print(e)
            continue

        tmp_list.append(df)
        print(df.columns)
        if len(tmp_list) == 1000:
            file = '%s\\%s_%s.pkl' % (sub_dir, timestamp, counter)
            with open(file, "wb") as f:
                pickle.dump(tmp_list, f)

            tmp_list = []
            counter += 1

        index += 1

    if len(tmp_list) > 0:
        file = '%s\\%s_%s.pkl' % (sub_dir, timestamp, counter)
        with open(file, "wb") as f:
            pickle.dump(tmp_list, f)

    MainLog.write('%s\\logs2.txt' % res_dir)


if __name__ == '__main__':
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    daily_update()
