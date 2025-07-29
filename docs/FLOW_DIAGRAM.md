# SBOM SaaS Application - Complete Flow Diagram

## 🏗️ Application Architecture & Flow

This document provides a comprehensive flow diagram covering all code flows in the SBOM SaaS application, including user authentication, Kong integration, session handling, and API access patterns.

## 📊 Complete Application Flow

```mermaid
graph TB
    %% Entry Points
    START[User Accesses Application] --> ROUTE_CHECK{Which Route?}
    
    %% Main Routes
    ROUTE_CHECK -->|GET /| INDEX[index route]
    ROUTE_CHECK -->|GET /login| LOGIN_ROUTE[login route]
    ROUTE_CHECK -->|GET /callback| CALLBACK[callback route]
    ROUTE_CHECK -->|GET /dashboard| DASHBOARD[dashboard route]
    ROUTE_CHECK -->|GET /logout| LOGOUT[logout route]
    ROUTE_CHECK -->|GET /get-token| GET_TOKEN[get_token route]
    ROUTE_CHECK -->|/api/*| API_ROUTES[API Blueprint Routes]
    
    %% Index Route Flow
    INDEX --> GET_COOKIE[get_user_from_cookie]
    GET_COOKIE --> COOKIE_CHECK{Valid JWT Cookie?}
    COOKIE_CHECK -->|Yes| RENDER_INDEX_AUTH[Render index.html with user]
    COOKIE_CHECK -->|No| RENDER_INDEX_ANON[Render index.html anonymous]
    
    %% Login Flow
    LOGIN_ROUTE --> GENERATE_STATE[Generate CSRF state token]
    GENERATE_STATE --> STORE_SESSION[Store state in Flask session]
    STORE_SESSION --> BUILD_OAUTH_URL[Build Google OAuth URL]
    BUILD_OAUTH_URL --> REDIRECT_GOOGLE[Redirect to Google OAuth]
    
    %% Google OAuth Flow
    REDIRECT_GOOGLE --> GOOGLE_CONSENT[Google OAuth Consent Screen]
    GOOGLE_CONSENT --> USER_GRANTS{User Grants Permission?}
    USER_GRANTS -->|No| OAUTH_DENIED[OAuth Denied]
    USER_GRANTS -->|Yes| GOOGLE_CALLBACK[Google Redirects to /callback]
    
    %% Callback Processing
    GOOGLE_CALLBACK --> CALLBACK
    CALLBACK --> VERIFY_STATE{Verify CSRF State?}
    VERIFY_STATE -->|Invalid| ERROR_400[Return 400 Error]
    VERIFY_STATE -->|Valid| EXTRACT_CODE[Extract Authorization Code]
    
    EXTRACT_CODE --> CODE_CHECK{Code Present?}
    CODE_CHECK -->|No| ERROR_400
    CODE_CHECK -->|Yes| EXCHANGE_TOKEN[Exchange Code for Access Token]
    
    EXCHANGE_TOKEN --> TOKEN_SUCCESS{Token Exchange Success?}
    TOKEN_SUCCESS -->|No| OAUTH_ERROR[OAuth Error Handler]
    TOKEN_SUCCESS -->|Yes| GET_USER_INFO[Get User Info from Google]
    
    GET_USER_INFO --> USER_INFO_SUCCESS{User Info Success?}
    USER_INFO_SUCCESS -->|No| OAUTH_ERROR
    USER_INFO_SUCCESS -->|Yes| KONG_INTEGRATION[Kong Consumer Management]
    
    %% Kong Integration Flow
    KONG_INTEGRATION --> CREATE_KONG_CONSUMER[create_or_get_kong_consumer function]
    CREATE_KONG_CONSUMER --> SANITIZE_EMAIL[Generate sanitized username from email]
    SANITIZE_EMAIL --> CHECK_CONSUMER{Kong Consumer Exists?}
    
    CHECK_CONSUMER -->|GET /consumers/{email}| KONG_GET_RESPONSE{Consumer Found?}
    KONG_GET_RESPONSE -->|200 OK| EXISTING_CONSUMER[Return existing consumer ID]
    KONG_GET_RESPONSE -->|404 Not Found| CREATE_NEW_CONSUMER[Create new Kong consumer]
    KONG_GET_RESPONSE -->|Other Error| KONG_ERROR[Log Kong error, continue]
    
    CREATE_NEW_CONSUMER --> POST_CONSUMER[POST /consumers with email as username]
    POST_CONSUMER --> CREATE_SUCCESS{Consumer Created?}
    CREATE_SUCCESS -->|201 Created| GET_CONSUMER_ID[Get new consumer ID]
    CREATE_SUCCESS -->|Failed| KONG_ERROR
    
    GET_CONSUMER_ID --> CREATE_API_KEY[Create API key for consumer]
    CREATE_API_KEY --> KEY_SUCCESS{API Key Created?}
    KEY_SUCCESS -->|201 Created| LOG_KEY_SUCCESS[Log API key creation success]
    KEY_SUCCESS -->|Failed| LOG_KEY_WARNING[Log API key creation warning]
    
    %% JWT Token Creation
    EXISTING_CONSUMER --> JWT_CREATION[Create JWT Token]
    LOG_KEY_SUCCESS --> JWT_CREATION
    LOG_KEY_WARNING --> JWT_CREATION
    KONG_ERROR --> JWT_CREATION
    
    JWT_CREATION --> BUILD_USER_DATA[Build user data payload]
    BUILD_USER_DATA --> GENERATE_JWT[generate_jwt_token function]
    GENERATE_JWT --> SET_COOKIE[Set HTTP-only cookie]
    SET_COOKIE --> CLEAN_SESSION[Clean up OAuth session]
    CLEAN_SESSION --> REDIRECT_DASHBOARD[Redirect to /dashboard]
    
    %% Dashboard Flow
    REDIRECT_DASHBOARD --> DASHBOARD
    DASHBOARD --> LOGIN_REQUIRED_COOKIE[@login_required_cookie decorator]
    LOGIN_REQUIRED_COOKIE --> VERIFY_COOKIE{Valid JWT Cookie?}
    VERIFY_COOKIE -->|No| REDIRECT_LOGIN[Redirect to /login]
    VERIFY_COOKIE -->|Yes| EXTRACT_USER[Extract user from JWT]
    EXTRACT_USER --> RENDER_DASHBOARD[Render dashboard.html with user & token]
    
    %% Get Token Route
    GET_TOKEN --> LOGIN_REQUIRED_COOKIE2[@login_required_cookie decorator]
    LOGIN_REQUIRED_COOKIE2 --> VERIFY_COOKIE2{Valid JWT Cookie?}
    VERIFY_COOKIE2 -->|No| REDIRECT_LOGIN2[Redirect to /login]
    VERIFY_COOKIE2 -->|Yes| GET_COOKIE_TOKEN[Get auth_token from cookie]
    GET_COOKIE_TOKEN --> RENDER_TOKEN[Render token.html with token]
    
    %% API Routes Flow
    API_ROUTES --> API_ROUTE_CHECK{Which API Route?}
    API_ROUTE_CHECK -->|/api/get-auth-token| API_GET_TOKEN[api_get_auth_token]
    API_ROUTE_CHECK -->|/api/profile| API_PROFILE[api_profile]
    API_ROUTE_CHECK -->|/api/protected| API_PROTECTED[api_protected]
    API_ROUTE_CHECK -->|/api/data| API_DATA[api_data]
    
    %% API Get Token (Cookie Auth)
    API_GET_TOKEN --> LOGIN_REQUIRED_COOKIE3[@login_required_cookie decorator]
    LOGIN_REQUIRED_COOKIE3 --> COOKIE_VALID3{Valid Cookie?}
    COOKIE_VALID3 -->|No| REDIRECT_LOGIN3[Redirect to /login]
    COOKIE_VALID3 -->|Yes| RETURN_TOKEN_JSON[Return JSON with token]
    
    %% API Routes (Bearer Token Auth)
    API_PROFILE --> LOGIN_REQUIRED_API[@login_required_api decorator]
    API_PROTECTED --> LOGIN_REQUIRED_API2[@login_required_api decorator]
    API_DATA --> LOGIN_REQUIRED_API3[@login_required_api decorator]
    
    LOGIN_REQUIRED_API --> CHECK_BEARER{Valid Bearer Token?}
    LOGIN_REQUIRED_API2 --> CHECK_BEARER2{Valid Bearer Token?}
    LOGIN_REQUIRED_API3 --> CHECK_BEARER3{Valid Bearer Token?}
    
    CHECK_BEARER -->|No| RETURN_401[Return 401 Unauthorized]
    CHECK_BEARER -->|Yes| RETURN_PROFILE[Return user profile JSON]
    
    CHECK_BEARER2 -->|No| RETURN_401_2[Return 401 Unauthorized]
    CHECK_BEARER2 -->|Yes| RETURN_PROTECTED[Return protected data JSON]
    
    CHECK_BEARER3 -->|No| RETURN_401_3[Return 401 Unauthorized]
    CHECK_BEARER3 -->|Yes| RETURN_DATA[Return data array JSON]
    
    %% Logout Flow
    LOGOUT --> CLEAR_COOKIE[Clear auth_token cookie]
    CLEAR_COOKIE --> REDIRECT_INDEX[Redirect to /]
    
    %% Authentication Utilities
    subgraph AUTH_UTILS ["🔐 Authentication Utilities (auth_utils.py)"]
        GET_USER_COOKIE[get_user_from_cookie]
        GET_USER_HEADER[get_user_from_header]
        GENERATE_JWT_FUNC[generate_jwt_token]
        VERIFY_JWT_FUNC[verify_jwt_token]
        COOKIE_DECORATOR[login_required_cookie]
        API_DECORATOR[login_required_api]
    end
    
    %% Kong Integration Details
    subgraph KONG_DETAILS ["🦍 Kong Integration Pattern"]
        EMAIL_USERNAME[Email used as Kong username]
        SANITIZED_CUSTOM[Sanitized email as custom_id]
        FREE_TAGS[Tags: 'free']
        AUTO_API_KEY[Automatic API key generation]
        CONSUMER_LOOKUP[Consumer lookup by email]
        ERROR_RESILIENCE[Error resilience - login continues if Kong fails]
    end
    
    %% Session Management
    subgraph SESSION_MGMT ["🍪 Session Management"]
        HTTP_ONLY_COOKIES[HTTP-only cookies for web UI]
        BEARER_TOKENS[Bearer tokens for API access]
        CSRF_PROTECTION[CSRF protection with state parameter]
        TOKEN_EXPIRATION[24-hour token expiration]
        SECURE_FLAGS[Secure cookie flags in production]
        SESSION_CLEANUP[OAuth session cleanup]
    end
    
    %% Error Handling
    subgraph ERROR_HANDLING ["⚠️ Error Handling"]
        OAUTH_ERRORS[OAuth request errors → error.html]
        JWT_ERRORS[JWT validation errors → error.html]
        KONG_FAILURES[Kong API failures → log & continue]
        AUTH_FAILURES[Authentication failures → redirect login]
        API_AUTH_FAILURES[API auth failures → 401 JSON]
        ERROR_404[404 errors → error.html]
        ERROR_500[500 errors → error.html]
    end
    
    %% Frontend Integration
    subgraph FRONTEND ["🌐 Frontend Integration"]
        DASHBOARD_UI[Dashboard with API testing buttons]
        TOKEN_DISPLAY[Token display page for developers]
        AJAX_CALLS[JavaScript AJAX calls with Bearer tokens]
        ERROR_PAGES[Error pages with user-friendly messages]
        RESPONSIVE_UI[Responsive Bootstrap UI]
    end
    
    %% Configuration & Setup
    subgraph CONFIG ["⚙️ Configuration & Setup"]
        FLASK_CONFIG[Flask configuration from config.py]
        OAUTH_CONFIG[Google OAuth configuration]
        KONG_CONFIG[Kong Admin API configuration]
        JWT_CONFIG[JWT secret and algorithm configuration]
        ENVIRONMENT_CONFIG[Environment-specific settings]
    end
    
    %% Data Flow Patterns
    subgraph DATA_FLOW ["📊 Data Flow Patterns"]
        WEB_UI_FLOW[Web UI: Cookie → JWT → User Data]
        API_FLOW[API: Bearer Header → JWT → User Data]
        KONG_FLOW[Kong: Email → Consumer → API Key]
        SESSION_FLOW[Session: OAuth State → CSRF Protection]
    end
    
    %% Security Features
    subgraph SECURITY ["🔒 Security Features"]
        CSRF_STATE[CSRF protection with random state]
        HTTP_ONLY[HTTP-only cookies prevent XSS]
        SECURE_COOKIES[Secure cookies in production]
        JWT_EXPIRY[JWT token expiration]
        BEARER_AUTH[Bearer token authentication for APIs]
        INPUT_VALIDATION[Request validation and sanitization]
    end
    
    style START fill:#e1f5fe
    style KONG_INTEGRATION fill:#fff3e0
    style JWT_CREATION fill:#f3e5f5
    style AUTH_UTILS fill:#e8f5e8
    style SESSION_MGMT fill:#fff8e1
    style ERROR_HANDLING fill:#ffebee
    style SECURITY fill:#f1f8e9
```

## 🔄 Key Flow Components

### 1. **Authentication Flow**
- **Entry Point**: User visits any route
- **OAuth Flow**: Google OAuth with CSRF protection
- **Token Management**: JWT generation and cookie storage
- **Session Handling**: Secure session management with cleanup

### 2. **Kong Integration Flow**
- **Consumer Pattern**: Email as username, sanitized email as custom_id
- **API Key Management**: Automatic API key creation for new consumers
- **Error Resilience**: Kong failures don't break authentication
- **Lookup Strategy**: GET by email, create if 404

### 3. **Authorization Patterns**
- **Web UI**: Cookie-based authentication with `@login_required_cookie`
- **API Access**: Bearer token authentication with `@login_required_api`
- **Dual Auth**: Support for both cookie and bearer token patterns

### 4. **API Architecture**
- **Blueprint Structure**: Separate API routes in `api_routes.py`
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Responses**: Consistent API response format
- **Error Handling**: Proper HTTP status codes for API errors

### 5. **Security Implementation**
- **CSRF Protection**: Random state parameter for OAuth flow
- **XSS Prevention**: HTTP-only cookies
- **Token Security**: JWT with expiration and secure flags
- **Input Validation**: Request parameter validation

### 6. **Frontend Integration**
- **Dashboard UI**: Interactive testing interface
- **Token Display**: Developer-friendly token access
- **AJAX Integration**: JavaScript API calls with authentication
- **Error Pages**: User-friendly error handling

## 🚀 Usage Patterns

### Web UI Authentication
1. User visits `/` → checks cookie → renders page
2. User clicks login → OAuth flow → Kong integration → JWT cookie → dashboard
3. Authenticated pages use `@login_required_cookie` decorator

### API Authentication
1. Client gets token from `/get-token` or `/api/get-auth-token`
2. Client includes `Authorization: Bearer <token>` header
3. API endpoints use `@login_required_api` decorator
4. Returns JSON responses with proper HTTP status codes

### Kong Consumer Management
1. OAuth callback creates/retrieves Kong consumer
2. Email used as Kong username for easy lookup
3. Sanitized email used as custom_id for compatibility
4. API keys automatically generated for API access
5. Error resilience ensures authentication works even if Kong is down

This comprehensive flow ensures secure, scalable authentication with Kong API gateway integration while maintaining excellent user experience and developer-friendly APIs.
