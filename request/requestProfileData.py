from request.requestData import split_metrics
from method.logMethod import log_it, MainLog
from method.sqlMethod import df2mysql
from method.sqlMethod import mysql2df

import urllib.request
import requests
import json
import time
import pandas as pd


@log_it(None)
def request_security_profile_cn():
    url = 'https://open.lixinger.com/api/a/company'

    data = {"token": "f819be3a-e030-4ff0-affe-764440759b5c"}

    post_data = json.dumps(data)
    header_dict = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
    res_txt = urllib.request.urlopen(req).read().decode()
    res = json.loads(res_txt)['data']

    df = pd.DataFrame(res)
    df = df.set_index(keys='stockCode', drop=False)
    df['mutualMarkets'] = df['mutualMarkets'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

    database = 'stock_profile_data'
    table = 'security_profile_cn'

    df["first_update"] = pd.NA
    df["last_update"] = pd.NA

    df2mysql(df=df, database=database, table=table, ini=True, log=False)

    data_list = res
    name_dict = dict()
    date_dict = dict()
    type_dict = dict()
    for data in data_list:
        code = data["stockCode"]
        if "name" in data:
            name_dict[code] = data["name"]
        if "ipoDate" in data:
            date_dict[code] = data["ipoDate"]
        else:
            date_dict[code] = None
        if "fsTableType" in data:
            type_dict[code] = data["fsTableType"]

    code_list = list(name_dict.keys())

    return code_list, name_dict, date_dict, type_dict


@log_it(None)
def request_company_profile_cn():
    database = 'stock_profile_data'
    table = 'security_profile_cn'
    df = mysql2df(database, table, fields=['stockCode'])
    codes = df['stockCode'].tolist()

    url = 'https://open.lixinger.com/api/cn/company/profile'

    stock_codes_list = split_metrics(codes, 100)
    data_list = []
    for index, sub_codes in enumerate(stock_codes_list):
        data = dict()
        data["token"] = "f819be3a-e030-4ff0-affe-764440759b5c"
        data["stockCodes"] = sub_codes

        post_data = json.dumps(data)
        header_dict = {'Content-Type': 'application/json'}

        MainLog.add_log('    index --> %s/%s' % (index+1, len(stock_codes_list)))
        MainLog.add_log('    stock_codes --> %s' % sub_codes)

        req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
        res_txt = urllib.request.urlopen(req).read().decode()
        data_list.extend(json.loads(res_txt)['data'])

    df = pd.DataFrame(data_list)
    df = df.set_index(keys='stockCode', drop=False)

    for column in [
        'historyStockNames',
        'actualControllerTypes',
        'independentDirectors',
    ]:

        df[column] = df[column].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

    # path = "../basicData/tmp/cn_company_profile_tmp.pkl"
    # dump_pkl(path, df)
    #
    # df = load_pkl(path)
    # for column in df.columns:
    #     length = 0
    #     if column == 'registeredCapital':
    #         continue
    #     for val in df[column].values:
    #         if pd.isna(val):
    #             continue
    #         length = max(length, len(val.encode('utf-8')))
    #     print(column, length)

    database = 'stock_profile_data'
    table = 'stock_profile_cn'

    df["first_update"] = pd.NA
    df["last_update"] = pd.NA

    df2mysql(df=df, database=database, table=table, ini=True, log=False)


def request_security_profile_hk():
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


def request_company_profile_hk():
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


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    pass
