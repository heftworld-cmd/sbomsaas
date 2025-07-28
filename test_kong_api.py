#!/usr/bin/env python3
"""
Test and example usage for KongAdminAPI class
This demonstrates server-to-server communication with Kong Gateway
"""

import logging
import sys
import time
from kong_admin_api import KongAdminAPI, KongAdminAPIError, KongServiceManager


def setup_logging():
    """Configure logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_kong_admin_api():
    """Test Kong Admin API basic functionality"""
    
    print("🔍 Testing Kong Admin API...")
    
    # Initialize Kong API client
    kong = KongAdminAPI("http://localhost:8001/")
    
    test_username = f"test-user-{int(time.time())}"
    test_custom_id = f"test_cust_{int(time.time())}"
    
    try:
        # Test 1: Health check
        print(f"\n1️⃣ Health Check:")
        health, status = kong.health_check()
        print(f"   ✅ Kong API Status: {status}")
        if status == 200:
            print(f"   ✅ Kong is healthy")
        
        # Test 2: Create consumer
        print(f"\n2️⃣ Creating consumer '{test_username}':")
        consumer, status = kong.create_consumer(
            username=test_username,
            custom_id=test_custom_id,
            tags=["test", "automation", "sbom-saas"]
        )
        
        if status == 201:
            consumer_id = consumer['id']
            print(f"   ✅ Created consumer with ID: {consumer_id}")
        else:
            print(f"   ❌ Failed to create consumer: {status}")
            return False
        
        # Test 3: Get consumer
        print(f"\n3️⃣ Getting consumer '{test_username}':")
        consumer_info, status = kong.get_consumer(test_username)
        if status == 200:
            print(f"   ✅ Found consumer: {consumer_info['username']} (ID: {consumer_info['id']})")
        
        # Test 4: Create API key (auto-generated)
        print(f"\n4️⃣ Creating auto-generated API key:")
        key_response, status = kong.create_consumer_key(test_username)
        if status == 201:
            api_key = key_response['key']
            key_id = key_response['id']
            print(f"   ✅ Created key: {api_key[:12]}***")
        else:
            print(f"   ⚠️  Failed to create key (key-auth plugin may not be enabled): {status}")
            key_id = None
        
        # Test 5: Create custom API key
        print(f"\n5️⃣ Creating custom API key:")
        custom_key = f"test-key-{int(time.time())}"
        try:
            key_response2, status = kong.create_consumer_key(test_username, custom_key)
            if status == 201:
                print(f"   ✅ Created custom key: {key_response2['key']}")
        except KongAdminAPIError as e:
            if e.status_code == 400:
                print(f"   ⚠️  Custom key failed (may be duplicate or invalid): {e.message}")
            else:
                raise
        
        # Test 6: Get all keys
        print(f"\n6️⃣ Getting all API keys:")
        keys_response, status = kong.get_consumer_keys(test_username)
        if status == 200:
            keys = keys_response.get('data', [])
            print(f"   ✅ Found {len(keys)} keys for consumer")
            for i, key in enumerate(keys, 1):
                print(f"      Key {i}: {key['key'][:12]}*** (ID: {key['id']})")
        
        # Test 7: Check if consumer exists
        print(f"\n7️⃣ Testing consumer existence:")
        exists = kong.consumer_exists(test_username)
        print(f"   ✅ Consumer exists: {exists}")
        
        # Test 8: Delete a key (if we have one)
        if key_id:
            print(f"\n8️⃣ Deleting API key:")
            delete_response, status = kong.delete_consumer_key(test_username, key_id)
            if status == 204:
                print(f"   ✅ Successfully deleted key {key_id}")
        
        # Test 9: Error handling - try to get non-existent consumer
        print(f"\n9️⃣ Testing error handling:")
        try:
            kong.get_consumer("non-existent-user-12345")
        except KongAdminAPIError as e:
            print(f"   ✅ Correctly caught 404 error: {e.message}")
        
        # Cleanup: Delete test consumer
        print(f"\n🧹 Cleanup - Deleting test consumer:")
        delete_response, status = kong.delete_consumer(test_username)
        if status == 204:
            print(f"   ✅ Successfully deleted consumer {test_username}")
        
        print(f"\n🎉 All Kong Admin API tests completed successfully!")
        return True
        
    except KongAdminAPIError as e:
        print(f"\n❌ Kong API Error: {e}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Response: {e.response_data}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def test_kong_service_manager():
    """Test the high-level KongServiceManager"""
    
    print(f"\n\n🏢 Testing Kong Service Manager...")
    
    service_manager = KongServiceManager("http://localhost:8001")
    
    test_user_id = f"user_{int(time.time())}"
    test_username = f"testuser_{int(time.time())}"
    test_email = f"test{int(time.time())}@example.com"
    
    try:
        # Test provisioning API access
        print(f"\n1️⃣ Provisioning API access for user:")
        result = service_manager.provision_user_api_access(
            user_id=test_user_id,
            username=test_username,
            email=test_email
        )
        
        if result['success']:
            print(f"   ✅ API access provisioned successfully")
            print(f"   Consumer ID: {result['consumer_id']}")
            print(f"   API Key: {result['api_key'][:12]}***")
        else:
            print(f"   ❌ Failed to provision API access: {result['error']}")
            return False
        
        # Test getting user API keys
        print(f"\n2️⃣ Getting user API keys:")
        keys_result = service_manager.get_user_api_keys(test_username)
        
        if keys_result['success']:
            print(f"   ✅ Found {keys_result['count']} API keys")
            if keys_result['keys']:
                key_to_revoke = keys_result['keys'][0]['id']
        else:
            print(f"   ❌ Failed to get API keys: {keys_result['error']}")
            return False
        
        # Test revoking an API key
        if 'key_to_revoke' in locals():
            print(f"\n3️⃣ Revoking API key:")
            revoke_result = service_manager.revoke_user_api_key(test_username, key_to_revoke)
            
            if revoke_result['success']:
                print(f"   ✅ API key revoked successfully")
            else:
                print(f"   ❌ Failed to revoke API key: {revoke_result['error']}")
        
        # Cleanup: Remove all user access
        print(f"\n🧹 Cleanup - Removing all user access:")
        cleanup_result = service_manager.cleanup_user_access(test_username)
        
        if cleanup_result['success']:
            print(f"   ✅ All user access removed successfully")
        else:
            print(f"   ❌ Failed to cleanup user access: {cleanup_result['error']}")
        
        print(f"\n🎉 Kong Service Manager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Service Manager error: {e}")
        return False


def main():
    """Main test runner"""
    setup_logging()
    
    print("=" * 60)
    print("🔧 Kong Admin API Test Suite")
    print("=" * 60)
    
    # Test basic API functionality
    api_success = test_kong_admin_api()
    
    if api_success:
        # Test high-level service manager
        service_success = test_kong_service_manager()
    else:
        print("\n⚠️  Skipping Service Manager tests due to API test failures")
        service_success = False
    
    print("\n" + "=" * 60)
    if api_success and service_success:
        print("🎉 All tests passed! Kong Admin API is working correctly.")
        print("\n💡 Integration Tips:")
        print("   - Use KongServiceManager in your Flask app for high-level operations")
        print("   - Use KongAdminAPI directly for fine-grained control")
        print("   - Make sure Kong Gateway is running with key-auth plugin enabled")
        print("   - Check Kong Admin API logs for detailed request/response info")
    else:
        print("❌ Some tests failed. Check Kong Gateway configuration.")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure Kong Gateway is running on http://localhost:8001")
        print("   - Enable the key-auth plugin: kong config key-auth")
        print("   - Check Kong Gateway logs for errors")
    print("=" * 60)


if __name__ == "__main__":
    main()
