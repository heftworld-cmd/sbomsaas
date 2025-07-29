"""
Unit tests for Kong Admin API
"""

import pytest
from unittest.mock import Mock, patch
from kong.kong_admin_api import KongAdminAPI, KongAdminAPIError

class TestKongAdminAPI:
    """Test Kong Admin API functionality"""
    
    def test_init(self):
        """Test KongAdminAPI initialization"""
        kong = KongAdminAPI("http://localhost:8001")
        assert kong.base_url == "http://localhost:8001"
    
    def test_health_check_success(self):
        """Test successful health check"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"database": {"reachable": True}}  # Kong status format
            mock_response.status_code = 200
            mock_request.return_value = mock_response
            
            response, status = kong.health_check()
            
            assert status == 200
            assert "database" in response
    
    def test_create_consumer_success(self):
        """Test successful consumer creation"""
        kong = KongAdminAPI("http://localhost:8001")
        
        # Mock the session.request method directly
        with patch.object(kong.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "consumer_123",
                "username": "test@example.com",
                "custom_id": "test_user"
            }
            mock_response.status_code = 201
            mock_request.return_value = mock_response
            
            response, status = kong.create_consumer(
                username="test@example.com", 
                custom_id="test_user",
                tags=["free"]
            )
            
            assert status == 201
            assert response["username"] == "test@example.com"
            assert response["custom_id"] == "test_user"
    
    def test_get_consumer_success(self):
        """Test successful consumer retrieval"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "consumer_123",
                "username": "test@example.com"
            }
            mock_response.status_code = 200
            mock_request.return_value = mock_response
            
            response, status = kong.get_consumer("test@example.com")
            
            assert status == 200
            assert response["username"] == "test@example.com"
    
    def test_get_consumer_not_found(self):
        """Test consumer not found"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"message": "Not found"}
            mock_response.status_code = 404
            mock_request.return_value = mock_response
            
            with pytest.raises(KongAdminAPIError) as exc_info:
                kong.get_consumer("nonexistent@example.com")
            
            assert exc_info.value.status_code == 404
    
    def test_create_consumer_key_success(self):
        """Test successful API key creation"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong.session, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {
                "id": "key_123",
                "key": "api_key_abcdef123456"
            }
            mock_response.status_code = 201
            mock_request.return_value = mock_response
            
            response, status = kong.create_consumer_key("test@example.com")
            
            assert status == 201
            assert "key" in response
            # Don't assert specific ID since Kong might generate UUIDs
    
    def test_consumer_exists_true(self):
        """Test consumer_exists returns True for existing consumer"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong, 'get_consumer') as mock_get:
            mock_get.return_value = ({"id": "consumer_123"}, 200)
            
            exists = kong.consumer_exists("test@example.com")
            assert exists is True
    
    def test_consumer_exists_false(self):
        """Test consumer_exists returns False for non-existing consumer"""
        kong = KongAdminAPI("http://localhost:8001")
        
        with patch.object(kong, 'get_consumer') as mock_get:
            mock_get.side_effect = KongAdminAPIError("Not found", 404, {})
            
            exists = kong.consumer_exists("test@example.com")
            assert exists is False

class TestKongAdminAPIError:
    """Test KongAdminAPIError exception"""
    
    def test_error_creation(self):
        """Test creating KongAdminAPIError"""
        error = KongAdminAPIError("Test error", 400, {"detail": "Bad request"})
        
        assert str(error) == "Kong API Error 400: Test error"
        assert error.status_code == 400
        assert error.response_data == {"detail": "Bad request"}
        assert error.message == "Test error"
