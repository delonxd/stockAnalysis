from method.fileMethod import load_json_txt
from method.sqlMethod import mysql2df
from method.sqlMethod import df2mysql

import pandas as pd
import re


def regular_controller_name(src):
    if pd.isna(src):
        return pd.NA
    lst = src.split(';')
    if len(lst) > 5:
        return ';'.join(lst[:5]) + '等%s人' % len(lst)
    return src


def regular_controller_type(src):
    if pd.isna(src):
        return pd.NA
    table = {
        'natural_person': '自然人',
        'collective': '集体',
        'foreign_company': '外企',
        'state_owned': '国有',
    }

    lst = src.split(',')
    return '&'.join(map(lambda x: table[x], lst))


def regular_board_cn(src):
    if pd.isna(src):
        return pd.NA
    lst = src.split('.')
    if lst[2] == 'b':
        ret = 'B股'
    elif lst[0] == '北京交易所':
        ret = '新三板'
    elif lst[1][:2] == '68':
        ret = '科创板'
    elif lst[1][:1] == '3':
        ret = '创业板'
    elif lst[1][:1] in ['0', '6']:
        ret = '主板'
    else:
        return pd.NA
    return ret


def regular_security_type_cn(src):
    if pd.isna(src):
        return pd.NA
    lst = src.split('.')
    if lst[2] == 'b':
        ret = 'B股'
    elif lst[1][:3] == '689':
        ret = '预托证券'
    else:
        return 'A股'
    return ret


def regular_reg_place_hk(src):
    if pd.isna(src):
        return pd.NA
    lst = src.split(' ')
    sub = list()
    for val in lst:
        if bool(re.match(r'^[a-zA-Z-]*$', val)):
            continue
        sub.append(val)
    ret = ' '.join(sub)
    return ret


def generate_all_code_info():
    ret = pd.DataFrame()

    path = '..\\basicData\\sqlFieldType\\sql_field_type_profile_combine.txt'
    columns = list(load_json_txt(path).keys())

    ####################################################################################################################
    # cn
    database = 'stock_profile_data'
    df1 = mysql2df(database=database, table='stock_profile_cn')
    df2 = mysql2df(database=database, table='security_profile_cn')

    df2 = df2.drop(['first_update', 'last_update', 'stockCode'], axis=1)

    df = pd.concat([df1, df2], axis=1, sort=True)
    df['code'] = df['stockCode']

    df['reg_place'] = df['province'] + '省' + df['city']
    table = {
        '北京省北京市': '北京市',
        '上海省上海市': '上海市',
        '重庆省重庆市': '重庆市',
        '天津省天津市': '天津市',
    }
    df['reg_place'] = '中国' + df['reg_place'].replace(table)

    df['found_date'] = df['establishDate'].str[:10]

    df['controller_name'] = df['actualControllerName'].apply(regular_controller_name)
    df.loc['002827', 'controller_name'] = '西藏自治区人民政府国有资产监督管理委员会'
    df['controller_type'] = df['actualControllerTypes'].apply(regular_controller_type)
    df['area'] = 'cn'

    table = {
        'sz': '深圳交易所',
        'sh': '上海交易所',
        'bj': '北京交易所',
    }
    df['exchange'] = df['exchange'].replace(table)

    df['type_info'] = df['exchange'] + '.' + df['code'] + '.' + df['market']
    df['board'] = df['type_info'].apply(regular_board_cn)

    df['security_type'] = df['type_info'].apply(regular_security_type_cn)
    df['mutual_markets'] = df['mutualMarkets'].replace('ha', '港股通')

    df['ipo_date'] = df['ipoDate'].str[:10]
    df['fs_type'] = df['fsTableType']

    src = load_json_txt('..\\basicData\\industry\\sw_2021_dict.txt')
    s0 = pd.Series(src, name='industry_lv3').dropna()
    name_dict = load_json_txt('..\\basicData\\industry\\sw_2021_name_dict.txt')

    df_ids = pd.DataFrame(s0)
    df_ids['industry_lv1'] = df_ids['industry_lv3'].str[:2] + '0000'
    df_ids['industry_lv2'] = df_ids['industry_lv3'].str[:4] + '00'
    df_ids = df_ids.replace(name_dict)

    df = pd.concat([df, df_ids], axis=1)
    df = df.reindex(columns=columns)

    ret = pd.concat([ret, df], axis=0)

    ####################################################################################################################
    # hk
    database = 'stock_profile_data'
    df1 = mysql2df(database=database, table='stock_profile_hk')
    df2 = mysql2df(database=database, table='security_profile_hk')

    lst = [
        'first_update',
        'last_update',
        'SECUCODE',
        'SECURITY_CODE',
        'SECURITY_NAME_ABBR',
    ]
    df2 = df2.drop(lst, axis=1)

    df = pd.concat([df1, df2], axis=1, sort=True, join='inner')
    df['code'] = 'hk-' + df['SECURITY_CODE']
    df['name'] = df['SECURITY_NAME_ABBR']
    df['reg_place'] = df['REG_PLACE'].apply(regular_reg_place_hk)
    df['found_date'] = df['FOUND_DATE'].str[:10]
    df['chairman'] = df['CHAIRMAN']

    df['area'] = 'hk'
    df['exchange'] = df['TRADE_MARKET']
    df['board'] = df['BOARD']

    table = {
        '是是': '沪深通',
        '是否': '沪股通',
        '否是': '深股通',
        '否否': pd.NA,
    }

    df['mutual_markets'] = df['GANGGUTONGBIAODIHU'] + df['GANGGUTONGBIAODISHEN']
    df['mutual_markets'] = df['mutual_markets'].replace(table)
    df['security_type'] = df['SECURITY_TYPE']
    df['ipo_date'] = df['LISTING_DATE'].str[:10]
    df['fs_type'] = 'hk_004'

    df['industry_lv1'] = df['BELONG_INDUSTRY']
    df['website'] = df['ORG_WEB']

    df = df.reindex(columns=columns)
    ret = pd.concat([ret, df], axis=0)

    ####################################################################################################################
    # todo us

    # print(ret)

    # print(df['mutual_markets'].size)
    # print(df['mutual_markets'])

    # print('-----')
    # s1 = df[~df['mutual_markets'].duplicated()]['mutual_markets']
    # print(s1)

    # for column in df.columns:
    #     length = 0
    #     if column == 'registeredCapital':
    #         continue
    #     for val in df[column].values:
    #         if pd.isna(val):
    #             continue
    #         length = max(length, len(val.encode('utf-8')))
    #     print(column, length)
    #
    # for index, row in df.iterrows():
    #     txt = row['controller_name']
    #     if pd.isna(txt):
    #         continue
    #
    #     length = len(txt.encode('utf-8'))
    #
    #     if length > 100:
    #         print(row['code'])
    #         print(length)
    #         print(txt)

    database = 'stock_profile_data'
    table = 'code_profile_combine'

    ret["first_update"] = pd.NA
    ret["last_update"] = pd.NA

    df2mysql(df=ret, database=database, table=table, ini=False)


# def test001():
#     import re
#
#     pattern = r'(.+?)\1+'
#     pattern
#     matches = re.findall(pattern, txt)
#     print(matches)
#     return matches


if __name__ == '__main__':

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    generate_all_code_info()
    # test001()
