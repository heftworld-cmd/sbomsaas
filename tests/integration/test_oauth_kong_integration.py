#!/usr/bin/env python3
"""
Test Kong integration with Flask OAuth callback
This simulates the OAuth flow and tests Kong consumer creation
"""

import sys
import logging
from kong.kong_admin_api import KongAdminAPI, KongAdminAPIError

def test_kong_user_creation():
    """Test creating Kong consumers for OAuth users"""
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Kong API
    kong_api = KongAdminAPI("http://localhost:8001")
    
    # Simulate user data from OAuth callback
    test_users = [
        {
            'email': 'test.user@example.com',
            'name': 'Test User',
            'id': 'google_123456'
        },
        {
            'email': 'jane.doe+work@company.com',
            'name': 'Jane Doe',
            'id': 'google_789012'
        }
    ]
    
    print("🧪 Testing Kong OAuth User Integration...")
    
    for user_info in test_users:
        print(f"\n👤 Processing user: {user_info['email']}")
        
        try:
            # Updated logic: email as username, sanitized username as custom_id
            kong_username_sanitized = user_info['email'].split('@')[0].replace('.', '_').replace('+', '_')
            print(f"   Kong username (email): {user_info['email']}")
            print(f"   Kong custom_id (sanitized): {kong_username_sanitized}")
            
            # Check if consumer already exists (using email as username)
            try:
                existing_consumer, status = kong_api.get_consumer(user_info['email'])
                if status == 200:
                    print(f"   ✅ Consumer already exists: {existing_consumer['id']}")
                    kong_consumer_id = existing_consumer['id']
                else:
                    raise KongAdminAPIError("Unexpected status", status)
                    
            except KongAdminAPIError as e:
                if e.status_code == 404:
                    # Consumer doesn't exist, create it
                    print(f"   🔄 Creating new Kong consumer...")
                    consumer_response, status = kong_api.create_consumer(
                        username=user_info['email'],  # Use email as username
                        custom_id=kong_username_sanitized,  # Use sanitized username as custom_id
                        tags=["sbom-saas", "oauth-user", "auto-created", "test"]
                    )
                    
                    if status == 201:
                        kong_consumer_id = consumer_response['id']
                        print(f"   ✅ Created Kong consumer: {kong_consumer_id}")
                        
                        # Create an API key for the user (using email as username)
                        try:
                            key_response, key_status = kong_api.create_consumer_key(user_info['email'])
                            if key_status == 201:
                                api_key = key_response['key']
                                print(f"   ✅ Created API key: {api_key[:12]}***")
                            else:
                                print(f"   ⚠️  Failed to create API key (status: {key_status})")
                        except KongAdminAPIError as key_error:
                            print(f"   ⚠️  Failed to create API key: {key_error.message}")
                    else:
                        print(f"   ❌ Failed to create Kong consumer (status: {status})")
                        kong_consumer_id = None
                else:
                    print(f"   ❌ Kong API error: {e.message}")
                    kong_consumer_id = None
            
            if kong_consumer_id:
                print(f"   ✅ User {user_info['email']} has Kong consumer: {kong_consumer_id}")
            else:
                print(f"   ❌ Failed to ensure Kong consumer for {user_info['email']}")
                
        except Exception as e:
            print(f"   ❌ Unexpected error for user {user_info['email']}: {str(e)}")
    
    print(f"\n🧹 Cleanup - Removing test consumers:")
    for user_info in test_users:
        # Use email as username for deletion
        try:
            delete_response, status = kong_api.delete_consumer(user_info['email'])
            if status == 204:
                print(f"   ✅ Deleted test consumer: {user_info['email']}")
            else:
                print(f"   ⚠️  Failed to delete consumer {user_info['email']} (status: {status})")
        except KongAdminAPIError as e:
            if e.status_code == 404:
                print(f"   ℹ️  Consumer {user_info['email']} not found (already deleted)")
            else:
                print(f"   ❌ Error deleting consumer {user_info['email']}: {e.message}")
    
    print(f"\n🎉 Kong OAuth integration test completed!")

def test_username_conversion():
    """Test email to Kong username conversion logic"""
    
    print("\n📧 Testing email to Kong username conversion:")
    print("   New pattern: email as username, sanitized email as custom_id")
    
    test_emails = [
        'user@example.com',
        'test.user@domain.com',
        'jane.doe+work@company.org',
        'special+tag@email-domain.co.uk',
        'simple@test.io'
    ]
    
    for email in test_emails:
        kong_username_sanitized = email.split('@')[0].replace('.', '_').replace('+', '_')
        print(f"   {email} → username: {email}, custom_id: {kong_username_sanitized}")

if __name__ == "__main__":
    test_username_conversion()
    
    try:
        test_kong_user_creation()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure Kong Gateway is running on localhost:8001")
        print("   and the key-auth plugin is enabled.")
        sys.exit(1)
