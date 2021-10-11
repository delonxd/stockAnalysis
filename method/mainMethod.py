import pickle
import re
import json

import pandas as pd
import numpy as np


def get_api_names(root, files, regular):

    api_list = list()
    for file in files:
        path = '%s/%s' % (root, file)
        with open(path, 'rb') as pk_f:
            text = pickle.load(pk_f)

        tmp = re.findall(regular, text)

        api_list.extend(tmp)

    return api_list


def config_api_names(infix_list, prefix=None, postfix=None):
    res_list = list()
    for infix in infix_list:
        tmp = list()
        if prefix:
            tmp.append(prefix)
        tmp.append(infix)
        if postfix:
            tmp.append(postfix)

        tmp_str = '.'.join(tmp)
        res_list.append(tmp_str)
    return res_list


def split_list(source, length):
    return_list = [[]]
    counter = 0
    for ele in source:
        if counter == length:
            return_list.append([])
            counter = 0
        return_list[-1].append(ele)
        counter += 1
    return return_list


def value2pkl(root, file_name, value):
    path = '%s/%s.pkl' % (root, file_name)
    with open(path, 'wb') as pk_f:
        pickle.dump(value, pk_f)


def read_pkl(root, file):
    path = '%s/%s' % (root, file)
    with open(path, 'rb') as pk_f:
        res = pickle.load(pk_f)
    return res


# def get_header_fs(root, file):
#     path = '%s/%s' % (root, file)
#     with open(path, 'rb') as pk_f:
#         res = pickle.load(pk_f)
#
#     data_header = [
#         ('代码', 'stockCode', 'VARCHAR(6)'),
#         ('货币', 'currency', 'VARCHAR(10)'),
#         ('标准日期', 'standardDate', 'VARCHAR(30) PRIMARY KEY'),
#         ('报告日期', 'reportDate', 'VARCHAR(30)'),
#         ('报告类型', 'reportType', 'VARCHAR(30)'),
#         ('日期', 'date', 'VARCHAR(30)'),
#     ]
#
#     for rowText in re.findall(r'\n(.*)', res):
#         tmp = re.findall(r'(.*):(.*)\.(.*)', rowText)
#
#         if len(tmp) == 0:
#             data_header.append((rowText, None, 'VARCHAR(1)'))
#         else:
#             data_header.append((tmp[0][0], tmp[0][2], 'DOUBLE'))
#
#     return data_header
#
#
# def get_header_price(root, file):
#     path = '%s/%s' % (root, file)
#     with open(path, 'rb') as pk_f:
#         res = pickle.load(pk_f)
#
#     data_header = [
#         ('代码', 'stockCode', 'VARCHAR(6)'),
#         ('日期', 'date', 'VARCHAR(30) PRIMARY KEY'),
#     ]
#
#     for rowText in re.findall(r'\n(.*)', res):
#         tmp = re.findall(r'(.*) :(.*)', rowText)
#
#         if len(tmp) == 0:
#             data_header.append((rowText, None, 'VARCHAR(1)'))
#         else:
#             data_header.append((tmp[0][0], tmp[0][1], 'DOUBLE'))
#
#     return data_header
#
#
# def format_res(res, prefix, infix, postfix, head_list):
#
#     index_dict = dict()
#     for index, item in enumerate(head_list):
#         if item[1] in index_dict.keys():
#             raise InterruptedError('error')
#         if item[1] is not None:
#             index_dict[item[1]] = index
#
#     tmp_dict = dict()
#     for subRes in res:
#         sub_list = json.loads(subRes.decode())['data']
#         for tmp in sub_list:
#             date = tmp['standardDate']
#
#             if date not in tmp_dict.keys():
#                 tmp_dict[date] = [None] * len(head_list)
#
#             for key, value in tmp.items():
#                 if key == prefix:
#                     if infix in value.keys():
#                         sub_dict = value[infix]
#                         for subKey, subValue in sub_dict.items():
#                             tmp_dict[date][index_dict[subKey]] = subValue.get(postfix)
#                 else:
#
#                     tmp_dict[date][index_dict[key]] = value
#
#     tmp_list = list()
#     for key, value in tmp_dict.items():
#         tmp_list.append(value)
#         # print(key)
#         # print(value)
#
#     # header = [value[0] for value in head_list]
#
#     return tmp_list


# def format_res_price(res, head_list):
#     index_dict = dict()
#     for index, item in enumerate(head_list):
#         if item[1] in index_dict.keys():
#             raise InterruptedError('error')
#         if item[1] is not None:
#             index_dict[item[1]] = index
#
#     list0 = json.loads(res.decode())['data']
#
#     tmp_dict = dict()
#     for tmp in list0:
#         date = tmp['date']
#
#         if date not in tmp_dict.keys():
#             tmp_dict[date] = [None] * len(head_list)
#
#         for key, value in tmp.items():
#
#             if key in index_dict.keys():
#                 tmp_dict[date][index_dict[key]] = value
#
#     tmp_list = list()
#     for key, value in tmp_dict.items():
#         tmp_list.append(value)
#
#     return tmp_list


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
            # if key == prefix:
            #     for infix in value.keys():
            #         sub_dict = value[infix]
            #         for subKey, subValue in sub_dict.items():
            #             field = '.'.join([infix, subKey])
            #             data_dict[date][index_dict[field]] = subValue.get(postfix)
            # else:
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


def get_header_df():
    bs_list = read_pkl(root='../basicData/', file='NsBsText.pkl')
    ps_list = read_pkl(root='../basicData/', file='NsPsText.pkl')
    cfs_list = read_pkl(root='../basicData/', file='NsCfsText.pkl')
    m_list = read_pkl(root='../basicData/', file='NsMText.pkl')

    index = ['txt_CN', 'sql_type', 'sheet_name', 'api']

    res_df = pd.DataFrame(index=index)

    res_df['first_update'] = ['首次上传日期', 'VARCHAR(30)', None, None]
    res_df['last_update'] = ['最近上传日期', 'VARCHAR(30)', None, None]
    res_df['stockCode'] = ['代码', 'VARCHAR(6)', None, None]
    res_df['currency'] = ['货币', 'VARCHAR(10)', None, None]
    res_df['standardDate'] = ['标准日期', 'VARCHAR(30) PRIMARY KEY', None, None]
    res_df['reportDate'] = ['报告日期', 'VARCHAR(30)', None, None]
    res_df['reportType'] = ['报告类型', 'VARCHAR(30)', None, None]
    res_df['date'] = ['日期', 'VARCHAR(30)', None, None]

    list1 = ['bs', 'ps', 'cfs', 'm']
    list2 = [bs_list, ps_list, cfs_list, m_list]

    counter = 0
    for infix, txt in zip(list1, list2):
        for rowText in re.findall(r'\n(.*)', txt):
            tmp = re.findall(r'(.*) : (.*)\.(.*)', rowText)
            counter += 1

            if len(tmp) == 0:
                sql_name = 'id_{:0>3}'.format(counter)
                res_df[sql_name] = [rowText, 'VARCHAR(1)', infix, None]
            else:
                sql_name = 'id_{:0>3}_{}_{}'.format(counter, infix, tmp[0][2])
                res_df[sql_name] = [tmp[0][0], 'DOUBLE', infix, tmp[0][2]]

    return res_df


def get_header_df_mvs():
    txt = read_pkl(root='../basicData/', file='priceText.pkl')

    index = ['txt_CN', 'sql_type', 'sheet_name', 'api']
    res_df = pd.DataFrame(index=index)

    res_df['first_update'] = ['首次上传日期', 'VARCHAR(30)', None, None]
    res_df['last_update'] = ['最近上传日期', 'VARCHAR(30)', None, None]
    res_df['stockCode'] = ['代码', 'VARCHAR(6)', None, None]
    res_df['date'] = ['日期', 'VARCHAR(30)', None, None]

    counter = 0
    infix = 'mvs'

    for rowText in re.findall(r'\n(.*)', txt):
        tmp = re.findall(r'(.*) :(.*)', rowText)
        counter += 1

        if len(tmp) == 0:
            sql_name = 'id_{:0>3}'.format(counter)
            res_df[sql_name] = [rowText, 'VARCHAR(1)', infix, None]
        else:
            sql_name = 'id_{:0>3}_{}_{}'.format(counter, infix, tmp[0][1])
            res_df[sql_name] = [tmp[0][0], 'DOUBLE', infix, tmp[0][1]]

    return res_df


def transpose_df(df):
    res = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
    return res


def write_header2txt():
    hd = get_header_df()
    tmp = transpose_df(hd)
    str1 = ''
    for tup in tmp.itertuples():
        sub_list = list(tup)
        sub_list.pop(1)
        sub_str = '%s_%s: %s' % (tup[3], tup[1], repr(sub_list))
        str1 = '\n'.join([str1, sub_str])
    print(str1)

    with open("../comparisonTable/fs_table.txt", "w", encoding="utf-8") as f:
        f.write(str1)


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
    }
    return res


if __name__ == '__main__':
    pass

