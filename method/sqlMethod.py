import json
import time
import pandas as pd
import numpy as np
from method.mainMethod import transpose_df, show_df


def update_df2sql(cursor, table, df_data, check_field, ini=False):
    df_data.insert(0, "last_update", np.NAN)

    if ini:
        df_data.insert(0, "first_update", np.NAN)
    else:
        df_sql = get_data_frame(cursor, table)
        df_first = df_sql.set_index(check_field, drop=False).loc[:, ['first_update']]
        df_data = pd.concat([df_first, df_data], axis=1, sort=True).reindex(df_data.index)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    new_data = df_data.loc[df_data['first_update'].isnull()]

    df_data.loc[:, 'first_update'].fillna(value=timestamp, inplace=True)
    df_data.loc[:, 'last_update'].fillna(value=timestamp, inplace=True)

    sql_execute_multi(cursor, 'SET autocommit = 0;')
    sql_execute_multi(cursor, 'START TRANSACTION;')

    # DELETE
    date_list = list(df_data[check_field].values)
    if date_list:
        date_str = json.dumps(date_list, ensure_ascii=False)
        date_str = '(%s)' % date_str[1:-1]
        condition = sql_format_condition(check_field, 'in', date_str)
        delete_str = sql_format_delete(table=table, where=condition)

        sql_execute_multi(cursor, delete_str)

    df_data = sql_format_df(df_data)

    for index in range(df_data.shape[0]):
        row_data = list(df_data.iloc[index, :].values)
        insert_str = sql_format_insert(table, values=row_data)

        sql_execute_multi(cursor, insert_str)

    sql_execute_multi(cursor, 'COMMIT;')

    return new_data


def sql_execute_multi(cursor, instruct):
    for _ in cursor.execute(instruct, multi=True):
        pass


def sql_format_df(df):
    for column in list(df.columns):
        if df.dtypes[column] == 'int64':
            df[column] = df[column].astype('float64')

    result = df.where(df.notnull(), None)
    return result


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


# def sql_format_header(header: list):
#     if not isinstance(header, list):
#         raise KeyboardInterrupt('header格式需为列表')
#
#     if len(header) == 0:
#         raise KeyboardInterrupt('header至少拥有一个字段')
#
#     sub_str = list()
#     for item in header:
#         if len(item) != 2:
#             raise KeyboardInterrupt('字段需要两种参数：字段名、字段类型')
#
#         if not isinstance(item[0], str):
#             raise KeyboardInterrupt('字段名需要为字符串类型')
#         else:
#             if item[0].isdigit():
#                 raise KeyboardInterrupt('字段名需要为非数值字符串类型')
#
#         if not isinstance(item[1], str):
#             raise KeyboardInterrupt('字段类型需要为字符串类型')
#
#         tmp_str = ' '.join(item)
#         sub_str.append(tmp_str)
#
#     res_str = ',\n'.join(sub_str)
#
#     return res_str


def sql_format_header_df(header: pd.DataFrame):
    if not isinstance(header, pd.DataFrame):
        raise KeyboardInterrupt('header格式需为DataFrame')

    if len(header.columns) == 0:
        raise KeyboardInterrupt('header至少拥有一个字段')

    df = transpose_df(header)

    sub_str = list()
    for index, row in df.iterrows():
        tmp_str = ' '.join([index, row['sql_type']])
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


def get_data_frame(cursor, table):
    # check_str = sql_format_select(
    #     select='COLUMN_name',
    #     table='information_schema.COLUMNS',
    #     where='table_name = "%s"' % table,
    #     order_by='ordinal_position',
    # )
    check_str = 'SHOW FIELDS FROM %s;' % table
    cursor.execute(check_str)
    res = cursor.fetchall()

    header_sql = [value[0] for value in res]

    select_str = sql_format_select('*', table)
    # cursor.execute(select_str, multi=True)
    cursor.execute(select_str)
    tmp_res = cursor.fetchall()

    df = pd.DataFrame(tmp_res, columns=header_sql)
    return df


def sql_if_table_exists(cursor, table):
    tmp = 'SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = "%s";' % table
    cursor.execute(tmp)
    res = cursor.fetchall()
    if res:
        return True
    else:
        return False


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
