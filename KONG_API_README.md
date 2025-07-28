# Kong Admin API Integration

This module provides server-to-server communication with Kong Gateway for managing consumers and API keys in your SBOM SaaS application.

## Files Overview

### `kong_admin_api.py` (534 lines)
Core implementation with two main classes:

#### `KongAdminAPI` - Low-level API client
- Direct Kong Admin API communication
- All required endpoints implemented
- Retry logic for 502/503 responses (3 attempts)
- Comprehensive logging and error handling
- Returns `(response_json, status_code)` tuples

#### `KongServiceManager` - High-level service wrapper  
- Business logic for user API access management
- Integration-friendly methods for your Flask app
- Graceful error handling and logging

### `test_kong_api.py` (235 lines)
Complete test suite demonstrating:
- Basic Kong API operations
- Error handling scenarios
- Service manager functionality
- Cleanup operations

### `kong_integration_example.py` (299 lines)
Integration examples showing:
- How to integrate with your existing Flask authentication
- User API service wrapper
- OAuth callback integration
- Dashboard API key display

## Key Features Implemented

### ✅ All Required Kong Admin API Endpoints

1. **Create Consumer**
   ```python
   response, status = kong.create_consumer("johndoe", custom_id="cust_001", tags=["paid"])
   ```

2. **Get Consumer**
   ```python
   response, status = kong.get_consumer("johndoe")
   ```

3. **Create Consumer Auth-Key**
   ```python
   response, status = kong.create_consumer_key("johndoe", key="custom-key-123")
   ```

4. **Get All Auth-Keys**
   ```python
   response, status = kong.get_consumer_keys("johndoe")
   ```

5. **Optional: Delete Consumer/Key**
   ```python
   response, status = kong.delete_consumer("johndoe")
   response, status = kong.delete_consumer_key("johndoe", "key_id")
   ```

### ✅ Technical Requirements

- **Configurable base URL**: `KongAdminAPI("http://localhost:8001")`
- **Retry logic**: 3 attempts for 502/503 responses with exponential backoff
- **Return format**: All methods return `(response_json, status_code)`
- **Comprehensive logging**: INFO level for requests, DEBUG for payloads/responses
- **Exception handling**: `KongAdminAPIError` for 400/404/409 with meaningful messages
- **Type hints**: Full type annotation support
- **Session management**: Connection pooling and retry strategies

### ✅ Security Features

- **No Flask routes**: Server-to-server only, not exposed to end users
- **Sensitive data masking**: API keys masked in logs (`key123***`)
- **Error message sanitization**: Clean error messages without exposing internals
- **Timeout handling**: Configurable request timeouts

## Quick Start

### Basic Usage
```python
from kong_admin_api import KongAdminAPI, KongAdminAPIError

# Initialize client
kong = KongAdminAPI("http://localhost:8001")

try:
    # Create consumer
    consumer, status = kong.create_consumer("user123", custom_id="user@example.com")
    
    # Create API key
    key_response, status = kong.create_consumer_key("user123")
    api_key = key_response['key']
    
    print(f"Created API key: {api_key}")
    
except KongAdminAPIError as e:
    print(f"Kong error: {e.message} (Status: {e.status_code})")
```

### Integration with Flask App
```python
from kong_integration_example import UserAPIService

# In your OAuth callback
api_service = UserAPIService()
result = api_service.setup_user_api_access(user_data)

if result['success']:
    api_key = result['api_key']
    # Store or use API key
```

## Error Handling

The implementation provides robust error handling:

```python
try:
    response, status = kong.create_consumer("duplicate_user")
except KongAdminAPIError as e:
    if e.status_code == 409:
        print("Consumer already exists")
    elif e.status_code == 400:
        print(f"Bad request: {e.message}")
    elif e.status_code == 404:
        print("Resource not found")
```

## Testing

Run the test suite:
```bash
python3 test_kong_api.py
```

This will test:
- Kong Gateway connectivity
- Consumer creation/retrieval
- API key management
- Error handling
- Service manager functionality

## Configuration

Add to your `config.py`:
```python
# Kong Gateway configuration
KONG_ADMIN_URL = os.getenv('KONG_ADMIN_URL', 'http://localhost:8001')
KONG_GATEWAY_URL = os.getenv('KONG_GATEWAY_URL', 'http://localhost:8000')
```

## Logging Configuration

```python
import logging

# Configure logging to see Kong API requests/responses
logging.basicConfig(level=logging.INFO)

# For detailed request/response logging
logging.getLogger('kong_admin_api').setLevel(logging.DEBUG)
```

## Prerequisites

1. **Kong Gateway running** on localhost:8001 (Admin API)
2. **key-auth plugin enabled** for API key functionality:
   ```bash
   curl -X POST http://localhost:8001/plugins \
     --data "name=key-auth"
   ```
3. **Compatible urllib3 version**: The code uses `allowed_methods` (urllib3 >= 1.26.0)

## Compatibility Notes

- **urllib3 compatibility**: Uses `allowed_methods` instead of deprecated `method_whitelist`
- **Python 3.7+**: Type hints and modern Python features
- **requests >= 2.28.0**: For session management and retry functionality

## Production Considerations

- Set appropriate timeouts for your environment
- Configure Kong Gateway with proper security settings
- Use environment variables for Kong URLs
- Monitor Kong Gateway health and API usage
- Implement rate limiting and monitoring
- Consider Kong's database backup and recovery

## Next Steps

1. **Enable key-auth plugin** in Kong Gateway
2. **Test connectivity** using `test_kong_api.py`
3. **Integrate** with your OAuth callback using `UserAPIService`
4. **Add API key display** to your dashboard
5. **Configure logging** for production monitoring
