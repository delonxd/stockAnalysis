from method.logMethod import MainLog


def update_latest_data(code_list):
    from request.requestData import request2mysql_daily

    list0 = []
    counter = 0
    for code in code_list:
        if counter == 0:
            list0.append([])
            counter = 100
        list0[-1].append(code)
        counter -= 1

    length = len(list0)
    MainLog.add_split('#')
    MainLog.add_log('total %s groups' % length)
    # print(length)
    # print(list0)

    start = 0
    end = length

    ret = []

    index = start
    while index < end:
        stock_codes = list0[index]

        MainLog.add_split('-')
        MainLog.add_log('group %s/%s' % (index, end))
        MainLog.add_split('-')

        new_data = request2mysql_daily(
            stock_codes=stock_codes,
            date='latest',
            data_type='fs',
        )

        ret.extend(new_data)

        MainLog.add_split('-')
        request2mysql_daily(
            stock_codes=stock_codes,
            date='latest',
            data_type='mvs',
        )
        index += 1

    return ret


def update_all_data(code_list, start_date):
    from request.requestData import request2mysql

    index = 0
    end = len(code_list)

    ret = []

    while index < end:
        code = code_list[index]

        MainLog.add_split('#')
        MainLog.add_log('%s/%s --> %s' % (index, end, code))

        new_data = request2mysql(
            stock_code=code,
            data_type='fs',
            start_date=start_date,
        )

        MainLog.add_split('-')

        request2mysql(
            stock_code=code,
            data_type='mvs',
            start_date=start_date,
        )
        index += 1

        if new_data is not None:
            ret.append(code)

    return ret


def tmp_update():
    from request.requestData import request2mysql
    from request.requestData import request2mysql_daily
    from request.requestEquityData import request_eq2mysql

    # path = "..\\basicData\\dailyUpdate\\latest\\s004_code_latest_update.txt"
    # path = "..\\basicData\\analyzedData\\temp_codes.txt"
    path = "..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code_list = json.loads(f.read())

    request_eq2mysql(code_list)
    # code_list = list(filter(lambda x: x < '100000', code_list))
    # code_list = code_list[:1]
    # code_list = ['000002']
    # code_list.reverse()
    # for code in code_list:
    #     print(code)
    #     # break
    #     request2mysql(
    #         stock_code=code,
    #         data_type='mvs',
    #         # start_date='2015-01-01',
    #         start_date='1970-01-01',
    #         # end_date='2022-01-01',
    #         metrics=['ta'],
    #     )
    #     request2mysql()

    # request2mysql_daily(
    #     stock_codes=code_list,
    #     data_type='mvs',
    #     date='latest',
    #     # metrics=['q.ps.foe_r.t'],
    #     # metrics=['q.bs.ta.t'],
    # )

    # update_all_data(code_list, start_date='2021-01-01')


def update_header():
    from method.sqlMethod import sql_drop_field, sql_add_field
    from request.requestData import get_cursor

    data_type = 'mvs'
    database = 'marketData'
    db, cursor = get_cursor(data_type)

    sql_str = 'SELECT table_name FROM information_schema.TABLES WHERE table_schema = "%s";' % database
    cursor.execute(sql_str)
    tmp_res = cursor.fetchall()

    MainLog.add_log('All table: %s' % tmp_res)

    for index in tmp_res:
        table = index[0]
        field = 'id_048_mvs_ta'
        command = sql_add_field(table, field, 'DOUBLE')
        # print(command)
        cursor.execute(command)
        db.commit()
        MainLog.add_log('Table %s add field %s' % (table, field))


def test_compare():
    from method.dataMethod import load_df_from_mysql
    import numpy as np

    data_type = 'mvs'
    code = '000002'

    df1 = load_df_from_mysql(code, data_type)
    df2 = load_df_from_mysql(code+'_copy1', data_type)

    df1 = df1.drop(['first_update', 'last_update'], axis=1)
    df2 = df2.drop(['first_update', 'last_update'], axis=1)

    for column in df1.columns:
        for index in df1.index:
            try:
                val1 = df1.loc[index, column]
                val2 = df2.loc[index, column]

                if val1 == val2:
                    pass
                elif np.isnan(val1) and np.isnan(val2):
                    pass
                else:
                    print(index, column, val1, val2)

            except:
                continue
    # print(df1.columns)


if __name__ == '__main__':
    import json
    import pandas as pd

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 3)
    pd.set_option('display.width', 10000)

    # mysql_update()
    # mysql_update_daily()
    # update_latest_data2()
    tmp_update()
    # test_compare()

