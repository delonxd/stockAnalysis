import pandas as pd
import time
import requests

from method.fileMethod import write_json_txt
from method.fileMethod import load_json_txt
# from method.fileMethod import dump_pkl
from method.fileMethod import load_pkl
from method.sqlMethod import df2mysql
from method.logMethod import MainLog


def get_all_us_code_profile():
    page = 0
    ret = pd.DataFrame()
    while True:
        time.sleep(1)
        page += 1
        url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
        params = {
            "reportName": "RPT_USF10_INFO_ORGPROFILE",
            "columns": "SECUCODE,SECURITY_CODE,SECURITY_INNER_CODE,SECURITY_NAME_ABBR,"
                       'ORG_CODE,ORG_NAME,ORG_EN_ABBR,'
                       'BELONG_INDUSTRY,FOUND_DATE,CHAIRMAN,'
                       'EMP_NUM,ORG_TEL,ORG_FAX,ORG_EMAIL,ORG_WEB,'
                       'REG_PLACE,ADDRESS,ORG_PROFILE',
            "quoteColumns": "",
            "filter": "",
            "pageNumber": str(page),
            "pageSize": "",
            "sortTypes": "1",
            "sortColumns": "SECUCODE",
            "source": "SECURITIES",
            "client": "PC",
            "v": "04406064331266868",
        }

        r = requests.get(url, params=params)
        data_json = r.json()
        res = data_json.get("result")
        if res is None:
            break
        print(page)
        tmp = pd.DataFrame(res["data"])
        ret = pd.concat([ret, tmp])

    # df = ret.copy()
    # database = 'stock_profile_data'
    # table = 'stock_profile_us'
    #
    # df["first_update"] = pd.NA
    # df["last_update"] = pd.NA
    # df2mysql(df=df, database=database, table=table, ini=True)
    #
    # # path = "../basicData/foreignCodes/all_us_code_profile.pkl"
    # # dump_pkl(path, ret, log=True)
    # # stock_code = data_json["result"]["data"][0]["SECUCODE"]
    # # return stock_code


def load_all_us_code_profile():
    path = "../basicData/foreignCodes/all_us_code_profile.pkl"
    df = load_pkl(path)
    for column in df.columns:
        length = 0
        if column == 'EMP_NUM':
            continue
        for val in df[column].values:
            if pd.isna(val):
                continue
            length = max(length, len(val.encode('utf-8')))
        print(column, length)


def regular_stock_code_us(symbol: str) -> str:
    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"
    params = {
        "reportName": "RPT_USF10_INFO_ORGPROFILE",
        "columns": "SECUCODE,SECURITY_CODE,ORG_CODE,SECURITY_INNER_CODE,ORG_NAME,ORG_EN_ABBR,BELONG_INDUSTRY,"
        "FOUND_DATE,CHAIRMAN,REG_PLACE,ADDRESS,EMP_NUM,ORG_TEL,ORG_FAX,ORG_EMAIL,ORG_WEB,ORG_PROFILE",
        "quoteColumns": "",
        "filter": f'(SECURITY_CODE="{symbol}")',
        "pageNumber": "1",
        "pageSize": "200",
        "sortTypes": "",
        "sortColumns": "",
        "source": "SECURITIES",
        "client": "PC",
        "v": "04406064331266868",
    }

    r = requests.get(url, params=params)
    data_json = r.json()
    print(data_json)
    stock_code = data_json["result"]["data"][0]["SECUCODE"]
    return stock_code


def stock_financial_us_report_em(stock: str, symbol: str) -> pd.DataFrame:
    time.sleep(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }

    url = "https://datacenter.eastmoney.com/securities/api/data/v1/get"

    if symbol == "资产负债表":
        report_name = "RPT_USF10_FN_BALANCE"
    elif symbol == "综合损益表":
        report_name = "RPT_USF10_FN_INCOME"
    elif symbol == "现金流量表":
        report_name = "RPT_USSK_FN_CASHFLOW"
    else:
        raise ValueError("请输入正确的 symbol 参数")

    params = {
        "reportName": report_name,
        "columns": "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,"
                   "REPORT_DATE,REPORT_TYPE,REPORT,"
                   "DATE_TYPE_CODE,FISCAL_YEAR,CURRENCY,"
                   "STD_ITEM_CODE,AMOUNT,ITEM_NAME,",
        "quoteColumns": "",
        "filter": f'(SECUCODE="{stock}")',
        "pageNumber": "",
        "pageSize": "",
        "sortTypes": "1,-1",
        "sortColumns": "REPORT,STD_ITEM_CODE",
        "source": "SECURITIES",
        "client": "PC",
        "v": "09583551779242467",
    }
    r = requests.get(url, params=params, headers=headers)
    data_json = r.json()
    ret = pd.DataFrame(data_json["result"]["data"])
    return ret


def get_header_mapping_table_us(df):
    df = df.copy()
    df['header_name'] = df.apply(lambda x: f"{x['column_header']} | {x['ITEM_NAME']}", axis=1)

    df = df.set_index('header_name', drop=False)
    df = df[~df.index.duplicated(keep='first')]

    ret = list(df.index)

    path = "../basicData/foreignCodes/us_header_mapping_table.txt"
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


def regular_us_df_src(df, sheet_name):
    df['column_header'] = df['STD_ITEM_CODE'].apply(lambda x: '%s_%s' % (sheet_name, x))
    df['standard_date'] = df['REPORT_DATE'].str[:10]
    df['standard_date'] = df.apply(lambda x: f"{x['standard_date']}  ({x['FISCAL_YEAR']})", axis=1)
    df['mix_index'] = df.apply(lambda x: f"{x['standard_date']} | ({x['column_header']})", axis=1)
    if sheet_name in ['ps', 'cfs']:
        type_dict = {
            '007': '001',
            '008': '002',
            '003': '003',
            '006': '004',
        }
        type_list = list(type_dict.keys())
        df = df[df['DATE_TYPE_CODE'].isin(type_list)]
        df.loc[:, 'DATE_TYPE_CODE'] = df['DATE_TYPE_CODE'].map(type_dict).copy()

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
        'CURRENCY',
        'STD_ITEM_CODE',
        'ITEM_NAME',
        'AMOUNT',
    ]

    df = df.reindex(columns=columns)

    MainLog.add_log('    %s sheet shape: %s' % (sheet_name, repr(df.shape)))
    # print(df)
    # print(df.shape)
    return df


def get_us_financial_sheet(code):
    MainLog.add_log('request fs table --> %s' % code)

    df_src1 = stock_financial_us_report_em(stock=code, symbol="资产负债表")
    df_src1 = regular_us_df_src(df_src1, 'bs')

    df_src2 = stock_financial_us_report_em(stock=code, symbol="综合损益表")
    df_src2 = regular_us_df_src(df_src2, 'ps')

    df_src3 = stock_financial_us_report_em(stock=code, symbol="现金流量表")
    df_src3 = regular_us_df_src(df_src3, 'cfs')

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
        'CURRENCY',
    ]
    df0 = df0.loc[:, columns]
    ret = pd.concat([df0, df], axis=1, sort=True)
    ret = ret.dropna(subset='STD_REPORT_DATE').copy()

    get_header_mapping_table_us(df_src)

    ret.insert(0, "last_update", pd.NA)
    ret.insert(0, "first_update", pd.NA)

    MainLog.add_log('get_us_financial_sheet complete.')

    return ret


def get_us_data2mysql():
    from method.sqlMethod import mysql2df
    df_src = mysql2df(
        database='stock_profile_data',
        table='stock_profile_us',
        fields=['SECUCODE'],
    )
    code_list = []

    for code in df_src['SECUCODE'].tolist():
        if code.split('.')[1] == 'F':
            continue
        code_list.append(code)

    print(code_list)
    print(len(code_list))

    # path = "../basicData/foreignCodes/code_list_foreign.txt"
    # src = load_json_txt(path)
    #
    # code_list = []
    # for val in src:
    #     market, code = val.split('-')
    #     if market == 'us':
    #         code_list.append(code)
    # print(code_list)
    # code_list = ['AFBI.O']
    code_list = ['ONEW.O']
    for index, code in enumerate(code_list):
        # if index < 775:
        #     continue
        MainLog.add_split('#')
        MainLog.add_log('index --> %s / %s' % (index, len(code_list)))

        try:
            df = get_us_financial_sheet(code)
            database = 'fsData_us'
            table = 'fs_us_%s' % code.replace('.', '_')

            MainLog.add_log('df2mysql --> %s' % code)
            df2mysql(df=df, database=database, table=table, ini=True, log=False)
            pass

        except BaseException as e:
            MainLog.add_log('request error --> %s' % code)
            path = "../basicData/foreignCodes/us_except_code_list.txt"
            tmp = load_json_txt(path)
            tmp[code] = str(e)
            write_json_txt(path, tmp)
        # break


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    get_us_data2mysql()
    # get_us_financial_sheet("VERV.O")
