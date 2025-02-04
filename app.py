from flask import Flask, request, jsonify, render_template, render_template_string, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from tinydb import TinyDB, Query
import pyrebase
import os
import hashlib
import secrets
import re

app = Flask(__name__)

# Intentionally weak configurations
app.config['SECRET_KEY'] = 'hardcoded_secret_key'  # Weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnerable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False  # CSRF protection disabled
app.config['DEBUG'] = True

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# TinyDB for NoSQL injection testing
tinydb = TinyDB('vulnerable_nosql.json')
UserQuery = Query()

# User Model with Vulnerable Design
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), default='user')

# User Profile Model (for IDOR)
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(20))
    sensitive_data = db.Column(db.String(255))  # Additional sensitive field

def create_db():
    with app.app_context():
        db.create_all()

# IDOR Vulnerable Endpoints
@app.route('/user/sensitive-data/<int:user_id>', methods=['GET'])
def get_sensitive_data(user_id):
    # Vulnerable IDOR endpoint - no proper authorization check
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    
    return jsonify({
        "sensitive_data": profile.sensitive_data
    })

# NoSQL Injection Vulnerable Endpoint
@app.route('/nosql/complex-search', methods=['GET'])
def nosql_complex_search():
    # Vulnerable NoSQL injection endpoint
    username = request.args.get('username', '')
    
    # Dangerous query construction
    query = {"$where": f"this.username == '{username}'"}
    
    try:
        # Simulated NoSQL injection vulnerability
        results = list(tinydb.search(query))
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# XSS Vulnerable Endpoints
@app.route('/render-user-content', methods=['POST'])
def render_user_content():
    # XSS Vulnerability: Direct template rendering
    user_input = request.form.get('user_content', '')
    
    # Unsafe rendering without proper sanitization
    rendered_content = render_template_string(
        f"<div>User Content: {user_input}</div>"
    )
    
    return rendered_content

# CSRF Vulnerable Endpoint
@app.route('/transfer-funds', methods=['POST'])
def transfer_funds():
    # Vulnerable CSRF endpoint
    recipient = request.form.get('recipient')
    amount = request.form.get('amount')
    
    # Simulate fund transfer without CSRF protection
    return jsonify({
        "status": "Transfer Initiated",
        "recipient": recipient,
        "amount": amount
    })

# Additional XSS Test Endpoint
@app.route('/stored-xss', methods=['POST'])
def stored_xss():
    # Stored XSS vulnerability
    comment = request.form.get('comment', '')
    
    # Store comment without sanitization
    tinydb.insert({'comment': comment})
    
    return jsonify({
        "message": "Comment stored successfully",
        "comment": comment
    })

# Admin-only Endpoint (Weak Authorization)
@app.route('/admin/user-list', methods=['GET'])
def list_all_users():
    # Weak authorization check
    if not session.get('is_admin', False):
        return jsonify({"error": "Unauthorized"}), 403
    
    users = User.query.all()
    return jsonify([{
        "id": user.id, 
        "username": user.username,
        "role": user.role
    } for user in users])

# Demonstration Route for Multiple Vulnerabilities
@app.route('/vulnerability-demo', methods=['GET', 'POST'])
def vulnerability_demo():
    # Combines multiple vulnerability demonstrations
    
    if request.method == 'POST':
        # XSS Demonstration
        username = request.form.get('username', '')
        
        # Unsafe rendering with user input
        response = make_response(
            render_template_string(
                f"<h1>Welcome, {username}!</h1>"
            )
        )
        
        return response
    
    return render_template('vulnerability_demo.html')

# Login Endpoint with Weak Authentication
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Weak authentication mechanism
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == hashlib.md5(password.encode()).hexdigest():
        # Insecure session management
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['role'] = user.role
        
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "is_admin": user.is_admin
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
