from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from scraper import search_data

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# MODELS
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    college = db.Column(db.String(100))
    result = db.Column(db.Text)


# -------------------------
# HOME (PROTECTED)
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        return redirect('/login')

    result = None

    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        college = request.form.get('college')

        if not name or not city or not college:
            flash("All fields required!")
            return redirect('/')

        result = search_data(name, city, college)

        # Save search
        new_search = Search(
            username=session['user'],
            name=name,
            city=city,
            college=college,
            result=result
        )
        db.session.add(new_search)
        db.session.commit()

    return render_template('index.html', result=result, user=session['user'])


# -------------------------
# DASHBOARD
# -------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    searches = Search.query.filter_by(username=session['user']).order_by(Search.id.desc()).all()

    return render_template('dashboard.html', searches=searches, user=session['user'])


# -------------------------
# DELETE SEARCH
# -------------------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/login')

    search = Search.query.get(id)

    if search and search.username == session['user']:
        db.session.delete(search)
        db.session.commit()

    return redirect('/dashboard')


# -------------------------
# SIGNUP
# -------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')

        if not user or not pwd:
            flash("Fill all fields")
            return redirect('/signup')

        existing = User.query.filter_by(username=user).first()
        if existing:
            flash("User already exists")
            return redirect('/signup')

        new_user = User(username=user, password=pwd)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Login now")
        return redirect('/login')

    return render_template('signup.html')


# -------------------------
# LOGIN
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')

        found = User.query.filter_by(username=user, password=pwd).first()

        if found:
            session['user'] = user
            return redirect('/')
        else:
            flash("Invalid credentials")

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