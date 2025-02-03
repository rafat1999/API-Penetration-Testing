from flask import Flask, request, jsonify, render_template, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from tinydb import TinyDB, Query
import pyrebase
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardcoded_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnerable.db'  # Using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress warning
app.config['WTF_CSRF_ENABLED'] = False  # CSRF disabled
app.config['DEBUG'] = True

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# TinyDB for NoSQL injection testing
tinydb = TinyDB('vulnerable_nosql.json')
UserQuery = Query()

# Firebase Configuration
firebase_config = {
    "apiKey": "AIzaSyBLU3Wbpw4p3w4J92YN36F0XCP5YJfhwCI",
    "authDomain": "api-pentesting.firebaseapp.com",
    "databaseURL": "https://console.firebase.google.com/project/api-pentesting/database/api-pentesting-default-rtdb/data/~2F",
    "projectId": "api-pentesting",
    "storageBucket": "api-pentesting.firebasestorage.app",
    "messagingSenderId": "396886780019",
    "appId": "1:396886780019:web:c86f4a9fed7becbcd52206"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db_firebase = firebase.database()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

def create_db():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    return render_template('index.html')  # Serve the index.html file

@app.route('/firebase/register', methods=['POST'])
def firebase_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return jsonify({"message": "User registered successfully", "user_id": user['localId']})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/firebase/login', methods=['POST'])
def firebase_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return jsonify({"message": "Login successful", "user_id": user['localId']})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=5000)
