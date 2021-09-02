from method.mainMethod import *
from method.sqlMethod import create_table, insert_values
from method.excelMethod import *
import pandas as pd


if __name__ == '__main__':

    table = 'bs'
    stockCode = '600012'

    headerList = get_header(root=r'..\basicData', table=table)

    fileName = 'FinancialSheet_%s.pkl' % stockCode
    res = read_pkl(root=r'..\bufferData', file_name=fileName)

    dataList = format_res(
        res=res,
        table=table,
        head_list=headerList,
    )

    df1 = pd.DataFrame(data=dataList)

    df2 = pd.DataFrame(data=headerList)

    header = list(df1[2].values)
    index = list(df2[0].values)

    print(header)
    print(index)
    df_output = pd.DataFrame(data=df1.values.T, index=index)

    root = '../sheets'
    excelName = 'Fs_%s.xlsx' % stockCode
    sheetName = table

    write2excel(
        root=root,
        file_name=excelName,
        sheet_name=sheetName,
        data_frame=df_output,
        index=True,
        header=header,
    )


