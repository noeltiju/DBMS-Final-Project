from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
from triggers import triggers_commands
from analytics import *
from datetime import datetime, timedelta
app = Flask(__name__)

db = SQLAlchemy()
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:"Appuannu12*@localhost/hike_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://udayk:hike@192.168.239.58:3306/hike_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kingmehul:hike@192.168.239.58:3306/hike_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# connection = pymysql.connect(
#     host='localhost',
#     user='root',
#     password='hike'
# )

connection = pymysql.connect(
    host='192.168.239.58',
    port=3306,
    user='udayk',
    password='hike'
) 

# connection = pymysql.connect(
#     host='192.168.239.58',
#     port=3306,
#     user='kingmehul',
#     password='hike'
# ) 

cursor = connection.cursor()
cursor.execute("USE hike;")
triggers_commands(cursor,connection)

@app.route('/')
def index():
    return render_template('welcome_page.html')

@app.route('/customersignup', methods=['GET', 'POST'])

#Non-Conflicting Transaction 1: Customer Signup
def customer_signup():
    if request.method == 'POST':
        customer_first_name = request.form['name']; customer_second_name  = ""; customer_third_name = "";
        customer_age = request.form['age']
        customer_address = request.form['address']
        customer_no = request.form['phone_number']
        customer_email = request.form['email']
        customer_postal_code = request.form['postal_code']
        customer_username = request.form['username']
        customer_password = request.form['password']
    
        cursor.execute("select Customer_ID from Customer_Login order by Customer_ID desc limit 1;")
        customer_id = cursor.fetchall()[0][0] + 1
        try:
            with connection.cursor() as cursor:
                cursor.execute("START TRANSACTION;")
                cursor.execute(f"insert into Customer values({customer_id}, '{customer_first_name}', '{customer_second_name}', '{customer_third_name}', {customer_age}, '2004-02-29', '{customer_email}', 'Bronze', 0);")
                cursor.execute(f"insert into Customer_Login values({customer_id}, '{customer_username}', '{customer_password}');")
                cursor.execute(f"insert into Addresses values({customer_id}, '{customer_address}', {customer_postal_code});")
                cursor.execute(f"insert into Phone_Numbers values({customer_id}, '{customer_no}');")
                cursor.execute("COMMIT;")
        except:
            cursor.execute("ROLLBACK;")
            return render_template('signup.html',status="FAIL")
        return redirect('/customerlogin')

    else:
        return render_template('signup.html',status="")


global signin_attempts
signin_attempts = 0

global user_id
user_id = 0

global user_details
global product_details

global user_address
global user_phone_number

@app.route('/customerlogin', methods=['GET', 'POST'])
def customer_signin():
    global signin_attempts
    global user_id
    if request.method == 'POST':
        if signin_attempts < 3:
            username = request.form['username']
            password = request.form['password']
            try:
                cursor.execute(f"select * from Customer_Login where Username = '{username}' and   Password = '{password}'; ")
                if cursor.rowcount > 0:
                    row = cursor.fetchone()
                    if row:
                        user_id = row[0]
                    signin_attempts = 0
                    return redirect("/main_page")
                else:
                    signin_attempts+=1
                    print("Incorrect login!")
                    return render_template('customer_login_fail.html')
            except:
                return redirect("/customerlogin")
        else:
            signin_attempts = 0
            return render_template('customer_login_fail3.html')
    else:
        return render_template('customer.html')

@app.route('/main_page', methods=['GET', 'POST'])
def after_login():
    return render_template('successful_login.html')

@app.route('/men_page', methods=['GET', 'POST'])
def men_main_page():
    cursor.execute("select Image, Category_Name from Category where Gender = 'Male';")
    rows = cursor.fetchall()
    categories = {}
    for row in rows:
        categories[row[1]] = {'image': row[0]}
    return render_template('categories.html', categories=categories, department='Male')

@app.route('/women_page', methods=['GET', 'POST'])
def women_main_page():
    cursor.execute("select Image, Category_Name from Category where Gender = 'Female';")
    rows = cursor.fetchall()
    categories = {}
    for row in rows:
        categories[row[1]] = {'image': row[0]}
    return render_template('categories.html', categories=categories, department='Female')

@app.route('/cart_page', methods=['GET', 'POST'])
def cart_page():
    cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}';")
    rows = cursor.fetchall()
    total_price = 0
    cart_items = []
    
    if rows:
        for row in rows:
            quantity = row[2]
            product_id = row[1]
            cursor.execute(f"select Product_Name, Price, Size, Product_ID from Product_Inventory where Product_ID = {product_id} and Stock > {quantity};")
            product_details = cursor.fetchone()
            if product_details:
                product_name = product_details[0]
                price = product_details[1]
                size = product_details[2]
                product_id = product_details[3]
                total_price += price * quantity

                cart_items.append({'name': product_name, 'quantity': quantity, 'price': price, 'size': size, 'status' : 'Available', 'product_id': product_id}) 

        cursor.execute(f'select Address, Pincode from Addresses where Customer_ID = {user_id};')
        addresses = [row[0] + " " + str(row[1]) for row in cursor.fetchall()]
        cursor.execute(f'select Phone_Number from Phone_Numbers where Customer_ID = {user_id};')
        phone_numbers = [row[0] for row in cursor.fetchall()]

        return render_template('cart_new.html', cart_items=cart_items, total_price=total_price, addresses=addresses, phone_numbers=phone_numbers)
    else:
        return render_template('cart_empty.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html')

#Conlicting Transaction 1: Placing Order Conflicting
@app.route('/place_order', methods=['POST'])
def place_order():
    global product_details
    global user_details
    if (request.method == 'POST'):
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"select * from Concurrency_Manager where Table_name = 'Product Inventory';")
            result = cursor.fetchone()
            if not (result[1] == 0 and result[2] == 0):
                print("Another user is performing write transaction on the database. Please try again later.")
                return redirect('/cart_page')
            
            cursor.execute(f"update Concurrency_Manager set Write_user = 1 where Table_name like 'Product_Inventory';")
            cursor.execute("COMMIT;")
            data = request.json
            payment_status = data['payment_status']
            address = data['address']
            phone_number = str(data['phone_number']).strip()
            cursor.execute(f"select First_name, Middle_name, Last_Name from Customer where Customer_ID = {user_id};")
            row = cursor.fetchone()
            user_name = row[0] + " " + row[1] + " " + row[2]
            cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}';")
            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name like 'Product_Inventory';")
                cursor.execute("COMMIT;")
                return render_template('cart_empty.html')
            total_price = 0
            cart_dict = {}
            for row in rows:
                quantity = row[2]
                product_id = row[1]
                cursor.execute(f"select Product_Name, Price, Size, Product_ID from Product_Inventory where Product_ID = {product_id} and Stock > {quantity};")
                product_details = cursor.fetchone()
                product_name = product_details[0]
                price = product_details[1]
                size = product_details[2]
                product_id = product_details[3]
                total_price += price * quantity
                cart_dict[product_name] = {'quantity': quantity, 'price': price, 'size': size, 'product_id': product_id}
            
            cursor.execute("select Order_ID from Orders order by Order_ID desc limit 1;")
            if cursor.rowcount == 0:
                order_id = 1
            else:
                order_id = cursor.fetchone()[0] + 1
            
            cursor.execute("select Delivery_ID from Deliveries order by Delivery_ID desc limit 1;")
            if cursor.rowcount == 0:
                delivery_id = 1
            else:
                delivery_id = cursor.fetchone()[0] + 1

            try:
                current_date = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(f"insert into Orders values({order_id}, '{current_date}', {delivery_id}, {user_id}, {total_price}, '{payment_status}');")
                cursor.execute("COMMIT;")
                cursor.execute(f"insert into Deliveries values({delivery_id}, {order_id}, 'NONE','PENDING',{user_id}, '{address}', '{phone_number}');")
                cursor.execute("COMMIT;")
                for product_name, attributes in cart_dict.items():
                    cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {attributes['product_id']};")
                    cursor.execute("COMMIT;")
                    cursor.execute(f"select Stock from Product_Inventory where Product_ID = {attributes['product_id']};")
                    stock = cursor.fetchone()[0]
                    if stock < attributes['quantity']:
                        print("Stock not available")
                        cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name like 'Product_Inventory';")
                        cursor.execute("COMMIT;")
                        return redirect('/cart_page')
                    
                    cursor.execute(f"update Product_Inventory set Stock = Stock - {attributes['quantity']} where Product_ID = {attributes['product_id']};")
                    cursor.execute("COMMIT;")
                    cursor.execute(f"insert into Order_Items values({order_id}, {attributes['product_id']}, {attributes['quantity']});")
                    cursor.execute("COMMIT;")

            
                user_details = {'total_price': total_price, 'user_name': user_name, 'date': current_date, 'order_id': order_id, 'delivery_id': delivery_id}
                product_details = cart_dict

                cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name like 'Product_Inventory';;")
                cursor.execute("COMMIT;")
                return redirect('/order_confirmation')
            except:
                cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name like 'Product_Inventory';")
                cursor.execute("ROLLBACK;")
                return redirect('/cart_page')

@app.route('/order_confirmation', methods=['GET'])
def orderconfirmation():
    global user_details
    global product_details
    print(user_details)
    print(product_details)
    if request.method == 'GET':

        return render_template('order_confirmation.html', user_details=user_details, product_attributes= product_details)

@app.route('/upi', methods=['GET', 'POST'])
def upi_payment():
    data = request.json
    address = data['address']
    phone_number = data['phone_number']
    return render_template('upi_payment.html', address=address, phone_number=phone_number)

@app.route('/category', methods=['GET', 'POST'])
def category_page():
    if (request.method == 'POST'):
        cursor.execute(f"select * from Concurrency_Manager where Table_name = 'Product Inventory';")
        result = cursor.fetchone()
        if result[2] != 0:
            return render_template('successful_login.html', message = 'Another user is performing write transaction on the database. Please try again later.')
    
        cursor.execute(f"update Concurrency_Manager set Read_user = 1 where Table_name like 'Product_Inventory';")
        connection.commit()
        category = request.form['category']
        dept  = request.form['department']
        cursor.execute(f"select Product_Inventory.Product_Name, Price, Description, Image from Product_Inventory , Product_Description where Category = '{category}' and Gender = '{dept}' and Product_Inventory.Product_Name = Product_Description.Product_Name;")
        product_dict = {}
        rows = cursor.fetchall()

        for row in rows:
            product_dict[row[0]] = {'description': row[2], 'price': row[1], 'image': row[3]}

        cursor.execute(f"update Concurrency_Manager set Read_user = 0 where Table_name like 'Product_Inventory';")
        connection.commit()
        return render_template('product_page.html', product_dict=product_dict, category=category, department = dept)
    return render_template('/')

@app.route('/product_details', methods = ['POST'])
def product_details_():
    if request.method == 'POST':
        cursor.execute(f"select * from Concurrency_Manager where Table_name = 'Product Inventory';")
        result = cursor.fetchone()
        if result[2] != 0:
            return render_template('successful_login.html', message = 'Another user is performing write transaction on the database. Please try again later.')
    
        cursor.execute(f"update Concurrency_Manager set Read_user = 1 where Table_name like 'Product_Inventory';")
        connection.commit()

        product_name = request.form['product_name']
        cursor.execute(f"select Price from Product_Inventory where Product_Name = '{product_name}';")
        product_price = cursor.fetchone()[0]

        cursor.execute(f"select distinct Size from Product_Inventory where Product_Name = '{product_name}' and Stock > 0;")
        product_sizes = [row[0] for row in cursor.fetchall()]

        cursor.execute(f"select Description, Image from Product_Description where Product_Name = '{product_name}';")
        result = cursor.fetchone()
        product_description = result[0]
        image_address = result[1]

        cursor.execute(f"update Concurrency_Manager set Read_user = 0 where Table_name like 'Product_Inventory';")
        connection.commit()
        return render_template('product_details_page.html', product_name = product_name, product_price = product_price, sizes = product_sizes, product_description = product_description, image_address = image_address)

    return redirect('/')

#Non-Conflicting Transaction 2: Adding to Cart
@app.route('/addtocart', methods=['GET','POST'])
def add_to_cart():
    data = request.json

    product_name = data['name']
    size = data['size']
    quantity = data['quantity']
    try:
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"select Product_ID from Product_Inventory where Product_Name = '{product_name}' and Size = '{size}' and Stock > {quantity};")
            if (cursor.rowcount == 1):
                product_id = cursor.fetchone()[0]
                cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
                if (cursor.rowcount == 1):
                    cursor.execute(f"update Cart_Items set Quantity = Quantity + {quantity} where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
                    cursor.execute("COMMIT;")

                else:
                    cursor.execute(f"insert into Cart_Items values('Cart_{user_id}', {product_id}, {quantity});")
                    cursor.execute("COMMIT;")
                    connection.commit()
            else: 
                return render_template('successful_login.html', message = 'Stock not available!')
            
    except:
        cursor.execute("ROLLBACK;")
        return render_template('successful_login.html', message = 'Item could not be added to cart!')
        
    finally:
        return redirect('/cart_page')

#Non-Conflicting Transaction 3: Removing from Cart
@app.route('/remove_from_cart', methods=['GET','POST'])
def removing_item():
    data = request.json
    product_id = data['product_id']
    try:
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
            cursor.execute("COMMIT;")
    except:
        cursor.execute("ROLLBACK;")
        return render_template('successful_login.html', message = 'Item could not be removed!')
    return redirect('/cart_page')

@app.route('/customer_orders', methods = ['GET', 'POST'])
def customer_orders():
    cursor.execute(f"select * from Orders where Customer_ID = {user_id};")
    orders = cursor.fetchall()
    order_dict = {}
    for order in orders:
        order_dict[order[0]] = {'date': order[1], 'total_price': order[4], 'payment_status': order[5]}
    return render_template('customer_orders.html', order_dict=order_dict)

@app.route('/view_order', methods = ['GET', 'POST'])
def view_customer_order():
    data = request.form['order_id']
    cursor.execute(f"SELECT Order_Date FROM Orders WHERE Order_ID = {data};")
    date = cursor.fetchone()[0]
    date = datetime.strptime(date, '%Y-%m-%d').date()
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    if date < seven_days_ago:
        redirect('/customer_orders')
    cursor.execute(f"select * from Order_Items where Order_ID = {data};")
    order_items_dict = {}
    result1 = cursor.fetchall()
    for row in result1:
        cursor.execute(f"select Product_Name, Price from Product_Inventory where Product_ID = {row[1]};")
        result2 = cursor.fetchone()
        product_name = result2[0]; price = result2[1]
        order_items_dict[row[1]] = {'quantity': row[2], "name": product_name ,'price': price}

    if order_items_dict == {}:
        return render_template('empty_order.html', order_id = data)
    
    return render_template('order_return.html', order_items_dict=order_items_dict, order_id = data)

@app.route('/return_item', methods = ['GET', 'POST'])
def return_item():
    order_id = request.form['order_id']
    product_id = request.form['product_id']

    cursor.execute(f"delete from Order_Items where Order_ID = {order_id} and Product_ID = {product_id};")
    cursor.execute(f"select Delivery_ID from Orders where Order_ID = {order_id};")
    delivery_id = cursor.fetchone()[0]
    cursor.execute(f"insert into Returns values({order_id}, {product_id}, {delivery_id}, {user_id});")
    connection.commit()
    return render_template('return_confirmed.html')

@app.route('/managerlogin', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        manager_email = request.form['manager_email']
        password = request.form['password']

        try:
            cursor.execute(f"select * from Manager_Login M1, Managers M2 where M1.Manager_ID = M2.Manager_ID and Email = '{manager_email}' and Password = '{password}';")
            if (len(cursor.fetchall()) > 0):
                return redirect('/manager_home_page')
            else:
                print("Incorrect login!")
                return redirect('/managerlogin')
        except:
            print("Error in query")
            return redirect('/managerlogin')
    return render_template('manager.html')

@app.route('/manager_home_page',methods =['GET','POST'])
def manager_home_page():
    return render_template('Manager_home_page.html')

@app.route('/manager_inventory_page',methods =['GET','POST'])
def manager_inventory_page():
    error_message  = None
    if request.method == 'POST':
        product_id = request.form.get('productId')
        product_name = request.form.get('productName')
        category = request.form.get('category')
        where_clause = []
        query_params = []
        if product_id:
            where_clause.append("product_id = %s")
            query_params.append(product_id)
        if product_name:
            where_clause.append("product_name = %s")
            query_params.append(product_name)
        if category:
            where_clause.append("Category = %s")
            query_params.append(category)
        
        sql_query = "SELECT * FROM product_inventory"
        if where_clause:
            sql_query += " WHERE " + " AND ".join(where_clause)
        cursor.execute(sql_query, tuple(query_params))
        result = cursor.fetchone()
        if result:
            return redirect(url_for('manager_inventory_table_page', sql_query=sql_query, query_params=query_params))
        else:
            error_message = "Entered details do not exist in the inventory."
            return render_template('Manager_inventory_order.html', error_message = error_message)
    return render_template('Manager_inventory_order.html', error_message = error_message)

#Non-Conflicting Transaction 4: Manager Viewing Inventory
@app.route('/manager_inventory_table_page',methods =['GET','POST'])
def manager_inventory_table_page():
    success_message = None
    sql_query = request.args.get('sql_query')
    query_params = request.args.get('query_params')
    product_data = []
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("START TRANSACTION;")
            product_id = request.form['productId']
            quantity = request.form['quantity']
            cursor.execute("SELECT product_id from product_inventory where product_id = %s",(product_id,))
            product_id_new = cursor.fetchone()
            if product_id_new:
                product_id_new = product_id_new[0]
                cursor.start
                try:
                    cursor.execute("UPDATE product_inventory SET stock = stock + %s where product_id = %s",(quantity,product_id_new))
                    cursor.execute("COMMIT;")
                    success_message = "Order placed successfully!"
                except:
                    cursor.execute("ROLLBACK;")
                    success_message = "Updating Inventory failed!"
            else:
                success_message = "Invalid Product ID. Please eneter a valid ID"
     
    if query_params:
        cursor.execute(sql_query, tuple(query_params.split(',')))
        result = cursor.fetchall()
        for r  in result:
            product_col = {}
            product_col['product_id'] = r[0]
            product_col['product_name'] = r[1]
            product_col['category'] = r[2]
            product_col['size'] = r[3]
            product_col['price'] = r[4]
            product_col['quantity'] = r[5]
            product_col['gender'] = r[6]
            product_data.append(product_col) 
    return render_template('Manager_inventory_table.html', product_data = product_data, success_message= success_message)


#Conflicting Transaction 2: Manager Alert
@app.route('/manager_alert_page', methods=['GET', 'POST'])
def manager_alert_page():
    success_message = None

    if request.method == 'POST':

        cursor.execute(f"select * from Concurrency_Manager where Table_name = 'Manager_Alert';")
        result = cursor.fetchone()
        if not (result[1] == 0 and result[2] == 0):
            return redirect('/manager_home_page')
        
        cursor.execute(f"update Concurrency_Manager set Write_user = 1 where Table_name = 'Manager_Alert';")
        connection.commit()
        alert_id = request.form['alertId']
        quantity = request.form['quantity']

        with connection.cursor() as cursor:
            try:
                cursor.execute("START TRANSACTION;")
                cursor.execute("SELECT product_id FROM manager_alert WHERE alert_id = %s and approval='NO'", (alert_id,))
                product_id = cursor.fetchone()
                if product_id:
                    product_id = product_id[0]
                    cursor.execute("INSERT INTO manager_orders (product_id, quantity, alert_id) VALUES (%s, %s, %s)", (product_id, quantity, alert_id))
                    connection.commit()
                    cursor.execute("UPDATE manager_alert SET approval = 'YES' WHERE alert_id = %s", (alert_id,))
                    connection.commit()
                    success_message = "Order placed successfully!"
                else:
                    success_message = "Invalid Alert ID. Please enter a valid ID."

                cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name = 'Manager_Alert';")
                cursor.execute("COMMIT")
            except:
                cursor.execute("ROLLBACK")
                success_message = "Order placement failed!"
                cursor.execute(f"update Concurrency_Manager set Write_user = 0 where Table_name = 'Manager_Alert';")

    cursor.execute(f"select * from Concurrency_Manager where Table_name = 'Manager_Alert';")
    result = cursor.fetchone()
    if not (result[2] == 0):
        success_message = "Another user is performing write transaction on the database. Please try again later."
        return render_template('manager_main_page.html', alert_data=[], empty_message=empty_message, success_message=success_message)

    cursor.execute(f"update Concurrency_Manager set Read_user = 1 where Table_name = 'Manager_Alert';")
    connection.commit()

    cursor.execute("SELECT * FROM manager_alert WHERE approval = 'No';")
    alert_temp = cursor.fetchall()
    alert_data = []
    for alert in alert_temp:
        alert_col = {}
        alert_col['alert_id'] = alert[0]
        alert_col['product_id'] = alert[1]
        alert_col['quantity'] = alert[2]
        alert_data.append(alert_col)

    empty_message = "There are currently no alerts in the database." if not alert_data else None
    cursor.execute(f"update Concurrency_Manager set Read_user = 0 where Table_name = 'Manager_Alert';")
    connection.commit()

    return render_template('manager_main_page.html', alert_data=alert_data, empty_message=empty_message, success_message=success_message)

@app.route('/analytics_homepage', methods=['GET', 'POST'])
def alerts_main_page():
    return render_template('analytics_home_page.html')

@app.route('/order_analytics', methods=['GET', 'POST'])
def order_analytics_page():
    val = order_analytics(cursor, '2024-03-01', '2025-05-01')
    return render_template('order_analytics.html',  value = val)

@app.route('/product_analytics', methods=['GET', 'POST'])
def product_analytics_page():
    product_id = request.form['product_id']
    if product_id:
        val = product_analytics(cursor, product_id,'2024-03-01', '2025-05-01')
        return render_template('product_analytics.html',  value = val)
    
    return redirect('/analytics_homepage')

@app.route('/customer_analytics', methods=['GET', 'POST'])
def customer_analytics_page():
    customer_id = request.form['customer_id']
    if customer_id:
        val = customer_analytics(cursor, customer_id,'2024-03-01', '2025-05-01')
        return render_template('customer_analytics.html', value = val)
    return redirect('/analytics_homepage')


if __name__ == '__main__':
    app.run(debug=True)