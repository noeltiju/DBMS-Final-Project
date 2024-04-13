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
cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
db.commit()
for i in cursor:
    print(i)

cursor.close()
db.close()

# def cart_page():
#     try:
#         cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}';")
#     except:
#         print("Error in query")
#     rows = cursor.fetchall()
#     if len(rows) == 0:
#         return render_template('cart_empty.html')
    # total_price = 0
    # cart_dict = {}
    # for row in rows:
    #     quantity = row[2]
    #     product_id = row[1]
    #     cursor.execute(f"select Product_Name, Price, Size, Product_ID from Product_Inventory where Product_ID = {product_id} and Stock > {quantity};")
    #     product_details = cursor.fetchall()
    #     if product_details:
    #         product_details = product_details[0]
    #         product_name = product_details[0]
    #         price = product_details[1]
    #         size = product_details[2]
    #         product_id = product_details[3]
    #         total_price += price * quantity
    #         cart_dict[product_name] = {'quantity': quantity, 'price': price, 'size': size, 'status': 'Available', product_id: product_id}
    #     else:
    #         cursor.execute(f"select Product_Name, Price, Size from Product_Inventory where Product_ID = {product_id};")
    #         product_details = cursor.fetchone()
    #         product_name = product_details[0]
    #         price = product_details[1]
    #         size = product_details[2]
    #         cart_dict[product_name] = {'quantity': quantity, 'price': price, 'size': size, 'status': 'Not Available', product_id: product_id}
    # return render_template('cart_new.html', cart_dict=cart_dict, total_price=total_price)

                # {% if attributes['status'] == 'Available' %}
                #     <button class="remove-from-cart" onclick="removeFromCart('{{ attributes.product_id }}')">Remove from Cart</button>
                # {% else %}
                #     <button class="remove-from-cart" onclick="removeFromCart('{{ attributes.product_id }}')">Out of Stock</button>
                # {% endif %}