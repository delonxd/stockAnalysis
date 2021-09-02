import pandas as pd
import numpy as np
import os
import time
from Data2Excel import *

data2excel = SheetDataGroup(sheet_names=[])

# 获取时间戳
localtime = time.localtime()
timestamp = time.strftime("%Y%m%d%H%M%S", localtime)
print(time.strftime("%Y-%m-%d %H:%M:%S", localtime))

df_input = pd.read_excel('计算条件.xlsx')

df_input = df_input.where(df_input.notnull(), None)
num_len = len(list(df_input['序号']))

excel_data = []
excel_data_first = []
excel_data_end = []

pd_read_flag = True
# pd_read_flag = False

# for temp in np.arange(0, 1.01, 0.1):
for temp in range(num_len):

    data2excel.add_new_row()

    if pd_read_flag:
        df_input_row = df_input.iloc[temp]
        valuation = df_input_row['资金(万元)']
        fixed_assets0 = df_input_row['房价(万元)']
        income_month = df_input_row['月净收入(万元)']
        fund_month = df_input_row['月公积金(万元)']
        expense_month = df_input_row['月消费(万元)']
        investment_rate = df_input_row['现金投资比例(%)'] / 100
        loan_rate_year = df_input_row['商业贷款利率(%)'] / 100
        loan_fund_rate_year = df_input_row['公积金贷款利率(%)'] / 100
        return_rate_year = df_input_row['现金年回报率(%)'] / 100
        estate_rate_year = df_input_row['房屋价格年增长率(%)'] / 100
        inflation_rate_year = df_input_row['年通货膨胀率(%)'] / 100
        income_rate_year = df_input_row['收入年增长率(%)'] / 100
        rate = df_input_row['贷款比率(%)'] / 100
        period_years = int(df_input_row['贷款年数(年)'])
        period_months = period_years * 12

    else:
        valuation = 530
        fixed_assets0 = 530
        income_month = 1
        fund_month = 0.5
        expense_month = 0
        investment_rate = 0.7
        loan_rate_year = 0.049 * 1.05
        loan_fund_rate_year = 0.0325
        return_rate_year = 0.04
        estate_rate_year = 0.01
        inflation_rate_year = 0.035
        income_rate_year = 0.03
        rate = temp
        period_years = 30
        period_months = period_years * 12

    fixed_assets = [fixed_assets0]

    loan = [fixed_assets[0]*rate]
    fund_loan = [0]
    k = 40
    if loan[0] >= k:
        fund_loan[0] = k
        loan[0] = loan[0] - fund_loan[0]
    else:
        fund_loan[0] = loan[0]
        loan[0] = 0
    first_payment = fixed_assets[0] - loan[0] - fund_loan[0]
    cash = [valuation - first_payment]

    income = [income_month]
    fund = [fund_month]
    expense = [expense_month]

    length = period_months

    r = loan_rate_year/12
    a1 = loan[-1] * r * (1+r)**period_months/((1+r)**period_months - 1)

    r = loan_fund_rate_year/12
    a2 = fund_loan[-1] * r * (1+r)**period_months / ((1+r)**period_months - 1)

    payment = [a1 + a2]
    inflation = [1]

    for i in range(period_months):
        data2excel.add_data(sheet_name="现金(万元)", data1=cash[-1])
        data2excel.add_data(sheet_name="房价(万元)", data1=fixed_assets[-1])
        data2excel.add_data(sheet_name="净资产(万元)", data1=cash[-1] + fixed_assets[-1])
        data2excel.add_data(sheet_name="资产折算后(万元)", data1=((cash[-1] + fixed_assets[-1]) / inflation[-1]))
        data2excel.add_data(sheet_name="月净收入(万元)", data1=income[-1])
        data2excel.add_data(sheet_name="月消费(万元)", data1=expense[-1])
        data2excel.add_data(sheet_name="月公积金(万元)", data1=fund[-1])
        data2excel.add_data(sheet_name="通货膨胀率(%)", data1=inflation[-1])
        data2excel.add_data(sheet_name="剩余贷款(万元)", data1=loan[-1] + fund_loan[-1])
        data2excel.add_data(sheet_name="资产负债比率(%)", data1=(loan[-1] + fund_loan[-1])/(cash[-1] + fixed_assets[-1])*100)

        rate_year = estate_rate_year
        rslt = fixed_assets[-1] * (1 + rate_year/12)
        fixed_assets.append(rslt)

        r = loan_rate_year / 12
        B = loan[0] * r * (1+r)**i / ((1+r)**period_months - 1)
        loan.append(loan[-1] - B)

        r = loan_fund_rate_year / 12
        B = fund_loan[0] * r * (1+r)**i / ((1+r)**period_months - 1)
        fund_loan.append(fund_loan[-1] - B)

        rate_year = return_rate_year
        rslt = cash[-1] + income[-1] - expense[-1] - payment[-1] + cash[-1] * (rate_year/12) * investment_rate + fund[-1]
        cash.append(rslt)

        rslt = inflation[-1] * (1 + inflation_rate_year/12)
        inflation.append(rslt)

        rslt = income[-1] * (1 + income_rate_year/12)
        income.append(rslt)

        rslt = fund[-1] * (1 + income_rate_year/12)
        fund.append(rslt)

    print('\n',
          '资金:', round(valuation, 2), '万元', '\n',
          '房价:', round(fixed_assets0, 2), '万元', '\n',
          '月净收入:', round(income_month, 2), '万元', '\n',
          '月消费:', round(expense_month, 2), '万元', '\n',
          '月公积金:', round(fund_month, 2), '万元', '\n',
          '现金投资比例:', round(investment_rate, 2), '\n',
          '商业贷款利率:', round(loan_rate_year * 100, 2), '%', '\n',
          '公积金贷款利率:', round(loan_fund_rate_year * 100, 2), '%', '\n',
          '现金年回报率:', round(return_rate_year * 100, 2), '%', '\n',
          '房屋价值年增长率:', round(estate_rate_year * 100, 2), '%', '\n',
          '年通货膨胀率:', round(inflation_rate_year * 100, 2), '%', '\n',
          '收入年增长率:', round(income_rate_year * 100, 2), '%', '\n',
          '贷款年数:', round(period_years, 2), '年', '\n',
          '贷款月数:', round(period_months, 2), '月', '\n',
              )

    print('首年:  ',
          '净资产:', round(valuation, 2),
          '房价:', round(fixed_assets[0], 2),
          '首付:', round(first_payment, 2),
          '商业贷款:', round(loan[0], 2),
          '公积金贷款:', round(fund_loan[0], 2),
          '贷款比率:', round(rate*100, 2), '%',
          '剩余现金:', round(cash[0], 2),
          '资产折算后', round((cash[-1] + fixed_assets[-1]), 2),
          )

    print('末年:  ',
          '净资产:', round(cash[-1] + fixed_assets[-1], 2),
          '现金:', round(cash[-1], 2),
          '固资:', round(fixed_assets[-1], 2),
          '月存款:', round(income[-1], 2),
          '通货膨胀:', round(inflation[-1], 2),
          '首月还款除公积金:', round((payment[0]-fund[0]), 2),
          '首月公积金:', round(fund[0], 2),
          '资产折算后', round(((cash[-1] + fixed_assets[-1])/inflation[-1]), 2),
          )

    print('')

    data = dict()
    data['资金(万元)'] = round(valuation, 2)
    data['房价(万元)'] = round(fixed_assets0, 2)
    data['月净收入(万元)'] = round(income_month, 2)
    data['月消费(万元)'] = round(expense_month, 2)
    data['月公积金(万元)'] = round(fund_month, 2)
    data['现金投资比例(%)'] = round(investment_rate * 100, 2)
    data['商业贷款利率(%)'] = round(loan_rate_year * 100, 2)
    data['公积金贷款利率(%)'] = round(loan_fund_rate_year * 100, 2)
    data['现金年回报率(%)'] = round(return_rate_year * 100, 2)
    data['房屋价格年增长率(%)'] = round(estate_rate_year * 100, 2)
    data['年通货膨胀率(%)'] = round(inflation_rate_year * 100, 2)
    data['收入年增长率(%)'] = round(income_rate_year * 100, 2)
    data['贷款年数(年)'] = round(period_years, 2)
    data['贷款月数(月)'] = round(period_months, 2)
    data['贷款比率(%)'] = round(rate * 100, 2)

    data_first = dict()
    data_first['净资产(万元)'] = round(valuation, 2)
    data_first['房价(万元)'] = round(fixed_assets[0], 2)
    data_first['首付(万元)'] = round(first_payment, 2)
    data_first['商业贷款金额(万元)'] = round(loan[0], 2)
    data_first['公积金贷款金额(万元)'] = round(fund_loan[0], 2)
    data_first['贷款比率(%)'] = round(rate * 100, 2)
    data_first['剩余现金(万元)'] = round(cash[0], 2)
    data_first['资产折算后(万元)'] = round(valuation, 2)
    data_first['月净收入(万元)'] = round(income[0], 2)
    data_first['月消费(万元)'] = round(expense[0], 2)
    data_first['月公积金(万元)'] = round(fund[0], 2)
    data_first['月还款额(万元)'] = round(payment[0], 2)
    data_first['月还款额除公积金(万元)'] = round((payment[0]-fund[0]), 2)

    data_end = dict()
    data_end['净资产(万元)'] = round(cash[-1] + fixed_assets[-1], 2)
    data_end['房价(万元)'] = round(fixed_assets[-1], 2)
    data_end['资产折算后(万元)'] = round(((cash[-1] + fixed_assets[-1]) / inflation[-1]), 2)
    data_end['剩余现金(万元)'] = round(cash[-1], 2)
    data_end['月净收入(万元)'] = round(income[-1], 2)
    data_end['月消费(万元)'] = round(expense[-1], 2)
    data_end['月公积金(万元)'] = round(fund[-1], 2)
    data_end['贷款比率(%)'] = round(rate * 100, 2)
    data_end['通货膨胀率(%)'] = round(inflation[-1] * 100, 2)

    data_row = [data[key] for key in data.keys()]
    data_first_row = [data_first[key] for key in data_first.keys()]
    data_end_row = [data_end[key] for key in data_end.keys()]

    excel_data.append(data_row)
    excel_data_first.append(data_first_row)
    excel_data_end.append(data_end_row)


    # print(fixed_assets[-1])

# print('')
#
# for temp in np.arange(1, 0.31, -0.1):
#     fixed_assets = [fixed_assets0]
#
#     # rate = 0.5
#     rate = temp
#     loan = [fixed_assets[0]*(1-rate)]
#     cash = [valuation-fixed_assets[0]+loan[0]]
#     print('资金:', round(valuation, 2),
#           '现金:', round(cash[0], 2),
#           '固资:', round(fixed_assets[0], 2),
#           '贷款:', round(loan[0], 2),
#           '比率:', round(rate*100, 2), '%')
#     # print(valuation, cash[0], loan[0])
#
#     income = [income_month]
#     expense = [expense_month]
#
#     period_years = 30
#     period_months = period_years * 12
#
#     length = period_months
#
#     # r = loan_rate_year/12
#     # a = loan[-1] * r * (1+r)**period_months/((1+r)**period_months - 1)
#     payment = []
#     inflation = [1]
#
#     for i in range(period_months):
#         loan_month = loan[-1]
#         principal = loan[0] / period_months
#
#         interest_rate_year = loan_rate_year
#         interest_expense = loan_month * (interest_rate_year/12)
#         loan.append(loan_month-principal)
#
#         payment.append(interest_expense + principal)
#
#         rate_year = estate_rate_year
#         rslt = fixed_assets[-1] * (1 + rate_year/12)
#         fixed_assets.append(rslt)
#
#         rate_year = return_rate_year
#         rslt = cash[-1] + income[-1] - expense[-1] - payment[-1] + cash[-1] * (rate_year/12) * investment_rate
#         cash.append(rslt)
#
#         rslt = inflation[-1] * (1 + inflation_rate_year/12)
#         inflation.append(rslt)
#
#         rslt = income[-1] * (1 + income_rate_year/12)
#         income.append(rslt)
#
#     print('资产:', round(cash[-1] + fixed_assets[-1], 2),
#           '现金:', round(cash[-1], 2),
#           '固资:', round(fixed_assets[-1], 2),
#           '月存款:', round(income[-1], 2),
#           '通货膨胀:', round(inflation[-1], 2),
#           '资产折算后', round(((cash[-1] + fixed_assets[-1])/inflation[-1]), 2))
#
#     print('')
#     # print(fixed_assets[-1])

df_data = pd.DataFrame(excel_data, columns=data.keys())
df_data_first = pd.DataFrame(excel_data_first, columns=data_first.keys())
df_data_end = pd.DataFrame(excel_data_end, columns=data_end.keys())

pass

# 保存到本地excel
filename = '计算结果'
# filename = '仿真输出_拆电容'
# filepath = 'src/Output/'+ filename + timestamp + '.xlsx'
filepath = '' + filename + '_' + timestamp + '.xlsx'
with pd.ExcelWriter(filepath) as writer:
    df_input.to_excel(writer, sheet_name="参数输入", index=False)
    df_data.to_excel(writer, sheet_name="计算条件", index=False)
    df_data_first.to_excel(writer, sheet_name="首月净资产", index=False)
    df_data_end.to_excel(writer, sheet_name="末月净资产", index=False)

    names = [
        "现金(万元)",
        "房价(万元)",
        "净资产(万元)",
        "资产折算后(万元)",
        "月净收入(万元)",
        "月消费(万元)",
        "月公积金(万元)",
        "通货膨胀率(%)",
        "剩余贷款(万元)",
        "资产负债比率(%)",
    ]

    data2excel.write2excel(sheet_names=names, writer=writer)
