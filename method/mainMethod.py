import pickle
import re
import json


def get_api_names(tables, root):

    api_list = list()
    for table in tables:
        path = '%s/Ns%sText.pkl' % (root, table.capitalize())
        with open(path, 'rb') as pk_f:
            text = pickle.load(pk_f)

        tmp = re.findall(r'\n.* : (.*)', text)

        api_list.extend(tmp)

    return api_list


def config_api_names(infix_list, prefix, postfix):
    res_list = list()
    for infix in infix_list:
        tmp = "%s.%s.%s" % (prefix, infix, postfix)
        res_list.append(tmp)
    return res_list


def split_list(source, length):
    return_list = [[]]
    counter = 0
    for ele in source:
        if counter == length:
            return_list.append([])
            counter = 0
        return_list[-1].append(ele)
        counter += 1
    return return_list


def value2pkl(root, file_name, value):
    path = '%s/%s.pkl' % (root, file_name)
    with open(path, 'wb') as pk_f:
        pickle.dump(value, pk_f)


def read_pkl(root, file_name):
    path = '%s/%s' % (root, file_name)
    with open(path, 'rb') as pk_f:
        res = pickle.load(pk_f)
    return res


def get_header(root, table):
    file_name = 'Ns%sText.pkl' % table.capitalize()
    path = '%s/%s' % (root, file_name)
    with open(path, 'rb') as pk_f:
        res = pickle.load(pk_f)

    head_list = [
        ('代码', 'stockCode', 'VARCHAR(6)'),
        ('货币', 'currency', 'VARCHAR(10)'),
        ('标准日期', 'standardDate', 'VARCHAR(30)'),
        ('报告日期', 'reportDate', 'VARCHAR(30)'),
        ('报告类型', 'reportType', 'VARCHAR(30)'),
        ('日期', 'date', 'VARCHAR(30)'),
    ]

    for rowText in re.findall(r'\n(.*)', res):
        tmp = re.findall(r'(.*):(.*)\.(.*)', rowText)

        if len(tmp) == 0:
            head_list.append((rowText, None, 'VARCHAR(1)'))
        else:
            head_list.append((tmp[0][0], tmp[0][2], 'DOUBLE'))

    return head_list


def format_res(res, table, head_list):

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
                    if table in value.keys():
                        sub_dict = value[table]
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

    return tmp_list
