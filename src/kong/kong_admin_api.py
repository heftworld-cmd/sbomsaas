"""
Kong Admin API Client for server-to-server communication
Manages Kong Gateway Consumers and API Keys via Admin API
"""

import requests
import logging
import time
from typing import Tuple, Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class KongAdminAPIError(Exception):
    """Base exception for Kong Admin API errors"""
    
    def __init__(self, message: str, status_code: int, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(f"Kong API Error {status_code}: {message}")


class KongAdminAPI:
    """
    Kong Gateway Admin API client for managing Consumers and API Keys
    
    This class handles server-to-server communication with Kong Gateway
    for creating/managing consumers and their API keys.
    
    Example usage:
        kong = KongAdminAPI("http://localhost:8001")
        response, status = kong.create_consumer("johndoe", custom_id="cust_001")
        if status == 201:
            key_response, key_status = kong.create_consumer_key("johndoe")
    """
    
    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 30):
        """
        Initialize Kong Admin API client
        
        Args:
            base_url: Kong Admin API base URL (default: http://localhost:8001)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Configure session with retry strategy for 502/503 responses
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KongAdminAPI-Client/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, json_data: Dict = None) -> Tuple[Dict, int]:
        """
        Make HTTP request to Kong Admin API with logging and error handling
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (without base_url)
            json_data: Request payload for POST/PUT requests
            
        Returns:
            Tuple of (response_json, status_code)
            
        Raises:
            KongAdminAPIError: For 400/404/409 status codes with meaningful messages
        """
        url = f"{self.base_url}{endpoint}"
        
        # Log request details
        self.logger.info(f"Kong API Request: {method} {url}")
        if json_data:
            # Log payload but mask sensitive data
            safe_payload = {k: v for k, v in json_data.items()}
            if 'key' in safe_payload and safe_payload['key']:
                safe_payload['key'] = f"{safe_payload['key'][:8]}***"
            self.logger.debug(f"Request payload: {safe_payload}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                timeout=self.timeout
            )
            
            # Log response status
            self.logger.info(f"Kong API Response: {response.status_code} for {method} {url}")
            
            # Parse JSON response
            try:
                response_json = response.json()
                self.logger.debug(f"Response body: {response_json}")
            except ValueError:
                response_json = {"message": response.text or "Empty response"}
                self.logger.debug(f"Non-JSON response: {response.text}")
            
            # Handle specific error status codes with meaningful messages
            if response.status_code in [400, 404, 409]:
                error_message = self._extract_error_message(response_json, response.status_code)
                self.logger.error(f"Kong API error {response.status_code}: {error_message}")
                raise KongAdminAPIError(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=response_json
                )
            
            return response_json, response.status_code
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            self.logger.error(f"Kong API request exception: {error_msg}")
            raise KongAdminAPIError(
                message=error_msg,
                status_code=0,
                response_data={"original_error": str(e)}
            )
    
    def _extract_error_message(self, response_json: Dict, status_code: int) -> str:
        """Extract meaningful error message from Kong API response"""
        message = response_json.get('message', f'HTTP {status_code} error')
        
        # Enhance error messages based on status code
        if status_code == 400:
            if 'required' in message.lower():
                return f"Missing required field: {message}"
            elif 'invalid' in message.lower():
                return f"Invalid data provided: {message}"
            else:
                return f"Bad request: {message}"
        elif status_code == 404:
            return f"Resource not found: {message}"
        elif status_code == 409:
            if 'UNIQUE violation' in message:
                return f"Duplicate resource: {message}"
            else:
                return f"Conflict: {message}"
        
        return message
    
    def create_consumer(self, username: Optional[str] = None, custom_id: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> Tuple[Dict, int]:
        """
        Create a new consumer in Kong
        
        Args:
            username: Consumer username (required if custom_id not provided)
            custom_id: Custom ID for consumer (optional but must be unique)
            tags: List of tags for the consumer (optional)
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 201: {"id": "uuid", "username": "johndoe", ...}
            
        Raises:
            KongAdminAPIError: 
                - 400: Missing required field
                - 409: Duplicate username/custom_id
        """
        if not username and not custom_id:
            raise ValueError("Either username or custom_id must be provided")
        
        payload = {}
        if username:
            payload['username'] = username
        if custom_id:
            payload['custom_id'] = custom_id
        if tags:
            payload['tags'] = tags
        
        self.logger.info(f"Creating Kong consumer: username={username}, custom_id={custom_id}")
        return self._make_request('POST', '/consumers', payload)
    
    def get_consumer(self, username_or_id: str) -> Tuple[Dict, int]:
        """
        Retrieve consumer information by username or ID
        
        Args:
            username_or_id: Consumer username or UUID
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 200: {"id": "uuid", "username": "johndoe", ...}
            
        Raises:
            KongAdminAPIError: 404 if consumer not found
        """
        self.logger.info(f"Getting Kong consumer: {username_or_id}")
        return self._make_request('GET', f'/consumers/{username_or_id}')
    
    def create_consumer_key(self, username_or_id: str, key: Optional[str] = None) -> Tuple[Dict, int]:
        """
        Create an API key for a consumer
        
        Note: The key-auth plugin must be enabled for this to work
        
        Args:
            username_or_id: Consumer username or UUID
            key: Custom API key (optional, Kong will generate if not provided)
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 201: {
                "key": "custom-api-key-123",
                "consumer_id": "uuid",
                "id": "abcd...",
                "created_at": 1723456700000
              }
            
        Raises:
            KongAdminAPIError: 
                - 400: Invalid key format or duplicate key
                - 404: Consumer not found
        """
        payload = {}
        if key:
            payload['key'] = key
        
        self.logger.info(f"Creating API key for consumer: {username_or_id}")
        return self._make_request('POST', f'/consumers/{username_or_id}/key-auth', payload)
    
    def get_consumer_keys(self, username_or_id: str) -> Tuple[Dict, int]:
        """
        Get all API keys for a consumer
        
        Args:
            username_or_id: Consumer username or UUID
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 200: {
                "data": [
                  {
                    "key": "custom-api-key-123",
                    "id": "abcd...",
                    "created_at": 1723456700000
                  }
                ],
                "next": null
              }
            
        Raises:
            KongAdminAPIError: 404 if consumer not found
        """
        self.logger.info(f"Getting API keys for consumer: {username_or_id}")
        return self._make_request('GET', f'/consumers/{username_or_id}/key-auth')
    
    def delete_consumer(self, username_or_id: str) -> Tuple[Dict, int]:
        """
        Delete a consumer and all associated data
        
        Args:
            username_or_id: Consumer username or UUID
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 204: {} (empty response)
            
        Raises:
            KongAdminAPIError: 404 if consumer not found
        """
        self.logger.info(f"Deleting Kong consumer: {username_or_id}")
        return self._make_request('DELETE', f'/consumers/{username_or_id}')
    
    def delete_consumer_key(self, username_or_id: str, key_id: str) -> Tuple[Dict, int]:
        """
        Delete a specific API key for a consumer
        
        Args:
            username_or_id: Consumer username or UUID
            key_id: The ID of the key to delete
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 204: {} (empty response)
            
        Raises:
            KongAdminAPIError: 404 if consumer or key not found
        """
        self.logger.info(f"Deleting API key {key_id} for consumer: {username_or_id}")
        return self._make_request('DELETE', f'/consumers/{username_or_id}/key-auth/{key_id}')
    
    def health_check(self) -> Tuple[Dict, int]:
        """
        Check Kong Admin API health and connectivity
        
        Returns:
            Tuple of (response_json, status_code)
            - Success 200: Kong status information
        """
        self.logger.debug("Performing Kong health check")
        return self._make_request('GET', '/status')
    
    def list_consumers(self, size: int = 100, offset: Optional[str] = None) -> Tuple[Dict, int]:
        """
        List all consumers with pagination support
        
        Args:
            size: Number of consumers to return (default: 100)
            offset: Pagination offset (optional)
            
        Returns:
            Tuple of (response_json, status_code)
            - Success 200: {"data": [...], "next": "..."}
        """
        params = {'size': size}
        if offset:
            params['offset'] = offset
        
        endpoint = '/consumers'
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            endpoint = f"{endpoint}?{query_string}"
        
        self.logger.info(f"Listing consumers with size={size}")
        return self._make_request('GET', endpoint)
    
    def consumer_exists(self, username_or_id: str) -> bool:
        """
        Check if a consumer exists
        
        Args:
            username_or_id: Consumer username or UUID
            
        Returns:
            bool: True if consumer exists, False otherwise
        """
        try:
            _, status = self.get_consumer(username_or_id)
            return status == 200
        except KongAdminAPIError as e:
            if e.status_code == 404:
                return False
            raise  # Re-raise other errors


# Example usage for integration with your Flask app
class KongServiceManager:
    """
    High-level service for managing Kong consumers in your Flask application
    This wraps the KongAdminAPI with business logic specific to your SBOM SaaS app
    """
    
    def __init__(self, kong_base_url: str = "http://localhost:8001"):
        self.kong_api = KongAdminAPI(kong_base_url)
        self.logger = logging.getLogger(__name__)
    
    def provision_user_api_access(self, user_id: str, username: str, email: str) -> Dict[str, Any]:
        """
        Provision API access for a new user by creating Kong consumer and API key
        
        Args:
            user_id: Internal user ID
            username: User's username
            email: User's email
            
        Returns:
            Dict with success status, consumer_id, and api_key
        """
        try:
            # Create consumer using email as custom_id for uniqueness
            consumer_response, status = self.kong_api.create_consumer(
                username=username,
                custom_id=email,
                tags=["sbom-saas", "api-user", f"user-{user_id}"]
            )
            
            if status == 201:
                consumer_id = consumer_response['id']
                self.logger.info(f"Created Kong consumer {consumer_id} for user {user_id}")
                
                # Create API key for the consumer
                key_response, key_status = self.kong_api.create_consumer_key(username)
                
                if key_status == 201:
                    api_key = key_response['key']
                    self.logger.info(f"Created API key for user {user_id}")
                    
                    return {
                        'success': True,
                        'consumer_id': consumer_id,
                        'api_key': api_key,
                        'username': username,
                        'message': 'API access provisioned successfully'
                    }
                else:
                    self.logger.error(f"Failed to create API key for user {user_id}")
                    return {
                        'success': False,
                        'error': 'Failed to create API key',
                        'consumer_id': consumer_id
                    }
            else:
                self.logger.error(f"Failed to create Kong consumer for user {user_id}")
                return {
                    'success': False,
                    'error': 'Failed to create Kong consumer'
                }
                
        except KongAdminAPIError as e:
            self.logger.error(f"Kong API error for user {user_id}: {e}")
            
            # Handle duplicate consumer gracefully
            if e.status_code == 409:
                return {
                    'success': False,
                    'error': 'User already has API access',
                    'duplicate': True
                }
            
            return {
                'success': False,
                'error': f'Kong API error: {e.message}',
                'status_code': e.status_code
            }
        except Exception as e:
            self.logger.error(f"Unexpected error provisioning API access for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_user_api_keys(self, username: str) -> Dict[str, Any]:
        """
        Get all API keys for a user
        
        Args:
            username: User's username
            
        Returns:
            Dict with success status and keys list
        """
        try:
            keys_response, status = self.kong_api.get_consumer_keys(username)
            
            if status == 200:
                keys = keys_response.get('data', [])
                return {
                    'success': True,
                    'keys': [
                        {
                            'id': key['id'],
                            'key': key['key'],
                            'created_at': key.get('created_at'),
                            'consumer_id': key.get('consumer', {}).get('id')
                        }
                        for key in keys
                    ],
                    'count': len(keys)
                }
            
            return {'success': False, 'error': 'Failed to retrieve API keys'}
            
        except KongAdminAPIError as e:
            return {
                'success': False,
                'error': f'Kong API error: {e.message}',
                'status_code': e.status_code
            }
    
    def revoke_user_api_key(self, username: str, key_id: str) -> Dict[str, Any]:
        """
        Revoke a specific API key for a user
        
        Args:
            username: User's username
            key_id: ID of the key to revoke
            
        Returns:
            Dict with success status
        """
        try:
            response, status = self.kong_api.delete_consumer_key(username, key_id)
            
            if status == 204:
                self.logger.info(f"Revoked API key {key_id} for user {username}")
                return {
                    'success': True,
                    'message': 'API key revoked successfully'
                }
            
            return {'success': False, 'error': 'Failed to revoke API key'}
            
        except KongAdminAPIError as e:
            return {
                'success': False,
                'error': f'Kong API error: {e.message}',
                'status_code': e.status_code
            }
    
    def cleanup_user_access(self, username: str) -> Dict[str, Any]:
        """
        Remove all API access for a user (delete consumer and all keys)
        
        Args:
            username: User's username
            
        Returns:
            Dict with success status
        """
        try:
            response, status = self.kong_api.delete_consumer(username)
            
            if status == 204:
                self.logger.info(f"Deleted Kong consumer for user {username}")
                return {
                    'success': True,
                    'message': 'All API access removed successfully'
                }
            
            return {'success': False, 'error': 'Failed to remove API access'}
            
        except KongAdminAPIError as e:
            return {
                'success': False,
                'error': f'Kong API error: {e.message}',
                'status_code': e.status_code
            }
