import datetime
from flask import Blueprint, request, jsonify
from auth_utils import login_required_api, login_required_cookie

# Create API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/get-auth-token')
@login_required_cookie
def api_get_auth_token(user):
    """API endpoint to get current user's JWT token for frontend use"""
    token = request.cookies.get('auth_token')
    return jsonify({'token': token})

@api_bp.route('/profile')
@login_required_api
def api_profile(user):
    """API endpoint to get user profile - requires Bearer token"""
    return jsonify({
        'user_id': user.get('user_id'),
        'email': user.get('email'),
        'name': user.get('name'),
        'picture': user.get('picture')
    })

@api_bp.route('/protected')
@login_required_api
def api_protected(user):
    """Example protected API endpoint - requires Bearer token"""
    return jsonify({
        'message': 'This is a protected API endpoint',
        'user': user.get('email'),
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

@api_bp.route('/data')
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
