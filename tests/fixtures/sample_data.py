"""
Test fixtures and sample data for SBOM SaaS tests
"""

# Sample user data for OAuth testing
SAMPLE_USERS = [
    {
        'id': 'google_123456',
        'email': 'test.user@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/avatar1.jpg'
    },
    {
        'id': 'google_789012',
        'email': 'jane.doe+work@company.com',
        'name': 'Jane Doe',
        'picture': 'https://example.com/avatar2.jpg'
    },
    {
        'id': 'google_345678',
        'email': 'admin@example.org',
        'name': 'Admin User',
        'picture': None
    }
]

# Sample Kong consumer data
SAMPLE_KONG_CONSUMERS = [
    {
        'id': 'consumer_123',
        'username': 'test.user@example.com',
        'custom_id': 'test_user',
        'tags': ['free']
    },
    {
        'id': 'consumer_456',
        'username': 'jane.doe+work@company.com',
        'custom_id': 'jane_doe_work',
        'tags': ['free']
    }
]

# Sample API key data
SAMPLE_API_KEYS = [
    {
        'id': 'key_123',
        'key': 'test_api_key_abcdef123456',
        'consumer': {'id': 'consumer_123'}
    },
    {
        'id': 'key_456',
        'key': 'test_api_key_ghijkl789012',
        'consumer': {'id': 'consumer_456'}
    }
]

# Sample JWT payload
SAMPLE_JWT_PAYLOAD = {
    'user_id': 'google_123456',
    'email': 'test.user@example.com',
    'name': 'Test User',
    'picture': 'https://example.com/avatar1.jpg',
    'exp': 1700000000,  # Future timestamp
    'iat': 1699000000   # Past timestamp
}

# OAuth flow test data
OAUTH_TEST_DATA = {
    'authorization_code': 'test_auth_code_123',
    'state': 'test_state_456',
    'access_token': 'test_access_token_789',
    'redirect_uri': 'http://localhost:5000/callback'
}
