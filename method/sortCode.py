from method.fileMethod import *
from method.dataMethod import load_df_from_mysql
from method.recognitionMethod import RecognitionStr
import json
import datetime as dt
import numpy as np
import pickle
import os
import re
import time

# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *


def sort_daily_code(dir_name):

    res_dir = '..\\basicData\\dailyUpdate\\%s' % dir_name
    sub_dir = '%s\\res_daily\\' % res_dir
    list0 = [x for x in os.listdir(sub_dir) if os.path.isfile(sub_dir + x)]

    res = list()
    for file in list0:
        path = '%s\\%s' % (sub_dir, file)
        print(path)
        with open(path, "rb") as f:
            res.extend(pickle.load(f))

    val_list = list()
    for tmp in res:
        code = tmp[0]
        df = tmp[1]

        s1 = df.loc[:, 's_037_real_pe_return_rate'].dropna()
        val1 = s1[-1] if s1.size > 0 else -np.inf

        s2 = df.loc[:, 's_016_roe_parent'].dropna()
        val2 = s2[-1] if s2.size > 0 else -np.inf

        s1 = df.loc[:, 's_027_pe_return_rate'].dropna()
        val3 = s1[-1] if s1.size > 0 else -np.inf

        val_list.append((code, val1, val2, val3))

    res1 = sorted(val_list, key=lambda x: x[1], reverse=True)
    res2 = sorted(val_list, key=lambda x: x[2], reverse=True)
    res3 = sorted(val_list, key=lambda x: x[3], reverse=True)

    sorted1 = zip(*res1).__next__()
    sorted2 = zip(*res2).__next__()
    sorted3 = zip(*res3).__next__()

    res = json.dumps(sorted1, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_real_pe.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(sorted2, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_roe_parent.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(sorted3, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_pe.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


def get_codes_from_sel():
    with open("..\\basicData\\self_selected\\hs300_src.txt", "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
        code_list = re.findall(r'([0-9]{6})', txt)
    code_list.reverse()

    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    file = '..\\basicData\\self_selected\\hs300.txt'
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


def pick_number(src, weight, total):
    if sum(src) == 0:
        return [0] * len(src)

    if sum(weight) == 0:
        return [0] * len(src)

    ret = allot_weight(weight, total)
    left = src.copy()
    left_weight = weight.copy()
    for index, value in enumerate(src):
        if src[index] >= ret[index]:
            left[index] = src[index] - ret[index]
        else:
            ret[index] = src[index]
            left[index] = 0
            left_weight[index] = 0

    margin = total - sum(ret)
    if margin > 0:
        left_ret = pick_number(left, left_weight, margin)

        for index, value in enumerate(left_ret):
            ret[index] += value

    return ret


def allot_weight(weight, total):
    import random
    ret = list(map(lambda x: int(x * total / sum(weight)), weight))

    tmp = []

    for index, value in enumerate(weight):
        if value > 0:
            tmp.append(index)
        elif value < 0:
            raise KeyboardInterrupt('权重错误：权重小于0')

    for _ in range(total - sum(ret)):
        index = random.randint(0, len(tmp)-1)
        ret[tmp[index]] += 1
    return ret


def sort_discount(path="../basicData/dailyUpdate/latest/a005_equity_dict.txt"):
    import json
    path_ass = "../basicData/self_selected/gui_assessment.txt"
    with open(path_ass, "r", encoding="utf-8", errors="ignore") as f:
        assessment_dict = json.loads(f.read())

    # path = "../basicData/dailyUpdate/latest/a004_real_cost_dict.txt"
    # path = "../basicData/dailyUpdate/latest/a005_equity_dict.txt"
    # path = "../basicData/dailyUpdate/latest/a006_turnover_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res_dict = json.loads(f.read())

    tmp = []
    for key, value in assessment_dict.items():
        data = res_dict.get(key)

        assessment = int(value)
        if data is not None:
            discount = data / assessment
            tmp.append([key, discount])
        # elif key in set0:
        #     tmp.append([key, 0])

    tmp.sort(key=lambda x: x[1])

    ret = list(list(zip(*tmp))[0])
    return ret


def sort_hold():
    path = '..\\basicData\\self_selected\\gui_hold.txt'
    hold_dict = load_json_txt(path)

    name_dict = load_json_txt('..\\basicData\\code_names_dict.txt')
    ass_dict = load_json_txt('..\\basicData\\self_selected\\gui_assessment.txt')

    ret = []
    for val in hold_dict:
        code = val[0]
        number = val[2]
        if number == 0:
            price = 0
            mkt = np.inf
            ass = 0
        else:
            df = load_df_from_mysql(code, 'mvs')
            price = df['id_035_mvs_sp'].iloc[-1]

            mkt = df['id_041_mvs_mc'].iloc[-1]
            ass = int(ass_dict[code])

        value = int(round(price * number))
        i_value = int(round(price * number / mkt * ass * 1e8))
        name = name_dict[code]

        tmp = [code, name, number, value, i_value, price, mkt, ass]
        MainLog.add_log(repr(tmp))
        ret.append(tmp)
    ret.sort(key=lambda x: x[3], reverse=True)

    list0 = []
    for row in ret:
        tmp_txt = json.dumps(row, ensure_ascii=False)
        list0.append(tmp_txt)
    res = '[\n\t' + ',\n\t'.join(list0) + '\n]'

    with open(path, "w", encoding='utf-8') as f:
        f.write(res)


def refresh_gui_counter():
    path = '..\\basicData\\self_selected\\gui_counter.txt'
    counter_dict = load_json_txt(path)

    path = '..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt'
    all_code = load_json_txt(path)

    new_code = []
    for code in all_code:
        if code not in counter_dict:
            new_code.append(code)

    print(new_code)
    # res = json.dumps(res_dict, indent=4, ensure_ascii=False)
    # path = "../basicData/self_selected/gui_counter.txt"
    # with open(path, "w", encoding='utf-8') as f:
    #     f.write(res)


def sift_codes(
        source='',
        sort=None,
        ascending=None,
        sort_ids=False,
        random=False,
        interval=100,
        df_all=None,
):
    # print(df_all)
    str0 = RecognitionStr(source, df_all)

    str0.get_code_list()

    ret = str0.get_sort_list(sort, ascending, sort_ids)

    if random is None or random is True:
        ret = str0.random(interval)

    # para = [source, sort, ascending, sort_ids, random, interval, ret]
    # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    # path = "..\\basicData\\self_selected\\backup_sift.txt"
    # backup_sift_code(para, timestamp, path)

    return ret


def backup_codes(codes, path, label=''):
    source = load_json_txt(path)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    source[timestamp] = [label, codes]
    write_json_txt(path, source)


def sort_industry(by='ass/equity'):
    ids_name = load_json_txt("..\\basicData\\industry\\sw_2021_name_dict.txt")
    ids_dict = load_json_txt("..\\basicData\\industry\\sw_2021_dict.txt")

    ids_list = []
    for ids in ids_name.keys():
        if ids[-2:] != '00':
            ids_list.append(ids)

    if by == 'ass/equity':
        code_list = sift_codes(source='whitelist', sort='sort-ass/equity')
    else:
        code_list = []

    counter = 1
    counter_dict = dict()
    for code in code_list:
        ids = ids_dict.get(code)
        if ids is None:
            continue
        if ids not in counter_dict:
            counter_dict[ids] = counter
            counter += 1

    counter = 100001
    for ids in ids_list:
        if ids not in counter_dict:
            counter_dict[ids] = counter
            counter += 1

    # ids_list.sort(key=lambda x: counter_dict.get(x))

    write_json_txt("..\\basicData\\industry\\industry_sorted.txt", counter_dict)
    # print(ids_list)
    # return ids_list


if __name__ == '__main__':
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # date_dir = 'update_20220601153504'
    # load_daily_res(date_dir)
    # sort_daily_code(date_dir)
    # new_enter_code(date_dir)
    # generate_list()
    # get_codes_from_sel()
    # get_random_list()
    # save_latest_list(date_dir)

    # sift_codes(source='kk{(m2{zz{白名单}-xx{hold}}-m3{自选})-()|()}')
    # sift_codes(source='backup:20230816:{hold}')

    sort_hold()
    # refresh_gui_counter()
    # sort_industry()
