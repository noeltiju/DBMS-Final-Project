import pymysql

hostname = 'localhost'
user = 'root'
password = 'Appuannu12*'

db = pymysql.connections.Connection(
    host = hostname,
    user = user,
    password = password,
)

cursor = db.cursor()
cursor.execute('USE hike')
cursor.execute('select * from phone_numbers')

for i in cursor:
    print(i)

cursor.close()
db.close()