from method.profileMethod import get_code_profile_df
from method.sqlMethod import df2mysql
from method.sqlMethod import mysql2df
from method.logMethod import MainLog
import pandas as pd
import json
import os


def update_salary_data_hk():
    pass


def data_frame2mysql_hk_salary():

    df = get_code_profile_df()
    df = df[df['area'] == 'hk']

    code_list = df.index.to_list()

    index = code_list.index('hk-02898')
    code_list = code_list[index:]
    print(code_list)

    outer_counter = 0
    list_size = len(code_list)
    for code in code_list:
        outer_counter += 1
        # code = 'hk-00001'

        # path = '..\\method\\利润表(原始)_%s.HK.xls' % code[3:]
        path = 'D:\\薪酬数据backup\\利润表(原始)_%s.HK.xls' % code[3:]

        if not os.path.exists(path):
            MainLog.add_log_accurate('文件不存在：%s' % path)
            continue

        df = pd.read_excel(path)
        df = df.dropna(how='all')
        if df.size <= 1:
            MainLog.add_log_accurate('文件为空：%s' % path)
            continue

        df = df.set_index('Unnamed: 0')
        df = df.T

        df['代码'] = code
        df['标准日期'] = df.index
        df['报表年结日'] = df['报表年结日'].str.lstrip('0')
        df['标准日期'] = df.apply(lambda x: f"{x['标准日期']}  ({x['报表年结日']})", axis=1)

        drop_columns = [
            '数据来源：东方财富Choice数据',
            '区间起始日',
            '区间截止日',
            '上市前/上市后',
            '报告期',
            '报表类型',
        ]
        df = df.drop(columns=drop_columns)

        comparison_table = {
            "首次上传日期": "first_update",
            "最近上传日期": "last_update",
            '代码': 'code',
            '标准日期': 'STD_REPORT_DATE',
            '公告日期': 'REPORT_DATE',
            '报表年结日': 'FISCAL_YEAR',
            '显示币种': 'CURRENCY_SHOW',
            '原始币种': 'CURRENCY_ORG',
            '会计准则': 'ACCOUNTING_STD',
            '审计意见': 'AUDIT_OPINION',
        }

        pre_columns = list(comparison_table.keys())
        rename_table = comparison_table.copy()
        counter = 0
        for col in df.columns:
            if col not in pre_columns:
                if col[-4:] == '(万元)':
                    counter += 1
                    key = '利润表(原始)-' + col[:-4].lstrip()
                    val = 'id_%03d' % counter

                    comparison_table[key] = val
                    df[col] = (df[col] * 10000).astype('float').round(0)
                    rename_table[col] = val
                else:
                    raise KeyboardInterrupt('column单位错误：应为"(万元)"')

        df = df.rename(rename_table, axis=1)
        df = df.reindex(rename_table.values(), axis=1)

        df = df.set_index('STD_REPORT_DATE', drop=False)
        dup_col = df.columns.duplicated().any()
        dup_idx = df.index.duplicated().any()
        if dup_col or dup_idx:
            raise KeyboardInterrupt('包含重复的index or column')

        cmp_table_json = json.dumps(comparison_table, ensure_ascii=False)
        # print(cmp_table_json)
        str1 = '%s/%s' % (outer_counter, list_size)
        str2 = '%s %s %s' % (code, (len(cmp_table_json.encode('utf-8'))), str1)
        MainLog.add_log_accurate(str2)

        df_header = pd.DataFrame({'code': [code], 'cmp_table_json': cmp_table_json})
        df_header = df_header.set_index('code', drop=False)
        columns = [
            'first_update',
            'last_update',
            'code',
            'cmp_table_json',
        ]
        df_header = df_header.reindex(columns=columns)
        # print(df)
        # print(df_header)

        database = 'orgData_hk_ps'
        table = 'org_ps_hk_%s' % code[3:]

        df2mysql(df=df, database=database, table=table, ini=True, log=False)
        df2mysql(df=df_header, database=database, table='header_table', ini=False, log=False)


def get_org_ps_hk_columns():

    df = get_code_profile_df()
    df_cn = df[df['area'] == 'cn']
    cn_company = df_cn['company_name'].values.tolist()

    df_hk = df[df['area'] == 'hk']

    name_dict = df_hk['name'].to_dict()
    company_name_dict = df_hk['company_name'].to_dict()

    database = 'orgData_hk_ps'
    table = 'header_table'

    df = mysql2df(database=database, table=table)

    column_list = dict()
    name_list = []
    counter = 0
    for index, row in df.iterrows():
        code = row['code']
        cmp_table_json = row['cmp_table_json']
        table = json.loads(cmp_table_json)

        s = pd.Series(table)
        if '利润表(原始)-职工薪酬' in s.index:
            pass
        elif '利润表(原始)-职工福利费用' in s.index:
            pass
        elif '利润表(原始)-员工薪金及雇员福利' in s.index:
            pass
        elif '利润表(原始)-薪酬费用' in s.index:
            pass
        elif '利润表(原始)-薪酬及福利总额' in s.index:
            pass
        else:
            cnd1 = s.index.str.contains('职工')
            cnd2 = s.index.str.contains('员工')
            cnd3 = s.index.str.contains('薪')
            cnd4 = s.index.str.contains('雇员')

            cnd = cnd1 | cnd2 | cnd3 | cnd4
            if cnd.any():
                txt = s.index[cnd].tolist()

                counter += 1
                print(code, txt)
            else:
                # print(s)

                company_name = company_name_dict[code]
                if company_name in cn_company:
                    # print(company_name)
                    pass
                    # print(code, company_name)
                    # counter += 1

                else:

                    name_list.append((code, name_dict[code]))
                    # print(code, name_dict[code])
                    # counter += 1

        column_list.update(table)

    # for val in name_list:
    #     print(val)
    print(counter)

    # for column in column_list.keys():
    #     print(column)
    #
    # print(len(column_list))


def test001():

    df = get_code_profile_df()
    df = df[df['area'] == 'hk']

    code_list = df.index.to_list()
    print(code_list)

    non_exist = []
    for code in code_list:
        # code = 'hk-00001'

        # path = '..\\method\\利润表(原始)_%s.HK.xls' % code[3:]
        path = 'D:\\薪酬数据backup\\利润表(原始)_%s.HK.xls' % code[3:]
        if not os.path.exists(path):
            print(code)
            non_exist.append(code)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 10000)
