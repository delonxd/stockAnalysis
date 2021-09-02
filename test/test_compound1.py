import time
import pandas as pd


path1 = '07291输出_%s.xlsx' % time.strftime("%Y%m%d%H%M%S", time.localtime())

year_list = [3, 4, 5]
year_list.extend(range(6, 41, 2))
c_list = list(range(10, 151, 5))
c_list.extend(list(range(200, 1001, 100)))
c_list.extend([2000, 5000, 10000])

data = []
for c in c_list:

    data_tmp = list()
    data_tmp.append('%s倍' % c)

    for year in year_list:

        tag = True
        rate = 1
        while tag is True:
            rate += 0.001
            tmp1 = (rate ** year - 1) / (rate - 1) - c

            if tmp1 >= 0:
                tag = False
        percent = round((rate-1)*100, 1)
        data_tmp.append(percent)
    print(data_tmp)

    data.append(data_tmp)


head = list()
head.append(None)
for year in year_list:
    head.append('%s年' % year)

with pd.ExcelWriter(path1) as writer:
    df_output = pd.DataFrame(data)
    df_output.to_excel(writer, sheet_name='输出', index=False, header=head)
