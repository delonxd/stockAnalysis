from method.profileMethod import get_code_profile_df
from method.sqlMethod import df2mysql
from method.sqlMethod import mysql2df
from method.fileMethod import load_json_txt
from method.fileMethod import dump_pkl
from method.fileMethod import load_pkl
import pandas as pd
import numpy as np
import re


def update_dv_data_hk():
    pass


def hk_dv_rf2hk_dv_data_tmp_pkl():
    df = get_code_profile_df()
    df = df[df['area'] == 'hk']

    code_list = df.index.to_list()
    # code_list = ['hk-00316']
    # index = code_list.index('hk-01273')
    # code_list = code_list[:index]
    print(code_list)

    date_set = set()
    dv_data = dict()
    type_set = set()

    outer_counter = 0
    size = len(code_list)
    counter = 0
    for code in code_list:
        outer_counter += 1
        # MainLog.add_log_accurate(f'{code} {outer_counter}/{size}')

        database = 'dvData_hk_rf'
        table = f'dv_hk_{code[3:]}'

        df = mysql2df(database=database, table=table)

        # content = df['content']
        if df.size == 0:
            continue

        last_ann = df.iloc[-1, :].loc['announcementDate']

        dv_lst = list()
        for index, row in df.iterrows():
            txt = row['content']
            if pd.isna(txt):
                continue

            tmp = txt
            tmp = re.sub(r'\([^()]*\)', '', tmp)
            tmp = re.sub(r'(?<=\d),(?=\d|$)', '', tmp)
            tmp = re.sub(r',(?= Inc.)', '', tmp)
            tmp = re.sub(r',当中包括.*。$', '', tmp)

            tmp = tmp.replace('。', '')
            tmp = tmp.replace(' ', '')
            tmp = tmp.replace('\n', '')

            tmp = tmp.replace('，', ',')
            tmp = tmp.replace(';', ',')
            tmp = tmp.replace('；', ',')

            tmp = re.sub(r'(?<=[^,])每', ',每', tmp)

            sub_lst = tmp.split(',')

            # tmp = tmp.removesuffix('|')
            # sub_txt = re.sub(r'\([^()]*\)', '', sub_txt)

            # print(sub_lst)
            for sub_txt in sub_lst:
                val = re_dv_hk_rf_sub_txt(sub_txt)
                # if val is None:
                #     MainLog.add_log_accurate(f'{code} {outer_counter}/{size} {sub_txt}')

                if val is None or val[0] == 0:
                    continue

                if row['status'] == '实施终止':
                    continue

                date = row['exDate']
                if pd.isna(date):
                    if last_ann != row['announcementDate']:
                        continue
                    else:
                        date = "2025-06-18"
                        # MainLog.add_log_accurate(f'{code} {outer_counter}/{size} {sub_txt}')

                # if val[1] in '林吉特':
                #     print(date, val[1])
                #     MainLog.add_log_accurate(f'{code} {outer_counter}/{size} {sub_txt}')

                date_set.add(date)
                report_type = row['reportType']

                if report_type is None:
                    report_type = '其他'
                elif report_type[:3] == '一季报':
                    report_type = '一季报'
                elif report_type[:3] == '二季报':
                    report_type = '中报'
                elif report_type[:3] == '三季报':
                    report_type = '三季报'
                elif report_type[:3] == '四季报':
                    report_type = '年报'

                dv_lst.append([date, val[0], val[1], report_type])

                type_set.add(report_type)
                print(f'{code} {outer_counter}/{size}', counter, sub_txt, report_type)
                counter += 1

        if len(dv_lst) > 0:
            dv_data[code] = dv_lst

    print(type_set)
    path = "..\\basicData\\tmp\\hk_dv_data_tmp.pkl"
    dump_pkl(path, dv_data)


def hk_dv_data_tmp_pkl2mysql():
    path = "..\\basicData\\tmp\\hk_dv_data_tmp.pkl"
    dv_data: dict = load_pkl(path)

    date_set = set()
    for value in dv_data.values():
        for date, _, _, _ in value:
            date_set.add(date)
    lst1 = list(date_set)

    df = mysql2df(database='basicData', table='exchange_rate')
    path = "..\\basicData\\chineseComparison\\zh_cmp_table_exchange_rate.txt"
    cmp_table = load_json_txt(path)
    df = df.reindex(columns=cmp_table.values())
    df.columns = cmp_table.keys()

    lst2 = df.index.to_list()

    dates = list(set(lst1 + lst2))
    dates.sort()
    df_exchange = df.reindex(dates)
    df_exchange['人民币'] = 1

    outer_counter = 0
    size = len(dv_data)
    for code, dv_lst in dv_data.items():
        outer_counter += 1
        print(f'{code} {outer_counter}/{size}')

        eq_df = mysql2df(database='eqData_hk', table=f'eq_hk_{code[3:]}')
        eq_df = eq_df.sort_index()
        eq_df['LAST_TOTAL_SHARES'] = eq_df['TOTAL_SHARES'].shift(1)
        tmp = pd.concat([df_exchange, eq_df], axis=1, sort=True)
        tmp = tmp.ffill(axis=0)

        val_dict = dict()
        for row in dv_lst:
            date = row[0]
            val = row[1]
            currency = row[2]
            report_type = row[3]

            row_info = tmp.loc[date, :]
            val2 = np.round(val * row_info[currency] * row_info['LAST_TOTAL_SHARES'])
            val1 = val_dict.get(date)
            if val1 is None:
                val_dict[date] = [val2, report_type]
            else:
                if report_type == '其他':
                    report_type = val1[1]
                val_dict[date] = [val1[0] + val2, report_type]
            # print(code, row, val2)

        df = pd.DataFrame.from_dict(val_dict, orient='index', columns=['DIVIDEND', 'REPORT_TYPE'])
        df = df.dropna(subset='DIVIDEND').sort_index()
        df = df.reindex(columns=['first_update', 'last_update', 'date', 'DIVIDEND', 'REPORT_TYPE'])
        df['date'] = df.index

        df2mysql(df, database='dvData_hk_regular', table=f'df_hk_reg_{code[3:]}', ini=True, log=False)
        # print(df)
        # break


def re_dv_hk_rf_sub_txt(sub_txt):
    # prefix1 = r'^每(1)?(股)?((本)?公司)?(已发行)?' \
    #           r'((合并后)?普通(股)?|H股|合并|拆细(前)?|合共|经调整|换股|股|每股)?(股份)?' \
    #           r'(普通股及(每股)?可换股优先股)?'
    #
    # prefix1 = r'^(每(1)?(普通)?股((.*)(股|股份))?' \
    #           r'|每|每股份|每拆细股份|每持有1股股份|每每股|每股合共|每派股' \
    #           r'|(每(个)?股份合订单位|每份香港预托证券)' \
    #           r'|(每(?P<times>10|100|1000)股(股份|H股)?))'
    #
    # prefix2 = r'^每(个)?股份合订单位|每份香港预托证券'
    # prefix3 = r'^每(10|100|1000)股(股份|H股)?'
    #
    # mid1 = '(拟|(将)?获|应得)?(派|分配|分派|派付|派息)?(发|送)?' \
    #        '(的)?(现金)?(分红|股利|红利|((应付)?(的|之)?((中|末)?期)?股息))?(约)?((金额)?为(现金)?)?(税前)?'
    #
    # suffix1 = r'(?P<value>(\d+(\.\d+)?港(.*)|港(.*))'
    #
    # suffix1 = r'(\d+(\.\d+)?(港)?元)?' \
    #           r'(\d+(\.\d+)?角)?' \
    #           r'(\d+(\.\d+)?(港)?(仙|分))?' \
    #           r'(\d+(\.\d+)?)?' \
    #           r'(港元|港仙|港分|港|元)'
    #
    # suffix2 = r'(港币|港元|港)' \
    #           r'(\d+(\.\d+)?(港)?元)?' \
    #           r'(\d+(\.\d+)?角)?' \
    #           r'(\d+(\.\d+)?(港)?(仙|分))?' \
    #           r'(\d+(\.\d+)?)?'

    # suffix3 = r'人民币(\d+(\.\d+)?元(人民币)?)?(\d+(\.\d+)?角)?(\d+(\.\d+)?(仙|分))?(\d+)?'
    # suffix4 = r'\d+(\.\d+)?(人民币元|人民币|元人民币|分人民币|人民币分)'
    #
    # suffix5 = r'\d+(\.\d+)?(美元|美仙|美分)$'
    # suffix6 = r'\d+(\.\d+)?(加元|加拿大元|欧元|欧仙|日元|新加坡元|新分|英镑|便士|令吉)$'
    #
    # suffix_tax = r'(\((含税|税前)\))?$'

    # prefix4 = r'^每(持)?(有)?\d+(\.\d+)?股.+股(份)?'
    # mid2 = '(将)?(可)?(获|获取|获得)?((分)?派|配)?(送|发|发行)?'
    # mid3 = '(转赠|转增|增发)'
    # r'^每(\d+)?股送\d+(\.\d+)?(红)?股$'
    # r'^每(持有)?(\d+)?股(现有)?(股份)?(可)?(获)?(派)?(送|发)\d+(\.\d+)?(股)?(红|新)?股$'
    # r'^(每)?(持有)?(\d+)?股(现有)?(股份)?(可)?获(发|发行)\d+(\.\d+)?(股|份)?(\d+年)?(红利)?认股权证$'
    # suffix4 = r'\d+(\.\d+)?(股)?(红|新)?(普通)?(股|股份)$'
    # suffix5 = r'\d+(\.\d+)?(股|份)?(\d+年)?(红利)?认股权证$'
    # suffix6 = r'(.*)\d+(\.\d+)?股.+股份(.*)?$'

    sub_txt = re.sub(r'(以及|及|或)$', '', sub_txt)

    re_list = [
        # r'^不分红$',
        # r'^可选择收取现金$',
        # r'^及$',
        r'^\D*$',
        r'^(.*)(股|股份|认股权证|股票|合订单位|基金单位|公司|股票股利)$',
        r'^(.*)(股份转增资本公积金|股份可选择收取现金|股份或支付相当现金)$',
        r'^每份名义价值为港币0.10元的红利可换股票据代替$',
        r'^每1股现有普通股按面值$',
        # r'^(.*)股份\(可选择可换股债券代替红股\)$',
        # r'^(.*)股份\(以下列方式收取:(.*)\)$',
    ]

    for re_txt in re_list:
        match = re.match(re_txt, sub_txt)
        if match is not None:
            # if re.match(r'^\D*$', sub_txt) is None:
            #     if re.match(r'^.*(及|或).*$', sub_txt) is not None:
            #         print(sub_txt)
            return 0, '港元'

    ####################################################################################################################

    # sub_txt = re.sub(r'\([^()]*\)', '', sub_txt)
    # sub_txt = re.sub(r'当中包括.*$', '', sub_txt)

    prefix = r'^(每(1)?(普通)?股((\D*)(股|股份))?' \
             r'|每|每股份|每拆细股份|每持有1股股份|每每股|每股合共|每派股' \
             r'|(每(个)?股份合订单位|每份香港预托证券)' \
             r'|(每股面值0.05港元(之)?股份)' \
             r'|(每(?P<multi>10|100|1000)股(股份|H股)?))'

    mid = r'(拟|(将)?(可)?获|应得)?(派|分配|分派|派付|派息)?(发|送)?' \
          r'(的)?(现金)?(分红|股利|红利|((应付)?(的|之)?((中|末)?期)?股息))?' \
          r'(约)?((金额)?为(现金)?)?(税前)?'

    prefix = prefix + mid

    unit_lst = [
        '元港币|港币|港元|港|元|元港元',
        '角港币',
        '仙港币|港仙|港分|港币港仙',
        '人民币元|人民币|元人民币',
        '分人民币|人民币分|分',
        '美元|美仙|美分',
        '加元|加拿大元',
        '欧元|欧仙',
        '日元',
        '新加坡元|新分',
        '英镑|便士',
        '令吉',
    ]
    tmp = '|'.join(unit_lst)

    re_txt = prefix + r'(?P<value>\d+(\.\d+)?)(?P<unit>%s)$' % tmp
    match = re.match(re_txt, sub_txt)
    if match is not None:
        multi = match.group('multi')
        value = match.group('value')
        unit = match.group('unit')
        return convert_currency(value=float(value), unit=unit, multi=multi)

    ####################################################################################################################

    re_txt = prefix + r'(?P<unit>港元|港币|人民币|新币|港)(?P<value>.+)$'
    match = re.match(re_txt, sub_txt)
    if match is not None:
        value = match.group('value')
        unit = match.group('unit')
        value = value.replace('币', '')
        value = value.replace('港', '')

        res = regular_currency_value(txt=value)
        if res is not None:
            multi = match.group('multi')
            return convert_currency(value=res, unit=unit, multi=multi)

    ####################################################################################################################

    re_txt = prefix + r'(?P<value>\d+(\.\d+)?.*)$'
    match = re.match(re_txt, sub_txt)
    if match is not None:
        value = match.group('value')
        value = value.replace('币', '')
        value = value.replace('港', '')

        res = regular_currency_value(txt=value)
        if res is not None:
            multi = match.group('multi')
            return convert_currency(value=res, unit='港币', multi=multi)

    tmp_lst = [
        # r'^每1000股股份收取约615股力宝华润有限公司股份或每()股(?P<value>0.564)(?P<unit>港元)$',
        # r'^以资本公积金转拨.*及现金分红每(10)股可获(?P<unit>人民币)(?P<value>0.5)元$',
        # r'^每股股份获发1股美的建业有限公司股份或收取现金每()股(?P<value>5.9)(?P<unit>港元)$',
        r'^每持有(1000)股股份可获发1股Mynd.aiInc.美国存托股份或(?P<value>137.38)(?P<unit>港元)$',
        r'^每持有(1)股股份派发1股私人公司股份及现金(?P<value>0.7803)(?P<unit>港元)$',
    ]

    for re_txt in tmp_lst:
        match = re.match(re_txt, sub_txt)
        if match is not None:
            value = match.group('value')
            unit = match.group('unit')

            return float(value), unit

    # print(sub_txt)
    return None


def regular_currency_value(txt: str) -> None | float:
    re_txt = r'^((?P<val1>\d+(\.\d+)?)元)?' \
              r'((?P<val2>\d+(\.\d+)?)角)?' \
              r'((?P<val3>\d+(\.\d+)?)(仙|分))?' \
              r'(?P<val4>\d+(\.\d+)?)?$'
    match = re.match(re_txt, txt)
    if match is None:
        return None

    multi_table = {
        'val1': 1,
        'val2': 0.1,
        'val3': 0.01,
        'val4': 0.001,
    }
    if match.group('val4') is not None:
        for i in ['val3', 'val2', 'val1']:
            if match.group(i) is not None:
                multi_table['val4'] = multi_table[i] * 0.1
                break
    ret = 0
    for key, value in multi_table.items():
        add = match.group(key)
        if add is not None:
            ret += (float(add) * value)
    return ret


def convert_currency(value: float | int, unit, multi):

    table = {
        '元港币': (1, '港元'),
        '港币': (1, '港元'),
        '港元': (1, '港元'),
        '港': (1, '港元'),
        '元': (1, '港元'),
        '元港元': (1, '港元'),

        '角港币': (0.1, '港元'),

        '仙港币': (0.01, '港元'),
        '港仙': (0.01, '港元'),
        '港分': (0.01, '港元'),
        '港币港仙': (0.01, '港元'),

        '人民币元': (1, '人民币'),
        '人民币': (1, '人民币'),
        '元人民币': (1, '人民币'),

        '分人民币': (0.01, '人民币'),
        '人民币分': (0.01, '人民币'),
        '分': (0.01, '人民币'),

        '美元': (1, '美元'),
        '美仙': (0.01, '美元'),
        '美分': (0.01, '美元'),

        '加元': (1, '加元'),
        '加拿大元': (1, '加元'),

        '欧元': (1, '欧元'),
        '欧仙': (0.01, '加元'),

        '日元': (1, '日元'),

        '新加坡元': (1, '新加坡元'),
        '新币': (1, '新加坡元'),
        '新分': (0.01, '新加坡元'),

        '英镑': (1, '英镑'),
        '便士': (0.01, '英镑'),

        '令吉': (1, '林吉特'),
    }

    indicator = table.get(unit)
    if indicator is None:
        print(unit)
        raise KeyboardInterrupt('unit不存在')

    ret1 = value * indicator[0]
    ret2 = indicator[1]
    if multi is not None:
        ret1 = ret1 / float(multi)

    return ret1, ret2


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 10000)
    hk_dv_data_tmp_pkl2mysql()
