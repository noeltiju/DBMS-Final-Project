from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
from triggers import triggers_commands
from datetime import datetime
app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:"Appuannu12*@localhost/hike_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://udayk:hike@192.168.239.58:3306/hike_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kingmehul:hike@192.168.239.58:3306/hike_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='hike'
)

# connection = pymysql.connect(
#     host='192.168.239.58',
#     port=3306,
#     user='udayk',
#     password='hike'
# ) 

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

#Transaction 1: Customer Signup
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
            cursor.execute(f"insert into Customer values({customer_id}, '{customer_first_name}', '{customer_second_name}', '{customer_third_name}', {customer_age}, '2004-02-29', '{customer_email}', 'Bronze', 0);")
            cursor.execute(f"insert into Customer_Login values({customer_id}, '{customer_username}', '{customer_password}');")
            cursor.execute(f"insert into Addresses values({customer_id}, '{customer_address}', {customer_postal_code});")
            cursor.execute(f"insert into Phone_Numbers values({customer_id}, '{customer_no}');")
            connection.commit()
            return redirect('/customerlogin')
        except:
            connection.rollback()
            return render_template('signup.html',status="FAIL")
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
    
@app.route('/managerlogin', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        manager_email = request.form['manager_email']
        password = request.form['password']

        try:
            cursor.execute(f"select * from Manager_Login M1, Managers M2 where M1.Manager_ID = M2.Manager_ID and Email = '{manager_email}' and Password = '{password}';")
            if (len(cursor.fetchall()) > 0):
                return redirect('/manager_page')
            else:
                print("Incorrect login!")
                return redirect('/managerlogin')
        except:
            print("Error in query")
            return redirect('/managerlogin')
    return render_template('manager.html')

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

#Transaction 2: Placing Order
@app.route('/place_order', methods=['POST'])
def place_order():
    global product_details
    global user_details
    if (request.method == 'POST'):
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
            connection.commit()
            print(phone_number)
            cursor.execute(f"insert into Deliveries values({delivery_id}, {order_id}, 'NONE','PENDING',{user_id}, '{address}', '{phone_number}');")
            connection.commit()
            for product_name, attributes in cart_dict.items():
                cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {attributes['product_id']};")
                connection.commit()
                cursor.execute(f"select Stock from Product_Inventory where Product_ID = {attributes['product_id']};")
                stock = cursor.fetchone()[0]
                if stock < attributes['quantity']:
                    print("Stock not available")
                    return redirect('/cart_page')
                
                cursor.execute(f"update Product_Inventory set Stock = Stock - {attributes['quantity']} where Product_ID = {attributes['product_id']};")
                connection.commit()
                cursor.execute(f"insert into Order_Items values({order_id}, {attributes['product_id']}, {attributes['quantity']});")
                connection.commit()

            user_details = {'total_price': total_price, 'user_name': user_name, 'date': current_date, 'order_id': order_id, 'delivery_id': delivery_id}
            product_details = cart_dict
            return redirect('/order_confirmation')
        except:
            connection.rollback()
            return redirect('/cart_page', status = 'FAIL')
    
@app.route('/order_confirmation', methods=['GET'])
def orderconfirmation():
    global user_details
    print(user_details)
    global product_details
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
        category = request.form['category']
        dept  = request.form['department']
        cursor.execute(f"select Product_Inventory.Product_Name, Price, Description, Image from Product_Inventory , Product_Description where Category = '{category}' and Gender = '{dept}' and Product_Inventory.Product_Name = Product_Description.Product_Name;")
        product_dict = {}
        rows = cursor.fetchall()

        for row in rows:
            product_dict[row[0]] = {'description': row[2], 'price': row[1], 'image': row[3]}
        return render_template('product_page.html', product_dict=product_dict, category=category, department = dept)
    return render_template('/')

@app.route('/product_details', methods = ['POST'])
def product_details():
    if request.method == 'POST':
        product_name = request.form['product_name']
        cursor.execute(f"select Price from Product_Inventory where Product_Name = '{product_name}';")
        product_price = cursor.fetchone()[0]

        cursor.execute(f"select distinct Size from Product_Inventory where Product_Name = '{product_name}' and Stock > 0;")
        product_sizes = [row[0] for row in cursor.fetchall()]

        cursor.execute(f"select Description, Image from Product_Description where Product_Name = '{product_name}';")
        result = cursor.fetchone()
        product_description = result[0]
        image_address = result[1]
        return render_template('product_details_page.html', product_name = product_name, product_price = product_price, sizes = product_sizes, product_description = product_description, image_address = image_address)

    return redirect('/')

#Transaction 3: Adding to Cart
@app.route('/addtocart', methods=['GET','POST'])
def add_to_cart():
    data = request.json

    product_name = data['name']
    size = data['size']
    quantity = data['quantity']
    cursor.execute(f"select Product_ID from Product_Inventory where Product_Name = '{product_name}' and Size = '{size}' and Stock > {quantity};")
    if (cursor.rowcount == 1):
        product_id = cursor.fetchone()[0]
        cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
        try:
            cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
            if (cursor.rowcount == 1):
                cursor.execute(f"update Cart_Items set Quantity = Quantity + 1 where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
                connection.commit()

            else:
                cursor.execute(f"insert into Cart_Items values('Cart_{user_id}', {product_id}, {quantity});")
                connection.commit()
        except:
            connection.rollback()
            return render_template('successful_login.html', message = 'Item could not be added!')
    else:
        return render_template('successful_login.html', message = 'Stock not available!')
    return redirect('/cart_page')

#Transaction 4: Removing from Cart
@app.route('/remove_from_cart', methods=['GET','POST'])
def removing_item():
    data = request.json
    product_id = data['product_id']
    try:
        cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
        connection.commit()
    except:
        connection.rollback()
        return render_template('successful_login.html', message = 'Item could not be removed!')
    return redirect('/cart_page')

@app.route('/manager_page', methods=['GET', 'POST'])
def manager_main_page():
    success_message = None

    if request.method == 'POST':
        alert_id = request.form['alertId']
        quantity = request.form['quantity']
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

    return render_template('manager_main_page.html', alert_data=alert_data, empty_message=empty_message, success_message=success_message)


if __name__ == '__main__':
    app.run(debug=True)