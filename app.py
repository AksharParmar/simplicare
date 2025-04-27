from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
import bcrypt
import json
import os
import base64

# >>> Add Gemini Imports <<<
import google.generativeai as genai
# Ensure os is imported above, but adding it here again for clarity if you missed it
import os
# <<< End Gemini Imports >>>


from datetime import timedelta
from werkzeug.utils import secure_filename


app = Flask(__name__)
# >>> IMPORTANT: Change this secret key for production <<<
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key_if_env_not_set')
# <<< End IMPORTANT >>>

app.permanent_session_lifetime = timedelta(minutes=15)

# Database file
USERS_FILE = 'users.json'

# Profile picture uploads
UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Gemini API Configuration ---
# >>> Configure Gemini API KEY <<<
# It's recommended to load your API key from environment variables
GOOGLE_API_KEY = os.environ.get('AIzaSyABf7-QG_oIC82wG8nHB7lnT5w_7NK_rd8')

if not GOOGLE_API_KEY:
    # In a production app, you might want to log this and exit
    print("Warning: GOOGLE_API_KEY environment variable not set.")
    print("Please set the GOOGLE_API_KEY environment variable with your Google Gemini API key.")
    # You might want to raise an error or handle this more gracefully
    # if the API is strictly necessary for the app to run.
    # For this example, we'll proceed but the /ask route will fail without it.
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Gemini API configured successfully.")

# Initialize the Gemini model once globally after configuration
# This is more efficient than creating the model in every request
try:
    # Choose a Gemini model (e.g., 'gemini-pro' for text generation)
    # Use a recent model like 'gemini-1.5-flash-latest' if available and preferred
    # You can list available models using genai.list_models() if needed
    gemini_model = genai.GenerativeModel('gemini-pro') # Or 'gemini-1.5-flash-latest' etc.
    print("Gemini model loaded.")
except Exception as e:
    gemini_model = None # Set to None if configuration failed
    print(f"Error loading Gemini model: {e}")
    print("The /ask route will not function.")

# <<< End Gemini API Configuration >>>


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

# Landing Page
@app.route('/')
def landing():
    return render_template('landing.html')

# Login Page
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

# Register Page
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

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html',
        username=session['username'],
        display_name=session.get('display_name', session['username']),
        profile_pic=session.get('profile_pic')
    )

# Calendar View
@app.route('/calendar')
def calendar():
    if 'username' not in session:
        return redirect('/')
    return render_template('calendar.html')

# Chatbot View
@app.route('/chatbot')
def chatbot():
    if 'username' not in session:
        return redirect('/')
    # You'll need to create a chatbot.html template
    return render_template('chatbot.html')

# List View
@app.route('/listview')
def listview():
    if 'username' not in session:
        return redirect('/')
    return render_template('listview.html')

# Settings View
@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect('/')
    return render_template('settings.html',
        username=session['username'],
        display_name=session.get('display_name', session['username']),
        profile_pic=session.get('profile_pic')
    )

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- MEDICATION APIs ----------------

# Add Medication
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

# Get Medications (NEW)
@app.route('/get_medications', methods=['GET'])
def get_medications():
    if 'username' not in session:
        return jsonify([])

    users = load_users()
    username = session['username']

    medications = users.get(username, {}).get('medications', [])
    return jsonify(medications)

# Delete Medication
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

# Update Profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect('/')

    users = load_users()
    username = session['username']
    user = users.get(username, {})

    name = request.form.get('name')
    email = request.form.get('email')
    new_username = request.form.get('username') # Be careful with username changes, requires updating session etc.
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
    # Handling username change is complex (sessions, keys in dict) - simplified here
    if new_username and new_username != username:
         # Check if new username is already taken
         if new_username in users:
             flash('New username already exists.', 'error')
         else:
            users[new_username] = users.pop(username) # Rename the key
            session['username'] = new_username # Update session
            username = new_username # Update local variable for saving

    if profile_pic and allowed_file(profile_pic.filename):
        # Make sure the upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(profile_pic.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_pic.save(filepath)
        user['profile_pic'] = filepath
        session['profile_pic'] = filepath

    # Ensure user is saved under the (potentially new) username
    users[username] = user
    save_users(users)
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('settings')) # Redirect back to settings page

# Delete Account
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect('/')

    users = load_users()
    username = session['username']

    if username in users:
        del users[username]
        save_users(users)

    session.clear()
    flash('Your account has been deleted.', 'success')
    return redirect('/')

# --- Gemini Chatbot API Endpoint ---
# >>> Implement /ask route for Gemini <<<
@app.route('/ask', methods=['POST'])
def ask():
    # Check if user is logged in
    if 'username' not in session:
        # If using a public chatbot, you might remove this check
        # If it's user-specific, keep it.
        return jsonify({'error': 'Unauthorized'}), 403

    # Check if the Gemini model was initialized successfully
    if gemini_model is None:
         return jsonify({'error': 'Chatbot service is not available. API key or model setup failed.'}), 503


    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Use the globally initialized model
        # The generate_content method sends the prompt to Gemini
        response = gemini_model.generate_content(user_message)

        # Access the text from the response object
        # response.text is the simplest way for basic text responses
        # A more robust way checking candidates might be needed for complex scenarios
        # (e.g., if the model returns safety blocks instead of text)
        if response.text:
            # You could add logging here to see the prompt and response
            # print(f"User: {user_message}\nBot: {response.text}")
            return jsonify({'response': response.text})
        elif response.prompt_feedback:
             # Handle cases where the prompt was blocked
             safety_ratings = response.prompt_feedback.safety_ratings
             print(f"Prompt blocked due to safety reasons: {safety_ratings}")
             # You might return a specific message to the user
             return jsonify({'response': "I'm sorry, I cannot respond to that query due to safety policies."})
        else:
             # Handle other cases where no text was returned
             print(f"Gemini returned no text and no prompt feedback for prompt: {user_message}")
             print(f"Full response object: {response}")
             return jsonify({'response': "I'm sorry, I couldn't generate a response for that."}), 500


    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        # Log the full traceback for debugging server-side
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to get response from Gemini. Please try again.'}), 500

# <<< End Gemini Chatbot API Endpoint >>>


# ---------------- MAIN ----------------

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # Create users.json file if it doesn't exist
    if not os.path.exists(USERS_FILE):
         with open(USERS_FILE, 'w') as f:
              json.dump({}, f)


    # Set the secret key from environment variable if available
    # app.run will pick up the secret_key configured globally
    # IMPORTANT: In production, debug=False and serve with a production WSGI server (like Gunicorn or uWSGI)
    app.run(debug=True)