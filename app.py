import os
import jwt
import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from authlib.integrations.flask_client import OAuth
import requests
import secrets
from urllib.parse import urlencode
from config import config

app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    request_token_url=None,
    access_token_url=app.config['GOOGLE_TOKEN_URL'],
    authorize_url=app.config['GOOGLE_DISCOVERY_URL'],
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# JWT Helper Functions
def generate_jwt_token(user_data):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_data.get('sub'),
        'email': user_data.get('email'),
        'name': user_data.get('name'),
        'picture': user_data.get('picture'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
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

# Routes
@app.route('/')
def index():
    """Landing page - accessible to both anonymous and authenticated users"""
    user = get_user_from_cookie()
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    # Generate a random state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    # Build authorization URL
    auth_params = {
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'redirect_uri': url_for('callback', _external=True),
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = app.config['GOOGLE_DISCOVERY_URL'] + '?' + urlencode(auth_params)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Google OAuth callback"""
    # Verify state parameter
    if request.args.get('state') != session.get('oauth_state'):
        return render_template('error.html', error='Invalid state parameter'), 400
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        return render_template('error.html', error='Authorization code not found'), 400
    
    # Exchange code for token
    token_data = {
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('callback', _external=True)
    }
    
    try:
        token_response = requests.post(app.config['GOOGLE_TOKEN_URL'], data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Get user info
        headers = {'Authorization': f'Bearer {token_info["access_token"]}'}
        user_response = requests.get(app.config['GOOGLE_USERINFO_URL'], headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Create JWT token
        payload = {
            'user_id': user_info['id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        jwt_token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])
        
        # Set cookie and redirect
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie(
            'auth_token',
            jwt_token,
            httponly=True,
            secure=app.config['ENV'] == 'production',
            samesite='Lax',
            max_age=24*60*60  # 24 hours
        )
        
        # Clean up session
        session.pop('oauth_state', None)
        
        return response
        
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error=f'OAuth error: {str(e)}'), 400
    except jwt.InvalidTokenError as e:
        return render_template('error.html', error=f'JWT error: {str(e)}'), 400

@app.route('/logout')
def logout():
    """Logout user by clearing the JWT cookie"""
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', expires=0, httponly=True, secure=False, samesite='Lax')
    return response

@app.route('/dashboard')
@login_required_cookie
def dashboard(user):
    """Dashboard page - requires authentication via cookie"""
    token = request.cookies.get('auth_token')
    return render_template('dashboard.html', user=user, auth_token=token)

@app.route('/api/get-auth-token')
@login_required_cookie
def api_get_auth_token(user):
    """API endpoint to get current user's JWT token for frontend use"""
    token = request.cookies.get('auth_token')
    return jsonify({'token': token})

# API Routes
@app.route('/api/profile')
@login_required_api
def api_profile(user):
    """API endpoint to get user profile - requires Bearer token"""
    return jsonify({
        'user_id': user.get('user_id'),
        'email': user.get('email'),
        'name': user.get('name'),
        'picture': user.get('picture')
    })

@app.route('/api/protected')
@login_required_api
def api_protected(user):
    """Example protected API endpoint - requires Bearer token"""
    return jsonify({
        'message': 'This is a protected API endpoint',
        'user': user.get('email'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

@app.route('/api/data')
@login_required_api
def api_data(user):
    """Example API endpoint that returns some data - requires Bearer token"""
    return jsonify({
        'data': [
            {'id': 1, 'name': 'Item 1', 'description': 'First item'},
            {'id': 2, 'name': 'Item 2', 'description': 'Second item'},
            {'id': 3, 'name': 'Item 3', 'description': 'Third item'}
        ],
        'user': user.get('email')
    })

# Utility endpoint to get JWT token for API testing
@app.route('/get-token')
@login_required_cookie
def get_token(user):
    """Get JWT token for API testing (web UI only)"""
    token = request.cookies.get('auth_token')
    return render_template('token.html', token=token, user=user)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
