import mysql.connector
import pandas as pd


config = {
    'user': 'root',
    'password': 'aQLZciNTq4sx',
    'host': 'localhost',
    'port': '3306',
    'database': 'world',
}

con = mysql.connector.connect(**config)

cursor = con.cursor(buffered=True)


instruct = """
    SELECT
        * 
    FROM
        world.city
        
    WHERE id = 1111;
"""

cursor.execute(instruct)

result = cursor.fetchall()

print(result)
print(type(result))


# df1 = pd.DataFrame(result)
# # print(df1)
# print(df1[3][0])
# print(type(df1[3][0]))


