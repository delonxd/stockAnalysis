def daily_update():
    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from request.requestBasicData import request_basic, request_industry_sample
    from method.logMethod import MainLog
    from method.sortCode import sort_daily_code
    from method.dailyMethod import basic_daily_update
    from method.dailyMethod import mysql_daily_update
    from method.dailyMethod import daily_analysis
    from method.dailyMethod import generate_daily_table
    from method.dailyMethod import save_latest_list
    from method.dailyMethod import generate_log_data
    from method.fileMethod import load_json_txt
    from sql.load_data_infile import output_databases
    from request.requestMirData import request_mir_y10
    from request.requestSwData import update_sw_2021
    from request.requestEquityData import request_eq2mysql

    import time

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dir_name = 'update_%s' % timestamp
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    ################################################################################################################

    all_codes, name_dict, ipo_dates = basic_daily_update(dir_name)

    MainLog.add_split('#')
    mysql_daily_update(dir_name, all_codes, ipo_dates)
    MainLog.add_log('mysql_daily_update complete')

    MainLog.add_split('#')
    update_sw_2021()
    MainLog.add_log('update_sw_2021 complete')

    MainLog.write('%s\\logs1.txt' % res_dir)
    MainLog.init_log()

    ################################################################################################################

    MainLog.add_split('#')
    generate_log_data(dir_name)
    MainLog.add_log('generate_log_data complete')

    daily_analysis(dir_name, all_codes)
    MainLog.add_log('data analysis complete')

    # MainLog.add_split('#')
    # sort_daily_code(dir_name)
    # MainLog.add_log('sort_daily_code complete')

    MainLog.add_split('#')
    generate_daily_table(dir_name)
    MainLog.add_log('generate_daily_table complete')

    MainLog.add_split('#')
    save_latest_list(dir_name)
    MainLog.add_log('save_latest_list complete')

    ################################################################################################################

    # MainLog.add_split('#')
    # output_databases()
    # MainLog.add_log('output_databases complete')

    MainLog.add_split('#')
    request_mir_y10()
    MainLog.add_log('request_mir_y10 complete')

    # MainLog.add_split('#')
    # request_industry_sample()
    # MainLog.add_log('request_industry_sample complete')

    MainLog.write('%s\\logs2.txt' % res_dir)
    MainLog.init_log()

    list1 = load_json_txt("..\\basicData\\self_selected\\gui_whitelist.txt")
    list2 = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")
    list3 = list(set(list1 + list2))
    request_eq2mysql(list3)
    MainLog.write('%s\\logs3.txt' % res_dir)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    daily_update()
