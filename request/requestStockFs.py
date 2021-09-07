import time
from method.urlMethod import *
from method.mainMethod import *


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    tables = ['bs', 'ps', 'cfs', 'm']

    files = [''.join(['Ns', value.capitalize(), 'Text.pkl']) for value in tables]

    subs = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* : (.*)',
    )

    apiAll = config_api_names(
        infix_list=subs,
        prefix='q',
        postfix='t',
    )

    metricsList = split_list(
        source=apiAll,
        length=100,
    )

    index = 400
    while index < 402:
        stockCode = codeList[index]

        try:

            # 显示时间戳
            startTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(startTime)
            print(index, stockCode)

            resList = list()

            for metrics in metricsList:

                url = 'https://open.lixinger.com/api/a/company/fs/non_financial'
                api = {
                    "token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
                    "startDate": "1970-01-01",
                    "stockCodes": [stockCode],
                    "metricsList": metrics,
                }

                res = data_request(url=url, api_dict=api)
                resList.append(res)

                time.sleep(0.2)

            endTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(endTime)

            bufferData = {
                'startTime': startTime,
                'endTime': endTime,
                'resList': resList,
            }

            fileName = 'FinancialSheet_%s' % stockCode
            value2pkl(
                root='../bufferData/financialData',
                file_name=fileName,
                value=bufferData,
            )
            index += 1

        except BaseException as r:
            print(r)
            time.sleep(1)
