# from method.mainMethod import *
# from method.sqlMethod import *
# import mysql.connector


if __name__ == '__main__':
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'bsdata',
    }
    db = mysql.connector.connect(**config)

    cursor = db.cursor()
    df = get_data_frame(cursor=cursor, table='bs_600008')

    df_first = df.set_index('standardDate', drop=False).loc[:, ['first_update']]

    tuple1 = tuple(df.columns.values.tolist()[2:])
    print(tuple1)

    infix = 'bs'
    tFile = 'Ns%sText.pkl' % infix.capitalize()
    dataHeader = get_header_fs(root=r'..\basicData', file=tFile)

    zip_list = list(zip(*dataHeader))
    zip_list.insert(0, tuple1)
    print(zip_list)

    res = list(zip(zip_list[0], zip_list[1], zip_list[2], zip_list[3]))
    print(res)

    str1 = ''
    for row in res:
        tmp = '%s: %s , %s , bs.%s' % (row[1], row[0], row[3], row[2])
        str1 = '\n'.join([str1, tmp])

    print(str1)
    with open("bs_table.txt", "w", encoding="utf-8") as f:
        f.write(str1)


