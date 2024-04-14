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
cursor.execute("select Delivery_ID from Deliveries order by Delivery_ID desc limit 1;")
if cursor.rowcount == 0:
    delivery_id = 1
else:
    delivery_id = cursor.fetchone()[0] + 1

print(delivery_id)
db.commit()
for i in cursor:
    print(i)

cursor.close()
db.close()