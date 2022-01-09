
def load_daily_res():
    import pickle
    import numpy as np
    import json

    datetime = '20220107153503'
    res_dir = '..\\basicData\\dailyUpdate\\update_%s' % datetime

    file = '%s\\res_daily_%s.pkl' % (res_dir, datetime)
    with open(file, "rb") as f:
        res = pickle.load(f)

    val_list = list()
    for tup in res:
        code = tup[0]
        df = tup[1]

        # s1 = df.loc[:, 's_016_roe_parent'].dropna()
        s1 = df.loc[:, 's_027_pe_return_rate'].dropna()
        val = s1[-1] if s1.size > 0 else -np.inf

        val_list.append((code, val))

    res_list = sorted(val_list, key=lambda x: x[1], reverse=True)

    code_sorted = zip(*res_list).__next__()
    print(code_sorted)

    res = json.dumps(code_sorted, indent=4, ensure_ascii=False)
    file = '%s\\code_sorted_2.txt' % res_dir
    with open(file, "w", encoding='utf-8') as f:
        f.write(res)


if __name__ == '__main__':
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    load_daily_res()
