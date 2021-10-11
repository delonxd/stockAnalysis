import time
import pickle
import datetime as dt
from method.urlMethod import data_request
from method.mainMethod import value2pkl
from method.updateMethod import buffer2mysql_mvs


def request_mvs_data(stock_code, metrics, start_date):
    flag = True
    while flag is True:
        try:
            # 显示时间戳
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(start_time, ' request url')
            print(start_time, ' stock_code --> %s' % stock_code)

            url = 'https://open.lixinger.com/api/a/company/fundamental/non_financial'
            api = {
                "token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
                "startDate": start_date,
                "stockCodes": [stock_code],
                "metricsList": metrics,
            }

            res = data_request(url=url, api_dict=api)
            time.sleep(0.2)

            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(end_time, ' request finished\n')
            flag = False

            return res

        except BaseException as e:
            print(e)
            time.sleep(1)


def dump_mvs_data2buffer(res, stock_code):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(start_time, ' dump to buffer')

    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    file = 'marketSheet_%s_%s' % (stock_code, time_str)
    print(start_time, ' filename --> %s' % file)

    value2pkl(
        root='../bufferData/marketData',
        file_name=file,
        value=res,
    )

    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(end_time, ' dump finished\n')


def request_mvs_data2mysql(stock_code, metrics, start_date, datetime):

    res0 = request_mvs_data(stock_code, metrics, start_date)
    dump_mvs_data2buffer(res0, stock_code)
    buffer2mysql_mvs(datetime)


if __name__ == '__main__':

    # with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
    #     codeList = pickle.load(pk_f)

    with open('../basicData/metricsMvs.pkl', 'rb') as pk_f:
        metrics0 = pickle.load(pk_f)

    datetime0 = dt.datetime(2021, 10, 9, 16, 30, 0)

    # index = 305
    # while index < 306:
    #     stockCode = codeList[index]
    #
    #     request_mvs_data(
    #         stock_code=stockCode,
    #         metrics=metrics0,
    #         start_date="2008-01-01",
    #     )
    #
    #     index += 1

    request_mvs_data2mysql(
        stock_code='000002',
        metrics=metrics0,
        start_date="2017-12-20",
        datetime=datetime0,
    )