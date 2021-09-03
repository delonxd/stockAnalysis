from method.mainMethod import *
from method.sqlMethod import *


if __name__ == '__main__':
    # infixList = ['bs', 'ps', 'cfs', 'm']
    infixList = ['bs']
    for infix in infixList:
        stockCode = '600008'

        tFile = 'Ns%sText.pkl' % infix.capitalize()
        dataHeader = get_header(root=r'..\basicData', file=tFile)

        tFile = 'FinancialSheet_%s.pkl' % stockCode
        res = read_pkl(root=r'..\bufferData\financialData', file=tFile)

        dataList = format_res(
            res=res,
            prefix='q',
            infix=infix,
            postfix='t',
            head_list=dataHeader,
        )

        # header = [("id_%s" % index, value[2]) for index, value in enumerate(sql_header)]

        iniHeader = [
            ('first_update', 'VARCHAR(50)'),
            ('last_update', 'VARCHAR(50)'),
        ]
        sqlHeader = get_sql_header(dataHeader, iniHeader)

        print(sqlHeader)
        print(dataHeader)

        config = {
            'user': 'root',
            'password': 'aQLZciNTq4sx',
            'host': 'localhost',
            'port': '3306',
            'database': '%sData' % infix,
        }

        table = '%s_%s' % (infix, stockCode)

        db = mysql.connector.connect(**config)

        # if not sql_check_table_exists(db, table):
        #     sql_create_table(db, table, sqlHeader)
        #
        # for data in dataList:
        #     tmp = [1, 1]
        #     tmp.extend(data)
        #     sql_insert_value(db, table, tuple(tmp))

        for data in dataList:
            tmp = [4, 4]
            tmp.extend(data)

            date = data[2]
            sql_update_value(
                db=db,
                table=table,
                value=tmp,
                sift_field='standardDate',
                sift_key=date,

                )

        db.close()
