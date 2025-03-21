from flask import Blueprint, request, jsonify, session, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                print('No Authorization header found')
                return jsonify({'error': 'Authentication required'}), 401
                
            # Check Bearer format
            parts = auth_header.split()
            if parts[0].lower() != 'bearer' or len(parts) != 2:
                print('Invalid Authorization header format')
                return jsonify({'error': 'Invalid authentication format'}), 401
            
            # Extract token
            token = parts[1]
            print(f'Processing token: {token[:10]}...')
            
            try:
                # Decode token with proper error handling
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                # Verify user_id in payload
                if 'user_id' not in payload:
                    print('Token missing user_id claim')
                    return jsonify({'error': 'Invalid token'}), 401
                
                # Store user_id in request for route handlers
                request.user_id = payload['user_id']
                print(f'Authenticated user_id: {request.user_id}')
                
                # Call the original route function
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                print('Token has expired')
                return jsonify({'error': 'Session expired'}), 401
                
            except jwt.InvalidTokenError as e:
                print(f'Invalid token: {str(e)}')
                return jsonify({'error': 'Invalid authentication token'}), 401
                
        except Exception as e:
            print(f'Authentication error: {str(e)}')
            return jsonify({'error': 'Authentication failed'}), 401
            
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password', 'name']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get user model from current app
    user_model = current_app.config.get('user_model')
    
    # Check if user already exists
    existing_user = user_model.get_user_by_email(data['email'])
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user_id = user_model.create_user(
        name=data['name'],
        email=data['email'],
        password=data['password']
    )
    
    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get user model from current app
    user_model = current_app.config.get('user_model')
    
    # Find user by email
    user = user_model.get_user_by_email(data['email'])
    if not user or not user_model.verify_password(user, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create JWT token
    try:
        # Create token payload with proper expiration
        token_data = {
            'user_id': str(user['_id']),
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        
        # Generate token
        token = jwt.encode(
            token_data,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Ensure token is string (PyJWT < 2.0 returns bytes)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        print(f'Generated token for user {user["email"]}: {token[:10]}...')
        
        # Validate token can be decoded
        try:
            decoded = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            print(f'Token validation successful: {decoded["user_id"]}')
        except Exception as e:
            print(f'Token validation failed: {str(e)}')
            return jsonify({'error': 'Authentication error - token validation failed'}), 500
            
    except Exception as e:
        print(f'Token generation error: {str(e)}')
        return jsonify({'error': 'Authentication failed'}), 500
    
    # Return successful response with token
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'name': user['name'],
        'email': user['email'],
        'is_admin': user.get('is_admin', False)
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    # Get user model from current app
    user_model = current_app.config.get('user_model')
    user = user_model.get_user_by_id(request.user_id)
    
    return jsonify({
        'name': user['name'],
        'email': user['email']
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    
    # Get user model from current app
    user_model = current_app.config.get('user_model')
    
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name']
    if 'password' in data:
        update_data['password'] = data['password']
    
    user_model.update_user(request.user_id, update_data)
    return jsonify({'message': 'Profile updated successfully'}), 200
