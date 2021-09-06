from method.mainMethod import *
from method.sqlMethod import *
import pandas as pd


if __name__ == '__main__':

    with open('../basicData/nfCodeList.pkl', 'rb') as pk_f:
        codeList = pickle.load(pk_f)

    # infixList = ['bs', 'ps', 'cfs', 'm']
    infixList = ['bs']
    for infix in infixList:

        config = {
            'user': 'root',
            'password': 'aQLZciNTq4sx',
            'host': 'localhost',
            'port': '3306',
            'database': '%sData' % infix,
        }
        db = mysql.connector.connect(**config)

        for stockCode in codeList[:5]:

            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
            print(stockCode)
            # stockCode = '600008'

            tFile = 'Ns%sText.pkl' % infix.capitalize()
            dataHeader = get_header_fs(root=r'..\basicData', file=tFile)

            tFile = 'FinancialSheet_%s.pkl' % stockCode
            res = read_pkl(root=r'..\bufferData\financialData', file=tFile)

            dataList = format_res(
                res=res,
                prefix='q',
                infix=infix,
                postfix='t',
                head_list=dataHeader,
            )

            iniHeader = [
                ('first_update', 'VARCHAR(50)'),
                ('last_update', 'VARCHAR(50)'),
            ]
            sqlHeader = get_sql_header(dataHeader, iniHeader)

            table = '%s_%s' % (infix, stockCode)

            # # DROP
            # db.cursor().execute('DROP TABLE if EXISTS %s;' % table)
            # db.commit()

            if not sql_check_table_exists(db, table):
                sql_create_table(db, table, sqlHeader)

            header = list(zip(*sqlHeader))[0]

            for data in dataList:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                tmp = [timestamp, timestamp]
                tmp.extend(data)

                df = pd.DataFrame(tmp, index=header)

                sql_update_value(
                    db=db,
                    table=table,
                    df=df,
                    check_field='standardDate',
                    alter=True,
                )

        db.close()
