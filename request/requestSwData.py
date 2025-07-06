from request.requestData import try_request, data_request
from method.fileMethod import load_json_txt, write_json_txt
from method.logMethod import MainLog
from method.profileMethod import get_code_profile_df

import json
import urllib.request
from collections import defaultdict


def request_industry_sample():
    url = 'https://open.lixinger.com/api/a/industry/constituents/cni'

    with open("..\\basicData\\industry\\industry3_list.txt", "r", encoding="utf-8", errors="ignore") as f:
        industry3_list = json.loads(f.read())

    data = dict()
    token = load_json_txt("../request/lxr_token.txt", log=False)
    data["token"] = token

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


@try_request(None)
def request_industry_sw_2021(code):
    token = load_json_txt("../request/lxr_token.txt", log=False)

    url = 'https://open.lixinger.com/api/cn/company/industries'

    api_dict = {
        "token": token,
        "stockCode": code,
    }

    res = data_request(url=url, api_dict=api_dict)
    data = res['data']

    ret = None

    for row in data:
        source = row['source']
        code = row['stockCode']

        if code[-2:] == '00':
            continue
        if source == 'sw_2021':
            ret = code
    return ret


@try_request(None)
def request_sw_2021_names():
    token = load_json_txt("../request/lxr_token.txt", log=False)

    url = 'https://open.lixinger.com/api/cn/industry'

    api_dict = {
        "token": token,
        "source": "sw_2021",
    }

    res = data_request(url=url, api_dict=api_dict)
    data = res['data']

    ret = dict()

    for row in data:
        name = row['name']
        code = row['stockCode']

        ret[code] = name

    write_json_txt("..\\basicData\\industry\\sw_2021_name_dict.txt", ret)
    return ret


def update_sw_2021():
    MainLog.add_split('#')

    df = get_code_profile_df()
    df = df[df['area'] == 'cn']

    code_list = df.index.to_list()
    ret = dict()
    for code in code_list:
        MainLog.add_log('request_industry_sw_2021 --> %s' % code)
        res = request_industry_sw_2021(code)
        ret[code] = res

    write_json_txt("..\\basicData\\industry\\sw_2021_dict.txt", ret)

    MainLog.add_log('update_sw_2021 complete')
    MainLog.add_split('#')


if __name__ == '__main__':
    update_sw_2021()
