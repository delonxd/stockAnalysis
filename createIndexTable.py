from indexMethod import *
from sqlMethod import create_table, insert_values


if __name__ == '__main__':
    sheetName = 'bs'
    stockCode = '600004'

    headerList, bsList = res2list(sheetName, stockCode)

    header = list()

    for index, value in enumerate(headerList):
        header.append((index, value[0], value[1], value[2]))

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'fsIndex',
    }

    table = '%sIndex2' % sheetName

    headList = [
        ('id', 'INT'),
        ('header', 'VARCHAR(50)'),
        ('apiName', 'VARCHAR(50)'),
        ('dataType', 'VARCHAR(20)'),
    ]

    res = create_table(
        config=config,
        table=table,
        head_list=headList,
    )
    print(res)

    res = insert_values(
        config=config,
        table=table,
        data_list=header,
    )
    print(res)
