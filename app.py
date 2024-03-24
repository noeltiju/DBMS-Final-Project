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
        try:
            cursor.execute(f"insert into Customer_Login values({customer_id}, '{customer_first_name}', '{customer_second_name}', '{customer_third_name}', {customer_age}, '2004-02-29', '{customer_email}', 'Bronze', 0;")
            cursor.execute(f"insert into Customer_Login values({customer_id}, '{customer_username}', '{customer_password}';")
            cursor.execute(f"insert into Addresses values({customer_id}, '{customer_address}', {customer_postal_code};")
            return redirect('/')
        except:
            print("Error in query")
            return redirect('/customersignup')
        return redirect('/')
    else:
        return render_template('signup.html')

@app.route('/customerlogin', methods=['GET', 'POST'])
def customer_signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cursor.execute(f"select * from Customer_Login where Username = '{username}' and   Password = '{password}'; ")
            if (len(cursor.fetchall()) > 0):
                return redirect("/")
            else:
                print("Incorrect login!")
                return redirect("/customerlogin")
        except:
            print("Error in query")
            return redirect("/customerlogin")
    else:
        return render_template('customer.html')
    
@app.route('/managerlogin', methods=['GET', 'POST'])
def signup():
    return render_template('manager.html')

if __name__ == '__main__':
    app.run(debug=True)