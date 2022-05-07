import os
import pickle
import shutil
from method.logMethod import MainLog


def load_daily_res(dir_str):
    import pickle
    import numpy as np
    import json

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


def sort_daily_code(dir_str):
    import pickle
    import numpy as np
    import json
    import os

    datetime = dir_str[-14:]
    res_dir = '..\\basicData\\dailyUpdate\\update_%s' % datetime

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


def new_enter_code(dir_str):
    import pickle
    import numpy as np
    import json
    import os

    datetime = dir_str[-14:]
    res_dir = '..\\basicData\\dailyUpdate\\update_%s' % datetime

    sub_dir = '%s\\res_daily\\' % res_dir
    list0 = [x for x in os.listdir(sub_dir) if os.path.isfile(sub_dir + x)]

    res = list()
    for file in list0:
        path = '%s\\%s' % (sub_dir, file)
        print(path)
        with open(path, "rb") as f:
            res.extend(pickle.load(f))

    base_line = 1 / 22
    offset = 30

    val_list1 = list()
    val_list2 = list()
    val_list3 = list()
    for tmp in res:
        code = tmp[0]
        df = tmp[1]

        s1 = df.loc[:, 's_037_real_pe_return_rate'].dropna()

        # print(s1)

        val1 = s1[-1] if s1.size > 0 else -np.inf
        val2 = s1[-1-offset] if s1.size > offset else -np.inf

        if val1 >= base_line:
            val_list1.append((code, val1))
            val3 = (val1 - val2) / val1
            val_list3.append((code, val3))

        if val2 >= base_line:
            val_list2.append((code, val2))

    res1 = sorted(val_list1, key=lambda x: x[1], reverse=True)
    res2 = sorted(val_list2, key=lambda x: x[1], reverse=True)

    sorted1 = zip(*res1).__next__()
    sorted2 = zip(*res2).__next__()

    sorted3 = list()
    for code in sorted1:
        if code not in sorted2:
            sorted3.append(code)

    # res = json.dumps(sorted3, indent=4, ensure_ascii=False)
    # file = '%s\\new_enter_code.txt' % res_dir
    # with open(file, "w", encoding='utf-8') as f:
    #     f.write(res)

    res4 = sorted(val_list3, key=lambda x: x[1], reverse=True)
    sorted4 = zip(*res4).__next__()

    res = json.dumps(sorted4, indent=4, ensure_ascii=False)
    file = '%s\\increase_code.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


def generate_list():
    import json

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
    import re
    import json

    with open("..\\basicData\\self_selected\\hs300_src.txt", "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
        code_list = re.findall(r'([0-9]{6})', txt)
    code_list.reverse()

    res = json.dumps(code_list, indent=4, ensure_ascii=False)
    file = '..\\basicData\\self_selected\\hs300.txt'
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


def save_latest_list(dir_str):
    src_dir = '..\\basicData\\dailyUpdate\\%s' % dir_str
    target_dir = '..\\basicData\\dailyUpdate\\latest'

    files = [
        'a001_code_list.txt',
        'a002_name_dict.txt',
        'a003_report_date_dict.txt',
        'a004_real_cost_dict.txt',
        's001_code_sorted_pe.txt',
        's002_code_sorted_real_pe.txt',
        's003_code_sorted_roe_parent.txt',
        's004_code_latest_update.txt',
        'z001_daily_table.pkl',
    ]

    for file in files:
        path1 = '%s\\%s' % (src_dir, file[5:])
        path2 = '%s\\%s' % (target_dir, file)
        copy_file(path1, path2)

    dir1 = '..\\basicData\\dailyUpdate\\%s\\res_daily' % dir_str
    dir2 = '..\\basicData\\dailyUpdate\\latest\\res_daily'
    clear_dir(dir2)
    copy_dir(dir1, dir2)


def clear_dir(dir_path):
    for file in os.listdir(dir_path):
        path = '%s\\%s' % (dir_path, file)
        MainLog.add_log('Delete %s' % path)
        os.remove(path)


def copy_dir(dir1, dir2):
    for file in os.listdir(dir1):
        path1 = '%s\\%s' % (dir1, file)
        path2 = '%s\\%s' % (dir2, file)
        # command = 'copy %s %s' % (path1, path2)
        # shutil.copytree(path1, path2)
        if os.path.isfile(path1):
            shutil.copy(path1, path2)
            MainLog.add_log('Copy %s --> %s' % (path1, path2))


def copy_file(path1, path2):
    import json

    type1 = path1[-3:]
    type2 = path2[-3:]

    if type1 == type2 == 'txt':
        with open(path1, "r", encoding='utf-8') as f:
            data = json.loads(f.read())

        res = json.dumps(data, indent=4, ensure_ascii=False)
        with open(path2, "w", encoding='utf-8') as f:
            f.write(res)

        MainLog.add_log('Copy %s --> %s' % (path1, path2))

    elif type1 == type2 == 'pkl':
        with open(path1, "rb") as f:
            data = pickle.load(f)

        with open(path2, "wb") as f:
            pickle.dump(data, f)
        MainLog.add_log('Copy %s --> %s' % (path1, path2))

    else:
        MainLog.add_log("CopyError: invalid type for copy_file(): '%s' --> '%s'" % (path1, path2))


def random_code_list(code_list, pick_weight):
    import json
    import datetime as dt
    import numpy as np
    from method.mainMethod import sift_codes

    path = "../basicData/dailyUpdate/latest/s002_code_sorted_real_pe.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        sorted_list = json.loads(f.read())

    path = "../basicData/self_selected/gui_selected.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        gui_selected = json.loads(f.read())

    path = "../basicData/self_selected/gui_whitelist.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        gui_whitelist = json.loads(f.read())

    path = "../basicData/dailyUpdate/latest/a003_report_date_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        report_date_dict = json.loads(f.read())

    set_all = set(code_list)
    tmp_selected = set(gui_selected)
    tmp_whitelist = set(gui_whitelist)

    set_selected = set_all & tmp_selected
    set_whitelist = set_all & tmp_whitelist - set_selected
    set_normal = set_all - set_selected - set_whitelist

    base_rate = 100000
    weight_dict = dict.fromkeys(set_all, base_rate * 3000)

    date1 = dt.date.today()
    with open("..\\basicData\\self_selected\\gui_counter.txt", "r", encoding="utf-8", errors="ignore") as f:
        gui_counter = json.loads(f.read())

    for key, value in gui_counter.items():

        report_date = report_date_dict.get(key)
        if report_date is None or report_date == 'Invalid da':
            report_date = ''
        tmp_rate = base_rate if report_date > value[1] else 1

        date2 = dt.datetime.strptime(value[1], '%Y-%m-%d').date()
        margin = (date1 - date2).days

        if margin == 1 and tmp_rate == base_rate:
            print(key, report_date, value[1])

        if margin >= 40:
            print(key, date2)
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

    list1 = generate_random_list(set_normal, weight_dict)
    list2 = generate_random_list(set_selected, weight_dict)
    list3 = generate_random_list(set_whitelist, weight_dict)
    total_list = [list1, list2, list3]
    # pick_weight = [75, 10, 15]

    ret_list = []
    while True:
        picked_list = []
        src_number = [len(list1), len(list2), len(list3)]
        if sum(np.array(src_number) * np.array(pick_weight)) == 0:
            break

        picked = pick_number(src_number, pick_weight, 100)
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

    path = "../basicData/dailyUpdate/latest/a004_real_cost_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        real_cost_dict = json.loads(f.read())

    tmp = []
    for key, value in assessment_dict.items():
        real_cost = real_cost_dict.get(key)

        assessment = int(value)
        if real_cost is not None:
            discount = real_cost / assessment
            tmp.append([key, discount])

    tmp.sort(key=lambda x: x[1])

    ret = list(list(zip(*tmp))[0])
    return ret


if __name__ == '__main__':
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    date_dir = 'update_20220506153503'

    # save_latest_list(date_dir)
    # load_daily_res(date_dir)
    # sort_daily_code(date_dir)
    # new_enter_code(date_dir)
    # generate_list()
    # get_codes_from_sel()
    # get_random_list()

    save_latest_list(date_dir)