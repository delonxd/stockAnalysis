import pandas as pd
import pickle
import time


def get_style_df_mvs():
    header_df = get_header_df_mvs()
    df = header_df.T.copy()

    df.insert(0, "ma_mode", 0)
    df.insert(1, "delta_mode", False)
    df.insert(2, "default_ds", False)
    df.insert(3, "show_name", '')
    df.insert(4, "index_name", '')
    df.insert(5, "selected", False)

    df.insert(6, "color", QColor(Qt.red))
    df.insert(7, "line_thick", 2)
    df.insert(8, "pen_style", Qt.SolidLine)

    df.insert(9, "scale_min", 0)
    df.insert(10, "scale_max", 100)
    df.insert(11, "scale_div", 10)
    df.insert(12, "logarithmic", False)

    df.insert(13, "info_priority", 0)

    df.insert(14, "units", '倍')
    df.insert(15, "child", None)
    df.insert(16, "ds_type", 'digit')

    df.loc['first_update', 'ds_type'] = 'str'
    df.loc['last_update', 'ds_type'] = 'str'
    df.loc['stockCode', 'ds_type'] = 'const'
    df.loc['date', 'ds_type'] = 'str'

    df.loc['id_001_mvs_pe_ttm', 'selected'] = True

    return df


def combine_style_df():

    path = '../gui/styles/style_df_standard.pkl'
    with open(path, 'rb') as pk_f:
        df1 = pickle.load(pk_f)

    df1.insert(0, "frequency", "QUARTERLY")

    df2 = get_style_df_mvs()

    df2.insert(0, "frequency", "DAILY")

    res = pd.merge(df1.T, df2.T, how='outer', left_index=True, right_index=True,
                   suffixes=('_fs', '_mvs'), copy=True).T

    res["index_name"] = res.index.values

    res.loc['first_update_fs', 'txt_CN'] = '首次上传日期_fs'
    res.loc['last_update_fs', 'txt_CN'] = '最近上传日期_fs'

    res.loc['first_update_mvs', 'txt_CN'] = '首次上传日期_mvs'
    res.loc['last_update_mvs', 'txt_CN'] = '最近上传日期_mvs'

    # print(res)
    # print(res.index.values)
    # print(res.columns.values)
    #
    # for _, row in res.iterrows():
    #     print(row.values)

    # path = '../gui/style_combined_default0.pkl'
    path = '../gui/style_default.pkl'

    with open(path, 'wb') as pk_f:
        pickle.dump(res, pk_f)


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


def add_new_style(df: pd.DataFrame, index_name, src=None):
    if src is None:
        row = df[df['default_ds'] == True].copy()
    else:
        row = df.loc[[src], :].copy()

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
    # df0 = add_new_style(df0, 's_001_roe', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_002_equity')
    # df0 = add_new_style(df0, 's_003_profit')
    # df0 = add_new_style(df0, 's_004_pe', src='id_001_mvs_pe_ttm')
    # df0 = add_new_style(df0, 's_005_stocks')
    # df0 = add_new_style(df0, 's_006_stocks_rate', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_007_asset')
    # df0 = add_new_style(df0, 's_008_revenue')
    # df0 = add_new_style(df0, 's_009_revenue_rate', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_010_main_profit')
    # df0 = add_new_style(df0, 's_011_main_profit_rate', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_012_return_year', src='id_001_mvs_pe_ttm')
    # df0 = add_new_style(df0, 's_014_pe2', src='id_001_mvs_pe_ttm')
    # df0 = add_new_style(df0, 's_015_return_year2', src='id_001_mvs_pe_ttm')
    # df0 = add_new_style(df0, 's_016_roe_parent', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_017_equity_parent')
    # df0 = add_new_style(df0, 's_018_profit_parent')
    # df0 = add_new_style(df0, 's_019_monetary_asset')
    # df0 = add_new_style(df0, 's_020_cap_asset')
    # df0 = add_new_style(df0, 's_021_cap_expenditure')
    # df0 = add_new_style(df0, 's_022_profit_no_expenditure')
    # df0 = add_new_style(df0, 's_023_liabilities')
    # df0 = add_new_style(df0, 's_024_real_liabilities')
    # df0 = add_new_style(df0, 's_025_real_cost', src='id_041_mvs_mc')
    # df0 = add_new_style(df0, 's_026_holder_return_rate', src='id_041_mvs_mc')
    # df0 = add_new_style(df0, 's_027_pe_return_rate', src='id_041_mvs_mc')
    # df0 = add_new_style(df0, 's_028_market_value', src='id_041_mvs_mc')
    # df0 = add_new_style(df0, 's_029_return_predict', src='s_027_pe_return_rate')
    # df0 = add_new_style(df0, 's_030_parent_equity_delta')
    # df0 = add_new_style(df0, 's_031_financing_outflow')
    # df0 = add_new_style(df0, 's_032_remain_rate', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_033_profit_compound', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 'mir_y10', src='s_027_pe_return_rate')
    # df0 = add_new_style(df0, 's_034_real_pe', src='s_004_pe')
    # df0 = add_new_style(df0, 's_035_pe2rate', src='s_004_pe')
    # df0 = add_new_style(df0, 's_036_real_pe2rate', src='s_004_pe')
    # df0 = add_new_style(df0, 's_037_real_pe_return_rate', src='s_027_pe_return_rate')
    # df0 = add_new_style(df0, 's_038_pay_for_long_term_asset')
    # df0 = add_new_style(df0, 's_039_profit_adjust')
    # df0 = add_new_style(df0, 's_040_profit_adjust2')
    # df0 = add_new_style(df0, 's_041_profit_adjust_ttm')
    # df0 = add_new_style(df0, 's_041_profit_adjust_ttm')
    # df0 = add_new_style(df0, 's_042_roe_adjust', src='id_004_bs_tca_ta_r')
    # df0 = add_new_style(df0, 's_043_turnover_volume_ttm', src='id_041_mvs_mc')
    # df0 = add_new_style(df0, 'market_change_rate', src='s_027_pe_return_rate')
    # df0 = add_new_style(df0, 's_044_turnover_volume', src='s_043_turnover_volume_ttm')
    # df0 = add_new_style(df0, 's_045_main_cost_adjust', src='s_008_revenue')
    df0 = add_new_style(df0, 's_046_profit_adjust3', src='s_040_profit_adjust2')
    # df0.drop('s_012_return_year', inplace=True)

    # df0.loc[
    #     df0['logarithmic'].values &
    #     (df0['units'].values == '亿'),
    #     ['scale_max', 'scale_min']
    # ] = ['auto', 'auto']
    #
    # print(df0[['scale_min', 'scale_max', 'units']])
    save_default_style(df0)
    pass