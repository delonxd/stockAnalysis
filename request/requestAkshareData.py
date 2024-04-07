import time

import akshare as ak
import pandas as pd
from method.fileMethod import write_json_txt, dump_pkl
from method.logMethod import MainLog


def request_mir_y10_ak():
    MainLog.add_log('request_mir_y10_ak was called...')
    df = pd.DataFrame()
    flag = True
    while flag:
        try:
            df = ak.bond_zh_us_rate(start_date="19901219")
            flag = False
        except BaseException as e:
            MainLog.add_log(e.__repr__())
            sec = 120
            MainLog.add_log('sleep %ss...' % sec)
            time.sleep(sec)

    df['date'] = df['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
    df['mir_y10'] = df['中国国债收益率10年'].apply(lambda x: round(x/100, 15))
    df = df.set_index('date')
    s0 = df['mir_y10'].dropna()
    s0.sort_index(ascending=False, inplace=True)

    d0 = s0.to_dict()
    write_json_txt("..\\basicData\\nationalDebt\\mir_y10_akshare.txt", d0)
    MainLog.add_log('request_mir_y10_ak complete.')


def request_futures_data():
    MainLog.add_log('request_futures_data was called...')
    path = "..\\basicData\\futures\\futures_code.xlsx"

    try:
        MainLog.add_log('ak.futures_display_main_sina() was called...')
        df = ak.futures_display_main_sina()
        MainLog.add_log('ak.futures_display_main_sina() complete.')

        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, sheet_name="数据输出", index=True)
    except BaseException as e:
        MainLog.add_log(e.__repr__())

    src = pd.read_excel(path)
    df = pd.DataFrame()

    for index, row in src.iterrows():
        symbol = row['symbol']
        name = row['name']

        MainLog.add_log('row: %s | download futures data： %s --> %s' % (index, name, symbol))

        flag = True
        while flag:
            try:
                tmp = ak.futures_main_sina(symbol=symbol)
                tmp['date'] = tmp['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
                tmp = tmp.set_index('date')

                s0 = tmp['收盘价']
                s0.name = '%s_%s' % (symbol, name)
                df = pd.concat([df, s0], axis=1)

                flag = False
            except BaseException as e:
                MainLog.add_log(e.__repr__())
                sec = 120
                MainLog.add_log('sleep %ss...' % sec)
                time.sleep(sec)

    df.sort_index(ascending=False, inplace=True)

    path = "..\\basicData\\futures\\futures_prices_history.xlsx"

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=True)

    dump_pkl("..\\basicData\\futures\\futures_prices_history.pkl", df)
    MainLog.add_log('request_futures_data complete.')


if __name__ == '__main__':
    import warnings
    from scipy.optimize import OptimizeWarning
    warnings.simplefilter("ignore", OptimizeWarning)
    warnings.simplefilter(action='ignore', category=FutureWarning)

    request_mir_y10_ak()
    request_futures_data()
