import jwt
import datetime
from functools import wraps
from flask import request, jsonify, redirect, url_for, current_app

def get_app_config():
    """Get the current app configuration"""
    return current_app.config

# JWT Helper Functions
def generate_jwt_token(user_data):
    """Generate JWT token for authenticated user"""
    config = get_app_config()
    payload = {
        'user_id': user_data.get('sub'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'picture': user_data.get('picture'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, config['JWT_SECRET_KEY'], algorithm=config['JWT_ALGORITHM'])

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    config = get_app_config()
    try:
        payload = jwt.decode(token, config['JWT_SECRET_KEY'], algorithms=[config['JWT_ALGORITHM']])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_cookie():
    """Get user data from JWT stored in cookie"""
    token = request.cookies.get('auth_token')
    if token:
        return verify_jwt_token(token)
    return None

def get_user_from_header():
    """Get user data from JWT in Authorization header"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        return verify_jwt_token(token)
    return None

# Decorators
def login_required_cookie(f):
    """Decorator for web routes that require authentication via cookie"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_cookie()
        if not user:
            return redirect(url_for('login'))
        return f(user, *args, **kwargs)
    return decorated_function

def login_required_api(f):
    """Decorator for API routes that require authentication via Bearer token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_header()
        if not user:
            return jsonify({'error': 'Authentication required', 'message': 'Please provide a valid Bearer token'}), 401
        return f(user, *args, **kwargs)
    return decorated_function
