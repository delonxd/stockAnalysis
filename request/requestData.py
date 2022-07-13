
from method.urlMethod import data_request
from method.mainMethod import sift_codes
from method.mainMethod import res2df_fs, res2df_mvs
# from method.mainMethod import get_header_df, get_header_df_mvs

from method.sqlMethod import sql_format_header_df
from method.sqlMethod import sql_format_create_table
from method.sqlMethod import update_df2sql

from method.logMethod import log_it, MainLog

from functools import wraps

import json
import mysql.connector
import os
import shutil
import time
import pickle
import datetime as dt
import pandas as pd


def try_request(time0):
    def logging_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            flag = True
            while flag is True:
                try:
                    res = func(*args, **kwargs)
                    flag = False
                    return res

                except BaseException as e:
                    print(e)
                    time.sleep(1)
        return wrapped_function
    return logging_decorator


@try_request(None)
@log_it(None)
def request_data(stock_code, start_date, data_type):
    MainLog.add_log('    stock_code --> %s' % stock_code)
    MainLog.add_log('    start_date --> %s' % start_date)
    MainLog.add_log('    data_type --> %s' % data_type)
    token = "f819be3a-e030-4ff0-affe-764440759b5c"

    if data_type == 'fs':
        with open('../basicData/metrics/metrics_fs.txt', 'r', encoding='utf-8') as f:
            metrics_list = json.loads(f.read())

        res_list = list()
        for metrics in metrics_list:
            url = 'https://open.lixinger.com/api/a/company/fs/non_financial'
            api = {
                "token": token,
                "startDate": start_date,
                "stockCodes": [stock_code],
                "metricsList": metrics,
            }

            res = data_request(url=url, api_dict=api)
            res_list.append(res)

            time.sleep(0.2)

        return res_list

    elif data_type == 'mvs':
        with open('../basicData/metrics/metrics_mvs.txt', 'r', encoding='utf-8') as f:
            metrics = json.loads(f.read())

        url = 'https://open.lixinger.com/api/a/company/fundamental/non_financial'
        api = {
            "token": token,
            "startDate": start_date,
            "stockCodes": [stock_code],
            "metricsList": metrics,
        }

        res = data_request(url=url, api_dict=api)

        time.sleep(0.2)
        return res


@try_request(None)
@log_it(None)
def request_daily_data(stock_codes, date, data_type):
    MainLog.add_log('    stock_codes --> %s' % stock_codes)
    MainLog.add_log('    date --> %s' % date)
    MainLog.add_log('    data_type --> %s' % data_type)
    token = "f819be3a-e030-4ff0-affe-764440759b5c"

    if data_type == 'fs':
        with open('../basicData/metrics/metrics_fs_latest.txt', 'r', encoding='utf-8') as f:
            metrics_list = json.loads(f.read())

        res_list = list()
        for metrics in metrics_list:
            url = 'https://open.lixinger.com/api/a/company/fs/non_financial'
            api = {
                "token": token,
                "date": date,
                "stockCodes": stock_codes,
                "metricsList": metrics,
            }

            res = data_request(url=url, api_dict=api)
            res_list.append(res)

            time.sleep(0.2)

        return res_list

    elif data_type == 'mvs':
        with open('../basicData/metrics/metrics_mvs.txt', 'r', encoding='utf-8') as f:
            metrics = json.loads(f.read())

        url = 'https://open.lixinger.com/api/a/company/fundamental/non_financial'
        api = {
            "token": token,
            "date": date,
            "stockCodes": stock_codes,
            "metricsList": metrics,
        }

        res = data_request(url=url, api_dict=api)

        time.sleep(0.2)
        return res


@log_it(None)
def dump_res2buffer(res, stock_code, data_type):
    time_str = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

    if data_type == 'fs':
        file = 'fs_data_%s_%s' % (stock_code, time_str)
        path = '..\\bufferData\\buffer\\fs_buffer\\' + file

    elif data_type == 'mvs':
        file = 'mvs_data_%s_%s' % (stock_code, time_str)
        path = '..\\bufferData\\buffer\\mvs_buffer\\' + file

    else:
        return

    MainLog.add_log('    filepath --> %s' % path)
    with open(path, 'wb') as pk_f:
        pickle.dump(res, pk_f)

    return path


def get_cursor(data_type):

    if data_type == 'fs':
        database = 'fsData'
    elif data_type == 'mvs':
        database = 'marketData'
    else:
        return

    host = 'localhost'
    port = '3306'

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': host,
        'port': port,
        'database': database,
    }

    db_name = '%s_%s\\%s' % (host, port, database)
    # MainLog.add_log('connect database --> ' + db_name)

    db = mysql.connector.connect(**config)
    cursor = db.cursor()
    return db, cursor

# def get_files_by_datetime(dir_path, datetime):
#     list0 = [x for x in os.listdir(dir_path) if os.path.isfile(dir_path + x)]
#
#     file_list = list()
#     for file in list0:
#         file_path = '\\'.join([dir_path, file])
#         t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
#         delta = (t0 - datetime).days
#         # print(type(delta), delta)
#         if delta >= 0:
#             file_list.append(file)
#     return file_list
#
# def buffer_files2mysql(datetime):
#     dir_path = '..\\bufferData\\financialData\\'
#     file_list = get_files_by_datetime(dir_path, datetime)
#
#     date_str = dt.date.today().strftime("%Y%m%d")
#     new_dir = '..\\bufferData\\fsData_updated\\fsData_update_%s\\' % date_str
#     if not os.path.exists(new_dir):
#         os.makedirs(new_dir)
#         MainLog.add_log('    make dir --> %s' % new_dir)
#
#     db, cursor = get_cursor('fsData')
#
#     # new_list = list()
#     for file in file_list:
#
#         stock_code = file[15:21]
#         file_path = dir_path + file
#
#         new_data = buffer2mysql(
#             path=file_path,
#             db=db,
#             cursor=cursor,
#             stock_code=stock_code,
#             data_type='fs',
#         )
#
#         # if len(new_data.index) == 0:
#         #     new_list.append((file, new_data))
#
#         MainLog.add_log('move file: ' + file_path + '-->' + new_dir)
#         shutil.move(file_path, new_dir)
#         MainLog.add_log('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
#
#     db.close()


def get_header_df(data_type):
    if data_type == 'fs':
        with open("../basicData/header_df/header_df_fs.txt", "r", encoding='utf-8') as f:
            return pd.read_json(f.read(), orient="columns")

    elif data_type == 'mvs':
        with open("../basicData/header_df/header_df_mvs.txt", "r", encoding='utf-8') as f:
            return pd.read_json(f.read(), orient="columns")


@log_it(None)
def buffer2mysql(path, db, cursor, stock_code, data_type, res=None):

    MainLog.add_log('    read buffer %s' % path)
    MainLog.add_log('    stock_code --> %s' % stock_code)

    if res is None:
        with open(path, 'rb') as pk_f:
            res = pickle.load(pk_f)

    header_df = get_header_df(data_type)

    if data_type == 'fs':
        df = res2df_fs(res=res, header_df=header_df)
        table = 'fs_%s' % stock_code
        check_field = 'standardDate'

    elif data_type == 'mvs':
        df = res2df_mvs(res=res, header_df=header_df)
        table = 'mvs_%s' % stock_code
        check_field = 'date'

    else:
        return

    MainLog.add_log('    table --> %s' % table)

    header_str = sql_format_header_df(header_df)

    # cursor.execute(sql_format_drop_table(table, if_exists=True))
    # db.commit()

    cursor.execute(sql_format_create_table(table, header_str))
    db.commit()

    df.drop(['first_update', 'last_update'], axis=1, inplace=True)

    new_data = update_df2sql(
        cursor=cursor,
        table=table,
        df_data=df,
        check_field=check_field,
        # ini=True,
        ini=False,
    )

    if len(new_data.index) == 0:
        MainLog.add_log('    new data: None')
        return
    else:
        MainLog.add_log('    new data:\n%s' % repr(new_data))

    return new_data


def move_buffer_file(path, data_type):
    date_str = dt.date.today().strftime("%Y%m%d")
    if data_type == 'fs':
        new_dir = '..\\bufferData\\updated\\fs\\date_%s\\' % date_str
    elif data_type == 'mvs':
        new_dir = '..\\bufferData\\updated\\mvs\\date_%s\\' % date_str
    else:
        return

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
        MainLog.add_log('make dir --> %s' % new_dir)

    MainLog.add_log('move file: %s --> %s' % (path, new_dir))
    shutil.move(path, new_dir)


def request_data2mysql(stock_code, data_type, start_date):
    res = request_data(
        stock_code=stock_code,
        start_date=start_date,
        data_type=data_type,
    )

    MainLog.add_split('-')

    path = dump_res2buffer(
        res=res,
        stock_code=stock_code,
        data_type=data_type,
    )

    MainLog.add_split('-')

    db, cursor = get_cursor(data_type)

    new_data = buffer2mysql(
        path=path,
        db=db,
        cursor=cursor,
        stock_code=stock_code,
        data_type=data_type,
    )

    MainLog.add_split('-')

    db.close()
    move_buffer_file(path, data_type)

    return new_data


def request_daily_data2mysql(stock_codes, date, data_type):
    res = request_daily_data(
        stock_codes=stock_codes,
        date=date,
        data_type=data_type,
    )

    dict0 = config_daily_res(
        res=res,
        data_type=data_type,
    )

    ret = []

    counter = 0
    for code, txt in dict0.items():

        MainLog.add_split('-')
        MainLog.add_log('counter --> %s' % counter)
        counter += 1

        # path = dump_res2buffer(
        #     res=txt,
        #     stock_code=code,
        #     data_type=data_type,
        # )

        db, cursor = get_cursor(data_type)

        new_data = buffer2mysql(
            path=None,
            db=db,
            cursor=cursor,
            stock_code=code,
            data_type=data_type,
            res=txt,
        )

        if new_data is not None:
            ret.append(code)

        db.close()
        # move_buffer_file(path, data_type)

    return ret


def config_daily_res(res, data_type):
    dict0 = dict()
    if data_type == 'fs':
        for subRes in res:
            for data in json.loads(subRes.decode())['data']:
                code = data["stockCode"]
                tmp = dict()
                tmp["code"] = 1
                tmp["message"] = "success"
                tmp["data"] = [data.copy()]
                txt = json.dumps(tmp, ensure_ascii=False)
                b_txt = bytes(txt, encoding='utf-8')

                if code in dict0.keys():
                    dict0[code].append(b_txt)
                else:
                    dict0[code] = [b_txt]

    elif data_type == 'mvs':
        for data in json.loads(res.decode())['data']:
            code = data["stockCode"]
            tmp = dict()
            tmp["code"] = 1
            tmp["message"] = "success"
            tmp["data"] = [data.copy()]
            txt = json.dumps(tmp, ensure_ascii=False)
            b_txt = bytes(txt, encoding='utf-8')
            dict0[code] = b_txt
    return dict0


def split_metrics(source, length):
    ret = [[]]
    counter = 0
    for ele in source:
        if counter == length:
            ret.append([])
            counter = 0
        ret[-1].append(ele)
        counter += 1
    return ret


@try_request(None)
@log_it(None)
def request_data_2(stock_codes, data_type, metrics=None, date=None, start_date=None, end_date=None):

    token = "f819be3a-e030-4ff0-affe-764440759b5c"

    if data_type == 'fs':
        url = 'https://open.lixinger.com/api/cn/company/fs/non_financial'
    elif data_type == 'mvs':
        url = 'https://open.lixinger.com/api/cn/company/fundamental/non_financial'
    else:
        raise KeyboardInterrupt('data_type wrong')

    MainLog.add_log('    data_type --> %s' % data_type)

    if date is not None and start_date is None and end_date is None:
        span = False
    elif date is None and start_date is not None:
        span = True
    else:
        raise KeyboardInterrupt('keywords conflict')

    if span is True and len(stock_codes) > 1:
        raise KeyboardInterrupt('stockCodes must contain 1 items')

    if span is True and end_date is None:
        end_date = dt.date.today().strftime("%Y-%m-%d")

    if metrics is None:
        path = '../basicData/header_df/header_df_%s.txt' % data_type
        # path = '../basicData/metrics/metricsList_%s.txt' % data_type
        with open(path, 'r', encoding='utf-8') as f:
            header_df = json.loads(f.read())

        metrics = []

        for val in header_df.values():
            sheet = val['sheet_name']
            api = val['api']
            if sheet and api:
                if data_type == 'fs':
                    metrics.append('.'.join(['q', sheet, api, 't']))
                else:
                    metrics.append(api)

    else:
        MainLog.add_log('    metrics --> %s' % metrics)

    MainLog.add_log('    stock_codes --> %s' % stock_codes)

    ret = list()
    if span is False:
        MainLog.add_log('    date --> %s' % date)

        metrics_list = split_metrics(metrics, 48)

        for metrics in metrics_list:
            api = {
                "token": token,
                "date": date,
                "stockCodes": stock_codes,
                "metricsList": metrics,
            }

            res = data_request(url=url, api_dict=api)
            ret.append(res)
            time.sleep(0.2)
    else:
        metrics_list = split_metrics(metrics, 100)
        start_dt = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = dt.datetime.strptime(end_date, "%Y-%m-%d").date()

        start = dt.date(end_dt.year - 9, 1, 1)
        end = end_dt

        while True:
            if start < start_dt:
                start = start_dt

            sub_start = start.strftime("%Y-%m-%d")
            sub_end = end.strftime("%Y-%m-%d")
            MainLog.add_log('    date --> %s >> %s' % (sub_start, sub_end))

            for metrics in metrics_list:
                api = {
                    "token": token,
                    "startDate": sub_start,
                    "endDate": sub_end,
                    "stockCodes": stock_codes,
                    "metricsList": metrics,
                }

                res = data_request(url=url, api_dict=api)
                if len(json.loads(res.decode())['data']) == 0:
                    start = start_dt
                    break

                ret.append(res)
                time.sleep(0.2)

            if start == start_dt:
                break
            else:
                start = dt.date(start.year - 10, 1, 1)
                end = dt.date(start.year + 9, 12, 31)

    return ret


def regular_res(res):
    ret = dict()
    for subRes in res:
        for data in json.loads(subRes.decode())['data']:
            code = data["stockCode"]
            tmp = dict()
            tmp["code"] = 1
            tmp["message"] = "success"
            tmp["data"] = [data.copy()]
            txt = json.dumps(tmp, ensure_ascii=False)
            b_txt = bytes(txt, encoding='utf-8')

            if code in ret.keys():
                ret[code].append(b_txt)
            else:
                ret[code] = [b_txt]
    return ret


def request2mysql(stock_code, data_type, start_date, metrics=None, end_date=None):
    res = request_data_2(
        stock_codes=[stock_code],
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
    )

    res = regular_res(res)
    MainLog.add_split('-')

    new_data = res2mysql(
        res=res.get(stock_code),
        stock_code=stock_code,
        data_type=data_type,
    )

    return new_data


def request2mysql_daily(stock_codes, data_type, date, metrics=None):
    res = request_data_2(
        stock_codes=stock_codes,
        data_type=data_type,
        date=date,
        metrics=metrics,
    )
    res = regular_res(res)
    MainLog.add_split('-')

    ret = []
    counter = 0
    for code, txt in res.items():

        MainLog.add_split('-')
        MainLog.add_log('counter --> %s' % counter)
        counter += 1

        new_data = res2mysql(
            res=txt,
            stock_code=code,
            data_type=data_type,
        )

        if new_data is not None:
            ret.append(code)

    return ret


@log_it(None)
def res2mysql(res, stock_code, data_type):
    if data_type not in ['fs', 'mvs']:
        raise KeyboardInterrupt('data type wrong')

    # MainLog.add_log('    read buffer %s' % path)
    # MainLog.add_log('    stock_code --> %s' % stock_code)

    db, cursor = get_cursor(data_type)

    df, check_field, header_df = res2df(res, data_type)

    table = '%s_%s' % (data_type, stock_code)

    MainLog.add_log('    table --> %s' % table)

    header_str = sql_format_header_df(header_df)

    # cursor.execute(sql_format_drop_table(table, if_exists=True))
    # db.commit()

    cursor.execute(sql_format_create_table(table, header_str))
    db.commit()

    new_data = update_df2sql(
        cursor=cursor,
        table=table,
        df_data=df,
        check_field=check_field,
        # ini=True,
        ini=False,
    )

    if len(new_data.index) == 0:
        MainLog.add_log('    new data: None')
        return
    else:
        MainLog.add_log('    new data:\n%s' % repr(new_data))

    db.close()

    return new_data


def res2df(res, data_type):
    if res is None:
        res = []

    header_df = get_header_df(data_type)

    columns = list()
    for column in header_df.columns:
        api = header_df.loc['api', column]
        sheet = header_df.loc['sheet_name', column]
        if sheet and api:
            if data_type == 'fs':
                columns.append('_'.join([sheet, api]))
            else:
                columns.append(api)
        else:
            columns.append(column)

    data_dict = dict()

    if data_type == 'fs':
        check = 'standardDate'
    else:
        check = 'date'

    for subRes in res:
        sub_list = json.loads(subRes.decode())['data']
        for tmp in sub_list:
            date = tmp[check]
            if date not in data_dict.keys():
                data_dict[date] = dict()

            if data_type == 'fs':
                for key, value in tmp.items():
                    if key == 'q':
                        for infix in value.keys():
                            sub_dict = value[infix]
                            for subKey, subValue in sub_dict.items():
                                field = '_'.join([infix, subKey])
                                data_dict[date][field] = subValue.get('t')
                    else:
                        data_dict[date][key] = value
            else:
                for key, value in tmp.items():
                    data_dict[date][key] = value

    res_df = pd.DataFrame.from_dict(data_dict, orient='index')
    res_df = res_df.reindex(columns=columns)
    res_df.columns = header_df.columns
    res_df.set_index(check, drop=False, inplace=True)
    res_df.dropna(axis=1, how='all', inplace=True)

    return res_df, check, header_df


if __name__ == '__main__':
    pass
