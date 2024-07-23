import urllib.request
import json
import pickle

from collections import defaultdict
from request.requestData import split_metrics
from method.logMethod import log_it, MainLog


def request_basic():
    url = 'https://open.lixinger.com/api/a/company'

    data = {"token": "f819be3a-e030-4ff0-affe-764440759b5c"}

    post_data = json.dumps(data)
    header_dict = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
    res_txt = urllib.request.urlopen(req).read().decode()
    data_list = json.loads(res_txt)['data']

    name_dict = defaultdict(str)
    date_dict = defaultdict(str)
    for data in data_list:
        code = data["stockCode"]
        if "name" in data:
            name = data["name"]
            name_dict[code] = name
        if "ipoDate" in data:
            ipo_date = data["ipoDate"]
            date_dict[code] = ipo_date
        else:
            date_dict[code] = None

    code_list = list(name_dict.keys())

    return code_list, name_dict, date_dict


def request_industry_sample():
    url = 'https://open.lixinger.com/api/a/industry/constituents/cni'

    with open("..\\basicData\\industry\\industry3_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        industry3_list = json.loads(f.read())

    data = dict()
    data["token"] = "f819be3a-e030-4ff0-affe-764440759b5c"

    data["date"] = "latest"
    data["stockCodes"] = industry3_list

    post_data = json.dumps(data)
    header_dict = {'Content-Type': 'application/json'}

    req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
    res_txt = urllib.request.urlopen(req).read().decode()

    data_list = json.loads(res_txt)['data']
    dict0 = defaultdict(str)
    for data in data_list:
        sub_data = data["constituents"]
        industry = data["stockCode"]
        for val in sub_data:
            if not val == {}:
                dict0[val["stockCode"]] = industry

    dict1 = dict()
    for data in data_list:
        sub_data = data["constituents"]
        industry = data["stockCode"]
        tmp = []
        for val in sub_data:
            if not val == {}:
                tmp.append(val["stockCode"])

        dict1[industry] = tmp

    res = json.dumps(dict0, indent=4, ensure_ascii=False)
    with open("../basicData/industry/code_industry_dict.txt", "w", encoding='utf-8') as f:
        f.write(res)

    res = json.dumps(dict1, indent=4, ensure_ascii=False)
    with open("../basicData/industry/industry_code_dict.txt", "w", encoding='utf-8') as f:
        f.write(res)

    return dict0, dict1


def update_basic_data():
    _, name_dict, _ = request_basic()

    txt = json.dumps(name_dict, indent=4, ensure_ascii=False)
    with open("../basicData/code_names_dict.txt", "w", encoding='utf-8') as f:
        f.write(txt)


@log_it(None)
def request_company_profile(stock_codes):
    url = 'https://open.lixinger.com/api/cn/company/profile'

    stock_codes_list = split_metrics(stock_codes, 100)
    data_list = []
    for index, sub_codes in enumerate(stock_codes_list):
        data = dict()
        data["token"] = "f819be3a-e030-4ff0-affe-764440759b5c"
        data["stockCodes"] = sub_codes

        post_data = json.dumps(data)
        header_dict = {'Content-Type': 'application/json'}

        MainLog.add_log('    index --> %s/%s' % (index+1, len(stock_codes_list)))
        MainLog.add_log('    stock_codes --> %s' % sub_codes)

        req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
        res_txt = urllib.request.urlopen(req).read().decode()
        data_list.extend(json.loads(res_txt)['data'])

    res_dict = dict()
    for data in data_list:
        code = data["stockCode"]
        if "actualControllerTypes" in data:
            res_dict[code] = data["actualControllerTypes"]
        else:
            res_dict[code] = []

    type_dict = {
        'natural_person': '私有',
        'collective': '集体',
        'foreign_company': '外资',
        'state_owned': '国有',
    }

    res = dict()
    for code, value in res_dict.items():
        tmp = []
        for key in value:
            tmp.append(type_dict[key])
        txt = '&'.join(tmp)
        res[code] = txt

    return res


if __name__ == '__main__':
    #
    # dict0 = request_basic()
    # res = json.dumps(dict0, indent=4, ensure_ascii=False)
    #
    # # print(res)
    # with open("../basicData/res_basicData.txt", "w", encoding='utf-8') as f:
    #     f.write(res)

    # res = request_basic()
    # print(res[0])
    # print(res[1])
    # update_basic_data()

    # a = request_industry_sample()
    # txt = json.dumps(a, indent=4, ensure_ascii=False)
    # with open("../basicData/industry/code_industry_dict.txt", "w", encoding='utf-8') as f:
    #     f.write(txt)

    # print(a)

    # from method.fileMethod import write_json_txt
    # _, _, ipo_dates = request_basic()
    # write_json_txt('..\\basicData\\ipo_date.txt', ipo_dates)

    from method.fileMethod import load_json_txt, write_json_txt
    code_list = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
    write_json_txt("../basicData/actual_controller.txt", request_company_profile(code_list))
