from method.mainMethod import *
from method.sqlMethod import *
import mysql.connector


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
            'database': 'fsData',
        }

        db = mysql.connector.connect(**config)
        cursor = db.cursor()

        e_list = list(enumerate(codeList))
        for i, stockCode in e_list[4114:]:
            # for stockCode in ['600008']:

            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
            print(i, '-->', stockCode)

            tFile = 'FinancialSheet_%s.pkl' % stockCode
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

            update_df2sql(
                cursor=cursor,
                table=table,
                df_data=df,
                check_field='standardDate',
                ini=True,
                # ini=False,
            )

        db.close()
