import pickle
import json
import os
import shutil
import datetime as dt
import pandas as pd
from method.logMethod import MainLog


def dump_pkl(path, data):
    with open(path, "wb") as f:
        pickle.dump(data, f)
    MainLog.add_log('dump pkl --> %s' % path)


def load_pkl(path):
    with open(path, "rb") as f:
        ret = pickle.load(f)
    MainLog.add_log('load pkl --> %s' % path)
    return ret


def write_json_txt(path, data, log=True):
    res = json.dumps(data, indent=4, ensure_ascii=False)
    with open(path, "w", encoding='utf-8') as f:
        f.write(res)
    if log:
        MainLog.add_log('write json txt --> %s' % path)


def load_json_txt(path, log=True):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        ret = json.loads(f.read())
    if log:
        MainLog.add_log('loads json txt --> %s' % path)
    return ret


def clear_dir(dir_path):
    for file in os.listdir(dir_path):
        path = '%s\\%s' % (dir_path, file)
        MainLog.add_log('Delete --> %s' % path)
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


def file_add_codes(add_list, path, log=False):
    code_list = load_json_txt(path, log=log)
    for code in add_list:
        if code in code_list:
            continue
        else:
            code_list.append(code)
    write_json_txt(path, code_list, log=log)

    if log:
        MainLog.add_log('add codes -path  --> %s' % path)
        MainLog.add_log('add codes -codes --> %s' % add_list)


def file_del_codes(del_list, path, log=False):
    code_list = load_json_txt(path, log=log)
    for code in del_list:
        if code in code_list:
            index = code_list.index(code)
            code_list.pop(index)
        else:
            continue
    write_json_txt(path, code_list, log=log)

    if log:
        MainLog.add_log('add codes -path  --> %s' % path)
        MainLog.add_log('add codes -codes --> %s' % del_list)


def code_list_from_tags(tag):
    tmp = load_json_txt("..\\basicData\\self_selected\\gui_tags.txt")
    ret = []
    for code, txt in tmp.items():
        list0 = txt.split('#')
        if tag in list0:
            ret.append(code)
    return ret


def tags_operate(codes, tag, func):
    path = "..\\basicData\\self_selected\\gui_tags.txt"
    tags_dict = load_json_txt(path, log=False)

    if func == 'refresh':
        for code, txt in tags_dict.items():
            tags_list = txt.split('#')
            if tag in tags_list:
                tags_list.pop(tags_list.index(tag))
            txt = '#'.join(tags_list)
            tags_dict[code] = txt
        for code, txt in tags_dict.copy().items():
            if txt == '':
                tags_dict.pop(code)

    for code in codes:
        txt = tags_dict.get(code)
        txt = '' if txt is None else txt
        tags_list = txt.split('#')

        if func == 'add' or func == 'refresh':
            if tag not in tags_list:
                tags_list.append(tag)
        elif func == 'del':
            if tag in tags_list:
                tags_list.pop(tags_list.index(tag))
        txt = '#'.join(tags_list)
        tags_dict[code] = txt

        if txt == '':
            tags_dict.pop(code)

    write_json_txt(path, tags_dict, log=False)


def add_new_stock_tag():
    MainLog.add_log('refresh new stocks...')
    df1 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z001_daily_table.pkl")

    list1 = []
    list2 = []
    today = dt.date.today()
    for code, date in df1['ipo_date'].items():
        if pd.isna(date):
            list1.append(code)
        else:
            ipo_date = dt.datetime.strptime(date, "%Y-%m-%d").date()
            day = (today - ipo_date).days
            if day <= 365 * 3:
                list2.append(code)

    tags_operate(list1, '未上市', 'refresh')
    tags_operate(list2, '新上市', 'refresh')
    MainLog.add_log('refresh new stocks complete.')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    add_new_stock_tag()
