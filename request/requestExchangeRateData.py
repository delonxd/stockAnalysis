from method.fileMethod import dump_pkl
import pandas as pd
import akshare as ak
import time


def request_exchange_rate(start_date):
    request_exchange_rate_sina(start_date=start_date)
    request_exchange_rate_boc()


def request_exchange_rate_sina(start_date):
    lst = [
        '美元',
        '欧元',
        '日元',
        '港币',
        '英镑',
        '澳大利亚元',
        '加拿大元',
        '新西兰元',
        '新加坡元',
        '瑞士法郎',

        '韩国元',
        '瑞典克朗',
        '丹麦克朗',
        '挪威克朗',
        '菲律宾比索',
        '泰国铢',
        '澳门元',
    ]

    ret = pd.DataFrame()
    for column in lst:
        time.sleep(0.2)
        df = ak.currency_boc_sina(symbol=column, start_date=start_date, end_date="20500101")
        df = df.set_index('日期')
        df = df.reindex(columns=['央行中间价'])
        df.columns = [column]

        ret = pd.concat([ret, df], axis=1)
        path = "..\\basicData\\tmp\\exchange_rate_table_sina.pkl"
        dump_pkl(path, ret)


def request_exchange_rate_boc():
    df = ak.currency_boc_safe()
    path = "..\\basicData\\tmp\\exchange_rate_table.pkl"
    dump_pkl(path, df)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 10000)

    pass
