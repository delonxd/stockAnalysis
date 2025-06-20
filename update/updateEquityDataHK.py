from method.profileMethod import get_code_profile_df
from method.logMethod import MainLog
from method.sqlMethod import df2mysql
from method.sqlMethod import mysql2df
from method.fileMethod import load_json_txt
from method.fileMethod import dump_pkl
from method.fileMethod import load_pkl
import pandas as pd
import numpy as np
import re


def update_eq_data_hk():
    pass


def config_primary_key_eq_hk():
    from method.profileMethod import get_code_profile_df
    from method.sqlMethod import mysql2df

    df = get_code_profile_df()
    code_list = df[df['area'] == 'hk'].index.to_list()

    counter = 0
    size = len(code_list)
    for code in code_list:
        counter += 1
        MainLog.add_log_accurate('eq data: %s %s / %s' % (code, counter, size))

        database = 'eqData_hk'
        table = 'eq_hk_%s' % code[3:]
        df = mysql2df(database=database, table=table)

        if df.empty:
            MainLog.add_log_accurate('df is empty.')
            # continue

        tmp = df[df.index.duplicated()].copy()
        if tmp.size > 0:
            raise KeyboardInterrupt()

        # print(df)
        # break
        df2mysql(
            df=df,
            database=database,
            table=table,
            ini=True,
            log=False,
        )


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 10000)

    pass
