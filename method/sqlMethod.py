import json
import time
import pandas as pd
import numpy as np
from method.mainMethod import transpose_df
from method.logMethod import MainLog, log_it
from method.fileMethod import load_json_txt
import mysql.connector


def update_df2sql(cursor, table, df_data, check_field, ini=False):
    df_data.insert(0, "last_update", np.NAN)

    if ini:
        df_data.insert(0, "first_update", np.NAN)
        df_sql = pd.DataFrame()
    else:
        df_sql = get_data_frame(cursor, table)
        df_sql = df_sql.set_index(check_field, drop=False)
        df_org = df_sql.drop(df_data.columns, axis=1)

        df_data = pd.concat([df_org, df_data], axis=1, sort=True).reindex(df_data.index)
        df_data = df_data.reindex(df_sql.columns, axis=1)

        # df_sql = get_data_frame(cursor, table)
        # df_first = df_sql.set_index(check_field, drop=False).loc[:, ['first_update']]
        # df_data = pd.concat([df_first, df_data], axis=1, sort=True).reindex(df_data.index)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    # print(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    new_index = []

    changed = set()
    for index in df_data.index:
        if index not in df_sql.index:
            # print(index)
            new_index.append(index)
            continue

        flag = False
        for column in df_data.columns:
            if column in ['first_update', 'last_update']:
                continue
            val1 = df_data.loc[index, column]
            val2 = df_sql.loc[index, column]

            if val1 == val2:
                pass
            elif pd.isna(val1) and pd.isna(val2):
                pass
            else:
                changed.add(column)
                # print(index, column)
                flag = True
                # break
        if flag is True:
            new_index.append(index)

    changed = list(changed)
    changed.sort()

    MainLog.add_log('    changed columns --> %s' % changed)

    # print(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    new_data = df_data.loc[new_index, :]
    df_data = new_data.copy()

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


def get_sql_indicator(df, database):
    if database == 'fsData':
        check_field = 'standardDate'
        field_ascending = True

        path = "../basicData/sqlFieldType/sql_field_type_fs_cn_org.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = []

        for key in type_dict.keys():
            if key[:3] != 'id_':
                pre_fields.append(key)

    elif database == 'fsData_cn_bank':
        check_field = 'standardDate'
        field_ascending = True

        path = "../basicData/sqlFieldType/sql_field_type_fs_cn_bank.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = list(type_dict.keys())

        for key in df.columns:
            if key not in type_dict.keys():
                type_dict[key] = 'DOUBLE'

    elif database == 'fsData_hk':
        check_field = 'STD_REPORT_DATE'
        field_ascending = True

        path = "../basicData/sqlFieldType/sql_field_type_hk.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = list(type_dict.keys())

        for key in df.columns:
            if key not in type_dict.keys():
                type_dict[key] = 'DOUBLE'

    elif database == 'marketData':
        check_field = 'date'
        field_ascending = True

        path = "../basicData/sqlFieldType/sql_field_type_mvs_cn_org.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = []

        for key in type_dict.keys():
            if key[:3] != 'id_':
                pre_fields.append(key)

    elif database == 'dvData':
        check_field = 'id'
        field_ascending = False

        path = "../basicData/sqlFieldType/sql_field_type_dv_cn.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = list(type_dict.keys())

    elif database == 'eqData':
        check_field = 'date'
        field_ascending = False

        path = "../basicData/sqlFieldType/sql_field_type_eq_cn.txt"
        type_dict = load_json_txt(path, log=False)
        pre_fields = list(type_dict.keys())

    # elif database == 'test20250521':
    #     check_field = 'standardDate'
    #     field_ascending = True
    #     type_dict = {
    #         'first_update': "VARCHAR(30)",
    #         'last_update': "VARCHAR(30)",
    #         'stockCode': "VARCHAR(10)",
    #         'currency': "VARCHAR(10)",
    #         'standardDate': "VARCHAR(30) PRIMARY KEY",
    #         'reportDate': "VARCHAR(30)",
    #         'reportType': "VARCHAR(30)",
    #     }
    #     pre_fields = list(type_dict.keys())
    #     for key in df.columns:
    #         if key not in type_dict.keys():
    #             type_dict[key] = 'DOUBLE'

    else:
        raise KeyboardInterrupt('database错误')

    return [check_field, field_ascending, pre_fields, type_dict]


@log_it(None)
def df2mysql(df, database, table, ini=False):

    # 根据database获取check_field 还有数据起始列pre_fields 是否排序
    indicator = get_sql_indicator(df, database)
    check_field = indicator[0]
    field_ascending = indicator[1]
    pre_fields = indicator[2]
    type_dict = indicator[3]

    # 检查df应该包含所有的pre_field
    for field in pre_fields:
        if field not in df.columns:
            raise KeyboardInterrupt('pre_fields not in df.columns')
    # 设置index
    df = df.set_index(check_field, drop=False)

    # 检查index是否重复
    if df.index.duplicated().any():
        raise KeyboardInterrupt('index重复')

    # 设置update时间为空
    df['first_update'] = np.nan
    df['last_update'] = np.nan

    # columns排序
    l1 = df.drop(pre_fields, axis=1).columns.tolist()
    if field_ascending is True:
        l1.sort()
    l0 = pre_fields + l1
    df = df.reindex(l0, axis=1)

    # MainLog.add_log('%20s --> %s' % ('database', database))
    MainLog.add_log('%20s --> %s' % ('table', table))

    # 连接database
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': database,
    }
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    ########################################################################################

    # 如果初始化，删除初始表格
    if ini:
        cursor.execute(sql_format_drop_table(table))
        db.commit()

    # 修正原始的sql表
    if sql_if_table_exists(cursor, table):
        # 添加空列
        fields = sql_get_fields(cursor, table)
        new_columns = []
        for column in df.columns:
            if column not in fields:
                new_columns.append(column)
                sql_type = type_dict[column]
                cursor.execute(sql_add_field(table, column, sql_type))
                db.commit()
                if field_ascending is False:
                    fields.append(column)
                else:
                    pre_len = len(pre_fields)
                    counter = len(fields)
                    for field in fields[::-1]:
                        if counter == pre_len:
                            break
                        if column > field:
                            break
                        counter -= 1
                    tmp = sql_move_field(table, column, sql_type, fields[counter-1])
                    cursor.execute(tmp)
                    db.commit()
                    fields.insert(counter, column)
        if len(new_columns) > 0:
            MainLog.add_log('%20s --> %s' % ('add fields', new_columns))

    else:
        # 新建 table
        header_str = sql_format_fields_with_type(df.columns, type_dict)
        cursor.execute(sql_format_create_table(table, header_str))
        db.commit()
        MainLog.add_log('%20s --> %s' % ('create table', table))

    # 获取new_index
    new_columns = list(df.columns)

    df_sql = get_data_frame(cursor, table)
    df_sql = df_sql.set_index(check_field, drop=False)
    fields = df_sql.columns

    changed = set()
    add_indexes = []
    change_indexes = []
    change_list = []

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    df['first_update'] = df['first_update'].fillna(value=timestamp)
    df['last_update'] = df['last_update'].fillna(value=timestamp)

    df_sql_t = df_sql.T
    for index, row1 in df.iterrows():
        row2 = df_sql_t.get(index)
        if row2 is None:
            add_indexes.append(index)
            continue

        new_row = []
        flag = False

        for column, val2 in row2.items():
            if column not in row1.index:
                new_row.append(val2)
            elif column == 'first_update':
                new_row.append(val2)
            else:
                val1 = row1[column]
                new_row.append(val1)
                if column == 'last_update':
                    continue
                if val1 == val2:
                    pass
                elif pd.isna(val1) and pd.isna(val2):
                    pass
                else:
                    changed.add(column)
                    flag = True
        if flag is True:
            change_indexes.append(index)
            change_list.append(new_row)

    changed = list(changed)
    changed.sort()

    df_change = pd.DataFrame(change_list, columns=fields)
    df_change.index = change_indexes

    df_add = df.loc[add_indexes, :].copy()
    df_add = df_add.reindex(fields, axis=1)
    df = pd.concat([df_change, df_add], sort=True)
    df = df.reindex(fields, axis=1)
    new_data = df[new_columns].copy()

    # MainLog.add_log('%20s --> %s' % ('new_df columns', new_columns))
    MainLog.add_log('%20s --> %s' % ('change fields', changed))
    # MainLog.add_log('%20s --> %s' % ('change rows', change_indexes))
    # MainLog.add_log('%20s --> %s' % ('add rows', add_indexes))

    ########################################################################################

    sql_execute_multi(cursor, 'SET autocommit = 0;')
    sql_execute_multi(cursor, 'START TRANSACTION;')

    # 删除行
    date_list = list(df[check_field].values)
    if date_list:
        date_str = json.dumps(date_list, ensure_ascii=False)
        date_str = '(%s)' % date_str[1:-1]
        condition = sql_format_condition(check_field, 'in', date_str)
        delete_str = sql_format_delete(table=table, where=condition)
        sql_execute_multi(cursor, delete_str)

    # 添加行
    df = sql_format_df(df)
    for index in range(df.shape[0]):
        row_data = list(df.iloc[index, :].values)
        insert_str = sql_format_insert(table, values=row_data)
        sql_execute_multi(cursor, insert_str)

    sql_execute_multi(cursor, 'COMMIT;')
    db.close()

    if len(new_data.index) == 0:
        MainLog.add_log('%20s --> %s' % ('new_df', 'none'))
        return
    else:
        MainLog.add_log('%20s --> \n%s' % ('new_df', repr(new_data)))
        return new_data


def mysql2df(database, table, fields=None):
    # 连接database
    config = {
        'user': 'root',
        'password': 'aQLZciNTq4sx',
        'host': 'localhost',
        'port': '3306',
        'database': database,
    }
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    indicator = get_sql_indicator(pd.DataFrame(), database)
    check_field = indicator[0]
    type_dict = indicator[3]

    flag = sql_if_table_exists(cursor=cursor, table=table)
    if flag:
        sql_df = get_data_frame(cursor=cursor, table=table)
        sql_df = sql_df.set_index(check_field, drop=False)
        sql_df.sort_index(inplace=True)
        if 'Invalid date' in sql_df.index:
            sql_df.drop('Invalid date', inplace=True)

        if fields is not None:
            sql_df = sql_df.reindex(fields, axis=1)
        sql_df.index = sql_df.index.map(lambda x: x[:10])
        return sql_df
    else:
        if fields is None:
            columns = list(type_dict.keys())
            return pd.DataFrame(columns=columns)
        else:
            return pd.DataFrame(columns=fields)


def sql_execute_multi(cursor, instruct):
    for _ in cursor.execute(instruct, multi=True):
        pass


def sql_format_df(df):
    for column in list(df.columns):
        if df.dtypes[column] == 'int64':
            df[column] = df[column].astype('float64')

    # result = df.where(df.notnull(), None)
    result = df.replace(np.nan, None)
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


def sql_add_field(table, field, sql_type):
    result = """
        ALTER TABLE %s ADD %s %s;
    """ % (table, field, sql_type)
    return result


def sql_drop_field(table, field):
    result = """
        ALTER TABLE %s DROP %s;
    """ % (table, field)
    return result


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


def get_data_frame(cursor, table, fields=None):
    # check_str = sql_format_select(
    #     select='COLUMN_name',
    #     table='information_schema.COLUMNS',
    #     where='table_name = "%s"' % table,
    #     order_by='ordinal_position',
    # )
    if fields is None:
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

    else:
        field_str = ','.join(fields)
        select_str = sql_format_select(field_str, table)
        # cursor.execute(select_str, multi=True)
        cursor.execute(select_str)
        tmp_res = cursor.fetchall()

        df = pd.DataFrame(tmp_res, columns=fields)
        return df


def sql_if_table_exists(cursor, table):
    tmp = 'SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = "%s";' % table
    cursor.execute(tmp)
    res = cursor.fetchall()
    if res:
        return True
    else:
        return False


def sql_get_fields(cursor, table):
    check_str = 'SHOW FIELDS FROM %s;' % table
    cursor.execute(check_str)
    res = cursor.fetchall()
    ret = [value[0] for value in res]
    return ret


def sql_move_field(table, field, sql_type, after_field):
    ret = """
        ALTER TABLE %s MODIFY COLUMN %s %s AFTER %s;
    """ % (table, field, sql_type, after_field)
    return ret


def sql_format_fields_with_type(fields, type_dict: dict):
    if not isinstance(type_dict, dict):
        raise KeyboardInterrupt('type_dict格式需为dict')

    sub_str = list()
    for val in fields:
        sub_str.append('%s %s' % (val, type_dict[val]))
    ret = ',\n'.join(sub_str)
    return ret


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
