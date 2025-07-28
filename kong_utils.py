"""
Utility functions for Kong integration with your Flask SBOM SaaS app
These functions help manage user API access in your application
"""

from kong_admin_api import KongAdminAPI, KongAdminAPIError
from flask import current_app
import logging


def get_kong_api():
    """Get configured Kong API instance"""
    kong_url = current_app.config.get('KONG_ADMIN_URL', 'http://localhost:8001')
    return KongAdminAPI(kong_url)


def email_to_kong_username(email):
    """Convert email to Kong-compatible username"""
    return email.split('@')[0].replace('.', '_').replace('+', '_')


def get_user_api_keys(user_email):
    """
    Get API keys for a user by email
    
    Args:
        user_email: User's email address
        
    Returns:
        dict: {'success': bool, 'keys': list, 'error': str}
    """
    try:
        kong_api = get_kong_api()
        kong_username = email_to_kong_username(user_email)
        
        keys_response, status = kong_api.get_consumer_keys(kong_username)
        
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
        else:
            return {
                'success': False,
                'error': f'Unexpected status: {status}',
                'keys': []
            }
            
    except KongAdminAPIError as e:
        current_app.logger.error(f"Kong API error getting keys for {user_email}: {e.message}")
        return {
            'success': False,
            'error': f'Kong API error: {e.message}',
            'keys': []
        }
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting keys for {user_email}: {str(e)}")
        return {
            'success': False,
            'error': 'Internal error',
            'keys': []
        }


def create_user_api_key(user_email, custom_key=None):
    """
    Create a new API key for a user
    
    Args:
        user_email: User's email address
        custom_key: Optional custom API key string
        
    Returns:
        dict: {'success': bool, 'key': str, 'key_id': str, 'error': str}
    """
    try:
        kong_api = get_kong_api()
        kong_username = email_to_kong_username(user_email)
        
        key_response, status = kong_api.create_consumer_key(kong_username, custom_key)
        
        if status == 201:
            return {
                'success': True,
                'key': key_response['key'],
                'key_id': key_response['id'],
                'consumer_id': key_response.get('consumer', {}).get('id')
            }
        else:
            return {
                'success': False,
                'error': f'Failed to create API key (status: {status})'
            }
            
    except KongAdminAPIError as e:
        current_app.logger.error(f"Kong API error creating key for {user_email}: {e.message}")
        return {
            'success': False,
            'error': f'Kong API error: {e.message}'
        }
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating key for {user_email}: {str(e)}")
        return {
            'success': False,
            'error': 'Internal error'
        }


def revoke_user_api_key(user_email, key_id):
    """
    Revoke a specific API key for a user
    
    Args:
        user_email: User's email address
        key_id: ID of the key to revoke
        
    Returns:
        dict: {'success': bool, 'error': str}
    """
    try:
        kong_api = get_kong_api()
        kong_username = email_to_kong_username(user_email)
        
        response, status = kong_api.delete_consumer_key(kong_username, key_id)
        
        if status == 204:
            current_app.logger.info(f"Revoked API key {key_id} for user {user_email}")
            return {
                'success': True,
                'message': 'API key revoked successfully'
            }
        else:
            return {
                'success': False,
                'error': f'Failed to revoke API key (status: {status})'
            }
            
    except KongAdminAPIError as e:
        current_app.logger.error(f"Kong API error revoking key for {user_email}: {e.message}")
        return {
            'success': False,
            'error': f'Kong API error: {e.message}'
        }
    except Exception as e:
        current_app.logger.error(f"Unexpected error revoking key for {user_email}: {str(e)}")
        return {
            'success': False,
            'error': 'Internal error'
        }


def get_user_kong_info(user_email):
    """
    Get complete Kong information for a user (consumer + keys)
    
    Args:
        user_email: User's email address
        
    Returns:
        dict: Complete user Kong information
    """
    try:
        kong_api = get_kong_api()
        kong_username = email_to_kong_username(user_email)
        
        # Get consumer info
        consumer_response, consumer_status = kong_api.get_consumer(kong_username)
        
        if consumer_status == 200:
            # Get API keys
            keys_info = get_user_api_keys(user_email)
            
            return {
                'success': True,
                'consumer': {
                    'id': consumer_response['id'],
                    'username': consumer_response['username'],
                    'custom_id': consumer_response.get('custom_id'),
                    'tags': consumer_response.get('tags', []),
                    'created_at': consumer_response.get('created_at')
                },
                'api_keys': keys_info['keys'] if keys_info['success'] else [],
                'key_count': len(keys_info['keys']) if keys_info['success'] else 0
            }
        else:
            return {
                'success': False,
                'error': 'User not found in Kong',
                'consumer': None,
                'api_keys': []
            }
            
    except KongAdminAPIError as e:
        if e.status_code == 404:
            return {
                'success': False,
                'error': 'User not found in Kong',
                'consumer': None,
                'api_keys': []
            }
        else:
            current_app.logger.error(f"Kong API error getting info for {user_email}: {e.message}")
            return {
                'success': False,
                'error': f'Kong API error: {e.message}',
                'consumer': None,
                'api_keys': []
            }
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting Kong info for {user_email}: {str(e)}")
        return {
            'success': False,
            'error': 'Internal error',
            'consumer': None,
            'api_keys': []
        }
