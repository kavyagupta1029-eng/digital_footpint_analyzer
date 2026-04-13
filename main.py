from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

# your scraper function
from scraper import search_data  

app = Flask(__name__)
app.secret_key = "secret123"

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# USER MODEL
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# -------------------------
# HOME (PROTECTED)
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/login')

    result = None

    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        college = request.form['college']

        result = search_data(name, city, college)

    return render_template('index.html', result=result, user=session['user'])


# -------------------------
# SIGNUP
# -------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        # check if user exists
        existing = User.query.filter_by(username=user).first()
        if existing:
            return "User already exists"

        new_user = User(username=user, password=pwd)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')


# -------------------------
# LOGIN
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        found = User.query.filter_by(username=user, password=pwd).first()

        if found:
            session['user'] = user
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


# -------------------------
# LOGOUT
# -------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)