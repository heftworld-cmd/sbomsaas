#!/usr/bin/env python3
"""
Demo script to test the Flask OAuth2 API endpoints.
This script shows how to make authenticated API calls using a JWT token.
"""

import requests
import json
import sys

def test_api_endpoints(base_url, jwt_token):
    """Test all API endpoints with the provided JWT token"""
    
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/api/profile',
        '/api/data', 
        '/api/protected'
    ]
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n📡 Testing: {endpoint}")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                data = response.json()
                print("Response:")
                print(json.dumps(data, indent=2))
            else:
                print("❌ Failed!")
                print(f"Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
        
        print("-" * 30)

def main():
    """Main function"""
    
    print("🔐 Flask OAuth2 API Test Script")
    print("=" * 50)
    
    # Configuration
    base_url = "http://localhost:5000"
    
    # Check if JWT token is provided
    if len(sys.argv) < 2:
        print("\n❌ JWT token required!")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <JWT_TOKEN>")
        print("\nTo get your JWT token:")
        print("1. Start the Flask app: python app.py")
        print("2. Login via web interface: http://localhost:5000")
        print("3. Visit: http://localhost:5000/get-token")
        print("4. Copy your JWT token and use it with this script")
        print("\nExample:")
        print(f"  python {sys.argv[0]} eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        sys.exit(1)
    
    jwt_token = sys.argv[1]
    
    print(f"Base URL: {base_url}")
    print(f"JWT Token: {jwt_token[:50]}..." if len(jwt_token) > 50 else f"JWT Token: {jwt_token}")
    
    # Test if the server is running
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Is the Flask app running?")
        print("Start the server with: python app.py")
        sys.exit(1)
    
    # Test the API endpoints
    test_api_endpoints(base_url, jwt_token)
    
    print("\n✅ API testing completed!")
    print("\nNext steps:")
    print("- Integrate these API calls into your client application")
    print("- Use the same pattern for additional API endpoints")
    print("- Remember to handle token expiration and refresh logic")

if __name__ == "__main__":
    main()
