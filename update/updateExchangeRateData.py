from method.fileMethod import load_pkl
from method.fileMethod import load_json_txt
from method.sqlMethod import df2mysql
from request.requestExchangeRateData import request_exchange_rate
import pandas as pd


def update_exchange_rate_data(start_date="1990-01-01"):
    request_exchange_rate(start_date=''.join(start_date.split('-')))

    path = "..\\basicData\\tmp\\exchange_rate_table_sina.pkl"
    df: pd.DataFrame = load_pkl(path)

    mapping = {
        '港币': '港元',
        '澳大利亚元': '澳元',
        '加拿大元': '加元',
        '韩国元': '韩元',
        '菲律宾比索': '比索',
        '泰国铢': '泰铢',
    }
    df = df.sort_index()
    df = df.rename(mapping, axis=1)
    for column in df.columns:
        df[column] = df[column] / 100

    path = "..\\basicData\\tmp\\exchange_rate_table.pkl"
    df2: pd.DataFrame = load_pkl(path)
    df2 = df2.set_index('日期')

    df2 = df2.loc[:, ~df2.columns.isin(df.columns)].copy()
    for column in df2.columns:
        df2[column] = 100 / df2[column]

    df = pd.concat([df, df2], axis=1, sort=True)

    df = df.dropna(how='all', axis=0)
    df.index = df.index.astype('str')
    df = df[df.index > start_date]

    path = "..\\basicData\\chineseComparison\\zh_cmp_table_exchange_rate.txt"
    cmp_table = load_json_txt(path)

    df = df.reindex(columns=cmp_table.keys())
    df.columns = cmp_table.values()
    df['date'] = df.index

    database = 'basicData'
    table = 'exchange_rate'
    df2mysql(df=df, database=database, table=table, ini=False, log=True)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 10000)

    # update_exchange_rate_data('2025-04-30')
    pass
