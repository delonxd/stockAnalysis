from method.mainMethod import *
from method.sqlMethod import *
import mysql.connector
import pandas as pd


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'priceData',
    }
    db = mysql.connector.connect(**config)

    cursor = db.cursor()

    # for stockCode in codeList[:5]:
    for stockCode in ['600008']:

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        print('start update...')
        print('stockCode: %s' % stockCode)

        tFile = 'priceText.pkl'
        dataHeader = get_header_price(root=r'..\basicData', file=tFile)

        tFile = 'StockPrice_%s.pkl' % stockCode
        res = read_pkl(root=r'..\bufferData\priceData', file=tFile)

        dataList = format_res_price(
            res=res['res'],
            head_list=dataHeader,
        )

        iniHeader = [
            ('first_update', 'VARCHAR(50)'),
            ('last_update', 'VARCHAR(50)'),
        ]

        headerList = get_sql_header(dataHeader, iniHeader)
        headerStr = sql_format_header(headerList)

        columns = list(zip(*headerList))[0]
        primaryKey = 'date'

        df = pd.DataFrame(dataList, columns=columns[2:])
        df.set_index('date', drop=False, inplace=True)

        print('affected rows: %s' % df.shape[0])

        table = 'pr_%s' % stockCode

        # cursor.execute(sql_format_drop_table(table, if_exists=True))
        # db.commit()

        cursor.execute(sql_format_create_table(table, headerStr))
        db.commit()

        sql_update_data_list(
            cursor=cursor,
            table=table,
            df_data=df,
            check_field='date',
            ini=False,
        )

        db.close()

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        print('update complete.\n')
