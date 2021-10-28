import pandas as pd
import pickle
import time


def load_default_style():
    path = '../gui/styles/style_default.pkl'
    with open(path, 'rb') as pk_f:
        df = pickle.load(pk_f)
    return df


def save_default_style(df):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    path1 = '../gui/styles/style_%s.pkl' % timestamp
    with open(path1, 'wb') as pk_f:
        pickle.dump(df, pk_f)

    path2 = '../gui/styles/style_default.pkl'
    with open(path2, 'wb') as pk_f:
        pickle.dump(df, pk_f)


def add_new_style(df: pd.DataFrame, index_name):

    row = df[df['default_ds'] == True].copy()

    row['default_ds'] = False
    row['selected'] = False

    row['show_name'] = index_name
    row['index_name'] = index_name

    row['txt_CN'] = index_name
    row['sql_type'] = ''
    row['sheet_name'] = ''
    row['api'] = ''

    row.index = [index_name]

    res = df.append(row)

    return res


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('max_colwidth', 150)
    # test_analysis()
    df0 = load_default_style()
    res = add_new_style(df0, 's_001_roe')

    save_default_style(res)
    pass