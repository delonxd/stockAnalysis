from method.mainMethod import *
from method.sqlMethod import *
import mysql.connector
import datetime as dt
import os


if __name__ == '__main__':

    path = '..\\bufferData\\FinancialData\\'
    list0 = [x for x in os.listdir(path) if os.path.isfile(path + x)]
    date0 = dt.datetime(2021, 10, 9, 16, 30, 0)

    file_list = list()
    for file in list0:
        file_path = '/'.join([path, file])
        t0 = dt.datetime.fromtimestamp(os.path.getctime(file_path))
        delta = (t0 - date0).days
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

    new_dict = dict()

    for tFile in file_list:

        stockCode = tFile[15:21]

        print(type(stockCode), stockCode)

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        # print(i, '-->', stockCode)

        # tFile = 'FinancialSheet_%s.pkl' % stockCode
        res = read_pkl(root=r'..\bufferData\financialData', file=tFile)

        header_df = get_header_df()
        df = res2df_fs(res=res, header_df=header_df)

        headerStr = sql_format_header_df(header_df)
        # print(headerStr)

        table = 'fs_%s' % stockCode

        # cursor.execute(sql_format_drop_table(table, if_exists=True))
        # db.commit()

        cursor.execute(sql_format_create_table(table, headerStr))
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

    db.close()
