from method.fileMethod import load_json_txt
from method.fileMethod import write_json_txt
from method.logMethod import MainLog
from method.sqlMethod import df2mysql
from method.sqlMethod import mysql2df
from request.requestAkshareHkData import request_fs_data_hk_em
import pandas as pd


def update_fs_data_hk():
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


def get_hk_financial_sheet(code):
    MainLog.add_log('request fs table --> %s' % code)

    df_src1 = request_fs_data_hk_em(stock=code, symbol='资产负债表')
    df_src1 = regular_hk_df_src(df_src1, 'bs')

    df_src2 = request_fs_data_hk_em(stock=code, symbol='利润表')
    df_src2 = regular_hk_df_src(df_src2, 'ps')

    df_src3 = request_fs_data_hk_em(stock=code, symbol='现金流量表')
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


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # import warnings
    # from scipy.optimize import OptimizeWarning
    # warnings.simplefilter("ignore", OptimizeWarning)
    # warnings.simplefilter(action='ignore', category=FutureWarning)
