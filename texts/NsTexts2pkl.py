import re
import pickle

# 资产负债表
bsList = r"""
一、 资产合计 : bs.ta
净营运资本 : bs.nwc
流动资产合计 : bs.tca
流动资产占比 : bs.tca_ta_r
货币资金 : bs.cabb
货币资金占比 : bs.cabb_ta_r
结算备付金 : bs.sr
拆出资金 : bs.pwbaofi
交易性金融资产 : bs.tfa
衍生金融资产(流动) : bs.cdfa
应收票据及应收账款 : bs.nraar
(其中) 应收票据 : bs.nr
(其中) 应收账款 : bs.ar
应收款项融资 : bs.rf
预付款项 : bs.ats
应收保费 : bs.pr
应收分保账款 : bs.rir
应收分保合同准备金 : bs.crorir
其他应收款 : bs.or
(其中) 应收利息 : bs.ir
(其中) 应收股利 : bs.dr
买入返售金融资产 : bs.fahursa
存货 : bs.i
合同资产 : bs.ca
持有待售资产 : bs.ahfs
发放贷款及垫款(流动) : bs.claatc
待摊费用 : bs.pe
一年内到期的非流动资产 : bs.ncadwioy
其他流动资产 : bs.oca
流动比率 : bs.tca_tcl_r
速动比率 : bs.q_r
非流动资产合计 : bs.tnca
非流动资产占比 : bs.tnca_ta_r
重资产占比 : bs.ah_ta_r
发放贷款及垫款(非流动) : bs.nclaatc
债权投资 : bs.cri
其他债权投资 : bs.ocri
可供出售金融资产(非流动) : bs.ncafsfa
持有至到期投资 : bs.htmi
长期应收款 : bs.ltar
长期股权投资 : bs.ltei
其他权益工具投资 : bs.oeii
其他非流动金融资产 : bs.oncfa
投资性房地产 : bs.rei
固定资产 : bs.fa
(其中) 固定资产清理 : bs.dofa
固定资产占总资产比率 : bs.fa_ta_r
在建工程 : bs.cip
(其中) 工程物资 : bs.es
在建工程占固定资产比率 : bs.cip_fa_r
生产性生物资产 : bs.pba
油气资产 : bs.oaga
公益性生物资产 : bs.pwba
使用权资产 : bs.roua
无形资产 : bs.ia
开发支出 : bs.rade
商誉 : bs.gw
商誉占净资产比率 : bs.gw_toe_r
长期待摊费用 : bs.ltpe
递延所得税资产 : bs.dita
其他非流动资产 : bs.onca
二、 负债合计 : bs.tl
有息负债 : bs.lwi
有息负债率 : bs.lwi_ta_r
资产负债率 : bs.tl_ta_r
流动负债合计 : bs.tcl
流动负债占比 : bs.tcl_tl_r
短期借款 : bs.stl
向中央银行借款 : bs.bfcb
拆入资金 : bs.pfbaofi
衍生金融负债 : bs.dfl
交易性金融负债 : bs.tfl
应付票据及应付账款 : bs.npaap
(其中) 应付票据 : bs.np
(其中) 应付账款 : bs.ap
预收账款 : bs.afc
合同负债 : bs.cl
卖出回购金融资产 : bs.fasurpa
吸收存款及同业存放 : bs.dfcab
代理买卖证券款 : bs.stoa
代理承销证券款 : bs.ssoa
应付职工薪酬 : bs.sawp
应交税费 : bs.tp
其他应付款 : bs.oap
(其中) 应付利息 : bs.intp
(其中) 应付股利 : bs.dp
应付手续费及佣金 : bs.facp
应付分保账款 : bs.rip
持有待售负债 : bs.lhfs
一年内到期的非流动负债 : bs.ncldwioy
一年内到期的递延收益 : bs.didwioy
预计负债(流动) : bs.cal
短期应付债券 : bs.stbp
其他流动负债 : bs.ocl
非流动负债合计 : bs.tncl
非流动负债占比 : bs.tncl_tl_r
保险合同准备金 : bs.icr
长期借款 : bs.ltl
应付债券 : bs.bp
(其中) 优先股 : bs.psibp
(其中) 永续债 : bs.pcsibp
租赁负债 : bs.ll
长期应付款 : bs.ltap
(其中) 专项应付款 : bs.sap
长期应付职工薪酬 : bs.ltpoe
预计负债(非流动) : bs.ncal
长期递延收益 : bs.ltdi
递延所得税负债 : bs.ditl
其他非流动负债 : bs.oncl
三、 所有者权益合计 : bs.toe
股东权益占比 : bs.toe_ta_r
股本 : bs.sc
其他权益工具 : bs.oei
(其中) 优先股 : bs.psioei
(其中) 永续债 : bs.pcsioei
资本公积 : bs.capr
减： 库存股 : bs.is
其他综合收益 : bs.oci
专项储备 : bs.rr
盈余公积 : bs.surr
一般风险准备金 : bs.pogr
未分配利润 : bs.rtp
归属于母公司股东及其他权益持有者的权益合计 : bs.tetshaoehopc
归属于母公司普通股股东权益合计 : bs.tetoshopc
归属于母公司普通股股东的每股股东权益 : bs.tetoshopc_ps
少数股东权益 : bs.etmsh
四、 员工情况
员工人数 : bs.ep_stn
博士人数 : bs.ep_pn
硕士人数 : bs.ep_mn
学士人数 : bs.ep_bn
大专人数 : bs.ep_jcn
高中及以下人数 : bs.ep_hsabn
生产人员人数 : bs.ep_psn
销售人员人数 : bs.ep_spn
技术人员人数 : bs.ep_tsn
财务人员人数 : bs.ep_fon
行政人员人数 : bs.ep_asn
其他人员人数 : bs.ep_osn
五、 股本、股东和估值
市值 : bs.mc
总股本 : bs.tsc
流通股本 : bs.csc
股东人数(季度) : bs.shn
第一大股东持仓占总股本比例 : bs.shbt1sh_tsc_r
前十大股东持仓占总股本比例 : bs.shbt10sh_tsc_r
前十大流通股东持仓占流通股本比例 : bs.shbt10sh_csc_r
公募基金持仓占流通股本比例 : bs.shbpoof_csc_r
公募基金+自由流通股东持仓占自由流通股本比例 : bs.shbeosh_poof_ecsc_r
PE-TTM : bs.pe_ttm
PE-TTM(扣非) : bs.d_pe_ttm
PB : bs.pb
PB(不含商誉) : bs.pb_wo_gw
PS-TTM : bs.ps_ttm
股息率 : bs.dyr
分红率 : bs.d_np_r"""


# 利润表
psList = r"""
一、 营业总收入 : ps.toi
营业收入 : ps.oi
利息收入 : ps.ii
已赚保费 : ps.ep
手续费及佣金收入 : ps.faci
其他业务收入 : ps.ooi
二、 营业总成本 : ps.toc
营业成本 : ps.oc
毛利率(GM) : ps.gp_m
利息支出 : ps.ie
手续费及佣金支出 : ps.face
退保金 : ps.s
保险合同赔付支出 : ps.ce
提取保险责任准备金净额 : ps.iiicr
保单红利支出 : ps.phdrfpip
分保费用 : ps.rie
税金及附加 : ps.tas
销售费用 : ps.se
管理费用 : ps.ae
研发费用 : ps.rade
财务费用 : ps.fe
(其中) 利息费用 : ps.ieife
(其中) 利息收入 : ps.iiife
销售费用率 : ps.se_r
管理费用率 : ps.ae_r
研发费用率 : ps.rade_r
财务费用率 : ps.fe_r
总营业费用率 : ps.oe_r
三项费用率 : ps.te_r
加： 其他收益 : ps.oic
投资收益 : ps.ivi
(其中) 对联营企业及合营企业的投资收益 : ps.iifaajv
(其中) 以摊余成本计量的金融资产终止确认产生的投资收益 : ps.iftdofamaac
汇兑收益 : ps.ei
净敞口套期收益 : ps.nehb
公允价值变动收益 : ps.ciofv
信用减值损失 : ps.cilor
资产减值损失 : ps.ailor
其他资产减值损失 : ps.oail
资产处置收益 : ps.adi
其他业务成本 : ps.ooe
核心利润 : ps.cp
核心利润率 : ps.cp_r
三、 营业利润 : ps.op
营业利润率 : ps.op_s_r
其他营业利润率 : ps.op_op_r
加： 营业外收入 : ps.noi
(其中) 非流动资产毁损报废利得 : ps.ncadarg
减： 营业外支出 : ps.noe
(其中) 非流动资产毁损报废损失 : ps.ncadarl
四、 利润总额 : ps.tp
研发费占利润总额比值 : ps.rade_tp_r
减： 所得税费用 : ps.ite
有效税率 : ps.ite_tp_r
五、 净利润 : ps.np
净利润率 : ps.np_s_r
息税前净利润(EBIT) : ps.ebit
(一) 持续经营净利润 : ps.npfco
(二) 终止经营净利润 : ps.npfdco
归属于母公司股东及其他权益持有者的净利润 : ps.npatshaoehopc
归属于母公司普通股股东的净利润 : ps.npatoshopc
少数股东损益 : ps.npatmsh
归属于母公司普通股股东的扣除非经常性损益的净利润 : ps.npadnrpatoshaopc
扣非净利润占比 : ps.npadnrpatoshaopc_npatoshopc_r
归属于母公司普通股股东的加权ROE : ps.wroe
归属于母公司普通股股东的扣非加权ROE : ps.wdroe
六、 基本每股收益 : ps.beps
稀释每股收益 : ps.deps
七、 综合收益总额 : ps.tci
归属于母公司股东及其他权益持有者的综合收益总额 : ps.tciatshaoehopc
归属于母公司普通股股东的综合收益总额 : ps.tciatoshopc
归属于少数股东的综合收益总额 : ps.tciatmsh
其他综合收益的税后净额 : ps.natooci"""

# 现金流量表
cfsList = r"""
一、 经营活动产生的现金流量
销售商品、提供劳务收到的现金 : cfs.crfscapls
发放贷款及垫款的净减少额 : cfs.ndilaatc
客户存款和同业及其他金融机构存放款项净增加额 : cfs.niicdadfbaofi
向中央银行借款净增加额 : cfs.niibfcb
向其他金融机构拆入资金净增加额 : cfs.niipfofi
收到原保险合同保费取得的现金 : cfs.crfp
收到再保险业务现金净额 : cfs.ncrfrib
保户储金及投资款净增加额 : cfs.niiphd
为交易目的而持有的金融资产净减少额 : cfs.ndifahftp
拆入资金净增加额 : cfs.niipfbaofi
卖出回购业务资金净增加额 : cfs.niifasurpaioa
收取利息、手续费及佣金的现金 : cfs.crfifac
代理买卖证券收到的现金净额 : cfs.ncrfstoa
收到的税费返还 : cfs.crfwbot
收到的其他与经营活动有关现金 : cfs.crrtooa
经营活动现金流入小计 : cfs.stciffoa
购买商品、接收劳务支付的现金 : cfs.cpfpcarls
发放贷款及垫款的净增加额 : cfs.niilaatc
存放中央银行和同业及其他金融机构款项净增加额 : cfs.niibwcbbaofi
向其他金融机构拆入资金净减少额 : cfs.ndipfofi
支付原保险合同赔付等款项的现金 : cfs.cpfc
拆出资金增加额 : cfs.niipwbaofi
买入返售金融资产净增加额 : cfs.niifahursaioa
支付保单红利的现金 : cfs.cpfphd
为交易目的而持有的金融资产净增加额 : cfs.niifahftp
支付利息、手续费及佣金的现金 : cfs.cpfifac
支付给职工及为职工支付的现金 : cfs.cptofe
支付的各种税费 : cfs.cpft
支付的其他与经营活动有关现金 : cfs.cprtooa
经营活动现金流出小计 : cfs.stcoffoa
经营活动产生的现金流量净额 : cfs.ncffoa
二、 投资活动产生的现金流量金额
收回投资收到的现金 : cfs.crfrci
取得投资收益所收到的现金 : cfs.crfii
处置固定资产、无形资产及其他长期资产收到的现金 : cfs.crfdofiaolta
处置子公司、合营联营企业及其他营业单位收到的现金净额 : cfs.ncrfdossajvaou
(其中) 处置子公司或其他营业单位收到的现金净额 : cfs.ncrfdossaou
(其中) 处置合营或联营公司所收到的现金 : cfs.ncrfdoaajv
收到的其他与投资活动相关的现金 : cfs.crrtoia
投资活动现金流入小计 : cfs.stcifia
购建固定资产、无形资产及其他长期资产所支付的现金 : cfs.cpfpfiaolta
投资所支付的现金 : cfs.cpfi
质押贷款净增加额 : cfs.niipl
取得子公司、合营联营企业及其他营业单位支付的现金净额 : cfs.ncpfbssajvaou
(其中) 取得子公司及其营业单位支付的现金净额 : cfs.ncpfbssaou
(其中) 取得联营及合营公司支付的现金净额 : cfs.ncpfbajv
支付的其他与投资活动有关的现金 : cfs.cprtoia
投资活动现金流出小计 : cfs.stcoffia
投资活动产生的现金流量净额 : cfs.ncffia
三、 筹资活动产生的现金流量
吸收投资收到的现金 : cfs.crfai
(其中) 子公司吸收少数股东投资收到的现金 : cfs.crfamshibss
取得借款收到的现金 : cfs.crfl
发行债券收到的现金 : cfs.crfib
收到的其他与筹资活动有关的现金 : cfs.crrtofa
筹资活动产生的现金流入小计 : cfs.stcifffa
偿付债务支付的现金 : cfs.cpfbrp
分配股利、利润或偿付利息所支付的现金 : cfs.cpfdapdoi
(其中) 子公司支付少数股东股利及利润 : cfs.cpfdapomshpbss
支付的其他与筹资活动有关的现金 : cfs.cprtofa
筹资活动产生的现金流出小计 : cfs.stcofffa
筹资活动产生的现金流量净额 : cfs.ncfffa
四、 汇率变动对现金及现金等价物的影响 : cfs.iocacedtfier
期初现金及现金等价物的余额 : cfs.bocaceatpb
现金及现金等价物的净增加额 : cfs.niicace
期末现金及现金等价物净余额 : cfs.bocaceatpe
五、 附注
净利润 : cfs.np
加： 资产减值准备 : cfs.ioa
信用减值损失 : cfs.cilor
固定资产折旧、油气资产折耗、生产性生物资产折旧 : cfs.dofx_dooaga_dopba
投资性房地产的折旧及摊销 : cfs.daaorei
无形资产摊销 : cfs.aoia
长期待摊费用摊销 : cfs.aoltde
处置固定资产、无形资产和其他长期资产的损失 : cfs.lodofaiaaolta
固定资产报废损失 : cfs.lfsfa
公允价值变动损失 : cfs.lfcifv
财务费用 : cfs.fe
投资损失 : cfs.il
递延所得税资产减少 : cfs.didita
递延所得税负债增加 : cfs.iiditl
存货的减少 : cfs.dii
经营性应收项目的减少 : cfs.dior
经营性应付项目的增加 : cfs.iiop
其他 : cfs.o
债务转为资本 : cfs.coditc
一年内到期的可转换公司债券 : cfs.cbdwioy
融资租入固定资产 : cfs.flofa"""

mList = """
一、 人均指标
员工人数 : m.ep_stn
人均营业总收入 : m.toi_pc
人均净利润 : m.np_pc
人均薪酬 : m.s_pc
二、 每股指标
归属于母公司普通股股东的每股收益 : m.npatoshopc_ps
归属于母公司普通股股东的每股扣非收益 : m.npadnrpatoshaopc_ps
归属于母公司普通股股东的每股股东权益 : m.tetoshopc_ps
每股资本公积 : m.cr_ps
每股未分配利润 : m.rp_ps
每股经营活动产生的现金流量 : m.stciffoa_ps
每股经营活动产生的现金流量净额 : m.ncffoa_ps
三、 盈利能力
归属于母公司普通股股东的ROE : m.roe_atoshaopc
归属于母公司普通股股东的扣非ROE : m.roe_adnrpatoshaopc
归属于母公司普通股股东的加权ROE : m.wroe
净资产收益率(ROE) : m.roe
杠杆倍数 : m.l
总资产收益率(ROA) : m.roa
资产周转率 : m.ta_to
净利润率 : m.np_s_r
毛利率(GM) : m.gp_m
有形资产回报率(ROTA) : m.rota
资本回报率(ROIC) : m.roic
资本收益率(ROC) : m.roc
四、 营运能力(周转率)
预付账款周转率 : m.ats_tor
合同资产周转率 : m.ca_tor
存货周转率 : m.i_tor
应收票据和应收账款周转率 : m.nraar_tor
应收票据周转率 : m.nr_tor
应收账款周转率 : m.ar_tor
应收款项融资周转率 : m.rf_tor
预收账款周转率 : m.afc_tor
合同负债周转率 : m.cl_tor
应付票据和应付账款周转率 : m.npaap_tor
应付票据周转率 : m.np_tor
应付账款周转率 : m.ap_tor
固定资产周转率 : m.fa_tor
五、 营运能力(周转天数)
预付账款周转天数 : m.ats_ds
合同资产周转天数 : m.ca_ds
存货周转天数 : m.i_ds
应收票据和应收账款周转天数 : m.nraar_ds
应收票据周转天数 : m.nr_ds
应收账款周转天数 : m.ar_ds
应收款项融资周转天数 : m.rf_ds
预收账款周转天数 : m.afc_ds
合同负债周转天数 : m.cl_ds
应付票据和应付账款周转天数 : m.npaap_ds
应付票据周转天数 : m.np_ds
应付账款周转天数 : m.ap_ds
营业周转天数 : m.b_ds
净现金周转天数(CCC) : m.m_ds
固定资产周转天数 : m.fa_ds
流动资产周转天数 : m.tca_ds
股东权益周转天数 : m.toe_ds
总资产周转天数 : m.ta_ds
六、 偿债及资本结构
资产负债率 : m.tl_ta_r
有息负债率 : m.lwi_ta_r
货币资金占流动负债比率 : m.cabb_tcl_r
流动比率 : m.c_r
速动比率 : m.q_r
固定资产占总资产比率 : m.fa_ta_r
清算价值比率 : m.lv_r
七、 现金流量
自由现金流量 : m.fcf
销售商品提供劳务收到的现金对营业收入的比率 : m.crfscapls_oi_r
经营活动产生的现金流量净额对营业利润的比率 : m.ncffoa_op_r
经营活动产生的现金流量净额对净利润的比率 : m.ncffoa_np_r
销售商品提供劳务收到的现金对总资产的比率 : m.crfscapls_ta_r
经营活动产生的现金流量净额对固定资产的比率 : m.ncffoa_fa_r"""


with open('../pkl/NsBsText.pkl', 'wb') as pk_f:
    pickle.dump(bsList, pk_f)

with open('../pkl/NsPsText.pkl', 'wb') as pk_f:
    pickle.dump(psList, pk_f)

with open('../pkl/NsCfsText.pkl', 'wb') as pk_f:
    pickle.dump(cfsList, pk_f)

with open('../pkl/NsMText.pkl', 'wb') as pk_f:
    pickle.dump(mList, pk_f)
