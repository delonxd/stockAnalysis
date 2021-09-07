import pickle


bsList = r"""
PE-TTM :pe_ttm
PE-TTM分位点(3年) :pe_ttm_pos3
PE-TTM分位点(5年) :pe_ttm_pos5
PE-TTM分位点(10年) :pe_ttm_pos10
PE-TTM分位点(20年) :pe_ttm_pos20
PE-TTM分位点(全部) :pe_ttm_pos_all
PE-TTM(扣非) :d_pe_ttm
PE-TTM(扣非)分位点(3年) :d_pe_ttm_pos3
PE-TTM(扣非)分位点(5年) :d_pe_ttm_pos5
PE-TTM(扣非)分位点(10年) :d_pe_ttm_pos10
PE-TTM(扣非)分位点(20年) :d_pe_ttm_pos20
PE-TTM(扣非)分位点(全部) :d_pe_ttm_pos_all
PB :pb
PB分位点(3年) :pb_pos3
PB分位点(5年) :pb_pos5
PB分位点(10年) :pb_pos10
PB分位点(20年) :pb_pos20
PB分位点(全部) :pb_pos_all
PB(不含商誉) :pb_wo_gw
PB(不含商誉)分位点(3年) :pb_wo_gw_pos3
PB(不含商誉)分位点(5年) :pb_wo_gw_pos5
PB(不含商誉)分位点(10年) :pb_wo_gw_pos10
PB(不含商誉)分位点(20年) :pb_wo_gw_pos20
PB(不含商誉)分位点(全部) :pb_wo_gw_pos_all
PS-TTM :ps_ttm
PS-TTM分位点(3年) :ps_ttm_pos3
PS-TTM分位点(5年) :ps_ttm_pos5
PS-TTM分位点(10年) :ps_ttm_pos10
PS-TTM分位点(20年) :ps_ttm_pos20
PS-TTM分位点(全部) :ps_ttm_pos_all
PCF-TTM :pcf_ttm
EV/EBIT :ev_ebit_r
股票收益率 :ey
股息率 :dyr
股价 :sp
成交量 :tv
前复权 :fc_rights
后复权 :bc_rights
理杏仁前复权 :lxr_fc_rights
股东人数 :shn
市值 :mc
流通市值 :cmc
自由流通市值 :ecmc
人均自由流通市值 :ecmc_psh
融资余额 :fb
融券余额 :sb
陆股通持仓金额 :ha_shm"""


with open('../basicData/priceText.pkl', 'wb') as pk_f:
    pickle.dump(bsList, pk_f)
