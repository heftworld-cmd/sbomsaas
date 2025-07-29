"""
API endpoint tests
"""

import pytest
import json
from unittest.mock import patch
from tests.fixtures.sample_data import SAMPLE_USERS, OAUTH_TEST_DATA

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_api_profile_unauthorized(self, client):
        """Test API profile endpoint without authentication"""
        response = client.get('/api/profile')
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Authentication required'
    
    def test_api_profile_authorized(self, client, auth_headers):
        """Test API profile endpoint with valid authentication"""
        response = client.get('/api/profile', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'email' in data
        assert data['email'] == 'test.user@example.com'
    
    def test_api_protected_unauthorized(self, client):
        """Test protected API endpoint without authentication"""
        response = client.get('/api/protected')
        assert response.status_code == 401
    
    def test_api_protected_authorized(self, client, auth_headers):
        """Test protected API endpoint with valid authentication"""
        response = client.get('/api/protected', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'user' in data
        assert 'timestamp' in data
    
    def test_api_data_unauthorized(self, client):
        """Test data API endpoint without authentication"""
        response = client.get('/api/data')
        assert response.status_code == 401
    
    def test_api_data_authorized(self, client, auth_headers):
        """Test data API endpoint with valid authentication"""
        response = client.get('/api/data', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
    
    def test_api_get_auth_token_unauthorized(self, client):
        """Test get auth token endpoint without cookie authentication"""
        response = client.get('/api/get-auth-token')
        assert response.status_code == 302  # Redirect to login

class TestWebRoutes:
    """Test web routes"""
    
    def test_index_anonymous(self, client):
        """Test index page for anonymous user"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_route(self, client):
        """Test login route"""
        response = client.get('/login')
        assert response.status_code == 302  # Redirect to Google OAuth
        
        # Check that it redirects to Google
        location = response.headers.get('Location')
        assert 'accounts.google.com' in location or 'oauth' in location
    
    def test_logout_route(self, client):
        """Test logout route"""
        response = client.get('/logout')
        assert response.status_code == 302  # Redirect to index
        
        # Check that auth token cookie is cleared
        set_cookie = response.headers.get('Set-Cookie')
        assert 'auth_token=;' in set_cookie
    
    @patch('app.app.create_or_get_kong_consumer')
    def test_oauth_callback_success(self, mock_kong, client, mock_google_oauth):
        """Test successful OAuth callback"""
        mock_kong.return_value = 'consumer_123'
        
        # Set up session state
        with client.session_transaction() as session:
            session['oauth_state'] = 'test_state_456'
        
        response = client.get('/callback?code=test_code&state=test_state_456')
        
        # Should redirect to dashboard
        assert response.status_code == 302
        assert '/dashboard' in response.headers.get('Location')
        
        # Should set auth token cookie
        set_cookie = response.headers.get('Set-Cookie')
        assert 'auth_token=' in set_cookie
    
    def test_oauth_callback_invalid_state(self, client):
        """Test OAuth callback with invalid state"""
        with client.session_transaction() as session:
            session['oauth_state'] = 'valid_state'
        
        response = client.get('/callback?code=test_code&state=invalid_state')
        assert response.status_code == 400
    
    def test_oauth_callback_missing_code(self, client):
        """Test OAuth callback with missing authorization code"""
        with client.session_transaction() as session:
            session['oauth_state'] = 'test_state'
        
        response = client.get('/callback?state=test_state')
        assert response.status_code == 400

class TestErrorHandlers:
    """Test error handlers"""
    
    def test_404_error(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
