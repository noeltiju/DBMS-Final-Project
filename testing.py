import pymysql

hostname = 'localhost'
user = 'root'
password = 'hike'

db = pymysql.connections.Connection(
    host = hostname,
    user = user,
    password = password,
)

cursor = db.cursor()
cursor.execute('show databases;')
cursor.execute('use hike;')
user_id = 1
product_id = 1
cursor.execute("select * from Returns;")

for i in  cursor:
    print(i)

cursor.close()
db.close()