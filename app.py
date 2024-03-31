from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
from triggers import triggers_commands
from datetime import datetime
app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:"Appuannu12*@localhost/hike_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kingmehul:hike@192.168.239.58:3306/hike_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Appuannu12*'
)

# connection = pymysql.connect(
#     host='192.168.239.58',
#     port=3306,
#     user='kingmehul',
#     password='hike'
# ) 

cursor = connection.cursor()
cursor.execute("USE hike;")
triggers_commands(cursor)

@app.route('/')
def index():
    return render_template('main_page.html')

@app.route('/customersignup', methods=['GET', 'POST'])
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
        # try:
        try:
            cursor.execute(f"insert into Customer values({customer_id}, '{customer_first_name}', '{customer_second_name}', '{customer_third_name}', {customer_age}, '2004-02-29', '{customer_email}', 'Bronze', 0);")
            cursor.execute(f"insert into Customer_Login values({customer_id}, '{customer_username}', '{customer_password}');")
            cursor.execute(f"insert into Addresses values({customer_id}, '{customer_address}', {customer_postal_code});")
            cursor.execute(f"insert into Phone_Numbers values({customer_id}, '{customer_no}');")
            connection.commit()
            return redirect('/customerlogin')
        except:
            print("Error in query")
            connection.rollback()
            return redirect('/customersignup')
    else:
        return render_template('signup.html')

global signin_attempts
signin_attempts = 0

global user_id
user_id = 0

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
                    return redirect("/afterloginpage")
                else:
                    signin_attempts+=1
                    print("Incorrect login!")
                    return render_template('customer_login_fail.html')
            except:
                print("Error in query")
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
                return redirect('/')
            else:
                print("Incorrect login!")
                return redirect('/managerlogin')
        except:
            print("Error in query")
            return redirect('/managerlogin')
    return render_template('manager.html')

@app.route('/afterloginpage', methods=['GET', 'POST'])
def after_login():
    return render_template('successful_login.html')

@app.route('/men_page', methods=['GET', 'POST'])
def men_main_page():
    return render_template('men.html')

@app.route('/women_page', methods=['GET', 'POST'])
def women_main_page():
    return render_template('women.html')

@app.route('/shirt_page', methods=['GET', 'POST'])
def shirt_page():
    return render_template('shirt.html')

@app.route('/tshirt_page', methods=['GET', 'POST'])
def tshirt_page():
    cursor.execute("select * from Product_Inventory where Category = 'T-Shirt';")
    tshirt_dict = {}
    rows = cursor.fetchall()
    for row in rows:
        tshirt_dict[row[1]] = {'price': row[4], 'size': row[3]}

    return render_template('tshirt.html', tshirt_dict=tshirt_dict)

@app.route('/jackets_page', methods=['GET', 'POST'])
def jackets_page():
    return render_template('jacket.html')

@app.route('/womens_top_page', methods=['GET', 'POST'])
def womens_top_page():
    return render_template('top.html')

@app.route('/womens_jeans_page', methods=['GET', 'POST'])
def womens_jeans_page():
    return render_template('jeans.html')

@app.route('/womens_skirt_page', methods=['GET', 'POST'])
def womens_skirt_page():
    return render_template('skirt.html')

@app.route('/cart_page', methods=['GET', 'POST'])
def cart_page():
    cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}';")
    rows = cursor.fetchall()
    total_price = 0
    cart_dict = {}
    for row in rows:
        quantity = row[2]
        product_id = row[1]
        cursor.execute(f"select Product_Name, Price, Size from Product_Inventory where Product_ID = {product_id};")
        product_details = cursor.fetchone()
        product_name = product_details[0]
        price = product_details[1]
        size = product_details[2]
        total_price += price * quantity

        cart_dict[product_name] = {'quantity': quantity, 'price': price, 'size': size}
    return render_template('cart_new.html', cart_dict=cart_dict, total_price=total_price)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/productdetails', methods = ['POST'])
def product_details():
    data = request.get_json()
    size = data['size']
    product = data['product']
    cursor.execute(f"select Product_ID from Product_Inventory where Product_Name = '{product}' and Size = '{size}';")
    if (cursor.rowcount == 1):
        product_id = cursor.fetchone()[0]
        cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")

        if (cursor.rowcount == 1):
            cursor.execute(f"update Cart_Items set Quantity = Quantity + 1 where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
            connection.commit()

        else:
            cursor.execute(f"insert into Cart_Items values('Cart_{user_id}', {product_id}, 1);")
            connection.commit()

        cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {product_id};")
        for i in cursor:
            print(i)

    else:
        return jsonify({"message": "Product not found!"})
    return jsonify({"message": "success"})

@app.route('/placeorder', methods=['GET', 'POST'])
def place_order():
    cursor.execute(f"select First_name, Middle_name, Last_Name from Customer where Customer_ID = {user_id};")
    row = cursor.fetchone()
    user_name = row[0] + " " + row[1] + " " + row[2]
    cursor.execute(f"select * from Cart_Items where Cart_ID = 'Cart_{user_id}';")
    rows = cursor.fetchall()
    total_price = 0
    cart_dict = {}
    for row in rows:
        quantity = row[2]
        product_id = row[1]
        cursor.execute(f"select Product_Name, Price, Size, Product_ID from Product_Inventory where Product_ID = {product_id};")
        product_details = cursor.fetchone()
        product_name = product_details[0]
        price = product_details[1]
        size = product_details[2]
        total_price += price * quantity
        cart_dict[product_name] = {'quantity': quantity, 'price': price, 'size': size, 'product_id': product_details[3]}
    
    cursor.execute("select Order_ID from Orders order by Order_ID desc limit 1;")
    order_id = cursor.fetchall()[0][0] + 1

    cursor.execute("select Delivery_ID from Deliveries order by Delivery_ID desc limit 1;")
    delivery_id = cursor.fetchall()[0][0] + 1

    cursor.execute(f"insert into Orders values({order_id}, '2024-03-31', {delivery_id}, {user_id}, {total_price}, 'Pending');")
    current_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(f"insert into Orders values({order_id}, '{current_date}', {delivery_id}, {user_id}, {total_price}, 'Pending');")
    connection.commit()


    for product_name, attributes in cart_dict.items():
        cursor.execute(f"delete from Cart_Items where Cart_ID = 'Cart_{user_id}' and Product_ID = {attributes['product_id']};")
        connection.commit()
        cursor.execute(f"insert into Order_Items values({order_id}, {attributes['product_id']}, {attributes['quantity']});")
        connection.commit()

    return render_template('order.html',product_dict=cart_dict, total_price=total_price, user_name = user_name, date = '2024-03-31', order_id = order_id)
if __name__ == '__main__':
    app.run(debug=True)