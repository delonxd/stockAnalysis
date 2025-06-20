from method.fileMethod import write_json_txt
from method.sqlMethod import mysql2df

import pandas as pd


def get_code_profile_df(code: str = None, fields: list = None) -> pd.DataFrame:
    if code is None:
        where = None
    else:
        where = 'code = "%s"' % code

    df = mysql2df(database='stock_profile_data', table='code_profile_combine',
                  fields=fields, where=where, sort=False)

    table = {
        'industry_lv1': 'level1',
        'industry_lv2': 'level2',
        'industry_lv3': 'level3',
    }
    df = df.rename(columns=table)

    if fields is None:
        df = df.drop(['first_update', 'last_update'], axis=1)
    return df


def get_hk_code_type():
    from method.sqlMethod import get_cursor, sql_get_fields
    df = get_code_profile_df()
    df = df[df['area'] == 'hk']

    counter = 0
    fs_type_dict = dict()

    database = 'fsData_hk'
    db, cursor = get_cursor(database)

    for code in df.index:
        counter += 1

        sec_code = code.split('-')[1]
        table = 'fs_hk_%s' % sec_code
        columns = sql_get_fields(cursor, table)
        db.commit()

        s0 = pd.Series(columns)
        s0 = s0[s0.str.contains('bs_00')].to_list()

        if len(s0) > 0:
            val = 'hk_' + s0[0][3:6]
        else:
            val = 'hk_nan'

        if val != 'hk_004':
            print(counter, code, val)

        fs_type_dict[code] = val
        # if counter == 100:
        #     break

    path = '..\\basicData\\code_types_dict_hk_tmp.txt'
    write_json_txt(path, fs_type_dict)


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
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', 10000)

    pass

