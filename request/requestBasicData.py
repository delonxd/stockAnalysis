import urllib.request
import json
import pickle

from collections import defaultdict


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

    a = request_industry_sample()
    # txt = json.dumps(a, indent=4, ensure_ascii=False)
    # with open("../basicData/industry/code_industry_dict.txt", "w", encoding='utf-8') as f:
    #     f.write(txt)

    print(a)