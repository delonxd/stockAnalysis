import re
import json
import urllib.request
import pickle
import pandas as pd


def split_list(input_list):
    return_list = [[]]
    counter = 0
    for ele in input_list:
        if counter == 100:
            return_list.append([])
            counter = 0
        return_list[-1].append(ele)
        counter += 1
    return return_list


def get_metrics_list(path_list, q, t):
    all_list = list()
    for path in path_list:
        with open(path, 'rb') as pk_f:
            text_list = pickle.load(pk_f)

        tmp_list = re.findall(r'\n(.*) : (.*)', text_list)
        all_list.extend(tmp_list)

    output = list()
    for ele in all_list:
        str1 = ele[1]
        str2 = "%s.%s.%s" % (q, str1, t)
        output.append(str2)
        # print(str2)
    return output


def load_pkl(text_path, res_list):
    row_list, index_dict = pkl2list(text_path)

    time_list = get_time_list(res_list=res_list)

    header_show = extract_list(time_list, 1)
    index_show = extract_list(row_list, 1)

    df_output = pd.DataFrame(index=index_show, columns=header_show)

    for res in res_list:
        data_list = json.loads(res.decode())['data']
        for columnIndex, dataDict in enumerate(data_list):
            data = dataDict['q']
            # print(columnIndex)
            for key, apiDict in data.items():
                for api, valueDict in apiDict.items():
                    row_index = None
                    value = valueDict.get('t')
                    # if 't' not in valueDict.keys():
                    #     print(key, api)

                    sheet_dict = index_dict.get(key)
                    if sheet_dict is not None:
                        row_index = sheet_dict.get(api)
                    # print(key, api, rowIndex, value)
                    if row_index is not None:
                        # print(columnIndex, rowIndex)
                        df_output[header_show[columnIndex]][row_index] = value

    return df_output, index_show, header_show


def pkl2list(pkl_path):
    with open(pkl_path, 'rb') as pk_f:
        text = pickle.load(pk_f)

    tmp = list()
    row_list = re.findall(r'\n(.*)', text)
    for index, item in enumerate(row_list):
        tmp1 = re.findall(r'(.*):(.*)', item)

        if len(tmp1) == 0:
            tmp.append((index, item, None))
        else:
            tmp.append((index, tmp1[0][0], tmp1[0][1]))

    index_dict = row2index(row_list=tmp)
    return tmp, index_dict


def extract_list(source, index):
    tmp = list()
    for item in source:
        tmp.append(item[index])
    return tmp


def row2index(row_list):
    index_dict = dict()
    for index, name, api in row_list:

        if api is not None:
            key, value = re.findall(r' (.*)\.(.*)', api)[0]
            index_dict.setdefault(key, dict())
            index_dict[key].update({value: index})

    return index_dict


def get_time_list(res_list):

    tmp_dict = json.loads(res_list[0].decode())
    data_list = tmp_dict['data']

    time_list = list()
    for index, item in enumerate(data_list):
        date0 = item['standardDate']
        date_time = re.findall('^(.*)T', date0)[0]
        time_list.append((index, date_time))

    return time_list


def get_name(row_list, api):
    tmp = None
    for item in row_list:
        if item[2] == api:
            tmp = item[1]

    return tmp


def res2list(sheet_name, stock_code):
    head_path = 'pkl/Ns%sText.pkl' % sheet_name.capitalize()
    with open(head_path, 'rb') as pk_f:
        head_text = pickle.load(pk_f)

    file_name = 'FinancialSheet_%s.pkl' % stock_code
    file_path = 'SecurityData/%s' % file_name

    with open(file_path, 'rb') as pk_f:
        res = pickle.load(pk_f)

    head_list = [
        ('代码', 'stockCode', 'VARCHAR(6)'),
        ('货币', 'currency', 'VARCHAR(10)'),
        ('标准日期', 'standardDate', 'VARCHAR(30)'),
        ('报告日期', 'reportDate', 'VARCHAR(30)'),
        ('报告类型', 'reportType', 'VARCHAR(30)'),
        ('日期', 'date', 'VARCHAR(30)'),
    ]

    for rowText in re.findall(r'\n(.*)', head_text):
        tmp = re.findall(r'(.*):(.*)\.(.*)', rowText)

        if len(tmp) == 0:
            head_list.append((rowText, None, 'VARCHAR(1)'))
        else:
            head_list.append((tmp[0][0], tmp[0][2], 'DOUBLE'))

    index_dict = dict()
    for index, item in enumerate(head_list):
        if item[1] in index_dict.keys():
            raise InterruptedError('error')
        if item[1] is not None:
            index_dict[item[1]] = index

    tmp_dict = dict()
    for subRes in res:
        sub_list = json.loads(subRes.decode())['data']
        for tmp in sub_list:
            date = tmp['standardDate']

            if date not in tmp_dict.keys():
                tmp_dict[date] = [None] * len(head_list)

            for key, value in tmp.items():
                if key == 'q':
                    if sheet_name in value.keys():
                        sub_dict = value[sheet_name]
                        for subKey, subValue in sub_dict.items():
                            tmp_dict[date][index_dict[subKey]] = subValue.get('t')
                else:

                    tmp_dict[date][index_dict[key]] = value

    tmp_list = list()
    for key, value in tmp_dict.items():
        tmp_list.append(value)
        # print(key)
        # print(value)

    # header = [value[0] for value in head_list]

    return head_list, tmp_list
