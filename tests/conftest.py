"""
Pytest configuration and fixtures for SBOM SaaS tests
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app.app import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_EXPIRATION_HOURS'] = 24
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_kong_api():
    """Mock Kong Admin API for testing"""
    return Mock()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'sub': 'google_123456',
        'email': 'test.user@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/avatar.jpg'
    }

@pytest.fixture
def valid_jwt_token(app, sample_user_data):
    """Generate a valid JWT token for testing"""
    with app.app_context():
        from auth.auth_utils import generate_jwt_token
        return generate_jwt_token(sample_user_data)

@pytest.fixture
def auth_headers(valid_jwt_token):
    """Create authorization headers with valid token"""
    return {'Authorization': f'Bearer {valid_jwt_token}'}

@pytest.fixture
def mock_google_oauth():
    """Mock Google OAuth responses"""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get:
        
        # Mock token exchange
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'token_type': 'Bearer'
        }
        mock_post.return_value.status_code = 200
        
        # Mock user info
        mock_get.return_value.json.return_value = {
            'id': 'google_123456',
            'email': 'test.user@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        mock_get.return_value.status_code = 200
        
        yield mock_post, mock_get

@pytest.fixture
def mock_kong_success():
    """Mock successful Kong API responses"""
    with patch('kong.kong_admin_api.KongAdminAPI') as mock_kong:
        mock_instance = Mock()
        
        # Mock consumer creation/retrieval
        mock_instance.get_consumer.return_value = (
            {'id': 'consumer_123', 'username': 'test.user@example.com'}, 
            200
        )
        mock_instance.create_consumer.return_value = (
            {'id': 'consumer_123', 'username': 'test.user@example.com'}, 
            201
        )
        mock_instance.create_consumer_key.return_value = (
            {'id': 'key_123', 'key': 'test_api_key_123'}, 
            201
        )
        
        mock_kong.return_value = mock_instance
        yield mock_instance
