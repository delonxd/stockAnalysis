import mysql.connector
import pandas as pd


def insert_data(config=None, data=None):
    mysql.connector.connect(**config)


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
        ci.`Name`,
        co.`Name`,
        co.gnp,
        ci.Population
    FROM
        world.city ci,
        world.country co 
    WHERE
        ci.CountryCode = co.`Code` 
    ORDER BY
        ci.Population DESC 
        LIMIT 5;
"""

cursor.execute(instruct)

result = cursor.fetchall()

print(result)
print(type(result))


df1 = pd.DataFrame(result)
# print(df1)
print(df1[3][0])
print(type(df1[3][0]))


