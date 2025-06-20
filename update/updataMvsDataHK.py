from method.profileMethod import get_code_profile_df
from method.fileMethod import load_json_txt
from method.logMethod import MainLog
from method.sqlMethod import df2mysql
from request.requestMvsData import request_mvs_data_hk
import pandas as pd


def request_mvs2mysql_hk():
    df = get_code_profile_df()
    code_list = df[df['area'] == 'hk'].index.to_list()

    database = 'mvsData_hk'
    path = '..\\basicData\\sqlFieldType\\sql_field_type_mvs_hk.txt'
    field_type = load_json_txt(path)
    columns = list(field_type.keys())

    counter = 0
    size = len(code_list)
    for code in code_list:
        counter += 1
        MainLog.add_log_accurate('mvs data: %s %s / %s' % (code, counter, size))

        df = request_mvs_data_hk(code)
        if df is None:
            print(code)
            continue

        table = 'mvs_hk_%s' % code[3:]

        df = df.reindex(columns, axis=1)

        df2mysql(
            df=df,
            database=database,
            table=table,
            ini=True,
            log=False
        )


def mvs_data2():
    from method.sqlMethod import mysql2df

    dict1 = {
        "first_update": "first_update",
        "last_update": "last_update",
        "date": "date",
        "股价": "id_035_mvs_sp",
        "成交量": "id_036_mvs_tv",
        "成交金额": "id_048_mvs_ta",
        "市值": "id_041_mvs_mc",
        "流通市值": "id_042_mvs_cmc",
    }

    dict1 = {
        "first_update": "first_update",
        "last_update": "last_update",
        "date": "date",
        "PRICE": "id_035_mvs_sp",
        "TRADE_VOLUME": "id_036_mvs_tv",
        "TRADE_AMOUNT": "id_048_mvs_ta",
        "MARKET_CAP": "id_041_mvs_mc",
        "CIRC_MARKET_CAP": "id_042_mvs_cmc",
    }

    df = get_code_profile_df()
    code_list = df[df['area'] == 'cn'].index.to_list()

    for code in code_list:
        database = 'marketData'
        table = 'mvs_%s' % code
        df = mysql2df(database=database, table=table)

        columns = list(dict1.values())
        df = df.reindex(columns=columns)

        df.columns = dict1.keys()

        print(df)
        break


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    pass
