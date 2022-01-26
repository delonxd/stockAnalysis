
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
        s1 = df.loc[:, 's_037_real_pe_return_rate'].dropna()
        val1 = s1[-1] if s1.size > 0 else -np.inf

        s2 = df.loc[:, 's_016_roe_parent'].dropna()
        val2 = s2[-1] if s2.size > 0 else -np.inf

        val_list.append((code, val1, val2))

    res1 = sorted(val_list, key=lambda x: x[1], reverse=True)
    res2 = sorted(val_list, key=lambda x: x[2], reverse=True)

    sorted1 = zip(*res1).__next__()
    sorted2 = zip(*res2).__next__()

    res = json.dumps(sorted1, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_real_pe.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(sorted2, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_roe_parent.txt' % res_dir
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


if __name__ == '__main__':
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    date_dir = 'update_20220121153503'

    # load_daily_res(date_dir)
    # sort_daily_code(date_dir)
    # generate_list()
    get_codes_from_sel()
