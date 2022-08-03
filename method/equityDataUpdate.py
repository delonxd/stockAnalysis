def eq_update():
    import sys
    sys.path.append('D:\\PycharmProjects\\stockAnalysis')

    import os
    os.chdir("D:\\PycharmProjects\\stockAnalysis\\method")

    from method.fileMethod import load_json_txt
    from request.requestEquityData import request_eq2mysql

    code_list = load_json_txt("..\\basicData\\dailyUpdate\\latest\\a001_code_list.txt")
    request_eq2mysql(code_list)


if __name__ == '__main__':
    # import pandas as pd
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.width', 10000)

    eq_update()
