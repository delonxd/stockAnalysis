from method.mainMethod import get_units_dict
# from method.dataMethod import get_month_delta
# from method.dataMethod import get_month_data

import pandas as pd
import numpy as np
import datetime as dt


class DataSource:
    def __init__(
            self,
            parent,
            df,

            index_name,
            show_name,

            color,
            line_thick,
            pen_type,

            scale_min,
            scale_max,
            scale_div,
            logarithmic,
            units,

            info_priority,

            ds_type,
            delta_mode,
            default_ds,

            ma_mode,
            frequency,

            pix_show,
            info_show,
    ):

        self.parent = parent

        self.default_ds = default_ds

        self.index_name = index_name
        self.show_name = show_name

        # if index_name == 'id_141_bs_mc':
        #     df = np.trim_zeros(df.iloc[:, 0]).to_frame()

        self.df = df

        self.ds_type = ds_type
        self.delta_mode = delta_mode
        self.ma_mode = ma_mode
        self.frequency = frequency
        self.pix_show = pix_show
        self.info_show = info_show

        # self.format_data_source()

        self.color = color
        self.line_thick = line_thick
        self.pen_type = pen_type

        # if self.ds_type == 'digit':
        #     series = self.df.iloc[:, 0]
        #     d_max = series.max()
        #     d_min = series.min()
        #     if 0 <= d_min <= 1 and 0 <= d_max <= 1:
        #         scale_max = 100
        #         scale_min = 0
        #         units = '%'
        #         logarithmic = False
        #
        #         self.parent.style_df.loc[index_name, 'scale_min'] = scale_min
        #         self.parent.style_df.loc[index_name, 'scale_max'] = scale_max
        #         self.parent.style_df.loc[index_name, 'units'] = units
        #         self.parent.style_df.loc[index_name, 'logarithmic'] = logarithmic
        #

        self.units = units
        self.ratio = get_units_dict()[units]
        self.scale_min = scale_min * self.ratio
        self.scale_max = scale_max * self.ratio

        self.scale_div = scale_div
        self.logarithmic = logarithmic

        self.info_priority = info_priority

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        if self.ds_type == 'digit':
            self.format_fun = lambda x: '--' if x == 0 else '%.2f %s' % (x / self.ratio, units)
        else:
            self.format_fun = lambda x: '%s' % x

        self.set_val_scale()
        self.df.columns = [index_name]

        # self.offsets = None
        # self.init_offsets()

        assets_dict = {
            'id_005_bs_cabb': '货币资金',
            'id_007_bs_sr': '结算备付金',
            'id_008_bs_pwbaofi': '拆出资金',
            'id_009_bs_tfa': '交易性金融资产',
            'id_010_bs_cdfa': '衍生金融资产(流动)',
            'id_012_bs_nr': '应收票据',
            'id_013_bs_ar': '应收账款',
            'id_014_bs_rf': '应收款项融资',
            'id_015_bs_ats': '预付款项',
            'id_016_bs_pr': '应收保费',
            'id_017_bs_rir': '应收分保账款',
            'id_018_bs_crorir': '应收分保合同准备金',
            'id_019_bs_or': '其他应收款',
            'id_022_bs_fahursa': '买入返售金融资产',
            'id_023_bs_i': '存货',
            'id_024_bs_ca': '合同资产',
            'id_025_bs_ahfs': '持有待售资产',
            'id_026_bs_claatc': '发放贷款及垫款(流动)',
            'id_027_bs_pe': '待摊费用',
            'id_028_bs_ncadwioy': '一年内到期的非流动资产',
            'id_029_bs_oca': '其他流动资产',

            'id_035_bs_nclaatc': '发放贷款及垫款(非流动)',
            'id_036_bs_cri': '债权投资',
            'id_037_bs_ocri': '其他债权投资',
            'id_038_bs_ncafsfa': '可供出售金融资产(非流动)',
            'id_039_bs_htmi': '持有至到期投资',
            'id_040_bs_ltar': '长期应收款',
            'id_041_bs_ltei': '长期股权投资',
            'id_042_bs_oeii': '其他权益工具投资',
            'id_043_bs_oncfa': '其他非流动金融资产',
            'id_044_bs_rei': '投资性房地产',
            'id_045_bs_fa': '固定资产',
            'id_048_bs_cip': '在建工程',
            'id_051_bs_pba': '生产性生物资产',
            'id_052_bs_oaga': '油气资产',
            'id_053_bs_pwba': '公益性生物资产',
            'id_054_bs_roua': '使用权资产',
            'id_055_bs_ia': '无形资产',
            'id_056_bs_rade': '开发支出',
            'id_057_bs_gw': '商誉',
            'id_059_bs_ltpe': '长期待摊费用',
            'id_060_bs_dita': '递延所得税资产',
            'id_061_bs_onca': '其他非流动资产',
        }

        equity_dict = {
            'id_068_bs_stl': '短期借款',
            'id_069_bs_bfcb': '向中央银行借款',
            'id_070_bs_pfbaofi': '拆入资金',
            'id_071_bs_dfl': '衍生金融负债',
            'id_072_bs_tfl': '交易性金融负债',
            'id_073_bs_npaap': '应付票据及应付账款',
            'id_074_bs_np': '(其中) 应付票据',
            'id_075_bs_ap': '(其中) 应付账款',
            'id_076_bs_afc': '预收账款',
            'id_077_bs_cl': '合同负债',
            'id_078_bs_fasurpa': '卖出回购金融资产',
            'id_079_bs_dfcab': '吸收存款及同业存放',
            'id_080_bs_stoa': '代理买卖证券款',
            'id_081_bs_ssoa': '代理承销证券款',
            'id_082_bs_sawp': '应付职工薪酬',
            'id_083_bs_tp': '应交税费',
            'id_084_bs_oap': '其他应付款',
            'id_087_bs_facp': '应付手续费及佣金',
            'id_088_bs_rip': '应付分保账款',
            'id_089_bs_lhfs': '持有待售负债',
            'id_090_bs_ncldwioy': '一年内到期的非流动负债',
            'id_091_bs_didwioy': '一年内到期的递延收益',
            'id_092_bs_cal': '预计负债(流动)',
            'id_093_bs_stbp': '短期应付债券',
            'id_094_bs_ocl': '其他流动负债',

            'id_097_bs_icr': '保险合同准备金',
            'id_098_bs_ltl': '长期借款',
            'id_099_bs_bp': '应付债券',
            'id_102_bs_ll': '租赁负债',
            'id_103_bs_ltap': '长期应付款',
            'id_105_bs_ltpoe': '长期应付职工薪酬',
            'id_106_bs_ncal': '预计负债(非流动)',
            'id_107_bs_ltdi': '长期递延收益',
            'id_108_bs_ditl': '递延所得税负债',
            'id_109_bs_oncl': '其他非流动负债',

            'id_112_bs_sc': '股本',
            'id_113_bs_oei': '其他权益工具',
            'id_116_bs_capr': '资本公积',
            'id_118_bs_oci': '其他综合收益',
            'id_119_bs_rr': '专项储备',
            'id_120_bs_surr': '盈余公积',
            'id_121_bs_pogr': '一般风险准备金',
            'id_122_bs_rtp': '未分配利润',
            'id_126_bs_etmsh': '少数股东权益',
        }

        if self.index_name in assets_dict.keys():
            self.data_type = 'assets'
        elif self.index_name in equity_dict.keys():
            self.data_type = 'equity'
        else:
            self.data_type = None

    def format(self, value):
        if value is None:
            return 'None'
        else:
            try:
                return self.format_fun(value)
            except Exception as e:
                print(e)
                return repr(value)

    def set_val_scale(self):
        if self.logarithmic is True:
            self.val_max = 1
            self.val_min = 0
        else:
            self.val_max = self.scale_max
            self.val_min = self.scale_min

        self.val_delta = self.val_max - self.val_min
        self.metrics = list(np.linspace(self.val_min, self.val_max, self.scale_div+1))
        self.metrics = self.metrics[1:-1]

    def format_data_source(self):
        pass
        # if self.ds_type == 'digit':
        #     if self.frequency == 'DAILY':
        #         return
        #
        #     if self.delta_mode is True:
        #         self.df = get_month_delta(df=self.df, new_name=self.index_name)
        #     else:
        #         self.df = get_month_data(df=self.df, new_name=self.index_name)
        #
        #     if self.ma_mode > 1:
        #         # array0 = self.df.iloc[:, 0].values.copy()
        #         #
        #         # first = self.ma_mode - 1
        #         # array1 = array0[first:]
        #         #
        #         # last = 0
        #         # while first:
        #         #     first -= 1
        #         #     last -= 1
        #         #     array1 = array1 + array0[first:last].copy()
        #         #
        #         # array1 = array1 / self.ma_mode
        #         # # print('array1', array1)
        #         # indexes = self.df.index.values[(self.ma_mode - 1):]
        #         #
        #         # self.df = pd.DataFrame(array1, index=indexes, columns=[self.index_name])
        #
        #         # self.df = self.df.rolling(self.ma_mode, min_periods=1).sum()
        #         self.df = self.df.rolling(self.ma_mode, min_periods=1).mean()

    def init_offsets(self):
        if self.frequency == 'DAILY':
            self.offsets = np.zeros(self.df.index.values.shape[0], dtype='int32')
            date0 = self.parent.date_min
            for i, index in enumerate(self.df.index.values):
                date = dt.datetime.strptime(index, "%Y-%m-%d").date()
                offset = (date - date0).days
                self.offsets[i] = offset

    @staticmethod
    def index2date(index):
        return dt.datetime.strptime(index, "%Y-%m-%d").date()

    def map_indexes2date(self):
        return map(self.index2date, self.df.index)
        # date_list = list()
        # for index in self.df.index:
        #     date = dt.datetime.strptime(index, "%Y-%m-%d").date()
        #     date_list.append(date)
        #
        # self.date_list = date_list

    @staticmethod
    def copy(data):
        pass


class DefaultDataSource(DataSource):
    def __init__(self, parent):
        self.parent = parent

        self.default_ds = True

        self.index_name = 'DefaultDataSource'
        self.show_name = 'DefaultDataSource'

        self.df = pd.DataFrame(columns=[self.index_name])

        index = dt.datetime.now().date().strftime("%Y-%m-%d")

        self.data_max = 256 * 1e8
        self.df.loc[index] = [self.data_max]

        self.ds_type = 'digit'
        self.delta_mode = False
        self.ma_mode = 0
        self.frequency = None
        self.pix_show = [False, False, False, False]
        self.info_show = [False, False, False, False]

        self.format_data_source()

        self.color = None
        self.line_thick = None
        self.pen_type = None

        self.units = '亿'
        self.ratio = get_units_dict()[self.units]

        self.scale_max = self.data_max * parent.scale_ratio
        self.scale_min = self.scale_max / 1024

        self.scale_div = 10
        self.logarithmic = True

        self.info_priority = 0

        self.val_max = None
        self.val_min = None
        self.val_delta = None
        self.metrics = None

        self.set_val_scale()

        self.format_fun = lambda x: '%.2f%s' % (x / self.ratio, self.units)

        self.df.columns = [self.index_name]
        self.offsets = None
