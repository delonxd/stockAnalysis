import time
from method.urlMethod import *
from method.mainMethod import *


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    files = ['priceText.pkl']

    subs = get_api_names(
        files=files,
        root='../basicData',
        regular=r'\n.* :(.*)',
    )

    apiAll = config_api_names(infix_list=subs)

    index = 0
    while index < 1:
        stockCode = codeList[index]

        try:

            # 显示时间戳
            startTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(startTime)
            print(index, stockCode)

            url = 'https://open.lixinger.com/api/a/company/fundamental/non_financial'
            api = {
                "token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
                "startDate": "1970-01-01",
                "stockCodes": [stockCode],
                "metricsList": apiAll,
            }

            res = data_request(url=url, api_dict=api)

            time.sleep(0.2)

            endTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(endTime)

            bufferData = {
                'startTime': startTime,
                'endTime': endTime,
                'res': res,
            }

            fileName = 'StockPrice_%s' % stockCode
            value2pkl(
                root='../bufferData/priceData',
                file_name=fileName,
                value=bufferData,
            )
            index += 1

        except BaseException as r:
            print(r)
            time.sleep(1)
