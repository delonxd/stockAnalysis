import json
import pandas as pd
from method.fileMethod import *


def res2df_fs(res, header_df, prefix='q', postfix='t'):
    index_dict = dict()
    tmp_df = transpose_df(header_df)

    counter = -1
    for index, row in tmp_df.iterrows():
        counter += 1
        sheet = row['sheet_name']
        api = row['api']
        if sheet and api:
            key = '.'.join([sheet, api])
            index_dict[key] = counter
        else:
            index_dict[index] = counter

    columns = header_df.columns
    length = len(columns)

    data_dict = dict()
    for subRes in res:
        sub_list = json.loads(subRes.decode())['data']
        for tmp in sub_list:
            date = tmp['standardDate']

            if date not in data_dict.keys():
                data_dict[date] = [None] * length

            for key, value in tmp.items():
                if key == prefix:
                    for infix in value.keys():
                        sub_dict = value[infix]
                        for subKey, subValue in sub_dict.items():
                            field = '.'.join([infix, subKey])
                            data_dict[date][index_dict[field]] = subValue.get(postfix)
                else:
                    data_dict[date][index_dict[key]] = value

    data_list = list()
    for key, value in data_dict.items():
        data_list.append(value)

    res_df = pd.DataFrame(data_list, columns=columns)
    res_df.set_index('standardDate', drop=False, inplace=True)

    # res_df.replace(to_replace=[None], value=np.NAN, inplace=True)
    return res_df


def res2df_mvs(res, header_df):
    index_dict = dict()
    tmp_df = transpose_df(header_df)

    counter = -1
    for index, row in tmp_df.iterrows():
        counter += 1
        sheet = row['sheet_name']
        api = row['api']
        if sheet and api:
            key = api
            index_dict[key] = counter
        else:
            index_dict[index] = counter

    columns = header_df.columns
    length = len(columns)

    data_dict = dict()

    sub_list = json.loads(res.decode())['data']
    for tmp in sub_list:
        date = tmp['date']

        if date not in data_dict.keys():
            data_dict[date] = [None] * length

        for key, value in tmp.items():
            data_dict[date][index_dict[key]] = value

    data_list = list()
    for key, value in data_dict.items():
        data_list.append(value)

    res_df = pd.DataFrame(data_list, columns=columns)
    res_df.set_index('date', drop=False, inplace=True)

    # res_df.replace(to_replace=[None], value=np.NAN, inplace=True)
    return res_df


def show_type(value):
    print(type(value), '-->', value)


def show_df(df):
    # print(df.columns)
    for tup in df.itertuples():
        print(tup)


def transpose_df(df):
    res = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
    return res


def get_units_dict():
    res = {
        '亿': 1e8,
        '万': 1e4,
        '元': 1,
        '人': 1,
        '百万': 1e6,
        '千': 1e3,
        '百': 1e2,
        '%': 1e-2,
        '倍': 1,
        '年': 1,
    }
    return res


def sift_codes(
        source=None,
        whitelist=None,
        blacklist=None,
        sort=None,
        market='all',
        timestamp=None,
):

    with open("..\\basicData\\industry\\industry_code_dict.txt", "r", encoding="utf-8", errors="ignore") as f:
        ind_dict = json.loads(f.read())

    set_all = list_to_set(source, ind_dict)
    set_white = list_to_set(whitelist, ind_dict)
    set_black = list_to_set(blacklist, ind_dict)

    set_time_sift = set()

    if timestamp is not None:
        with open("..\\basicData\\self_selected\\gui_timestamp.txt", "r", encoding="utf-8", errors="ignore") as f:
            gui_timestamp = json.loads(f.read())

        for key, value in gui_timestamp.items():
            if value > timestamp:
                set_time_sift.add(key)
                print('sift:', key, value)

    if market == 'all':
        pass

    elif market == 'main':
        for code in set_all:
            if code[:3] == '688':
                set_black.add(code)
            elif code[0] != '0' and code[0] != '6':
                set_black.add(code)

    elif market == 'non_main':
        for code in set_all:
            if code[0] == '0' or code[0] == '6':
                if code[:3] != '688':
                    set_black.add(code)

    elif market == 'growth':
        for code in set_all:
            if code[0] != '3':
                set_black.add(code)

    elif market == 'main+growth':
        for code in set_all:
            if code[:3] == '688':
                set_black.add(code)
            elif code[0] != '0' and code[0] != '6' and code[0] != '3':
                set_black.add(code)

    set_sift = set_all - set_black
    set_sift = set_sift - set_time_sift
    set_sift.update(set_white)

    res_list = []
    for code in sort:
        if code in set_sift:
            res_list.append(code)
    return res_list


def list_to_set(src, ind_dict):
    ret = set()
    if src is None:
        return ret
    else:
        for code in src:
            if code[0] == 'C':
                length = len(code)
                for key, value in ind_dict.items():
                    if code == key[:length]:
                        ret.update(set(value))
            else:
                ret.add(code)
        return ret


def sift_show_table(sort_by, ascending):
    src = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")

    src['aaa'] = src['market_value_1'] / pd.to_numeric(src['gui_assessment'])

    print(src['aaa'])
    df = src.sort_values(by=sort_by, ascending=ascending)

    ret = df.index.values.tolist()
    print(ret)


if __name__ == '__main__':
    sift_show_table('real_pe_return_rate', False)
    pass
