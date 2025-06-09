import pandas as pd
import time
import requests

from method.fileMethod import write_json_txt
from method.fileMethod import load_json_txt
# from method.fileMethod import dump_pkl
from method.fileMethod import load_pkl

from method.sqlMethod import df2mysql
from method.logMethod import MainLog


def get_all_hk_security_profile():
    page = 0
    ret = pd.DataFrame()
    while True:
        time.sleep(1)
        page += 1
        url = 'https://datacenter.eastmoney.com/securities/api/data/v1/get'
        params = {
            'reportName': 'RPT_HKF10_INFO_SECURITYINFO',
            'columns': 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,'
                       'SECURITY_TYPE,ISIN_CODE,BOARD,'
                       'GANGGUTONGBIAODISHEN,GANGGUTONGBIAODIHU,'
                       'TRADE_MARKET,TRADE_UNIT,LISTING_DATE,'
                       'ISSUE_PRICE,ISSUE_NUM,PAR_VALUE,YEAR_SETTLE_DAY',
            # 'columns': 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,SECURITY_TYPE,LISTING_DATE,ISIN_CODE,BOARD,'
            #            'TRADE_UNIT,TRADE_MARKET,GANGGUTONGBIAODISHEN,GANGGUTONGBIAODIHU,PAR_VALUE,'
            #            'ISSUE_PRICE,ISSUE_NUM,YEAR_SETTLE_DAY',

            'quoteColumns': '',
            'filter': "",
            # 'pageNumber': '1',
            'pageNumber': str(page),
            'pageSize': '',
            'sortTypes': '1',
            'sortColumns': 'SECUCODE',
            'source': 'F10',
            'client': 'PC',
            'v': '04748497219912483'
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        res = data_json.get("result")

        if res is None:
            break
        print(page)
        tmp = pd.DataFrame(res["data"])
        ret = pd.concat([ret, tmp])

    df = ret.copy()
    database = 'stock_profile_data'
    table = 'security_profile_hk'

    df["first_update"] = pd.NA
    df["last_update"] = pd.NA
    df2mysql(df=df, database=database, table=table, ini=True)


def get_all_hk_code_profile():
    page = 0
    ret = pd.DataFrame()
    while True:
        time.sleep(1)
        page += 1
        url = 'https://datacenter.eastmoney.com/securities/api/data/v1/get'
        params = {
            'reportName': 'RPT_HKF10_INFO_ORGPROFILE',
            'columns': 'SECUCODE,SECURITY_CODE,SECURITY_INNER_CODE,SECURITY_NAME_ABBR,'
                       'ORG_CODE,ORG_NAME,ORG_EN_ABBR,'
                       'BELONG_INDUSTRY,FOUND_DATE,CHAIRMAN,SECRETARY,'
                       'EMP_NUM,ORG_TEL,ORG_FAX,ORG_EMAIL,ORG_WEB,'
                       'REG_PLACE,REG_ADDRESS,ADDRESS,ORG_PROFILE',
            'quoteColumns': '',
            'filter': "",
            'pageNumber': str(page),
            # 'pageNumber': "6",
            'pageSize': "",
            'sortTypes': '1',
            'sortColumns': 'SECUCODE',
            'source': 'F10',
            'client': 'PC',
            'v': '04748497219912483'
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        res = data_json.get("result")

        if res is None:
            break
        print(page)
        tmp = pd.DataFrame(res["data"])
        ret = pd.concat([ret, tmp])

        print(ret)
        return
    df = ret.copy()
    database = 'stock_profile_data'
    table = 'stock_profile_hk'

    df["first_update"] = pd.NA
    df["last_update"] = pd.NA
    df2mysql(df=df, database=database, table=table, ini=True)

    # path = "../basicData/foreignCodes/all_hk_code_profile.pkl"
    # dump_pkl(path, ret, log=True)
    # stock_code = data_json["result"]["data"][0]["SECUCODE"]
    # return stock_code


def stock_financial_hk_report_em(stock: str, symbol: str) -> pd.DataFrame:
    time.sleep(1)

    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

    if symbol == "资产负债表":
        report_name = "RPT_HKF10_FN_BALANCE_PC"
    elif symbol == "利润表":
        report_name = "RPT_HKF10_FN_INCOME_PC"
    elif symbol == "现金流量表":
        report_name = "RPT_HKF10_FN_CASHFLOW_PC"
    else:
        raise ValueError("请输入正确的 symbol 参数")

    params = {
        "reportName": report_name,
        "columns": "SECURITY_CODE,SECUCODE,SECURITY_NAME_ABBR,"
                   "REPORT_DATE,FISCAL_YEAR,DATE_TYPE_CODE,"
                   "STD_ITEM_CODE,AMOUNT,STD_ITEM_NAME",
        # "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,ORG_CODE,REPORT_DATE,DATE_TYPE_CODE,"
        #            "FISCAL_YEAR,STD_ITEM_CODE,STD_ITEM_NAME,AMOUNT,STD_REPORT_DATE",

        "quoteColumns": "",
        "filter": f'(SECUCODE="{stock}")',
        "pageNumber": "",
        "pageSize": "",
        "sortTypes": "-1,1",
        "sortColumns": "REPORT_DATE,STD_ITEM_CODE",
        "source": "F10",
        "client": "PC",
        "v": "01975982096513973",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    ret = pd.DataFrame(data_json["result"]["data"])
    print(ret.shape)
    return ret


def load_all_hk_code_profile():
    path = "../basicData/foreignCodes/all_hk_code_profile.pkl"
    df = load_pkl(path)
    # s0 = set()
    # for column in df.columns:
    #     length = 0
    #     if column == 'EMP_NUM':
    #         continue
    #     for val in df[column].values:
    #         if pd.isna(val):
    #             continue
    #         length = max(length, len(val.encode('utf-8')))
    #     print(column, length)

    database = 'stock_profile_data'
    table = 'stock_profile_hk'

    df["first_update"] = pd.NA
    df["last_update"] = pd.NA
    df2mysql(df=df, database=database, table=table, ini=True)


def get_header_mapping_table_hk(df):
    df = df.copy()
    df['header_name'] = df.apply(lambda x: f"{x['column_header']} | {x['STD_ITEM_NAME']}", axis=1)

    df = df.set_index('header_name', drop=False)
    df = df[~df.index.duplicated(keep='first')]

    ret = list(df.index)

    path = "../basicData/foreignCodes/hk_header_mapping_table2.txt"
    table0 = load_json_txt(path, log=False)

    for string in ret:
        tmp = string.split(' | ')
        key = tmp[0]
        value = tmp[1]

        value0 = table0.get(key)
        if value0 is None:
            table0[key] = value
        elif value != value0:
            code = df['SECUCODE'].iloc[0]
            code_name = df['SECURITY_NAME_ABBR'].iloc[0]
            txt = 'ITEM_NAME重复 %s %s %s %s' % (code, code_name, key, value)
            raise KeyboardInterrupt(txt)

    s0 = pd.Series(table0)
    table0 = s0.sort_index().to_dict()

    write_json_txt(path, table0, log=True)
    # print(ret)
    return ret


def regular_hk_df_src(df, sheet_name):
    df['column_header'] = df['STD_ITEM_CODE'].apply(lambda x: '%s_%s' % (sheet_name, x))
    df['standard_date'] = df['REPORT_DATE'].str[:10]
    df['standard_date'] = df.apply(lambda x: f"{x['standard_date']}  ({x['FISCAL_YEAR']})", axis=1)
    df['mix_index'] = df.apply(lambda x: f"{x['standard_date']} | ({x['column_header']})", axis=1)

    columns = [
        'mix_index',
        'standard_date',
        'column_header',
        'SECUCODE',
        'SECURITY_CODE',
        'SECURITY_NAME_ABBR',
        'REPORT_DATE',
        'FISCAL_YEAR',
        'DATE_TYPE_CODE',
        'STD_ITEM_CODE',
        'STD_ITEM_NAME',
        'AMOUNT',
    ]
    df = df.reindex(columns=columns)

    return df


def get_hk_financial_sheet(code):
    MainLog.add_log('request fs table --> %s' % code)

    df_src1 = stock_financial_hk_report_em(stock=code, symbol='资产负债表')
    df_src1 = regular_hk_df_src(df_src1, 'bs')

    df_src2 = stock_financial_hk_report_em(stock=code, symbol='利润表')
    df_src2 = regular_hk_df_src(df_src2, 'ps')

    df_src3 = stock_financial_hk_report_em(stock=code, symbol='现金流量表')
    df_src3 = regular_hk_df_src(df_src3, 'cfs')

    df_src = pd.concat([df_src1, df_src2, df_src3])
    df_src = df_src.drop_duplicates(subset=['mix_index'], keep='first')

    df = df_src.pivot(index='standard_date', columns='column_header', values='AMOUNT')

    # 获取pre_fields
    df0 = df_src.set_index('standard_date', drop=False)
    df0['STD_REPORT_DATE'] = df0['standard_date']
    df0 = df0[~df0.index.duplicated(keep='first')]
    columns = [
        'SECURITY_CODE',
        'SECUCODE',
        'SECURITY_NAME_ABBR',
        'STD_REPORT_DATE',
        'REPORT_DATE',
        'FISCAL_YEAR',
        'DATE_TYPE_CODE',
    ]
    df0 = df0.loc[:, columns]
    ret = pd.concat([df0, df], axis=1, sort=True)
    ret = ret.dropna(subset='STD_REPORT_DATE').copy()

    get_header_mapping_table_hk(df_src)

    ret.insert(0, "last_update", pd.NA)
    ret.insert(0, "first_update", pd.NA)

    MainLog.add_log('get_hk_financial_sheet complete.')

    return ret


def get_hk_data2mysql():
    from method.sqlMethod import mysql2df
    df_src = mysql2df(
        database='stock_profile_data',
        table='security_profile_hk',
        fields=['SECUCODE'],
    )
    code_list = df_src['SECUCODE'].tolist()

    print(code_list)
    print(len(code_list))

    # path = "../basicData/foreignCodes/code_list_foreign.txt"
    # src = load_json_txt(path)
    #
    # code_list = []
    # for val in src:
    #     market, code = val.split('-')
    #     if market == 'hk':
    #         code_list.append(code)
    # print(code_list)
    # print(len(code_list))

    # # code_list = ['01015']
    for index, code in enumerate(code_list):
        # if index < 775:
        #     continue
        MainLog.add_split('#')
        MainLog.add_log('index --> %s / %s' % (index, len(code_list)))

        try:
            df = get_hk_financial_sheet(code)
            table = 'fs_hk_%s' % code.split('.')[0]

            MainLog.add_log('df2mysql --> %s' % code)
            df2mysql(df, 'fsData_hk', table, ini=True, log=False)
        except BaseException as e:
            MainLog.add_log('request error --> %s' % code)
            path = "../basicData/foreignCodes/hk_except_code_list.txt"
            tmp = load_json_txt(path)
            tmp[code] = str(e)
            write_json_txt(path, tmp)
        # break


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # import warnings
    # from scipy.optimize import OptimizeWarning
    # warnings.simplefilter("ignore", OptimizeWarning)
    # warnings.simplefilter(action='ignore', category=FutureWarning)

    get_hk_data2mysql()
    # df11 = get_hk_financial_sheet('00001.HK')
    # print(df11)
