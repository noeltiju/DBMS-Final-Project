from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:"Appuannu12*@localhost/hike_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Appuannu12*'
)

cursor = connection.cursor()
cursor.execute('USE hike')

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

@app.route('/customerlogin', methods=['GET', 'POST'])
def customer_signin():
    global signin_attempts
    if request.method == 'POST':
        if signin_attempts < 3:
            username = request.form['username']
            password = request.form['password']
            try:
                cursor.execute(f"select * from Customer_Login where Username = '{username}' and   Password = '{password}'; ")
                if (len(cursor.fetchall()) > 0):
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
    return render_template('tshirt.html')

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
    return render_template('cart.html')


if __name__ == '__main__':
    app.run(debug=True)