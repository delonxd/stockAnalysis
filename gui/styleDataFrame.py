import pandas as pd
import pickle
import time


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
    # df0 = add_new_style(df0, 's_046_profit_adjust3', src='s_040_profit_adjust2')
    # df0.drop('s_012_return_year', inplace=True)

    # df0.loc[
    #     df0['logarithmic'].values &
    #     (df0['units'].values == '亿'),
    #     ['scale_max', 'scale_min']
    # ] = ['auto', 'auto']
    #
    # print(df0[['scale_min', 'scale_max', 'units']])

    print(df0.columns.values)

    tmp_dict = {
        's_022_profit_no_expenditure': '股东盈余',
        's_025_real_cost': '真实成本',
        'id_041_mvs_mc': '市值',
        'id_217_ps_npatoshopc': '归母净利润',
        's_018_profit_parent': '归母净利润',
        'id_124_bs_tetoshopc': '归母股东权益',
        's_017_equity_parent': '归母股东权益',
        'id_001_bs_ta': '资产合计',
        's_020_cap_asset': '资本化资产',
        'id_261_cfs_ncffoa': '经营现金流净额',
        's_026_holder_return_rate': '股东回报率',
        's_027_pe_return_rate': 'pe回报率',
        'id_341_m_gp_m': '毛利率',
        'id_157_ps_toi': '主营收入',
        'id_163_ps_toc': '主营成本',
        's_009_revenue_rate': '主营收入增速',
        's_029_return_predict': '预测回报率',
        's_016_roe_parent': 'roe',
        's_032_remain_rate': '资金留存率',
        'mir_y10': '十年期国债利率',
        's_004_pe': 'pe',
        's_034_real_pe': None,
        's_035_pe2rate': None,
        's_036_real_pe2rate': None,

        's_038_pay_for_long_term_asset': None,
        's_039_profit_adjust': None,
        's_040_profit_adjust2': None,
        's_041_profit_adjust_ttm': None,
        's_043_turnover_volume_ttm': None,
        'market_change_rate': None,
        's_045_main_cost_adjust': None,
        's_046_profit_adjust3': None,
    }
    index = list(tmp_dict.keys())
    df0.loc[index, 'pix4'] = True
    print(df0['pix4'])
    save_default_style(df0)
    pass