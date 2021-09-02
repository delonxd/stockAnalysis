from method.mainMethod import *
from method.sqlMethod import *


if __name__ == '__main__':
    tableList = ['bs', 'ps', 'cfs', 'm']
    for table in tableList:
        stockCode = '600012'

        headerList = get_header(root=r'..\basicData', table=table)

        fileName = 'FinancialSheet_%s.pkl' % stockCode
        res = read_pkl(root=r'..\bufferData', file_name=fileName)

        dataList = format_res(
            res=res,
            table=table,
            head_list=headerList,
        )

        header = [("id_%s" % index, value[2]) for index, value in enumerate(headerList)]

        database = '%sData' % table

        config = {
            'user': 'root',
            'password': 'aQLZciNTq4sx',
            'host': 'localhost',
            'port': '3306',
            'database': database,
        }

        tableName = '%s_%s' % (table, stockCode)

        create_table(
            config=config,
            table=tableName,
            head_list=header,
        )

        insert_values(
            config=config,
            table=tableName,
            data_list=dataList,
        )
