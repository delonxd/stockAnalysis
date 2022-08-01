
import pandas as pd
from method.fileMethod import *
from method.logMethod import log_it
import matplotlib.pyplot as plt


def get_recent_val(df, column, default, shift=1):
    series = df.loc[:, column].copy().dropna()
    val = series[-shift] if series.size >= shift else default
    return val


def generate_gui_table():
    df = pd.DataFrame()

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

    res = load_json_txt("..\\basicData\\self_selected\\gui_hold.txt")

    s0 = pd.Series(
        [True]*len(res),
        index=map(lambda x: x[0], res),
        name='gui_hold')
    df = pd.concat([df, s0], axis=1, sort=False)
    # print(s0)
    # for value in res:
    #     code = value[0]
    #     df.loc[code, 'gui_hold'] = True

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_remark.txt")

    df_tmp = pd.DataFrame.from_dict(
        res,
        columns=[0, 'key_remark', 'remark'],
        orient='index'
    )
    df_tmp = df_tmp.drop(0, axis=1)
    df = pd.concat([df, df_tmp], axis=1, sort=False)

    # print(df_tmp)
    # for key, value in res.items():
    #     df.loc[key, 'key_remark'] = value[1]
    #     df.loc[key, 'remark'] = value[2]

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_counter.txt")

    df_tmp = pd.DataFrame.from_dict(
        res,
        columns=[
            'counter_last_date',
            'counter_date',
            'counter_number',
            'counter_real_pe',
            'counter_delta',
        ],
        orient='index'
    )
    df = pd.concat([df, df_tmp], axis=1, sort=False)

    ################################################################################################################

    res = load_json_txt("..\\basicData\\self_selected\\gui_assessment.txt")

    s0 = pd.Series(res, name='gui_assessment')
    s0 = s0.apply(lambda x: int(x) * 1e8)
    df = pd.concat([df, s0], axis=1, sort=False)

    # for key, value in res.items():
    #     df.loc[key, 'gui_assessment'] = int(value) * 1e8

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl", df)

    return df


def add_bool_column(df, path, name):
    res = load_json_txt(path)
    s0 = pd.Series([True]*len(res), index=res, name=name)
    df = pd.concat([df, s0], axis=1, sort=False)
    # for key in res:
    #     df.loc[key, name] = True
    return df


def sum_value(res, column):
    ret = pd.Series()

    for tmp in res:
        code = tmp[0]
        src = tmp[1]
        s1 = src.loc[:, column].copy().dropna()

        df = pd.concat([s1, ret], axis=1, sort=False)
        df = df.fillna(0)
        ret = df.sum(axis=1)
    ret = ret.sort_index()
    # print(ret)

    return ret


def generate_code_df_src():
    df = pd.DataFrame()

    res = load_json_txt('..\\basicData\\code_names_dict.txt')
    s0 = pd.Series(res, name='name')
    df = pd.concat([df, s0], axis=1, sort=False)

    res = load_json_txt('..\\basicData\\industry\\sw_2021_dict.txt')
    i_code = pd.Series(res, name='i_code')

    res = load_json_txt('..\\basicData\\industry\\sw_2021_name_dict.txt')
    s1 = i_code.apply(lambda x: get_level_name(res, x, 1))
    s2 = i_code.apply(lambda x: get_level_name(res, x, 2))
    s3 = i_code.apply(lambda x: get_level_name(res, x, 3))
    s1.name = 'level1'
    s2.name = 'level2'
    s3.name = 'level3'
    df = pd.concat([df, s1, s2, s3, i_code], axis=1, sort=False)

    res = load_json_txt('..\\test\\test_analysis_dict.txt')
    s0 = pd.Series(res, name='salary')
    df = pd.concat([df, s0], axis=1, sort=False)

    # dump_pkl("..\\basicData\\code_df_src.pkl", df)

    return df


def get_level_name(ids_name_dict, i_code, level):
    if i_code:

        if level == 1:
            return ids_name_dict.get(i_code[:2] + '0000')
        elif level == 2:
            return ids_name_dict.get(i_code[:4] + '00')
        elif level == 3:
            return ids_name_dict.get(i_code[:6])
    else:
        return


@log_it(None)
def generate_show_table():
    # from method.dailyMethod import generate_daily_table
    # df1 = generate_daily_table('latest')
    df2 = generate_gui_table()
    df3 = generate_code_df_src()

    df1 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z001_daily_table.pkl")
    # df2 = load_pkl("..\\basicData\\dailyUpdate\\latest\\z002_gui_table.pkl")

    df = pd.concat([df3, df1, df2], axis=1, sort=True)

    s0 = pd.Series(df.index, index=df.index, name='code')
    df = pd.concat([s0, df], axis=1, sort=False)

    df['ass/equity'] = df['gui_assessment'] / df['equity']
    df['real_c/ass'] = df['real_cost'] / df['gui_assessment']
    df['market_v/ass'] = df['market_value_1'] / df['gui_assessment']
    df['tov/market_value'] = df['turnover_ttm20'] / df['market_value_1']
    df['tov/ass'] = df['turnover_ttm20'] / df['gui_assessment']

    order = [
        'code',
        'name',
        'level1',
        'level2',
        'level3',

        'real_c/ass',
        'market_v/ass',
        'ass/equity',

        'tov/ass',
        'tov/market_value',

        'gui_assessment',
        'market_value_1',
        'market_value_2',
        'real_cost',
        'equity',
        'turnover_ttm20',
        'salary',

        'update_recently',
        'gui_blacklist',
        'gui_whitelist',
        'gui_selected',
        'gui_non_cyclical',
        'gui_fund',
        'gui_hold',

        # 'key_remark',
        # 'remark',

        'ipo_date',
        'report_date',
        'counter_last_date',
        'counter_date',
        'counter_number',
        'counter_real_pe',
        'counter_delta',

        'roe_parent',
        'pe_return_rate',
        'real_pe_return_rate',
    ]

    df = df[order]

    ################################################################################################################

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl", df)

    path = "..\\basicData\\dailyUpdate\\latest\\show_table.xlsx"
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="数据输出", index=True)

    generate_show_table_mask(df)

    # dict0 = json.loads(df.to_json(orient="index", force_ascii=False))
    # write_json_txt("..\\basicData\\dailyUpdate\\latest\\show_table.txt", dict0)
    # print(df)

    return df


def generate_show_table_mask(df):
    # df = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")

    for column in [
        # 'ass/equity',
        # 'ass/real_cost',
        # 'ass/market_value',
        # 'tov/ass',
        # 'tov/market_value',

        'roe_parent',
        'pe_return_rate',
        'real_pe_return_rate',
        'counter_delta',
    ]:
        df[column] = df[column].apply(lambda x: '%.2f%%' % (x * 100))

    for column in [
        'tov/ass',
        'tov/market_value',
    ]:
        df[column] = df[column].apply(lambda x: '%.2f‰' % (x * 1000))

    for column in [
        # 'gui_assessment',
        'market_value_1',
        'market_value_2',
        'real_cost',
        'equity',
        'turnover_ttm20',
        # 'salary',
    ]:
        df[column] = df[column].apply(lambda x: format(x, '0,.0f'))

    column = 'gui_assessment'
    df[column] = df[column].apply(lambda x: format(x/1e8, '0,.0f'))

    column = 'salary'
    df[column] = df[column].apply(lambda x: format(x/1e4, '.2f'))

    for column in [
        'ass/equity',
        'real_c/ass',
        'market_v/ass',

        'counter_real_pe',
    ]:
        df[column] = df[column].apply(lambda x: format(x, '.2f'))

    dump_pkl("..\\basicData\\dailyUpdate\\latest\\show_table_mask.pkl", df)


def test_strategy():
    from method.dataMethod import load_df_from_mysql
    import datetime as dt

    df = load_df_from_mysql('600438', 'mvs')

    # s0 = df.loc[:, 'id_041_mvs_mc'].dropna()
    s0 = df.loc[:, 'id_035_mvs_sp'].dropna()
    s1 = s0[s0.index > '2021-01-04']

    profit = 0
    s2 = s1.copy()

    status = True
    value = s1[0]
    date = s1.index[0]
    print(status, value, profit)
    for index, val in s1.iteritems():
        if status is True:
            if val > value:
                profit += val - value
                value = val
                status = False
                d1 = dt.datetime.strptime(date, "%Y-%m-%d")
                d2 = dt.datetime.strptime(index, "%Y-%m-%d")
                delta = (d2 - d1).days
                print(date, index, delta)
                print(val, profit)
                # print('out')
        else:
            if val < value:
                value = val
                status = True
                date = index
        s2[index] = profit

    print(status, s1[-1], profit)

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False

    xx = range(s1.size)
    yy = s1.values
    fig = plt.figure(figsize=(16, 9), dpi=50)

    fig_tittle = 'Distribution'

    fig.suptitle(fig_tittle)
    fig.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(1, 1, 1)

    # ax1.yaxis.grid(True, which='both')
    # ax1.xaxis.grid(True, which='both')

    ax1.plot(xx, yy, linestyle='-', alpha=0.8, color='r', label='test')
    # plt.show()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 10000)

    # test_figure([1] * 21)
    # show_distribution()
    # test_strategy()
    generate_show_table()
    # generate_show_table_mask()
    # generate_code_df_src()

