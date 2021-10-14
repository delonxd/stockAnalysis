from method.mainMethod import *
from method.sqlMethod import *
import mysql.connector
import datetime as dt
import os
import shutil


def get_log(log_file, content):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    new_log = '%s  %s' % (time_str, content)

    print(new_log)

    res_log = '\n'.join([log_file, new_log])

    return res_log


def buffer2mysql(datetime):
    path = '../bufferData/financialData\\'
    list0 = [x for x in os.listdir(path) if os.path.isfile(path + x)]

    file_list = list()
    for file in list0:
        file_path = '\\'.join([path, file])
        t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
        delta = (t0 - datetime).days
        # print(type(delta), delta)
        if delta >= 0:
            file_list.append(file)

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'fsData',
    }

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    timestamp = time.localtime(time.time())

    time0_str = time.strftime("%Y%m%d", timestamp)
    new_dir = '..\\bufferData\\fsData_updated\\fsData_update_%s\\' % time0_str
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    log_str = 'make dir --> %s' % new_dir
    log_file = get_log('log_file:', log_str)

    new_dict = dict()
    for tFile in file_list:

        stock_code = tFile[15:21]

        log_str = 'stock_code --> %s' % stock_code
        log_file = get_log(log_file, log_str)

        log_str = 'read buffer %s' % tFile
        log_file = get_log(log_file, log_str)

        res = read_pkl(root=r'..\bufferData\financialData', file=tFile)

        header_df = get_header_df()
        df = res2df_fs(res=res, header_df=header_df)
        header_str = sql_format_header_df(header_df)

        table = 'fs_%s' % stock_code

        # cursor.execute(sql_format_drop_table(table, if_exists=True))
        # db.commit()

        cursor.execute(sql_format_create_table(table, header_str))
        db.commit()

        df.drop(['first_update', 'last_update'], axis=1, inplace=True)

        # show_df(df)

        new_data = update_df2sql(
            cursor=cursor,
            table=table,
            df_data=df,
            check_field='standardDate',
            # ini=True,
            ini=False,
        )

        if len(new_data.index.tolist()) == 0:
            log_str = 'new data: None'
            log_file = get_log(log_file, log_str)

        else:
            log_str = 'new data:\n%s' % repr(new_data)
            log_file = get_log(log_file, log_str)

            if stock_code in new_dict.keys():
                old_data = new_dict[stock_code]

                tmp = pd.concat([old_data, new_data])
                new_dict[stock_code] = tmp
            else:
                new_dict[stock_code] = new_data

        shutil.move(path + tFile, new_dir)

        log_str = 'move file:\n' + path + tFile + '-->' + new_dir
        log_file = get_log(log_file, log_str)
        log_file = get_log(log_file, '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

    db.close()

    # print('print:')
    # print(log_file)

    file = 'log_update_%s' % time0_str
    log_path = '..\\bufferData\\log_files\\' + file
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_file)

    return new_dict


def buffer2mysql_mvs(datetime):
    path = '../bufferData/marketData\\'
    list0 = [x for x in os.listdir(path) if os.path.isfile(path + x)]

    file_list = list()
    for file in list0:
        file_path = '\\'.join([path, file])
        t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
        delta = (t0 - datetime).days
        # print(type(delta), delta)
        if delta >= 0:
            file_list.append(file)

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'marketData',
    }

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    timestamp = time.localtime(time.time())

    time0_str = time.strftime("%Y%m%d%H%M%S", timestamp)
    new_dir = '..\\bufferData\\marketData_updated\\marketData_update_%s\\' % time0_str
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    log_str = 'make dir --> %s' % new_dir
    log_file = get_log('log_file:', log_str)

    new_dict = dict()
    # for tFile in file_list:
    for i, tFile in enumerate(file_list):
        print(i, '--->')

        stock_code = tFile[12:18]

        log_str = 'stock_code --> %s' % stock_code
        log_file = get_log(log_file, log_str)

        log_str = 'read buffer %s' % tFile
        log_file = get_log(log_file, log_str)

        res = read_pkl(root=r'..\bufferData\marketData', file=tFile)

        header_df = get_header_df_mvs()
        df = res2df_mvs(res=res, header_df=header_df)
        header_str = sql_format_header_df(header_df)

        table = 'mvs_%s' % stock_code

        # cursor.execute(sql_format_drop_table(table, if_exists=True))
        # db.commit()

        cursor.execute(sql_format_create_table(table, header_str))
        db.commit()

        df.drop(['first_update', 'last_update'], axis=1, inplace=True)

        # show_df(df)

        new_data = update_df2sql(
            cursor=cursor,
            table=table,
            df_data=df,
            check_field='date',
            # ini=True,
            ini=False,
        )

        if len(new_data.index.tolist()) == 0:
            log_str = 'new data: None'
            log_file = get_log(log_file, log_str)

        else:
            log_str = 'new data:\n%s' % repr(new_data)
            log_file = get_log(log_file, log_str)

            if stock_code in new_dict.keys():
                old_data = new_dict[stock_code]

                tmp = pd.concat([old_data, new_data])
                new_dict[stock_code] = tmp
            else:
                new_dict[stock_code] = new_data

        shutil.move(path + tFile, new_dir)

        log_str = 'move file:\n' + path + tFile + '-->' + new_dir
        log_file = get_log(log_file, log_str)
        log_file = get_log(log_file, '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

    db.close()

    # print('print:')
    # print(log_file)

    file = 'log_update_%s' % time0_str
    log_path = '..\\bufferData\\log_files_mvs\\' + file
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_file)

    return new_dict


def test_buffer2mysql_mvs():
    datetime0 = dt.datetime(2020, 10, 9, 16, 30, 0)
    buffer2mysql_mvs(datetime0)


if __name__ == '__main__':
    # datetime0 = dt.datetime(2021, 10, 9, 16, 30, 0)
    # buffer2mysql(datetime0)

    test_buffer2mysql_mvs()
