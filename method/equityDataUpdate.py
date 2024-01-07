def eq_update():
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from method.fileMethod import load_json_txt
    from method.logMethod import MainLog
    from request.requestEquityData import request_eq2mysql
    from request.requestDividendData import request_dv2mysql

    from request.requestAkshareData import request_mir_y10_ak
    from request.requestAkshareData import request_futures_data

    from method.sortCode import sort_hold

    code_list = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
    request_eq2mysql(code_list)
    request_dv2mysql(code_list)

    MainLog.write('..\\basicData\\dailyUpdate\\eq_update_log1.txt', init=True)

    request_mir_y10_ak()
    request_futures_data()
    sort_hold()

    MainLog.write('..\\basicData\\dailyUpdate\\eq_update_log2.txt', init=True)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    eq_update()
