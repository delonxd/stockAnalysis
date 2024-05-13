from request.requestData import *
from method.fileMethod import *

import json


@try_request("HTTP Error 500: Internal Server Error")
def request_industry_sw_2021(code):
    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    url = 'https://open.lixinger.com/api/cn/company/industries'

    api = {
        "token": token,
        "stockCode": code,
    }

    res = data_request(url=url, api_dict=api)
    data = json.loads(res.decode())['data']

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
    token = "f819be3a-e030-4ff0-affe-764440759b5c"
    url = 'https://open.lixinger.com/api/cn/industry'

    api = {
        "token": token,
        "source": "sw_2021",
    }

    res = data_request(url=url, api_dict=api)
    data = json.loads(res.decode())['data']

    ret = dict()

    for row in data:
        name = row['name']
        code = row['stockCode']

        ret[code] = name

    write_json_txt("..\\basicData\\industry\\sw_2021_name_dict.txt", ret)
    return ret


def update_sw_2021():
    MainLog.add_split('#')

    code_list = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")

    ret = dict()
    for code in code_list:
        MainLog.add_log('request_industry_sw_2021 --> %s' % code)
        res = request_industry_sw_2021(code)
        ret[code] = res

    write_json_txt("..\\basicData\\industry\\sw_2021_dict.txt", ret)

    MainLog.add_log('update_sw_2021 complete')
    MainLog.add_split('#')


if __name__ == '__main__':
    request_sw_2021_names()
