"""
Unit tests for authentication utilities
"""

import pytest
import jwt
import datetime
from unittest.mock import Mock, patch
from auth.auth_utils import (
    generate_jwt_token, 
    verify_jwt_token, 
    get_user_from_cookie, 
    get_user_from_header
)

class TestJWTFunctions:
    """Test JWT generation and verification functions"""
    
    def test_generate_jwt_token(self, app, sample_user_data):
        """Test JWT token generation"""
        with app.app_context():
            token = generate_jwt_token(sample_user_data)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 50  # JWT tokens are typically long
    
    def test_verify_jwt_token_valid(self, app, sample_user_data):
        """Test JWT token verification with valid token"""
        with app.app_context():
            token = generate_jwt_token(sample_user_data)
            payload = verify_jwt_token(token)
            
            assert payload is not None
            assert payload['email'] == sample_user_data['email']
            assert payload['name'] == sample_user_data['name']
            assert payload['user_id'] == sample_user_data['sub']
    
    def test_verify_jwt_token_invalid(self, app):
        """Test JWT token verification with invalid token"""
        with app.app_context():
            payload = verify_jwt_token('invalid_token')
            assert payload is None
    
    def test_verify_jwt_token_expired(self, app, sample_user_data):
        """Test JWT token verification with expired token"""
        with app.app_context():
            # Create expired token manually
            expired_payload = {
                'user_id': sample_user_data['sub'],
                'email': sample_user_data['email'],
                'name': sample_user_data['name'],
                'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1),  # Expired
                'iat': datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            }
            expired_token = jwt.encode(
                expired_payload, 
                app.config['JWT_SECRET_KEY'], 
                algorithm=app.config['JWT_ALGORITHM']
            )
            
            payload = verify_jwt_token(expired_token)
            assert payload is None

class TestCookieAuth:
    """Test cookie-based authentication functions"""
    
    def test_get_user_from_cookie_valid(self, app, valid_jwt_token):
        """Test getting user from valid cookie"""
        with app.test_request_context('/', headers={'Cookie': f'auth_token={valid_jwt_token}'}):
            user = get_user_from_cookie()
            assert user is not None
            assert user['email'] == 'test.user@example.com'
    
    def test_get_user_from_cookie_invalid(self, app):
        """Test getting user from invalid cookie"""
        with app.test_request_context('/', headers={'Cookie': 'auth_token=invalid_token'}):
            user = get_user_from_cookie()
            assert user is None
    
    def test_get_user_from_cookie_missing(self, app):
        """Test getting user when cookie is missing"""
        with app.test_request_context('/'):
            user = get_user_from_cookie()
            assert user is None

class TestHeaderAuth:
    """Test header-based authentication functions"""
    
    def test_get_user_from_header_valid(self, app, valid_jwt_token):
        """Test getting user from valid Authorization header"""
        with app.test_request_context('/', headers={'Authorization': f'Bearer {valid_jwt_token}'}):
            user = get_user_from_header()
            assert user is not None
            assert user['email'] == 'test.user@example.com'
    
    def test_get_user_from_header_invalid_format(self, app):
        """Test getting user from invalid header format"""
        with app.test_request_context('/', headers={'Authorization': 'InvalidFormat token'}):
            user = get_user_from_header()
            assert user is None
    
    def test_get_user_from_header_missing(self, app):
        """Test getting user when header is missing"""
        with app.test_request_context('/'):
            user = get_user_from_header()
            assert user is None
    
    def test_get_user_from_header_invalid_token(self, app):
        """Test getting user from header with invalid token"""
        with app.test_request_context('/', headers={'Authorization': 'Bearer invalid_token'}):
            user = get_user_from_header()
            assert user is None
