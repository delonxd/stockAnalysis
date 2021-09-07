import json
import time
import pandas as pd


def sql_update_data_list(cursor, table, data_list, check_field, ini=False):

    prefix = """
        SET autocommit = 0;
        START TRANSACTION;
    """
    postfix = """
        COMMIT;
    """
    infix = ""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    if ini:
        for _ in cursor.execute(prefix, multi=True):
            pass

        for data in data_list:
            row_data = [timestamp, timestamp]
            row_data.extend(data)

            insert_str = sql_format_insert(table, values=row_data)

            for _ in cursor.execute(insert_str, multi=True):
                pass

        for _ in cursor.execute(postfix, multi=True):
            pass

    else:
        check_str = sql_format_select(
            select='COLUMN_name',
            table='information_schema.COLUMNS',
            where='table_name = "%s"' % table,
            order_by='ordinal_position',
        )
        cursor.execute(check_str)
        res = cursor.fetchall()

        header1 = [value[0] for value in res]
        header = header1[2:]
        index = header.index(check_field)

        select_str = sql_format_select('*', table)
        cursor.execute(select_str, multi=True)
        tmp_res = cursor.fetchall()

        df = pd.DataFrame(tmp_res, columns=header1)
        df = df.set_index(check_field, drop=False)

        date_list = list(df[check_field].values)
        date_str = json.dumps(date_list, ensure_ascii=False)
        date_str = '(%s)' % date_str[1:-1]

        for _ in cursor.execute(prefix, multi=True):
            pass

        all_list = list()
        for data in data_list:
            row_data = [timestamp, timestamp]
            row_data.extend(data)

            date = data[index]
            if date in date_list:
                row_data[0] = df.loc[date, 'first_update']

            all_list.append(row_data)

        condition = sql_format_condition(check_field, 'in', date_str)
        delete_str = sql_format_delete(table=table, where=condition)

        for _ in cursor.execute(delete_str, multi=True):
            pass

        for _ in cursor.execute(postfix, multi=True):
            pass

        for _ in cursor.execute(prefix, multi=True):
            pass

        for row_data in all_list:
            insert_str = sql_format_insert(table, values=row_data)

            for _ in cursor.execute(insert_str, multi=True):
                pass

        for _ in cursor.execute(postfix, multi=True):
            pass

            # insert_str = sql_format_insert(table=table, values=row_data)
        #     for _ in cursor.execute(insert_str, multi=True):
        #         pass
        #
        # for _ in cursor.execute(postfix, multi=True):
        #     pass


        # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        # row_data = [tmp_res[0][0], timestamp]
        # row_data.extend(data)
        #
        # delete_str = sql_format_delete(table=table, where=condition)
        # insert_str = sql_format_insert(table=table, values=row_data)
        #
        # infix = ''.join([infix, delete_str, insert_str])
        #


        # instruct = ''.join([prefix, infix, postfix])
        # cursor.execute(instruct, multi=True)


def sql_format_condition(left, sign, right):
    condition = '%s %s %s' % (left, sign, right)
    return condition


def sql_format_insert(table, values):
    data_str = json.dumps(values, ensure_ascii=False)
    data_str = '(%s)' % data_str[1:-1]

    result = """
        INSERT INTO
            %s
        VALUES
            %s;
    """ % (table, data_str)
    return result


def sql_format_delete(table, where=None):

    result = """
        DELETE FROM
            %s
    """ % table

    if where is not None:
        postfix = """
        WHERE
            %s;
    """ % where
        result = ''.join([result, postfix])
    return result


def sql_format_select(select, table, where=None, order_by=None):

    result = """
        SELECT
            %s 
        FROM
            %s
    """ % (select, table)

    if where is not None:
        postfix = """
        WHERE
            %s 
    """ % where
        result = ''.join([result, postfix])

    if order_by is not None:
        postfix = """
        ORDER BY
            %s 
    """ % order_by
        result = ''.join([result, postfix])

    return result


def sql_format_create_table(table, header, if_not_exists=True):
    infix = ''
    if if_not_exists:
        infix = 'IF NOT EXISTS'

    result = """
        CREATE TABLE %s %s (
            %s
        );
    """ % (infix, table, header)

    return result


def sql_format_drop_table(table, if_exists=True):
    infix = ''
    if if_exists:
        infix = 'IF EXISTS'

    result = """
        DROP TABLE %s %s;
    """ % (infix, table, )

    return result


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


def get_sql_header(data_header, ini_header):

    special_header = [
        "stockCode",
        "currency",
        "standardDate",
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
