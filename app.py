from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
import bcrypt
import json
import os
import base64

# >>> Add Gemini Imports <<<
import google.generativeai as genai
import dotenv
# Ensure os is imported above, but adding it here again for clarity if you missed it
import os
# <<< End Gemini Imports >>>

from datetime import timedelta
from werkzeug.utils import secure_filename

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key_if_env_not_set')
app.permanent_session_lifetime = timedelta(minutes=15)

USERS_FILE = 'users.json'
UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Gemini API Configuration ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY environment variable not set.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Gemini API configured successfully.")

try:
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("Gemini model loaded.")
except Exception as e:
    gemini_model = None
    print(f"Error loading Gemini model: {e}")
# --- End Gemini API Configuration ---

# ---------------- HELPER FUNCTIONS ----------------

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ROUTES ----------------

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()

        if username not in users:
            flash('User not found. Please register.', 'error')
            return redirect('/login')

        hashed_pw = users[username]['password'].encode('utf-8')

        if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
            session.permanent = True
            session['username'] = username
            session['display_name'] = users[username].get('display_name', username)
            session['profile_pic'] = users[username].get('profile_pic', None)
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Incorrect password. Please try again.', 'error')
            return redirect('/login')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        if not name or not username or not password:
            flash('Please fill out all fields.', 'error')
            return redirect('/register')

        users = load_users()

        if username in users:
            flash('Username already exists. Please log in.', 'error')
            return redirect('/login')

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users[username] = {
            'password': hashed_pw.decode('utf-8'),
            'medications': [],
            'display_name': name,
            'email': "",
            'profile_pic': None
        }

        save_users(users)

        session.permanent = True
        session['username'] = username
        session['display_name'] = name
        session['profile_pic'] = None
        flash('Registration successful! Welcome.', 'success')
        return redirect('/dashboard')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html',
        username=session['username'],
        display_name=session.get('display_name', session['username']),
        profile_pic=session.get('profile_pic')
    )

@app.route('/calendar')
def calendar():
    if 'username' not in session:
        return redirect('/')
    return render_template('calendar.html')

@app.route('/chatbot')
def chatbot():
    if 'username' not in session:
        return redirect('/')
    return render_template('chatbot.html', display_name=session.get('display_name', 'Friend'))

@app.route('/listview')
def listview():
    if 'username' not in session:
        return redirect('/')
    return render_template('listview.html')

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect('/')
    return render_template('settings.html',
        username=session['username'],
        display_name=session.get('display_name', session['username']),
        profile_pic=session.get('profile_pic')
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- MEDICATION APIs ----------------

@app.route('/add_medication', methods=['POST'])
def add_medication():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    users = load_users()
    username = session['username']

    if username not in users:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    if 'medications' not in users[username]:
        users[username]['medications'] = []

    new_medication = {
        'name': data.get('name', ''),
        'dosage': data.get('dosage', ''),
        'daily_intake': data.get('daily_intake', ''),
        'weekly_frequency': data.get('weekly_frequency', '')
    }

    users[username]['medications'].append(new_medication)
    save_users(users)

    return jsonify({'message': 'Medication added successfully'})

@app.route('/get_medications', methods=['GET'])
def get_medications():
    if 'username' not in session:
        return jsonify([])

    users = load_users()
    username = session['username']

    medications = users.get(username, {}).get('medications', [])
    return jsonify(medications)

@app.route('/delete_medication/<int:index>', methods=['DELETE'])
def delete_medication(index):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    users = load_users()
    username = session['username']

    if 0 <= index < len(users[username]['medications']):
        users[username]['medications'].pop(index)
        save_users(users)
        return jsonify({'message': 'Medication deleted successfully'})
    else:
        return jsonify({'error': 'Invalid medication index'}), 400

# ---------------- PROFILE APIs ----------------

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect('/')

    users = load_users()
    username = session['username']
    user = users.get(username, {})

    name = request.form.get('name')
    email = request.form.get('email')
    new_username = request.form.get('username')
    password = request.form.get('password')
    profile_pic = request.files.get('profile_pic')

    if name:
        user['display_name'] = name
        session['display_name'] = name
    if email:
        user['email'] = email
    if password:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user['password'] = hashed_pw.decode('utf-8')
    if new_username and new_username != username:
        if new_username in users:
            flash('New username already exists.', 'error')
        else:
            users[new_username] = users.pop(username)
            session['username'] = new_username
            username = new_username

    if profile_pic and allowed_file(profile_pic.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(profile_pic.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_pic.save(filepath)
        user['profile_pic'] = filepath
        session['profile_pic'] = filepath

    users[username] = user
    save_users(users)
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('settings'))

# ✅ ✅ ✅ --- ADD THIS NEW ROUTE --- ✅ ✅ ✅
@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'username' not in session:
        return redirect('/')

    if 'profile_pic' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['profile_pic']

    if file.filename == '':
        flash('No selected file.', 'error')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        users = load_users()
        username = session['username']
        users[username]['profile_pic'] = save_path
        save_users(users)

        session['profile_pic'] = save_path
        flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    flash('Invalid file type.', 'error')
    return redirect(url_for('dashboard'))

# --- Gemini Chatbot API Endpoint ---
@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    if gemini_model is None:
        return jsonify({'error': 'Chatbot service is not available.'}), 503

    username = session['username']
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    users = load_users()
    user_data = users.get(username, {})
    medications = user_data.get('medications', [])

    medication_data_string = ""
    if medications:
        medication_data_string += "User's Registered Medications:\n"
        for med in medications:
            medication_data_string += f"- Name: {med.get('name', 'N/A')}, Dosage: {med.get('dosage', 'N/A')}, Daily Intake: {med.get('daily_intake', 'N/A')}, Weekly Frequency: {med.get('weekly_frequency', 'N/A')}\n"
        medication_data_string += "\nUse this list ONLY for medication-related queries.\n"
    else:
        medication_data_string += "The user has no registered medications.\n\n"

    try:
        tone_instruction = """Act as a friendly, simple health assistant. 
        Provide general health information, but never give medical advice. 
        Always recommend consulting a doctor for serious issues.
        """

        full_prompt = f"{tone_instruction}\n\n{medication_data_string}User Query: {user_message}"

        response = gemini_model.generate_content(full_prompt)

        if response.text:
            return jsonify({'response': response.text})
        elif response.prompt_feedback:
            return jsonify({'response': "Sorry, I couldn't answer due to safety reasons."})
        else:
            return jsonify({'response': "Sorry, no response could be generated."}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get response from Gemini.'}), 500

# ---------------- MAIN ----------------

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

    app.run(debug=True)
