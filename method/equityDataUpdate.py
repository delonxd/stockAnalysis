def eq_update():
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from method.logMethod import MainLog
    from request.requestEquityData import request_eq2mysql_cn
    from request.requestDividendData import request_dv2mysql_cn

    from request.requestAkshareData import request_mir_ak
    from request.requestAkshareData import request_futures_data
    from request.requestAkshareData import request_sz000001
    from request.requestCryptoData import request_crypto_data

    from method.sortCode import sort_hold
    from method.sortCode import get_hold_position

    request_eq2mysql_cn()
    request_dv2mysql_cn()

    MainLog.write('..\\basicData\\dailyUpdate\\eq_update_log1.txt', init=True)

    request_mir_ak()
    request_futures_data()
    request_sz000001()
    request_crypto_data()
    sort_hold()
    get_hold_position()

    MainLog.write('..\\basicData\\dailyUpdate\\eq_update_log2.txt', init=True)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    eq_update()
