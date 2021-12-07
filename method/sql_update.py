def mysql_update():
    # import sys
    # sys.path.append('D:\\PycharmProjects\\stockAnalysis')
    #
    # import os
    # os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from request.requestData import request_data2mysql
    from method.mainMethod import get_part_codes
    from method.dataMethod import load_df_from_mysql

    import json
    import time
    import datetime as dt

    # with open("..\\basicData\\code_list.txt", "r", encoding="utf-8", errors="ignore") as f:
    with open("..\\basicData\\analyzedData\\sift_code_010.txt", "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    code_list = get_part_codes(code_list)

    length = len(code_list)
    print(length)

    # start = code_list.index('600000')
    start = 280
    end = length
    # end = 3

    today = (dt.datetime.now() - dt.timedelta(hours=16)).date().strftime("%Y-%m-%d") + ' 16:00:00'
    # today = '2021-11-20'

    # start_date = (dt.date.today() - dt.timedelta(days=10)).strftime("%Y-%m-%d")
    start_date = '2021-04-01'

    index = start
    while index < end:
        code = code_list[index]
        print('\n')
        print('############################################################################################')
        print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())))
        print(index, '-->', code)

        df1 = load_df_from_mysql(code, 'fs')
        d0 = '' if df1.shape[0] == 0 else df1.iloc[-1, :]['last_update']

        if d0 < today:
            request_data2mysql(
                stock_code=code_list[index],
                data_type='fs',
                start_date=start_date,
            )

        df2 = load_df_from_mysql(code, 'mvs')
        d0 = '' if df2.shape[0] == 0 else df2.iloc[-1, :]['last_update']
        if d0 < today:
            request_data2mysql(
                stock_code=code_list[index],
                data_type='mvs',
                start_date=start_date,
            )

        index += 1


if __name__ == '__main__':
    import pandas as pd

    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    mysql_update()
