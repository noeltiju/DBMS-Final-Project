from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:"Appuannu12*@localhost/hike_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    return render_template('main_page.html')

@app.route('/customerlogin', methods=['GET', 'POST'])
def customer_signin():
    return render_template('customer.html')
    
@app.route('/managerlogin', methods=['GET', 'POST'])
def signup():
    return render_template('manager.html')
if __name__ == '__main__':
    app.run(debug=True)