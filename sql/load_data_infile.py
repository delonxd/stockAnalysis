
def output_database(database, target_dir):
    import mysql.connector
    import time
    import os
    import shutil

    date = time.strftime("%Y%m%d", time.localtime(time.time()))
    dir_path = '%s/%s_backups_%s' % (target_dir, database, date)

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    host = 'localhost'
    port = '3306'

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': host,
        'port': port,
        'database': database,
    }

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    sql_str = 'SELECT table_name FROM information_schema.TABLES WHERE table_schema = "%s";' % database
    cursor.execute(sql_str)
    tmp_res = cursor.fetchall()

    print('All table: ', tmp_res)

    for index in tmp_res:
        table = index[0]
        file = "%s/%s_backups.sql" % (dir_path, table)
        sql_str = 'SELECT * FROM %s INTO OUTFILE "%s";' % (table, file)
        print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())), sql_str)
        cursor.execute(sql_str)
        db.commit()


def input_database(dir_path, database):
    import mysql.connector
    import time
    import os
    from request.requestData import get_header_df
    from method.sqlMethod import sql_format_create_table
    from method.sqlMethod import sql_format_drop_table
    from method.sqlMethod import sql_format_header_df

    host = 'localhost'
    port = '3306'

    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': host,
        'port': port,
        'database': database,
    }

    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    file_list = [x for x in os.listdir(dir_path) if os.path.isfile(dir_path + x)]
    length = len(file_list)

    index = 0
    while index < length:
        file = file_list[index]
        tmp = file.split('_')
        table = '%s_%s' % (tmp[0], tmp[1])

        header_df = get_header_df(tmp[0])
        header_str = sql_format_header_df(header_df)

        path = dir_path + file
        print(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime(time.time())), path, table)

        cursor.execute(sql_format_drop_table(table, if_exists=True))
        db.commit()

        cursor.execute(sql_format_create_table(table, header_str))
        db.commit()

        sql_str = 'LOAD DATA INFILE "%s" INTO TABLE %s;' % (path, table)
        cursor.execute(sql_str)
        db.commit()

        index += 1


def output_databases():
    # target_dir = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads"
    target_dir = "F:/MysqlUploads"

    output_database('fsData', target_dir)
    output_database('marketData', target_dir)


def input_databases():
    src_dir = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads"
    # src_dir = "F:/MysqlUploads"

    dir_path = src_dir + '/fsData_backups_20220401/'
    input_database(dir_path, 'testData')

    dir_path = src_dir + '/marketData_backups_20220401/'
    input_database(dir_path, 'testData')


if __name__ == '__main__':
    output_databases()
    # input_databases()
