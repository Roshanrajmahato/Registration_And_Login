from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import bcrypt
import os
app = Flask(__name__)
app.secret_key = "secret_key"

# MongoDB Atlas connection
client = MongoClient(os.environ.get('MONGO_URI'))
db = client['mydatabase']
users_collection = db['users']

@app.route('/')
def index():
    return render_template('register.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = users_collection
        existing_user = users.find_one({'email': request.form['email']})
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'email': request.form['email'], 'password': hashpass})
            session['email'] = request.form['email']
            flash("Registration successful!", "success")
            return redirect(url_for('login'))
        flash("User already exists!", "danger")
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = users_collection
        login_user = users.find_one({'email': request.form['email']})

        if login_user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
                session['email'] = request.form['email']
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            flash("Invalid password!", "danger")
        else:
            flash("User does not exist!", "danger")
    return render_template('login.html')

# Dashboard route (protected)
@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return f"Welcome {session['email']}! <br> <a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("You have been logged out!", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
