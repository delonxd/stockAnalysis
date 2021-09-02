import urllib.request
import json
import pickle
import time
from indexMethod import *

if __name__ == '__main__':

    with open('../SecurityData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    # for item in codeList:
    #     print(item)

    pathList = [
        '../pkl/NsBsText.pkl',
        '../pkl/NsPsText.pkl',
        '../pkl/NsCfsText.pkl',
        '../pkl/NsMText.pkl',
    ]

    MetricsList = get_metrics_list(path_list=pathList, q='q', t='t')
    s_list = split_list(MetricsList)
    # print(s_list)

    allList = list()

    url = 'https://open.lixinger.com/api/a/company/fs/non_financial'
    # stockCode = "000065"
    # codeList = codeList[:2]
    # print(codeList)

    newList = list(enumerate(codeList))

    print(newList)
    for index, stockCode in newList[:10]:
        resList = list()

        for item in s_list:
            data = {"token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
                    "startDate": "1970-01-01",
                    "stockCodes": [stockCode],
                    "metricsList": item,
                    }

            post_data = json.dumps(data)

            # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
            # print(post_data)
            header_dict = {'Content-Type': 'application/json'}

            req = urllib.request.Request(url, data=bytes(post_data, 'gbk'), headers=header_dict)
            res = urllib.request.urlopen(req).read()

            resList.append(res)

            time.sleep(0.2)

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        print(index, stockCode)

        outputPath = '../SecurityData/FinancialSheet_%s.pkl' % stockCode
        with open(outputPath, 'wb') as pk_f:
            pickle.dump(resList, pk_f)
            # print(resList)
            print('')
