import json
import pandas as pd
import numpy as np
from method.fileMethod import *
from functools import wraps


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


def sift_show_table(sort_by, ascending):
    src = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")

    src['aaa'] = src['market_value_1'] / pd.to_numeric(src['gui_assessment'])

    print(src['aaa'])
    df = src.sort_values(by=sort_by, ascending=ascending)

    ret = df.index.values.tolist()
    print(ret)


def deco_show_stock_name(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        res = func(*args, **kwargs)

        self = args[0]
        self.show_stock_name()
        return res

    return wrapped_function


def discount_to_date(src, rate):
    val = np.log(src) / np.log(rate)
    if not pd.isna(val):
        val_year = int(abs(val))
        val_month = int((abs(val) % 1) * 12)

        str_pre = '-' if val < 0 else ''
        str_year = '%s年' % val_year if val_year != 0 else ''
        str_month = '%s个月' % val_month if val_year == 0 or val_month != 0 else ''
        ret = '%s%s%s' % (str_pre, str_year, str_month)
    else:
        ret = None
    return ret


def try_decorator(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except BaseException as e:
            print(e)
            raise KeyboardInterrupt
    return wrapped_function


def sort_tags(src: list):
    src = src.copy()
    ret1 = []
    ret2 = []
    # tmp = {
    #     'Src': 'Src',
    #     'Toc': 'ToC',
    #     'Mid': 'Mid',
    #     '排除': '排',
    #     '自选': '自选',
    #     '白名单': '白',
    #     '黑名单': '黑',
    #     '灰名单': '灰',
    #     '周期': '周期',
    #     '疫情': '疫',
    #     '忽略': '忽略',
    #     '国有': '国',
    #     '低价': '低',
    #     '新上市': '新上市',
    #     '未上市': '未上市',
    #     '买入': '买入',
    #     '自选202307': None,
    #     '测试20230516': None,
    # }

    tmp = {
        '买入': '买入',
        '关注': '关注',
        '自选': '自选',
        '白名单': '白',
    }

    for key, value in tmp.items():
        if key in src:
            ret1.append(value)
            src.pop(src.index(key))

    tmp = {
        'Src': 'green',
        'Toc': 'green',
        # '买入': 'green',
        # '关注': 'green',
        # '自选': 'green',
        # '白名单': 'green',
        '灰名单': 'yellow',
        '国有': 'yellow',
        '周期': 'yellow',
        '低价': 'yellow',
        'Mid': 'red',
        '排除': 'red',
        '黑名单': 'red',
        '忽略': 'red',
        '疫情': 'red',
        '新上市': 'red',
        '未上市': 'red',
    }

    for key, value in tmp.items():
        if key in src:
            ret2.append([key, value])
            # if value is not None:
            #     ret.append(value)
            src.pop(src.index(key))

    src.sort()
    for value in src:
        # ret.append(value)
        ret2.append([value, 'yellow'])

    return ret1, ret2


if __name__ == '__main__':
    sift_show_table('real_pe_return_rate', False)
    pass
