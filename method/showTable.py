import pickle
import numpy as np
import json
import os
import pandas as pd


def generate_data_table():
    ret = pd.DataFrame()

    ret = generate_basic_table(ret)

    sub_dir = '..\\basicData\\dailyUpdate\\latest\\res_daily\\'
    list0 = [x for x in os.listdir(sub_dir) if os.path.isfile(sub_dir + x)]

    res = list()
    for file in list0:
        path = '%s\\%s' % (sub_dir, file)
        print(path)
        with open(path, "rb") as f:
            res.extend(pickle.load(f))

    for tmp in res:
        code = tmp[0]
        df = tmp[1]

        val = get_recent_val(df, 's_037_real_pe_return_rate', -np.inf)
        ret.loc[code, 'real_pe_return_rate'] = val

        val = get_recent_val(df, 's_016_roe_parent', -np.inf)
        ret.loc[code, 'roe_parent'] = val

        val = get_recent_val(df, 's_027_pe_return_rate', -np.inf)
        ret.loc[code, 'pe_return_rate'] = val

        val = get_recent_val(df, 's_025_real_cost', np.inf)
        ret.loc[code, 'real_cost'] = val

        val = get_recent_val(df, 's_028_market_value', np.inf)
        ret.loc[code, 'market_value_1'] = val

        val = get_recent_val(df, 's_028_market_value', np.inf, 2)
        ret.loc[code, 'market_value_2'] = val

    ################################################################################################################

    # print(ret)

    path = "..\\basicData\\dailyUpdate\\latest\\show_table.xlsx"
    with pd.ExcelWriter(path) as writer:
        ret.to_excel(writer, sheet_name="数据输出", index=True)

    dict0 = json.loads(ret.to_json(orient="index", force_ascii=False))
    res = json.dumps(dict0, indent=4, ensure_ascii=False)
    path = "..\\basicData\\dailyUpdate\\latest\\show_table.txt"
    with open("../test/style_test.txt", "w", encoding="utf-8") as f:
        f.write(res)


def get_recent_val(df, column, default, shift=1):
    series = df.loc[:, column].copy().dropna()
    val = series[-shift] if series.size >= shift else default
    return val


def generate_basic_table(df: pd.DataFrame):
    # df = pd.DataFrame()

    ################################################################################################################

    path = "..\\basicData\\dailyUpdate\\latest\\a002_name_dict.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for key, value in res.items():
        df.loc[key, 'cn_name'] = value

    ################################################################################################################

    path = "..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt"
    df = add_bool_column(df, path, 'update_recently')

    ################################################################################################################

    path = "..\\basicData\\self_selected\\gui_blacklist.txt"
    df = add_bool_column(df, path, 'gui_blacklist')

    path = "..\\basicData\\self_selected\\gui_whitelist.txt"
    df = add_bool_column(df, path, 'gui_whitelist')

    path = "..\\basicData\\self_selected\\gui_selected.txt"
    df = add_bool_column(df, path, 'gui_selected')

    path = "..\\basicData\\self_selected\\gui_non_cyclical.txt"
    df = add_bool_column(df, path, 'gui_non_cyclical')

    path = "..\\basicData\\self_selected\\gui_fund.txt"
    df = add_bool_column(df, path, 'gui_fund')

    ################################################################################################################

    path = "..\\basicData\\self_selected\\gui_remark.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for key, value in res.items():
        df.loc[key, 'key_remark'] = value[1]
        df.loc[key, 'remark'] = value[2]

    ################################################################################################################

    path = "..\\basicData\\self_selected\\gui_hold.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for value in res:
        code = value[0]
        df.loc[code, 'gui_hold'] = True

    ################################################################################################################

    path = "..\\basicData\\self_selected\\gui_counter.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for key, value in res.items():
        df.loc[key, 'counter_last_date'] = value[0]
        df.loc[key, 'counter_date'] = value[1]
        df.loc[key, 'counter_number'] = value[2]
        df.loc[key, 'counter_real_pe'] = value[3]
        df.loc[key, 'counter_delta'] = value[4]

    ################################################################################################################

    path = "..\\basicData\\self_selected\\gui_assessment.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for key, value in res.items():
        df.loc[key, 'gui_assessment'] = value

    return df


def add_bool_column(df, path, name):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        res = json.loads(f.read())

    for key in res:
        df.loc[key, name] = True
    return df


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    a = pd.DataFrame()
    generate_basic_table(a)
    # generate_data_table()

