# import json
# import pandas as pd
import numpy as np
from method.fileMethod import *
from functools import wraps
import re


def res2df_fs(res, header_df, prefix='q', postfix='t'):
    index_dict = dict()
    tmp_df = transpose_df(header_df)

    counter = -1
    for index, row in tmp_df.iterrows():
        counter += 1
        sheet = row['sheet_name']
        api = row['api']
        if sheet and api:
            key = '.'.join([sheet, api])
            index_dict[key] = counter
        else:
            index_dict[index] = counter

    columns = header_df.columns
    length = len(columns)

    data_dict = dict()
    for subRes in res:
        sub_list = json.loads(subRes.decode())['data']
        for tmp in sub_list:
            date = tmp['standardDate']

            if date not in data_dict.keys():
                data_dict[date] = [None] * length

            for key, value in tmp.items():
                if key == prefix:
                    for infix in value.keys():
                        sub_dict = value[infix]
                        for subKey, subValue in sub_dict.items():
                            field = '.'.join([infix, subKey])
                            data_dict[date][index_dict[field]] = subValue.get(postfix)
                else:
                    data_dict[date][index_dict[key]] = value

    data_list = list()
    for key, value in data_dict.items():
        data_list.append(value)

    res_df = pd.DataFrame(data_list, columns=columns)
    res_df.set_index('standardDate', drop=False, inplace=True)

    # res_df.replace(to_replace=[None], value=np.NAN, inplace=True)
    return res_df


def res2df_mvs(res, header_df):
    index_dict = dict()
    tmp_df = transpose_df(header_df)

    counter = -1
    for index, row in tmp_df.iterrows():
        counter += 1
        sheet = row['sheet_name']
        api = row['api']
        if sheet and api:
            key = api
            index_dict[key] = counter
        else:
            index_dict[index] = counter

    columns = header_df.columns
    length = len(columns)

    data_dict = dict()

    sub_list = json.loads(res.decode())['data']
    for tmp in sub_list:
        date = tmp['date']

        if date not in data_dict.keys():
            data_dict[date] = [None] * length

        for key, value in tmp.items():
            data_dict[date][index_dict[key]] = value

    data_list = list()
    for key, value in data_dict.items():
        data_list.append(value)

    res_df = pd.DataFrame(data_list, columns=columns)
    res_df.set_index('date', drop=False, inplace=True)

    # res_df.replace(to_replace=[None], value=np.NAN, inplace=True)
    return res_df


def show_type(value):
    print(type(value), '-->', value)


def show_df(df):
    # print(df.columns)
    for tup in df.itertuples():
        print(tup)


def transpose_df(df):
    res = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
    return res


def get_units_dict():
    res = {
        '亿': 1e8,
        '万': 1e4,
        '元': 1,
        '人': 1,
        '百万': 1e6,
        '千': 1e3,
        '百': 1e2,
        '%': 1e-2,
        '倍': 1,
        '年': 1,
    }
    return res


def sift_show_table(sort_by, ascending):
    src = load_pkl("..\\basicData\\dailyUpdate\\latest\\show_table.pkl")

    src['aaa'] = src['market_value_1'] / pd.to_numeric(src['gui_assessment'])

    print(src['aaa'])
    df = src.sort_values(by=sort_by, ascending=ascending)

    ret = df.index.values.tolist()
    print(ret)


def deco_show_stock_name(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        res = func(*args, **kwargs)

        self = args[0]
        self.show_stock_name()
        return res

    return wrapped_function


def discount_to_date(src, rate):
    val = np.log(src) / np.log(rate)
    if not pd.isna(val):
        val_year = int(abs(val))
        val_month = int((abs(val) % 1) * 12)

        str_pre = '-' if val < 0 else ''
        str_year = '%s年' % val_year if val_year != 0 else ''
        str_month = '%s个月' % val_month if val_year == 0 or val_month != 0 else ''
        ret = '%s%s%s' % (str_pre, str_year, str_month)
    else:
        ret = None
    return ret


def try_decorator(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except BaseException as e:
            print(e)
            raise KeyboardInterrupt
    return wrapped_function


def sort_tags(src: list):
    src = src.copy()
    ret1 = []
    ret2 = []
    # tmp = {
    #     'Src': 'Src',
    #     'Toc': 'ToC',
    #     'Mid': 'Mid',
    #     '排除': '排',
    #     '自选': '自选',
    #     '白名单': '白',
    #     '黑名单': '黑',
    #     '灰名单': '灰',
    #     '周期': '周期',
    #     '疫情': '疫',
    #     '忽略': '忽略',
    #     '国有': '国',
    #     '低价': '低',
    #     '新上市': '新上市',
    #     '未上市': '未上市',
    #     '买入': '买入',
    #     '自选202307': None,
    #     '测试20230516': None,
    # }

    tmp = {
        '买入': '买入',
        '关注': '关注',
        '自选': '自选',
        '白名单': '白',
    }

    for key, value in tmp.items():
        if key in src:
            ret1.append(value)
            src.pop(src.index(key))

    tmp = {
        'Src': 'green',
        'Toc': 'green',
        # '买入': 'green',
        # '关注': 'green',
        # '自选': 'green',
        # '白名单': 'green',
        '灰名单': 'yellow',
        '国有': 'yellow',
        '周期': 'yellow',
        '低价': 'yellow',
        'Mid': 'red',
        '排除': 'red',
        '黑名单': 'red',
        '忽略': 'red',
        '疫情': 'red',
        '新上市': 'red',
        '未上市': 'red',
    }

    for key, value in tmp.items():
        if key in src:
            ret2.append([key, value])
            # if value is not None:
            #     ret.append(value)
            src.pop(src.index(key))

    src.sort()
    for value in src:
        # ret.append(value)
        ret2.append([value, 'yellow'])

    return ret1, ret2


def copy_export_ratio():
    import re
    path = "../basicData/self_selected/gui_remark.txt"
    res = load_json_txt(path, log=False)

    # export_ratio = dict()
    remark_dict = dict()
    for code, txt in res.items():
        print(code, txt)
        value = re.search(r'#出口占比(.*)%\n*', txt)
        if value is not None:
            # value = value.group(1)
            # print(code, value)
            # export_ratio[code] = value
            span = value.span()
            txt2 = '%s%s' % (txt[:span[0]], txt[span[1]:])
            print(txt2)
            if txt2 != '':
                remark_dict[code] = txt2
        else:
            remark_dict[code] = txt

    print(remark_dict)
    write_json_txt(path, remark_dict, log=False)

    # print(export_ratio)

    # path = "../basicData/self_selected/gui_export.txt"
    # res = load_json_txt(path, log=False)
    #
    # for code, txt in res.items():
    #     export_ratio[code] = txt
    #     print(code, txt)
    #
    # print(export_ratio)
    # print(len(export_ratio))
    # write_json_txt(path, export_ratio, log=False)


def get_rating_dict():
    ret = {
        100: 'AAA',
        90: 'AA',
        80: 'A',
        70: 'BBB',
        60: 'BB',
        50: 'B',
        40: 'CCC',
        30: 'CC',
        20: 'C',
        10: 'D',
        0: 'E',
    }

    return ret


def credit_rating2value(rating):
    dict0 = get_rating_dict()
    ret = None
    for key, value in dict0.items():
        if rating == value:
            ret = key
            break
    return ret


def value2credit_rating(src, color_flag=False, default=''):
    dict0 = get_rating_dict()
    ret = default
    if src is None:
        src = -1
    else:
        for key, value in dict0.items():
            if src >= key:
                ret = value
                break

    if color_flag:
        if src >= 80:
            color = 'green'
        elif src >= 50:
            color = 'yellow'
        elif src >= 20:
            color = 'red'
        else:
            color = 'gray'
        return ret, color
    else:
        return ret


def predict_year_value(src, year):
    value = src[0]
    rate_list = src[1:]
    counter = 0
    ret = []
    for y in range(1, year):
        if len(rate_list) == 0:
            ret.append(value)
            continue

        if counter >= float(rate_list[0][0]):
            rate_list = rate_list[1:]
            counter = 0

        rate = (rate_list[0][1] / 100) + 1
        value = value * rate
        ret.append(value)
        counter += 1
    ret.insert(0, src[0])
    return ret


def compare_return(cost, ps, arr_dv, rate):
    k = 1 + rate / 10000
    year = arr_dv.size
    arr_rate = np.array(list(map(lambda x: k**x, range(year))))[::-1]

    res = cost * (k ** year) - sum(arr_rate*arr_dv)
    if res > ps:
        return True
    else:
        return False


def predict_return_rate(cost, ps, dv_list):
    arr_dv = np.array(dv_list)
    power = 17
    rate = [-10000, None, 2**power-10000]
    res = [None, None, None]

    for i in range(power):
        rate[1] = rate[0] + 2**(power-i-1)
        for j in range(3):
            if res[j] is None:
                res[j] = compare_return(cost, ps, arr_dv, rate[j])
        if res[1] is True:
            index1 = 0
            index2 = 1
        else:
            index1 = 1
            index2 = 2
        rate = [rate[index1], None, rate[index2]]
        res = [res[index1], None, res[index2]]

    return rate[0] / 10000 + 1


def convert2value(ps_list, dv_list, rate0):

    ps0 = ps_list[0]
    dv_sum = -dv_list[0]
    rate = 1
    ret = []
    for i, ps in enumerate(ps_list):
        dv = dv_list[i]
        val_mk = ps / rate
        dv_sum += dv / rate
        ret.append([val_mk/ps0, dv_sum/ps0, (val_mk+dv_sum)/ps0])
        rate = rate0 * rate
    return ret


def predict_cap_return(pack):

    if pack is None:
        pack = dict()
        pack['market_value'] = 72 * 1e8
        pack['ps_src'] = (240-23) * 1e8
        pack['dv_src'] = 4.58 * 1e8
        pack['during'] = 50
        pack['gui_rate'] = 22
        # pack['gui_predict_data'] = 'ps-(100)[(3, 20), (5, 15), (inf, 10)]'
        # pack['gui_predict_data'] = "ps-(10%ps)[(3, 20), (5, 15), ('inf', 10)]"

    gui_rate = pack.get('gui_rate')
    txt_to_predict_pack(pack, gui_rate2predict_data(gui_rate))

    pack['ps0'] = pack['ps_src']
    pack['dv0'] = pack['dv_src']
    # pack['ps_rate'] = rate_list
    # pack['dv_rate'] = rate_list

    txt = pack.get('gui_predict_data')
    if txt is not None:
        try:
            pack = txt_to_predict_pack(pack, str(txt))
        except BaseException as e:
            print(e)

    mv = pack['market_value']
    during = pack['during'] + 1
    ps = [pack['ps0'], *pack['ps_rate']]
    dv = [pack['dv0'], *pack['dv_rate']]

    ps_list = predict_year_value(ps, during)
    dv_list = predict_year_value(dv, during)

    val_r16 = convert2value(ps_list, dv_list, 1.16)
    val_r18 = convert2value(ps_list, dv_list, 1.18)
    val_r20 = convert2value(ps_list, dv_list, 1.20)

    # dv_sum = dv_calculate(np.array(dv_list), 1.2)

    year_list = list(range(11))
    year_list.extend(list(range(12, 21, 2)))
    year_list.extend([25, 30, 35, 40, 45, 50])
    year_list = year_list[::-1]

    tl = list()
    tl.append("<span style='font-size: 16px;'>")

    tl.append("市值：\t%.2f亿/" % (mv / 1e8))
    tl.append("%.2f%%\n" % (mv / pack['ps0'] * 100))
    tl.append("预测：\t%.2f亿\n" % (pack['ps0'] / 1e8))
    # tl.append("倍率：\t%.2f倍\n" % (pack['ps0'] / mv))
    tl.append("分红：\t%.2f亿\n" % (pack['dv0'] / 1e8))
    tl.append("市值预测： %s\n" % repr(pack['ps_rate']).replace(' ', ''))
    tl.append("分红预测： %s\n" % repr(pack['dv_rate']).replace(' ', ''))

    tl.append("</span>")

    # # tl.append("折现/市值：\t%.2f亿" % (dv_sum / 1e8))
    # # tl.append("/%.2f亿\n" % (mv / 1e8))
    # # tl.append("分红折现比：\t%.2f%%\n" % (dv_sum / mv * 100))
    tl.append("<span style='font-size: 14px;'>")

    tl.append("\n    16mk 16dv 16sm")
    tl.append(" 18mk 18dv 18sm")
    tl.append(" 20mk 20dv 20sm\n")

    anchor = mv / pack['ps0']
    color_flag = True

    # tl.append("<pre style='font-family: Consolas;'>")

    for i in year_list:
        tl.append("%2s " % i)
        tl.append(regular_value_with_color(anchor, val_r16[i][0], False))
        tl.append(regular_value_with_color(anchor, val_r16[i][1], False))
        tl.append(regular_value_with_color(anchor, val_r16[i][2], color_flag))
        tl.append(regular_value_with_color(anchor, val_r18[i][0], False))
        tl.append(regular_value_with_color(anchor, val_r18[i][1], False))
        tl.append(regular_value_with_color(anchor, val_r18[i][2], color_flag))
        tl.append(regular_value_with_color(anchor, val_r20[i][0], False))
        tl.append(regular_value_with_color(anchor, val_r20[i][1], False))
        tl.append(regular_value_with_color(anchor, val_r20[i][0], color_flag) + "\n")
        # break

    tl.append("</span>")

    # for i in range(1, during):
    #     val = predict_return_rate(mv, ps_list[i], dv_list[:i])
    #     ret = "%s%s\t%.2f%%\n" % (ret, i, (val-1)*100)

    if color_flag is True:
        # ret = "<pre>%s</pre>" % ret
        tl.insert(0, "<pre style='font-family: Consolas, monospace;white-space: pre-wrap;'>")
        tl.append("</pre>")

    ret = "".join(tl)

    # print(ret)
    return ret


def regular_value_with_color(anchor, val, color):

    ret = '%4.0f%%' % (val * 100)
    if color is True:
        if val > anchor:
            ret = "<span style='color:green;'>%s</span>" % ret
        else:
            ret = "<span style='color:red;'>%s</span>" % ret

    return ret


def dv_calculate(arr_dv, rate):
    k = 1/rate
    year = arr_dv.size
    arr_rate = np.array(list(map(lambda x: k**x, range(year))))
    ret = sum(arr_rate*arr_dv)
    return ret


def txt_to_predict_pack(pack: dict, src: str):

    src_list = src.split(';')

    for txt in src_list:
        m1 = re.search(r"^(ps|dv)-(\(.*\))?(\[.*])?$", txt)
        if m1 is not None:
            txt1 = m1.group(1)
            txt2 = m1.group(2)
            txt3 = m1.group(3)

            if txt2 is not None:
                txt2 = txt2[1:-1]
                m2 = re.search(r"^(.*)%(ps|dv)$", txt2)
                if m2 is not None:
                    rate = float(m2.group(1))
                    key = "%s_src" % m2.group(2)
                    val = pack[key] * rate / 100
                else:
                    val = float(txt2) * 1e8
                key = '%s0' % txt1
                pack[key] = val

            if txt3 is not None:
                val = eval(txt3)
                key = '%s_rate' % txt1
                pack[key] = val

    return pack


def gui_rate2predict_data(gui_rate):
    gui_rate = int(gui_rate) if gui_rate is not None else 0

    if gui_rate > 25:
        val = [(1, gui_rate), (2, 25), (5, 15), ('inf', 10)]
    elif gui_rate > 15:
        val = [(3, gui_rate), (5, 15), ('inf', 10)]
    elif gui_rate > 10:
        val = [(8, gui_rate), ('inf', 10)]
    else:
        val = [('inf', gui_rate)]

    txt = repr(val)
    txt = txt.replace(' ', '')
    ret = "ps-%s;dv-%s" % (txt, txt)
    return ret


if __name__ == '__main__':
    # sift_show_table('real_pe_return_rate', False)
    # copy_export_ratio()
    predict_cap_return(None)
    pass
