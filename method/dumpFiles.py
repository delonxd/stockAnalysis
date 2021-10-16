# from method.mainMethod import read_pkl

import pickle
import json
import re
import pandas as pd


def get_api_names(paths, regular):
    api_list = list()
    for path in paths:
        with open(path, "r", encoding='utf-8') as f:
            text = f.read()

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


def dump_fs_metrics_list():

    tables = ['bs', 'ps', 'cfs', 'm']

    dir0 = '..\\basicData\\src_text\\'
    paths = [''.join([dir0, value, '_table.txt']) for value in tables]

    subs = get_api_names(
        paths=paths,
        regular=r'\n.* : (.*)',
    )

    api_all = config_api_names(
        infix_list=subs,
        prefix='q',
        postfix='t',
    )

    metrics_list = split_list(
        source=api_all,
        length=100,
    )

    res = json.dumps(metrics_list, indent=4, ensure_ascii=False)
    with open("../basicData/metrics/metrics_fs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_mvs_metrics():
    tables = ['mvs']

    dir0 = '..\\basicData\\src_text\\'
    paths = [''.join([dir0, value, '_table.txt']) for value in tables]

    metrics = get_api_names(
        paths=paths,
        regular=r'\n.* :(.*)',
    )

    print(metrics)

    res = json.dumps(metrics, indent=4, ensure_ascii=False)
    with open("../basicData/metrics/metrics_mvs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_header_df_fs():
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

    json_str = res_df.to_json(orient="columns", force_ascii=False)

    res = json.dumps(json.loads(json_str), indent=4, ensure_ascii=False)

    with open("../basicData/header_df/header_df_fs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_header_df_mvs():
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

    json_str = res_df.to_json(orient="columns", force_ascii=False)

    res = json.dumps(json.loads(json_str), indent=4, ensure_ascii=False)

    with open("../basicData/header_df/header_df_mvs.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_code_names_dict():
    with open("../basicData/res_basicData.txt", "r", encoding='utf-8') as f:
        data_list = json.loads(f.read())['data']

    dict0 = dict()
    for data in data_list:
        dict0[data['stockCode']] = data['name']

    res = json.dumps(dict0, indent=4, ensure_ascii=False)

    with open("../basicData/code_names_dict.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_code_list():
    with open("../basicData/res_basicData.txt", "r", encoding='utf-8') as f:
        data_list = json.loads(f.read())['data']

    list0 = list()
    for data in data_list:
        list0.append(data['stockCode'])

    res = json.dumps(list0, indent=4, ensure_ascii=False)

    with open("../basicData/code_list.txt", "w", encoding='utf-8') as f:
        f.write(res)


def dump_industry3_list():
    with open("../basicData/industry/res_industryData.txt", "r", encoding='utf-8') as f:
        data_list = json.loads(f.read())['data']

    list0 = list()
    dict0 = dict()
    for data in data_list:
        if data['level'] == 'three':
            list0.append(data['stockCode'])
        dict0[data['stockCode']] = data['name']

    res = json.dumps(list0, indent=4, ensure_ascii=False)
    with open("../basicData/industry/industry3_list.txt", "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(dict0, indent=4, ensure_ascii=False)
    with open("../basicData/industry/industry_dict.txt", "w", encoding='utf-8') as f:
        f.write(res)


if __name__ == '__main__':
    # dump_fs_metrics_list()
    # dump_mvs_metrics()
    # dump_nf_codes()
    # dump_list_code_names()
    # dump_header_df_fs()
    # dump_header_df_mvs()
    # dump_code_names_dict()
    # dump_code_list()
    dump_industry3_list()
    pass