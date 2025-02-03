from flask import Flask, request, jsonify, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
import re, os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardcoded_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnerable.db'
app.config['WTF_CSRF_ENABLED'] = False  # CSRF disabled
app.config['DEBUG'] = True

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
client = MongoClient('mongodb://localhost:27017/')
mongo_db = client['vulnerable_db']
mongo_users = mongo_db['users']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

def create_db():
    with app.app_context():
        db.create_all()

@app.route('/idor/profile', methods=['GET'])
def idor():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username, "email": user.email})
    return jsonify({"error": "User not found"}), 404

@app.route('/nosql/login', methods=['POST'])
def nosql_login():
    data = request.get_json()
    user = mongo_users.find_one({"username": data['username'], "password": data['password']})
    if user:
        return jsonify({"message": "Login successful", "user_id": str(user['_id'])})
    return jsonify({"message": "Login failed"}), 401

@app.route('/csrf/post', methods=['POST'])
def csrf_post():
    content = request.form.get('content')
    return jsonify({"message": "Post created", "content": content})

@app.route('/xss', methods=['POST'])
def xss():
    username = request.form.get('username')
    return f"<h1>Welcome, {username}</h1>"  # Reflected XSS

@app.route('/code_injection', methods=['POST'])
def code_injection():
    code = request.form.get('code')
    exec(code)  # Code Injection Vulnerability
    return "Executed"

@app.route('/ssti', methods=['GET'])
def ssti():
    name = request.args.get('name', 'User')
    template = """
    <h1>Hello {{ name }}</h1>
    """
    return render_template_string(template, name=name)

if __name__ == '__main__':
    create_db()
    app.run(host='0.0.0.0', port=5000)

