from indexMethod import *
from sqlMethod import *
import pandas as pd


if __name__ == '__main__':
    nameList = ['bs', 'ps', 'cfs', 'm']
    for sheetName in nameList:
        stockCode = '600007'
        headList, dataList = res2list(sheetName, stockCode)
        header = [("id_%s" % index, value[2]) for index, value in enumerate(headList)]

        database = '%sData' % sheetName
        config = {
            'user': 'root',
            'password': 'aQLZciNTq4sx',
            'host': 'localhost',
            'port': '3306',
            'database': database,
        }

        table = '%s_%s' % (sheetName, stockCode)

        create_table(
            config=config,
            table=table,
            head_list=header,
        )
        # print(res)

        insert_values(
            config=config,
            table=table,
            data_list=dataList,
        )
        # print(res)


