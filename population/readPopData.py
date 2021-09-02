import pickle
import json
import mysql.connector
import pandas as pd
import re

apiKeyText = r"""
总人口 :tp
男性总人口 :tmp
女性总人口 :tfp
人口增长率 :pb_r
人口死亡率 :pm_r
人口自然增长率 :png_r
14岁以下 :tp_a_0_14
15至64岁 :tp_a_15_64
65岁以上 :tp_a_65
少儿抚养比 :cr_r
老年抚养比 :or_r
"""

keyList = re.findall(r'\n(.*) :(.*)', apiKeyText)

print(keyList)

path = '../population/populationData.pkl'

with open(path, 'rb') as pk_f:
    resText = pickle.load(pk_f)

resList = json.loads(resText)['data']


for res in resList:
    print(type(res))
    print(res)


# config = {
#     'user': 'root',
#     'password': 'aQLZciNTq4sx',
#     'host': 'localhost',
#     'port': '3306',
#     'database': 'world',
# }
#
# con = mysql.connector.connect(**config)
#
# cursor = con.cursor(buffered=True)
#
#
# instruct = """
#     SELECT
#         ci.`Name`,
#         co.`Name`,
#         co.gnp,
#         ci.Population
#     FROM
#         world.city ci,
#         world.country co
#     WHERE
#         ci.CountryCode = co.`Code`
#     ORDER BY
#         ci.Population DESC
#         LIMIT 5;
# """
#
# cursor.execute(instruct)
#
# result = cursor.fetchall()
#
# print(result)
# print(type(result))
#
#
# df1 = pd.DataFrame(result)
# # print(df1)
# print(df1[3][0])
# print(type(df1[3][0]))