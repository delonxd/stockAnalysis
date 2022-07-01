from method.fileMethod import *
from method.dataMethod import load_df_from_mysql
from method.mainMethod import sift_codes
import json
import datetime as dt
import numpy as np
import pickle
import os
import re


def load_daily_res(dir_str):

    dir_str = 'update_20220117153503'

    datetime = dir_str[-14:]
    res_dir = '..\\basicData\\dailyUpdate\\update_%s' % datetime

    file = '%s\\res_daily_%s.pkl' % (res_dir, datetime)
    with open(file, "rb") as f:
        res = pickle.load(f)

    val_list = list()
    for tup in res:
        code = tup[0]
        df = tup[1]

        # s1 = df.loc[:, 's_016_roe_parent'].dropna()
        # s1 = df.loc[:, 's_027_pe_return_rate'].dropna()
        # s1 = df.loc[:, 's_037_real_pe_return_rate'].dropna()
        s1 = df.loc[:, 's_028_market_value'].dropna()
        # val = s1[-1] if s1.size > 0 else -np.inf

        if s1.size > 1:
            if s1[-1] < 0:
                val = np.inf
            else:
                size = min(s1.size, 5)
                val = s1[-1] / s1[-size] - 1
        else:
            val = np.inf

        val_list.append((code, val))

    res_list = sorted(val_list, key=lambda x: x[1], reverse=False)

    code_sorted = zip(*res_list).__next__()
    print(code_sorted)

    res = json.dumps(code_sorted, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_3.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


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


def generate_list():
    with open("..\\basicData\\analyzedData\\sift_002_real_pe.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    # with open("..\\basicData\\self_selected\\gui_selected.txt", "r", encoding="utf-8", errors="ignore") as f:
    with open("..\\basicData\\self_selected\\gui_whitelist.txt", "r", encoding="utf-8", errors="ignore") as f:
        select_list = json.loads(f.read())

    new_list = []
    for code in code_list:
        if code in select_list:
            new_list.append(code)

    res = json.dumps(new_list, indent=4, ensure_ascii=False)
    # file = '..\\basicData\\self_selected\\gui_selected2.txt'
    file = '..\\basicData\\self_selected\\gui_whitelist2.txt'
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


def random_code_list(code_list, pick_weight, sorted_list=None, interval=100, mode='normal'):

    if sorted_list is None:
        sorted_list = code_list

    path = "../basicData/self_selected/gui_selected.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        gui_selected = json.loads(f.read())

    path = "../basicData/self_selected/gui_whitelist.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        gui_whitelist = json.loads(f.read())

    set_all = set(code_list)
    tmp_selected = set(gui_selected)
    tmp_whitelist = set(gui_whitelist)

    set_selected = set_all & tmp_selected
    set_whitelist = set_all & tmp_whitelist - set_selected
    set_normal = set_all - set_selected - set_whitelist

    weight_dict = get_weight_dict(set_all)

    src_list = [set()]
    if mode == 'normal':
        src_list = [set_normal, set_selected, set_whitelist]
    elif mode == 'selected+whitelist':
        src_list = [set_selected | set_whitelist]

    total_list = list(map(lambda x: generate_random_list(x, weight_dict), src_list))

    ret_list = []
    while True:
        picked_list = []
        src_number = list(map(lambda x: len(x), total_list))
        if sum(np.array(src_number) * np.array(pick_weight)) == 0:
            break

        picked = pick_number(src_number, pick_weight, interval)
        print(picked)
        for index, value in enumerate(picked):
            for _ in range(value):
                code = total_list[index].pop(0)
                picked_list.append(code)

        sub_list = sift_codes(source=picked_list, sort=sorted_list)
        ret_list.extend(sub_list)

    path = "../basicData/dailyUpdate/latest/s005_code_random.txt"
    tmp = json.dumps(ret_list, indent=4, ensure_ascii=False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(tmp)

    return ret_list


def get_weight_dict(set_all):
    path = "../basicData/dailyUpdate/latest/a003_report_date_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        report_date_dict = json.loads(f.read())

    base_rate = 100000
    weight_dict = dict.fromkeys(set_all, base_rate * 3000)

    date1 = dt.date.today()
    with open("..\\basicData\\self_selected\\gui_counter.txt", "r", encoding="utf-8", errors="ignore") as f:
        gui_counter = json.loads(f.read())

    for key, value in gui_counter.items():
        if key not in set_all:
            continue

        report_date = report_date_dict.get(key)
        if report_date is None or report_date == 'Invalid da':
            report_date = ''
        tmp_rate = base_rate if report_date > value[1] else 1

        date2 = dt.datetime.strptime(value[1], '%Y-%m-%d').date()
        margin = (date1 - date2).days

        if margin == 1 and tmp_rate == base_rate:
            print(key, report_date, value[1], 'margin == 1')

        if margin >= 40:
            print(key, date2, 'margin >= 40')
        weight = margin ** 2 * tmp_rate
        weight_dict[key] = weight

    weight_counter = dict()
    for weight in weight_dict.values():
        if weight in weight_counter:
            weight_counter[weight] += 1
        else:
            weight_counter[weight] = 1

    print('All:', len(set_all))
    weight_list = list(weight_counter.keys())
    weight_list.sort()
    for weight in weight_list:
        if weight % base_rate == 0:
            margin = (weight / base_rate) ** 0.5
        else:
            margin = weight ** 0.5

        date2 = date1 - dt.timedelta(days=margin)
        date_str = dt.date.strftime(date2, '%Y-%m-%d')

        weight_str = '%s%18s%8s' % (date_str, weight, weight_counter[weight])
        print(weight_str)

    return weight_dict


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


def generate_random_list(src, weight_dict: dict):
    length = len(src)
    set_all = set(src)

    ret = []
    for _ in range(length):
        code = random_by_weight(set_all, weight_dict)
        set_all -= {code}
        ret.append(code)
    return ret


def random_by_weight(src, weight_dict: dict):
    import random

    total = 0
    for code in src:
        total += weight_dict.get(code)
    ra = random.uniform(0, total)

    current = 0
    for code in src:
        current += weight_dict.get(code)
        if ra <= current:
            return code


def get_random_list():
    import json
    from method.mainMethod import sift_codes

    path = "../basicData/dailyUpdate/latest/a001_code_list.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    # code_list = sift_codes(
    #     source=code_list,
    #     sort=code_list,
    #     market='main',
    # )

    ret = random_code_list(code_list, pick_weight=[75, 10, 15])
    return ret


def sort_discount():
    import json
    path = "../basicData/self_selected/gui_assessment.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        assessment_dict = json.loads(f.read())

    # path = "../basicData/dailyUpdate/latest/a004_real_cost_dict.txt"
    path = "../basicData/dailyUpdate/latest/a005_equity_dict.txt"
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

    ret = []
    for val in hold_dict:
        code = val[0]
        df = load_df_from_mysql(code, 'mvs')
        number = val[2]
        price = df['id_035_mvs_sp'].iloc[-1]

        value = int(round(100 * price * number))

        tmp = [code, val[1], number, value, price]
        print(tmp)
        ret.append(tmp)
    ret.sort(key=lambda x: x[3], reverse=True)

    list0 = []
    for row in ret:
        tmp_txt = json.dumps(row, ensure_ascii=False)
        list0.append(tmp_txt)
    res = '[\n\t' + ',\n\t'.join(list0) + '\n]'

    with open(path, "w", encoding='utf-8') as f:
        f.write(res)


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

    sort_hold()
