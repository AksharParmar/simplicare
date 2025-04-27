# SimpliCare - Medication Management Web App

SimpliCare is a web application designed to help users manage their medications in a simple, friendly, and supportive way.

## Features

- User registration and login
- Personalized dashboard
- Medication management (add, view, delete meds)
- Daily medication intake confirmation
- Browser notifications for medication times
- Sidebar navigation

## Technologies Used

- Flask (Python backend)
- HTML/CSS/JavaScript (Frontend)
- bcrypt (Password hashing)

## Folder Structure

```
simplicare-app/
├── app.py (Flask server)
├── users.json (user database)
├── templates/
│   ├── landing.html (Landing page)
│   ├── login.html (Login page)
│   ├── register.html (Registration page)
│   ├── dashboard.html (Main user dashboard)
│   ├── calendar.html (Calendar view page)
│   ├── chatbot.html (AI chatbot page)
│   ├── listview.html (List view of medications)
│   ├── settings.html (Profile and settings page)
├── static/
│   ├── styles.css (sitewide styling)
│   ├── app.js (dashboard functionality)
│   ├── auth.js (auth form validation if needed)
│   ├── icons/ (icons for sidebar)
└── README.md
```

## Setup Instructions

1.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

2.  Run the Flask server:

    ```bash
    python app.py
    ```

3.  Open your browser and navigate to `http://localhost:5000`