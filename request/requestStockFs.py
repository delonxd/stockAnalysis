import time
import pickle
import datetime as dt
from method.urlMethod import data_request
from method.mainMethod import value2pkl
from method.updateMethod import buffer2mysql
import json


def request_fs_data(stock_code, metrics_list, start_date):
    flag = True
    while flag is True:
        try:
            # 显示时间戳
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(start_time, ' request url')
            print(start_time, ' stock_code --> %s' % stock_code)
            res_list = list()

            for metrics in metrics_list:
                url = 'https://open.lixinger.com/api/a/company/fs/non_financial'
                api = {
                    "token": "e7a7f2e5-181b-4caa-9142-592ab6787871",
                    "startDate": start_date,
                    "stockCodes": [stock_code],
                    "metricsList": metrics,
                }

                res = data_request(url=url, api_dict=api)
                res_list.append(res)

                time.sleep(0.2)

            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(end_time, ' request finished\n')
            flag = False

            return res_list

        except BaseException as e:
            print(e)
            time.sleep(1)


def dump_fs_data2buffer(res_list, stock_code):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(start_time, ' dump to buffer')

    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    file = 'FinancialSheet_%s_%s' % (stock_code, time_str)
    print(start_time, ' filename --> %s' % file)

    value2pkl(
        root='../bufferData/financialData',
        file_name=file,
        value=res_list,
    )

    print(123)

    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(end_time, ' dump finished\n')


def request_fs_data2mysql(stock_code, metrics_list, start_date, datetime):

    res0 = request_fs_data(stock_code, metrics_list, start_date)
    dump_fs_data2buffer(res0, stock_code)
    buffer2mysql(datetime)


def test_request_fs_data():
    with open('../basicData/list_nf_codes.txt', 'r', encoding='utf-8') as f:
        code_list = json.loads(f.read())

    print(code_list)

    # with open('../basicData/metrics/metrics_fs.txt', 'r', encoding='utf-8') as f:
    #     metrics_list = json.loads(f.read())
    #
    # # index = 305
    # # while index < 306:
    # #     stock_code = code_list[index]
    # #
    # #     request_fs_data2mysql(
    # #         stock_code=stock_code,
    # #         metrics_list=metrics_list,
    # #         start_date="2008-01-01",
    # #         datetime=datetime0,
    # #     )
    # #
    # #     index += 1
    #
    # stock_code = '000002'
    # datetime0 = dt.datetime.now()
    #
    # request_fs_data2mysql(
    #     stock_code=stock_code,
    #     metrics_list=metrics_list,
    #     start_date="2008-01-01",
    #     datetime=datetime0,
    # )


if __name__ == '__main__':
    test_request_fs_data()
