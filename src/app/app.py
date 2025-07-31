import os
import sys
import jwt
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, session
from authlib.integrations.flask_client import OAuth
import requests
import secrets
from urllib.parse import urlencode

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.config import config
from auth.auth_utils import generate_jwt_token, get_user_from_cookie, login_required_cookie
from api.api_routes import api_bp
from kong.kong_admin_api import KongAdminAPI, KongAdminAPIError

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')

# Load configuration
config_name = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Register API Blueprint
app.register_blueprint(api_bp)

# Initialize Kong Admin API
kong_admin_url = app.config.get('KONG_ADMIN_URL', 'http://localhost:8001')
kong_api = KongAdminAPI(kong_admin_url)

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
        
        # Create or ensure Kong consumer exists for this user
        kong_consumer_id = create_or_get_kong_consumer(user_info['email'])

        # Create JWT token
        user_data = {
            'sub': user_info['id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture')
        }
        
        jwt_token = generate_jwt_token(user_data)
        
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

# Utility endpoint to get JWT token for API testing
@app.route('/get-token')
@login_required_cookie
def get_token(user):
    """Get JWT token for API testing (web UI only)"""
    token = request.cookies.get('auth_token')
    return render_template('token.html', token=token, user=user)

# Pricing page
@app.route('/pricing')
def pricing():
    """Show pricing table page"""
    user = get_user_from_cookie()
    return render_template('pricing.html', user=user)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

def create_or_get_kong_consumer(user_email):
    """
    Create or retrieve Kong consumer for a user.
    
    Args:
        user_email (str): User's email address
        
    Returns:
        str or None: Kong consumer ID if successful, None if failed
    """
    try:
        # Create username from email (remove @ and special chars for Kong compatibility)
        kong_username_sanitized = user_email.split('@')[0].replace('.', '_').replace('+', '_')
        
        # Check if consumer already exists (using email as username)
        try:
            existing_consumer, status = kong_api.get_consumer(user_email)
            if status == 200:
                app.logger.info(f"Kong consumer already exists for user: {user_email}")
                return existing_consumer['id']
            else:
                # This shouldn't happen if get_consumer worked, but handle it
                raise KongAdminAPIError("Unexpected status", status)
                
        except KongAdminAPIError as e:
            if e.status_code == 404:
                # Consumer doesn't exist, create it
                app.logger.info(f"Creating Kong consumer for new user: {user_email}")
                consumer_response, status = kong_api.create_consumer(
                    username=user_email,  # Use email as username
                    custom_id=kong_username_sanitized,  # Use sanitized username as custom_id
                    tags=["free"]
                )
                
                if status == 201:
                    kong_consumer_id = consumer_response['id']
                    app.logger.info(f"Successfully created Kong consumer {kong_consumer_id} for user: {user_email}")
                    
                    # Optionally create an API key for the user
                    try:
                        key_response, key_status = kong_api.create_consumer_key(user_email)
                        if key_status == 201:
                            app.logger.info(f"Created API key for user: {user_email}")
                        else:
                            app.logger.warning(f"Failed to create API key for user: {user_email} (status: {key_status})")
                    except KongAdminAPIError as key_error:
                        app.logger.warning(f"Failed to create API key for user {user_email}: {key_error.message}")
                    
                    return kong_consumer_id
                else:
                    app.logger.error(f"Failed to create Kong consumer for user: {user_email} (status: {status})")
                    return None
            else:
                # Some other error occurred
                app.logger.error(f"Kong API error for user {user_email}: {e.message}")
                return None
                
    except Exception as e:
        # Don't fail the login if Kong operations fail
        app.logger.error(f"Unexpected error creating Kong consumer for user {user_email}: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
