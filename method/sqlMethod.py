import mysql.connector
import json
import time
import pandas as pd


# def insert_values(config, table, data_list):
#     print('inserting data:')
#     print('    database: %s' % config['database'])
#     print('    table: %s' % table)
#     print('    influenced row: %s\n' % len(data_list))
#
#     sub_str = list()
#     for index, value in enumerate(data_list):
#         tmp_str = json.dumps(value, ensure_ascii=False)
#         tmp_str = "(%s)" % tmp_str[1:-1]
#
#         sub_str.append(tmp_str)
#
#     column_str = ',\n'.join(sub_str)
#
#     db = mysql.connector.connect(**config)
#
#     cursor = db.cursor()
#
#     instruct = """
#     INSERT INTO %s VALUES \n%s;
#     """ % (table, column_str)
#
#     cursor.execute(instruct)
#     db.commit()
#     db.close()
#
#     print('data insertion complete.\n')
#     return instruct
#
#
# def create_table(config, table, head_list):
#     print('creating table:')
#     print('    database: %s' % config['database'])
#     print('    table: %s' % table)
#     print('    influenced column: %s\n' % len(head_list))
#
#     sub_str = list()
#     for value in head_list:
#         tmp_str = ' '.join(value)
#         sub_str.append(tmp_str)
#
#     column_str = ',\n'.join(sub_str)
#     db = mysql.connector.connect(**config)
#     cursor = db.cursor()
#
#     instruct = """CREATE TABLE IF NOT EXISTS %s (\n%s\n);""" \
#                % (table, column_str)
#
#     cursor.execute(instruct)
#     db.commit()
#     db.close()
#
#     print('table creation complete.\n')
#     return instruct


def sql_condition(left, sign, right):
    condition = '%s %s %s' % (left, sign, right)
    return condition


def sql_select(db, select: str, table, where=None):
    cursor = db.cursor()

    if where is None:
        where = '1 = 1'

    tmp_str = """
        SELECT
            %s 
        FROM
            %s
        WHERE %s;
    """ % (select, table, where)

    cursor.execute(tmp_str)
    result = cursor.fetchall()

    return result


def sql_insert_values(db, table, values):
    cursor = db.cursor()

    sub_str = list()
    for value in values:
        tmp_str = json.dumps(value, ensure_ascii=False)
        tmp_str = "(%s)" % tmp_str[1:-1]

        sub_str.append(tmp_str)

    column_str = ',\n'.join(sub_str)

    tmp_str = """
        INSERT INTO
            %s
        VALUES
            %s;
    """ % (table, column_str)

    cursor.execute(tmp_str)
    db.commit()
    time.sleep(1)

    return tmp_str


def sql_insert_value(db, table, value):
    cursor = db.cursor()

    data = json.dumps(value, ensure_ascii=False)

    data = '(%s)' % data[1:-1]
    tmp_str = """
        INSERT INTO
            %s
        VALUES
            %s;
    """ % (table, data)

    cursor.execute(tmp_str)
    db.commit()

    return tmp_str


def sql_update_value(db, table, df, check_field, alter=True):

    if alter:
        condition = sql_condition(check_field, '=', '"%s"' % df.loc[check_field][0])
        tmp_res = sql_select(db, '*', table, where=condition)

        if tmp_res:
            df_res = pd.DataFrame(tmp_res[0], index=df.index)
            df.loc['first_update'][0] = df_res.loc['first_update'][0]

            cursor = db.cursor()

            data = json.dumps(list(df[0]), ensure_ascii=False)

            data = '(%s)' % data[1:-1]
            insert_str = """
                INSERT INTO
                    %s
                VALUES
                    %s;
            """ % (table, data)

            delete_str = """
                DELETE FROM
                    %s
                WHERE
                    %s;
            """ % (table, condition)

            tmp_str = delete_str + insert_str

            for _ in cursor.execute(tmp_str, multi=True):
                pass

            db.commit()

        else:
            value = list(df[0])
            sql_insert_value(db, table, value)

    else:
        value = list(df[0])
        sql_insert_value(db, table, value)


def sql_format_header(header: list):
    if not isinstance(header, list):
        raise KeyboardInterrupt('header格式需为列表')

    if len(header) == 0:
        raise KeyboardInterrupt('header至少拥有一个字段')

    sub_str = list()
    for item in header:
        if len(item) != 2:
            raise KeyboardInterrupt('字段需要两种参数：字段名、字段类型')

        if not isinstance(item[0], str):
            raise KeyboardInterrupt('字段名需要为字符串类型')
        else:
            if item[0].isdigit():
                raise KeyboardInterrupt('字段名需要为非数值字符串类型')

        if not isinstance(item[1], str):
            raise KeyboardInterrupt('字段类型需要为字符串类型')

        tmp_str = ' '.join(item)
        sub_str.append(tmp_str)

    res_str = ',\n'.join(sub_str)

    return res_str


def sql_create_table(db, table, header):

    if sql_check_table_exists(db, table):
        raise KeyboardInterrupt('table已存在')

    cursor = db.cursor()

    header_str = sql_format_header(header)
    instruct = """
        CREATE TABLE %s (
            %s
        );
        """ % (table, header_str)

    cursor.execute(instruct)
    db.commit()


def sql_check_table_exists(db, table):
    cursor = db.cursor()
    instruct = """
        SELECT 
            * 
        FROM 
            information_schema.TABLES 
        WHERE 
            table_name = '%s';
    """ % table

    cursor.execute(instruct)

    if not cursor.fetchall():
        return False
    else:
        return True


def get_sql_header(data_header, ini_header):

    special_header = [
        "stockCode",
        "currency",
        "standardDate" ,
        "reportDate",
        "reportType",
        "date"
     ]

    sql_header = ini_header
    for index, item in enumerate(data_header):
        if item[1] in special_header:
            tmp = (item[1], item[2])
        else:
            tmp = ('id_%s' % index, item[2])

        sql_header.append(tmp)

    return sql_header


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

