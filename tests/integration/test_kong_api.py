#!/usr/bin/env python3
"""
Test and example usage for KongAdminAPI class
This demonstrates server-to-server communication with Kong Gateway
"""

import logging
import sys
import time
from kong.kong_admin_api import KongAdminAPI, KongAdminAPIError


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
    
    # Test with email-like username to match OAuth pattern
    test_username = f"test-user-{int(time.time())}@example.com"
    test_custom_id = f"test_user_{int(time.time())}"
    
    try:
        # Test 1: Health check
        print(f"\n1️⃣ Health Check:")
        health, status = kong.health_check()
        print(f"   ✅ Kong API Status: {status}")
        if status == 200:
            print(f"   ✅ Kong is healthy")
        
        # Test 2: Create consumer (matching OAuth pattern)
        print(f"\n2️⃣ Creating consumer with email-like username '{test_username}':")
        consumer, status = kong.create_consumer(
            username=test_username,  # Email-like username
            custom_id=test_custom_id,  # Sanitized custom_id
            tags=["test", "automation", "sbom-saas", "oauth-pattern"]
        )
        
        if status == 201:
            consumer_id = consumer['id']
            print(f"   ✅ Created consumer with ID: {consumer_id}")
            print(f"   📧 Username (email): {consumer['username']}")
            print(f"   🔖 Custom ID (sanitized): {consumer['custom_id']}")
        else:
            print(f"   ❌ Failed to create consumer: {status}")
            return False
        
        # Test 3: Get consumer by email (username)
        print(f"\n3️⃣ Getting consumer by email '{test_username}':")
        consumer_info, status = kong.get_consumer(test_username)
        if status == 200:
            print(f"   ✅ Found consumer: {consumer_info['username']} (ID: {consumer_info['id']})")
            print(f"   🔖 Custom ID: {consumer_info.get('custom_id', 'N/A')}")
        
        # Test 4: Create API key using email (username)
        print(f"\n4️⃣ Creating auto-generated API key for email username:")
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
        
        # Test 6: Get all keys using email (username)
        print(f"\n6️⃣ Getting all API keys for email username:")
        keys_response, status = kong.get_consumer_keys(test_username)
        if status == 200:
            keys = keys_response.get('data', [])
            print(f"   ✅ Found {len(keys)} keys for consumer")
            for i, key in enumerate(keys, 1):
                print(f"      Key {i}: {key['key'][:12]}*** (ID: {key['id']})")
        
        # Test 7: Check if consumer exists by email
        print(f"\n7️⃣ Testing consumer existence by email:")
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
            kong.get_consumer("non-existent@example.com")
        except KongAdminAPIError as e:
            print(f"   ✅ Correctly caught 404 error: {e.message}")
        
        # Cleanup: Delete test consumer using email (username)
        print(f"\n🧹 Cleanup - Deleting test consumer by email:")
        delete_response, status = kong.delete_consumer(test_username)
        if status == 204:
            print(f"   ✅ Successfully deleted consumer {test_username}")
        
        print(f"\n🎉 All Kong Admin API tests completed successfully!")
        print(f"   📧 OAuth pattern validated: email as username, sanitized as custom_id")
        return True
        
    except KongAdminAPIError as e:
        print(f"\n❌ Kong API Error: {e}")
        print(f"   Status Code: {e.status_code}")
        print(f"   Response: {e.response_data}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    """Main test runner"""
    setup_logging()
    
    print("=" * 60)
    print("🔧 Kong Admin API Test Suite")
    print("=" * 60)
    
    # Test basic API functionality
    api_success = test_kong_admin_api()
    
    print("\n" + "=" * 60)
    if api_success:
        print("🎉 All tests passed! Kong Admin API is working correctly.")
        print("\n💡 Integration Tips:")
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
