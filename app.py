from flask import Flask, request, jsonify, render_template, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from tinydb import TinyDB, Query
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

@app.route('/idor')
def idor_page():
    return "<h1>IDOR Test Page</h1>"

@app.route('/nosql')
def nosql_page():
    return "<h1>NoSQL Injection Test Page</h1>"

@app.route('/csrf')
def csrf_page():
    return "<h1>CSRF Test Page</h1>"

@app.route('/xss')
def xss_page():
    return "<h1>XSS Test Page</h1>"

@app.route('/code_injection')
def code_injection_page():
    return "<h1>Code Injection Test Page</h1>"

@app.route('/ssti')
def ssti_page():
    return "<h1>Server-Side Template Injection (SSTI) Test Page</h1>"

if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=5000)
