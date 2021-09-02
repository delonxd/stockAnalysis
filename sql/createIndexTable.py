from method.mainMethod import *
from method.sqlMethod import create_table, insert_values


if __name__ == '__main__':
    table = 'bs'
    stockCode = '600006'

    headerList = get_header(root=r'..\basicData', table=table)

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

    tableName = '%sIndex4' % table

    headList = [
        ('id', 'INT'),
        ('header', 'VARCHAR(50)'),
        ('apiName', 'VARCHAR(50)'),
        ('dataType', 'VARCHAR(20)'),
    ]

    create_table(
        config=config,
        table=tableName,
        head_list=headList,
    )

    insert_values(
        config=config,
        table=tableName,
        data_list=header,
    )

