from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
import bcrypt
import json
import os
from datetime import timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # change this in production!
app.permanent_session_lifetime = timedelta(minutes=15)  # auto logout after 15 minutes

# File to store user data
USERS_FILE = 'users.json'

# Helper functions
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Please enter both username and password to register.', 'error')
        return redirect('/')

    users = load_users()

    if username in users:
        flash('Username already exists. Please log in.', 'error')
        return redirect('/')

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users[username] = {
        'password': hashed_pw.decode('utf-8'),
        'medications': []
    }

    save_users(users)

    session.permanent = True
    session['username'] = username
    flash('Registration successful! Welcome.', 'success')
    return redirect('/dashboard')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    users = load_users()

    if username not in users:
        flash('User not found. Please register.', 'error')
        return redirect('/')

    hashed_pw = users[username]['password'].encode('utf-8')

    if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
        session.permanent = True
        session['username'] = username
        flash('Login successful. Welcome back!', 'success')
        return redirect('/dashboard')
    else:
        flash('Incorrect password. Please try again.', 'error')
        return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_medication', methods=['POST'])
def add_medication():
    if 'username' not in session:
        return redirect('/')
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    users = load_users()
    username = session['username']
    users[username]['medications'].append(data)
    save_users(users)

    return jsonify({'message': 'Medication added successfully'})

@app.route('/get_medications', methods=['GET'])
def get_medications():
    if 'username' not in session:
        return jsonify([])
    
    users = load_users()
    username = session['username']
    return jsonify(users[username]['medications'])

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/')
    
    users = load_users()
    username = session['username']
    medications_count = len(users[username]['medications'])

    return render_template('profile.html', username=username, medications_count=medications_count)
