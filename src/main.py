from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import jwt
import datetime
from functools import wraps
import mysql.connector
from src.agent import TeachingAgent

app = Flask(__name__, static_folder="../static", template_folder="../static")
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key in production

# MySQL database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Hemarahith1!',  # Replace with your MySQL root password
    'database': 'edumate_db'  # Updated to new database
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        raise Exception(f"Database connection failed: {str(e)}")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            token = token.split(" ")[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['email']
        except Exception as e:
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def serve_index():
    print(f"Serving index.html from {app.static_folder}/index.html")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    print(f"Serving {path} from {app.static_folder}")
    return send_from_directory(app.static_folder, path)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')  # New field
    year = data.get('year')
    department = data.get('department')

    # Connect to the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"message": "User already exists!"}), 400

        # Insert new user
        cursor.execute(
            "INSERT INTO students (name, email, phone, year, department, password) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, email, phone, year, department, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201

    except mysql.connector.Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Connect to the database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check user credentials
        cursor.execute("SELECT * FROM students WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({"message": "Invalid credentials!"}), 401

        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "message": "Login successful!",
            "token": token,
            "user": {
                "email": user['email'],
                "name": user['name'],
                "phone": user['phone'],  # Include phone in response
                "year": user['year'],
                "department": user['department']
            }
        }), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
@token_required
def chat(current_user):
    print(f"Token validated for user: {current_user}")
    data = request.form if request.form else request.get_json()
    message = data.get('message') if isinstance(data, dict) else data

    files = request.files.getlist('files') if request.files else []
    uploaded_files = []
    for file in files:
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            uploaded_files.append(file_path)

    print(f"Chat request for user: {current_user}")
    # Fetch user data from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE email = %s", (current_user,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user_data:
            return jsonify({"message": "User not found!"}), 404

        agent = TeachingAgent(user_data, uploaded_files)
        response = agent.handle_message(message)

        return jsonify({
            "message": response['message'],
            "quick_replies": response.get('quick_replies', [])
        }), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

if __name__ == '__main__':
    static_folder = os.path.abspath(app.static_folder)
    print(f"Static folder path: {static_folder}")
    print(f"Login.html exists: {os.path.exists(os.path.join(static_folder, 'login.html'))}")
    app.run(debug=True, host='0.0.0.0', port=5000)