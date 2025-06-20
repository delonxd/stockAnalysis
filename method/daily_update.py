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

    from update.updateProfileData import update_security_profile_cn
    from update.updateProfileData import update_company_profile_cn
    from update.updateProfileData import update_profile_combine

    from method.dailyMethod import update_mysql_data_daily_cn

    from method.dailyMethod import daily_analysis_cn
    from method.dailyMethod import generate_daily_table
    from method.dailyMethod import save_latest_list
    from method.dailyMethod import generate_log_data
    # from method.dailyMethod import eq_daily_update
    from method.dailyMethod import backup_daily_update
    # from request.requestMirData import request_mir_y10
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

    update_security_profile_cn(dir_name)
    update_company_profile_cn()
    update_sw_2021()
    update_profile_combine()
    MainLog.write('%s\\logs0.txt' % res_dir, init=True)

    update_mysql_data_daily_cn(dir_name)
    MainLog.write('%s\\logs1.txt' % res_dir, init=True)

    generate_log_data(dir_name)
    daily_analysis_cn(dir_name)
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
