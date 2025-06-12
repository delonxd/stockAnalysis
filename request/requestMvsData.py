from method.fileMethod import load_json_txt
from method.logMethod import MainLog
from method.profileMethod import get_code_profile_df
from method.sqlMethod import df2mysql

import requests
import time
import pandas as pd
# import akshare as ak


def request_mvs_data_hk(code: str) -> pd.DataFrame | None:

    area = code[:2]
    if area != 'hk':
        return
    symbol = code[3:]

    time.sleep(1)

    url = "https://33.push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": f"116.{symbol}",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f56,f57",
        "klt": "101",
        "fqt": "",
        "end": "20500000",
        "lmt": "1000000",
    }
    r = requests.get(url, timeout=15, params=params)
    data_json = r.json()

    res = data_json.get("data")
    if res is None:
        return

    df = pd.DataFrame([item.split(",") for item in res["klines"]])

    if df.empty:
        return

    df.columns = [
        "date",
        "OPEN",
        "CLOSE",
        "TRADE_VOLUME",
        "TRADE_AMOUNT",
    ]

    df["OPEN"] = pd.to_numeric(df["OPEN"], errors="coerce")
    df["CLOSE"] = pd.to_numeric(df["CLOSE"], errors="coerce")
    df["TRADE_VOLUME"] = pd.to_numeric(df["TRADE_VOLUME"], errors="coerce")
    df["TRADE_AMOUNT"] = pd.to_numeric(df["TRADE_AMOUNT"], errors="coerce")
    df["date"] = df["date"]
    df = df.sort_values('date')

    return df


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


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # request_mvs_data_hk('hk-00001')
    request_mvs2mysql_hk()

    pass
