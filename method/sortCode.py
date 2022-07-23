from method.fileMethod import *
from method.dataMethod import load_df_from_mysql
import json
import datetime as dt
import numpy as np
import pickle
import os
import re
import pandas as pd


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


def random_code_list(code_list, pick_weight, interval, mode):
    if pick_weight is None:
        pick_weight = [1]

    sorted_list = code_list

    set_all = set(code_list)
    tmp_selected = set(str_recognition('selected'))
    tmp_whitelist = set(str_recognition('whitelist'))

    set_selected = set_all & tmp_selected
    set_whitelist = set_all & tmp_whitelist - set_selected
    set_normal = set_all - set_selected - set_whitelist

    src_list = [set()]
    if mode == 'normal':
        src_list = [set_normal, set_selected, set_whitelist]
    elif mode == 'whitelist+selected':
        src_list = [set_selected | set_whitelist]
    elif mode == 'whitelist-selected':
        src_list = [set_whitelist - set_selected]
    elif mode == 'selected':
        src_list = [set_selected]
    elif mode == 'all-whitelist':
        src_list = [set_normal]

    set_total = set()
    for tmp in src_list:
        set_total = set_total | set(tmp)

    weight_dict = get_weight_dict(set_total)

    total_list = list(map(lambda x: generate_random_list(x, weight_dict), src_list))

    ret = []
    while True:
        picked_list = []
        src_number = list(map(lambda x: len(x), total_list))
        if sum(np.array(src_number) * np.array(pick_weight)) == 0:
            break

        picked = pick_number(src_number, pick_weight, interval)

        MainLog.add_log('pick --> %s' % picked)

        for index, value in enumerate(picked):
            for _ in range(value):
                code = total_list[index].pop(0)
                picked_list.append(code)

        sub_list = sift_codes(source=picked_list, sort=sorted_list)
        ret.extend(sub_list)

    write_json_txt("..\\basicData\\tmp\\code_list_random.txt", ret)
    MainLog.add_split('#')

    return ret


def get_weight_dict(set_all):
    path = "..\\basicData\\dailyUpdate\\latest\\a003_report_date_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        report_date_dict = json.loads(f.read())

    base_rate = 10000000
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

        flag = True if report_date > value[1] else False

        date2 = dt.datetime.strptime(value[1], '%Y-%m-%d').date()
        margin = (date1 - date2).days

        if flag is True:
            weight = margin ** 2 * base_rate
            print(key, report_date, value[1], 'margin == 1')
        elif margin > 60:
            weight = margin ** 2 * 100
            print(key, date2, 'margin > 60')
        else:
            weight = margin ** 2

        weight_dict[key] = weight

    weight_counter = dict()
    for weight in weight_dict.values():
        if weight in weight_counter:
            weight_counter[weight] += 1
        else:
            weight_counter[weight] = 1

    MainLog.add_log('All --> %s' % len(set_all))

    weight_list = list(weight_counter.keys())
    weight_list.sort()
    for weight in weight_list:
        if weight % base_rate == 0:
            margin = (weight / base_rate) ** 0.5
        else:
            margin = weight ** 0.5

            if margin > 60:
                margin = margin / 10

        date2 = date1 - dt.timedelta(days=margin)
        date_str = dt.date.strftime(date2, '%Y-%m-%d')

        weight_str = '%s%18s%8s' % (date_str, weight, weight_counter[weight])
        MainLog.add_log(weight_str)

    MainLog.add_split('-')

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


def sift_codes(
        source=None,
        whitelist=None,
        blacklist=None,
        sort=None,
        reverse=False,

        market='all',
        ids_names=None,
        timestamp=None,
        insert=None,

        random=False,
        pick_weight=None,
        interval=100,
        mode='normal',
):
    if ids_names is not None:
        source = industry_name2code(ids_names)

    source = str_recognition(source)
    whitelist = str_recognition(whitelist)
    blacklist = str_recognition(blacklist)

    if sort is None:
        sort = source
    sort = str_recognition(sort)

    set_all = list_to_set(source)
    set_white = list_to_set(whitelist)
    set_black = list_to_set(blacklist)

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

    ret = []
    if reverse is True:
        sort.reverse()
    for code in sort:
        if code in set_sift:
            ret.append(code)

    if insert is not None:
        extend = list(set_sift - set(sort))
        if insert == -1:
            ret = ret + extend
        elif insert == 0:
            ret = extend + ret

    if random is False:
        return ret
    else:
        ret = random_code_list(
            ret,
            pick_weight=pick_weight,
            interval=interval,
            mode=mode,
        )
        return ret


def industry_name2code(ids_names):
    name_dict = load_json_txt('..\\basicData\\industry\\sw_2021_name_dict.txt')

    ids_codes = []

    for ids_code, name in name_dict.items():
        if ids_code[-4:] == '0000':
            ids_name = '1-' + name
        elif ids_code[-2:] == '00':
            ids_name = '2-' + name
        else:
            ids_name = '3-' + name

        if ids_name in ids_names:
            ids_codes.append(ids_code)

    sw_2021_dict = load_json_txt('..\\basicData\\industry\\sw_2021_dict.txt')

    ret = []
    for code, ids_code1 in sw_2021_dict.items():
        if ids_code1 is None:
            continue

        for ids_code2 in ids_codes:
            if ids_code2[-4:] == '0000':
                index = 2
            elif ids_code2[-2:] == '00':
                index = 4
            else:
                index = 6

            if ids_code1[:index] == ids_code2[:index]:
                ret.append(code)
    return ret


def list_to_set(src):
    ret = set()
    if src is None:
        return ret
    else:
        for code in src:
            # if code[0] == 'C':
            #     length = len(code)
            #     for key, value in ind_dict.items():
            #         if code == key[:length]:
            #             ret.update(set(value))
            # else:
            ret.add(code)
        return ret


def str_recognition(src):
    if isinstance(src, str):
        if src == 'all':
            ret = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")

        elif src == 'pe':
            ret = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s001_code_sorted_pe.txt")

        elif src == 'real_pe':
            ret = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s002_code_sorted_real_pe.txt")

        elif src == 'roe_parent':
            ret = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s003_code_sorted_roe_parent.txt")

        elif src == 'latest_update':
            ret = load_json_txt("..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt")

        elif src == 'hold':
            tmp = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt")
            ret = list(zip(*tmp).__next__())

        elif src == 'whitelist':
            ret = load_json_txt("..\\basicData\\self_selected\\gui_whitelist.txt")

        elif src == 'blacklist':
            ret = load_json_txt("..\\basicData\\self_selected\\gui_blacklist.txt")

        elif src == 'selected':
            ret = load_json_txt("..\\basicData\\self_selected\\gui_selected.txt")

        elif src == 'old':
            ret = load_json_txt("..\\basicData\\tmp\\code_list_latest.txt")

        elif src == 'sort-ass':
            dict0 = load_json_txt("..\\basicData\\self_selected\\gui_assessment.txt")
            df = pd.DataFrame.from_dict(dict0, orient='index', dtype='int64')
            df = df.sort_values(0, ascending=False)
            ret = df.index.to_list()

        elif src == 'sort-equity':
            path = "..\\basicData\\dailyUpdate\\latest\\a005_equity_dict.txt"
            dict0 = load_json_txt(path)
            df = pd.DataFrame.from_dict(dict0, orient='index')
            df = df.sort_values(0, ascending=False)
            ret = df.index.to_list()

        elif src[:4] == 'mark':
            mark = int(src.split('-')[1])
            ret = []
            mark_dict = load_json_txt("..\\basicData\\self_selected\\gui_mark.txt")
            for code, value in mark_dict.items():
                if value == mark:
                    ret.append(code)

        elif src == 'sort-ass/equity':
            ret = sort_discount()

        elif src == 'sort-ass/real_cost':
            path = "..\\basicData\\dailyUpdate\\latest\\a004_real_cost_dict.txt"
            ret = sort_discount(path)

        elif src == 'sort-ass/turnover':
            path = "..\\basicData\\dailyUpdate\\latest\\a006_turnover_dict.txt"
            ret = sort_discount(path)

        elif src == 'plate-50':
            path = "..\\basicData\\self_selected\\板块50.txt"
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
                ret = re.findall(r'([0-9]{6})', txt)
                ret.reverse()
        else:
            raise KeyboardInterrupt('error str_recognition')
        return ret
    else:
        return src


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
