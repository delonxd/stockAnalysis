import mysql.connector
import os
from request.requestData import get_header_df
from method.sqlMethod import sql_format_create_table
from method.sqlMethod import sql_format_drop_table
from method.sqlMethod import sql_format_header_df


def test_output_sql():
    host = 'localhost'
    port = '3306'
    # database = 'marketData'
    database = 'fsData'

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': host,
        'port': port,
        'database': database,
    }

    db_name = '%s_%s\\%s' % (host, port, database)
    # MainLog.add_log('connect database --> ' + db_name)

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    sql_str = 'SELECT table_name FROM information_schema.TABLES WHERE table_schema = "%s";' % database
    cursor.execute(sql_str)
    tmp_res = cursor.fetchall()

    print(tmp_res)
    # print(type(tmp_res))

    # dir_path = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/mvs_20220126/"
    dir_path = "F:/MysqlUploads/fs_backups_20220126/"

    for index in tmp_res:
        table = index[0]
        print(table)
        file = "%s%s_backups.sql" % (dir_path, table)
        sql_str = 'SELECT * FROM %s INTO OUTFILE "%s";' % (table, file)
        print(sql_str)
        cursor.execute(sql_str)
        db.commit()


def load_data_infile():
    host = 'localhost'
    port = '3306'
    # database = 'marketdata'
    database = 'testdata'

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': host,
        'port': port,
        'database': database,
    }

    db_name = '%s_%s\\%s' % (host, port, database)
    # MainLog.add_log('connect database --> ' + db_name)

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    dir_path = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/mvs_backups/"

    list0 = [x for x in os.listdir(dir_path) if os.path.isfile(dir_path + x)]

    length = len(list0)
    a = list0.index('mvs_600007_backups.sql')

    # print(a)
    index = a
    while index < length:
        file = list0[index]
        header_df = get_header_df('mvs')
        header_str = sql_format_header_df(header_df)

        table = file[:10]
        path = dir_path + file
        print(path, table)

        cursor.execute(sql_format_drop_table(table, if_exists=True))
        db.commit()

        cursor.execute(sql_format_create_table(table, header_str))
        db.commit()

        sql_str = 'LOAD DATA INFILE "%s" INTO TABLE %s;' % (path, table)
        cursor.execute(sql_str)
        db.commit()

        index += 1

        # break


if __name__ == '__main__':
    test_output_sql()
    # load_data_infile()
