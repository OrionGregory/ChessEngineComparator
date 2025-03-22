from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

user_auth_bp = Blueprint('user_auth', __name__)
bcrypt = Bcrypt()

@user_auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Lazy import to avoid circular dependency
    from app import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
            (username, email, hashed_password)
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@user_auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    # Lazy import to avoid circular dependency
    from app import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['id']))
        return jsonify({'token': access_token}), 200
    return jsonify({'error': 'Invalid username or password'}), 401