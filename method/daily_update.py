def daily_update():
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from method.logMethod import MainLog
    from method.dailyMethod import basic_daily_update
    from method.dailyMethod import mysql_daily_update2
    from method.dailyMethod import daily_analysis
    from method.dailyMethod import generate_daily_table
    from method.dailyMethod import save_latest_list
    from method.dailyMethod import generate_log_data
    from method.dailyMethod import eq_daily_update
    from method.dailyMethod import backup_daily_update
    from request.requestMirData import request_mir_y10
    from request.requestSwData import update_sw_2021
    # from request.requestAkshareData import request_mir_y10_ak
    # from request.requestAkshareData import request_futures_data

    from request.requestAkshareData import request_sz000001
    from method.sortCode import sort_hold
    from method.sortCode import get_hold_position

    import time

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    dir_name = 'update_%s' % timestamp
    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name

    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    ################################################################################################################

    all_codes, name_dict, ipo_dates = basic_daily_update(dir_name)
    mysql_daily_update2(dir_name, all_codes, ipo_dates)

    update_sw_2021()
    MainLog.write('%s\\logs1.txt' % res_dir, init=True)

    generate_log_data(dir_name)
    daily_analysis(dir_name, all_codes)
    MainLog.write('%s\\logs2.txt' % res_dir, init=True)

    generate_daily_table(dir_name)
    save_latest_list(dir_name)
    MainLog.write('%s\\logs3.txt' % res_dir, init=True)

    # eq_daily_update()
    # request_mir_y10_ak()
    # request_futures_data()
    # MainLog.write('%s\\logs4.txt' % res_dir, init=True)

    backup_daily_update()
    request_sz000001()
    sort_hold()
    get_hold_position()
    MainLog.write('%s\\logs5.txt' % res_dir, init=True)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    daily_update()
