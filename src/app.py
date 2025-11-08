from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta

app = Flask(__name__)

# Security Config
app.config['JWT_SECRET_KEY'] = 'super-secure-secret-key-change-this'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])
Talisman(app, content_security_policy=None)

# Temporary database (for demo)
users = {}

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users:
        return jsonify({'message': 'User already exists'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    users[username] = hashed_pw
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_pw = users.get(username)
    if not user_pw or not bcrypt.check_password_hash(user_pw, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/secure-data', methods=['GET'])
@jwt_required()
def secure_data():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Secure data accessed by {current_user}'}), 200

@app.route('/')
def home():
    return jsonify({'message': 'Secure AI business API running 🚀'}), 200

if __name__ == '__main__':
    app.run(debug=True)
