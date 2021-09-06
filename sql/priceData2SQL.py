from method.mainMethod import *
from method.sqlMethod import *
import pandas as pd


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    infix = 'price'
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': '%s' % infix,
    }

    db = mysql.connector.connect(**config)

    for stockCode in codeList[0:2]:

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        print(stockCode)
        # stockCode = '600008'

        tFile = '%sText.pkl' % infix.capitalize()
        dataHeader = get_header_price(root=r'..\basicData', file=tFile)

        tFile = 'FundamentalSheet_%s.pkl' % stockCode
        res = read_pkl(root=r'..\bufferData\priceData', file=tFile)

        res1 = json.loads(res.decode())['data']

        # dataHeader = [
        #     ('代码', 'stockCode', 'VARCHAR(6)'),
        #     ('日期', 'date', 'VARCHAR(30)'),
        #     ('股价', 'sp', 'DOUBLE'),
        #     ('市值', 'mc', 'DOUBLE'),
        #     ('PE-TTM', 'pe_ttm', 'DOUBLE'),
        #     ('PB', 'pb', 'DOUBLE'),
        #     ('股东人数', 'shn', 'DOUBLE'),
        # ]

        dataList = format_res_price(res=res, head_list=dataHeader)

        iniHeader = [
            ('first_update', 'VARCHAR(50)'),
            ('last_update', 'VARCHAR(50)'),
        ]
        sqlHeader = get_sql_header(dataHeader, iniHeader)

        print(sqlHeader)

        table = '%s_%s' % (infix, stockCode)

        # DROP
        db.cursor().execute('DROP TABLE if EXISTS %s;' % table)
        db.commit()

        if not sql_check_table_exists(db, table):
            sql_create_table(db, table, sqlHeader)

        header = list(zip(*sqlHeader))[0]

        print(len(dataList))

        data_buffer = list()
        counter = 0
        for data in dataList:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            tmp = [timestamp, timestamp]
            tmp.extend(data)
            data_buffer.append(tmp)
            counter += 1

            if counter == 3000:
                sql_insert_values(db, table, data_buffer)
                counter = 0
                data_buffer = list()

            # df = pd.DataFrame(tmp, index=header)
            #
            # sql_update_value(
            #     db=db,
            #     table=table,
            #     df=df,
            #     check_field='date',
            #     alter=True,
            # )

        sql_insert_values(db, table, data_buffer)
        counter = 0
        data_buffer = list()

    db.close()
