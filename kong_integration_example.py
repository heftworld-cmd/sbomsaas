"""
Integration example for Kong Admin API with your Flask SBOM SaaS application

This shows how to integrate Kong API management into your existing authentication flow
without exposing Kong endpoints to end users.
"""

from kong_admin_api import KongServiceManager, KongAdminAPIError
import logging


class UserAPIService:
    """
    Service layer for managing user API access in your SBOM SaaS application
    This integrates with your existing authentication system
    """
    
    def __init__(self, kong_base_url: str = "http://localhost:8001"):
        self.kong_service = KongServiceManager(kong_base_url)
        self.logger = logging.getLogger(__name__)
    
    def setup_user_api_access(self, user_data: dict) -> dict:
        """
        Set up API access for a newly authenticated user
        Call this after successful OAuth login
        
        Args:
            user_data: User data from JWT token containing user_id, email, name
            
        Returns:
            Dict with API key information or error details
        """
        user_id = user_data.get('user_id')
        email = user_data.get('email')
        name = user_data.get('name', '')
        
        # Create username from email (remove @ and special chars)
        username = email.split('@')[0].replace('.', '_').replace('+', '_')
        
        self.logger.info(f"Setting up API access for user {user_id} ({email})")
        
        try:
            result = self.kong_service.provision_user_api_access(
                user_id=user_id,
                username=username,
                email=email
            )
            
            if result['success']:
                self.logger.info(f"API access provisioned for user {user_id}")
                return {
                    'success': True,
                    'api_key': result['api_key'],
                    'consumer_id': result['consumer_id'],
                    'username': username
                }
            else:
                # Handle duplicate gracefully
                if result.get('duplicate'):
                    self.logger.info(f"User {user_id} already has API access")
                    # Try to get existing keys
                    keys_result = self.kong_service.get_user_api_keys(username)
                    if keys_result['success'] and keys_result['keys']:
                        return {
                            'success': True,
                            'api_key': keys_result['keys'][0]['key'],
                            'username': username,
                            'existing': True
                        }
                
                self.logger.error(f"Failed to provision API access for user {user_id}: {result['error']}")
                return {
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            self.logger.error(f"Unexpected error setting up API access for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Internal error setting up API access'
            }
    
    def get_user_api_info(self, email: str) -> dict:
        """
        Get API key information for a user
        
        Args:
            email: User's email address
            
        Returns:
            Dict with API keys and usage information
        """
        username = email.split('@')[0].replace('.', '_').replace('+', '_')
        
        try:
            result = self.kong_service.get_user_api_keys(username)
            
            if result['success']:
                return {
                    'success': True,
                    'username': username,
                    'keys': result['keys'],
                    'key_count': result['count']
                }
            else:
                return {
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            self.logger.error(f"Error getting API info for {email}: {e}")
            return {
                'success': False,
                'error': 'Failed to retrieve API information'
            }
    
    def regenerate_user_api_key(self, email: str) -> dict:
        """
        Regenerate API key for a user (revoke old, create new)
        
        Args:
            email: User's email address
            
        Returns:
            Dict with new API key or error details
        """
        username = email.split('@')[0].replace('.', '_').replace('+', '_')
        
        try:
            # Get existing keys
            keys_result = self.kong_service.get_user_api_keys(username)
            
            if keys_result['success']:
                # Revoke existing keys
                for key in keys_result['keys']:
                    revoke_result = self.kong_service.revoke_user_api_key(username, key['id'])
                    if revoke_result['success']:
                        self.logger.info(f"Revoked API key {key['id']} for {email}")
                
                # Create new key
                user_data = {'user_id': username, 'email': email}
                return self.setup_user_api_access(user_data)
            
            return {
                'success': False,
                'error': 'No existing API keys found'
            }
            
        except Exception as e:
            self.logger.error(f"Error regenerating API key for {email}: {e}")
            return {
                'success': False,
                'error': 'Failed to regenerate API key'
            }
    
    def revoke_user_access(self, email: str) -> dict:
        """
        Completely revoke API access for a user
        
        Args:
            email: User's email address
            
        Returns:
            Dict with success status
        """
        username = email.split('@')[0].replace('.', '_').replace('+', '_')
        
        try:
            result = self.kong_service.cleanup_user_access(username)
            
            if result['success']:
                self.logger.info(f"Revoked all API access for {email}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error revoking API access for {email}: {e}")
            return {
                'success': False,
                'error': 'Failed to revoke API access'
            }


# Example integration with your existing Flask app
def integrate_with_flask_app():
    """
    Example of how to integrate Kong API management with your existing Flask routes
    Add these calls to your existing route handlers
    """
    
    # Initialize the API service
    api_service = UserAPIService("http://localhost:8001")
    
    # Example: In your OAuth callback handler, after successful login
    def after_successful_oauth_login(user_data):
        """
        Add this to your existing callback() function in app.py
        """
        # Your existing JWT creation code...
        
        # NEW: Set up API access for the user
        api_result = api_service.setup_user_api_access(user_data)
        
        if api_result['success']:
            # Optionally store API key info in session or database
            api_key = api_result['api_key']
            # You could add this to your JWT payload or store separately
            print(f"User {user_data['email']} API key: {api_key}")
        else:
            # Log error but don't fail the login
            print(f"Warning: Failed to set up API access: {api_result['error']}")
        
        # Continue with your existing redirect logic...
    
    # Example: In your dashboard route, show API key information
    def enhanced_dashboard(user):
        """
        Add this to your existing dashboard() function in app.py
        """
        # Your existing dashboard logic...
        
        # NEW: Get user's API information
        api_info = api_service.get_user_api_info(user['email'])
        
        if api_info['success']:
            # Pass API key info to template
            api_keys = api_info['keys']
            # You can now show API keys in your dashboard template
        
        # Continue with existing render_template call, adding api_keys...
    
    # Example: New internal function for admin operations
    def admin_revoke_user_api_access(user_email):
        """
        Admin function to revoke user's API access
        This would be called from admin interface, not exposed to end users
        """
        result = api_service.revoke_user_access(user_email)
        
        if result['success']:
            return {'status': 'success', 'message': f'API access revoked for {user_email}'}
        else:
            return {'status': 'error', 'message': result['error']}


# Example configuration for your config.py
def add_kong_config():
    """
    Add these settings to your config.py file
    """
    kong_config = """
    # Kong Gateway configuration
    KONG_ADMIN_URL = os.getenv('KONG_ADMIN_URL', 'http://localhost:8001')
    KONG_GATEWAY_URL = os.getenv('KONG_GATEWAY_URL', 'http://localhost:8000')  # For API requests
    KONG_API_KEY_HEADER = 'X-API-Key'  # Header name for API key authentication
    """
    print("Add this to your Config class in config.py:")
    print(kong_config)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Test the integration service
    api_service = UserAPIService("http://localhost:8001")
    
    # Simulate user data from OAuth
    test_user = {
        'user_id': 'user123',
        'email': 'test.user@example.com',
        'name': 'Test User'
    }
    
    print("🧪 Testing User API Service integration...")
    
    # Test setting up API access
    result = api_service.setup_user_api_access(test_user)
    print(f"Setup result: {result}")
    
    if result['success']:
        # Test getting API info
        info_result = api_service.get_user_api_info(test_user['email'])
        print(f"API info: {info_result}")
        
        # Test regenerating API key
        regen_result = api_service.regenerate_user_api_key(test_user['email'])
        print(f"Regenerate result: {regen_result}")
        
        # Cleanup
        revoke_result = api_service.revoke_user_access(test_user['email'])
        print(f"Revoke result: {revoke_result}")
    
    print("\n💡 Integration example completed!")
    print("   Add the UserAPIService to your Flask app to manage API access")
    print("   Call setup_user_api_access() after successful OAuth login")
    print("   Use get_user_api_info() in your dashboard to show API keys")
