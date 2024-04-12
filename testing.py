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
cursor.execute("select * from Cart_Items1 where p;")
db.commit()
for i in cursor:
    print(i)

cursor.close()
db.close()