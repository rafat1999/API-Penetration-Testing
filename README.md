# Vulnerable API Learning

This project provides a **vulnerable API** for students to learn about common security vulnerabilities.

## Features & Vulnerabilities
- **IDOR (Insecure Direct Object Reference)**
- **NoSQL Injection** (Using TinyDB)
- **CSRF (Cross-Site Request Forgery)**
- **XSS (Cross-Site Scripting)**
- **Code Injection**
- **Server-Side Template Injection (SSTI)**

## Requirements
- Python 3.x
- SQLite (built into Python, no installation needed)
- TinyDB (for NoSQL simulation)

## Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/vulnerable-api-learning.git
cd vulnerable-api-learning
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API
```bash
python app.py
```

### 4. Access the Web UI
Open your browser and go to:
```
http://localhost:5000
```

## Endpoints & Testing
### IDOR (Insecure Direct Object Reference)
**URL:** `GET /idor/profile?user_id=1`
```bash
curl "http://localhost:5000/idor/profile?user_id=1"
```

### NoSQL Injection (Using TinyDB)
**URL:** `POST /nosql/login`
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}' "http://localhost:5000/nosql/login"
```

### CSRF Attack
**URL:** `POST /csrf/post`
```bash
curl -X POST -d "content=CSRF test" "http://localhost:5000/csrf/post"
```

### XSS (Cross-Site Scripting)
**URL:** `POST /xss`
```bash
curl -X POST -d "username=<script>alert('XSS')</script>" "http://localhost:5000/xss"
```

### Code Injection
**URL:** `POST /code_injection`
```bash
curl -X POST -d "code=print('Hacked')" "http://localhost:5000/code_injection"
```

### Server-Side Template Injection (SSTI)
**URL:** `GET /ssti?name={{7*7}}`
```bash
curl "http://localhost:5000/ssti?name={{7*7}}"
```

## Security Warning 🚨
**This application is intentionally vulnerable. Do NOT deploy it in a real environment.**

## License
MIT License
