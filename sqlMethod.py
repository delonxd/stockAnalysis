import mysql.connector
import json
import time


def insert_values(config, table, data_list):
    print('inserting data:')
    print('    database: %s' % config['database'])
    print('    table: %s' % table)
    print('    influenced row: %s\n' % len(data_list))

    sub_str = list()
    for index, value in enumerate(data_list):
        tmp_str = json.dumps(value, ensure_ascii=False)
        tmp_str = "(%s)" % tmp_str[1:-1]

        sub_str.append(tmp_str)

    column_str = ',\n'.join(sub_str)

    db = mysql.connector.connect(**config)

    cursor = db.cursor()

    instruct = """
    INSERT INTO %s VALUES \n%s;
    """ % (table, column_str)

    cursor.execute(instruct)
    db.commit()
    db.close()

    print('data insertion complete.\n')
    return instruct


def create_table(config, table, head_list):
    print('creating table:')
    print('    database: %s' % config['database'])
    print('    table: %s' % table)
    print('    influenced column: %s\n' % len(head_list))

    sub_str = list()
    for value in head_list:
        tmp_str = ' '.join(value)
        sub_str.append(tmp_str)

    column_str = ',\n'.join(sub_str)
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    instruct = """CREATE TABLE IF NOT EXISTS %s (\n%s\n);""" \
               % (table, column_str)

    cursor.execute(instruct)
    db.commit()
    db.close()

    print('table creation complete.\n')
    return instruct


if __name__ == '__main__':
    sql_config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': 'fs',
    }

    tmpList = [
        ('id', 'INT'),
        ('name', 'VARCHAR(20)'),
    ]

    res = create_table(
        config=sql_config,
        table='test02',
        head_list=tmpList,
    )
    print(res)
