# Flask OAuth2 Web Application

A modern Flask web application featuring Google OAuth2 authentication, JWT tokens, and a beautiful responsive UI built with Tailwind CSS and jQuery.

## Features

- **Google OAuth2 Authentication**: Secure login using Google accounts
- **JWT Tokens**: Stateless authentication with separate cookie and Bearer token support
- **Dual Authentication Modes**:
  - Web UI: JWT stored in HTTP-only cookies
  - API: Bearer tokens in Authorization headers
- **Modern UI**: Responsive design with Tailwind CSS
- **Interactive Frontend**: jQuery for enhanced user experience
- **Protected Routes**: Both web pages and API endpoints
- **Security Features**: HTTP-only cookies, CSRF protection considerations

## Project Structure

```
sbomsaas/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── templates/           # HTML templates
    ├── base.html        # Base template with navigation
    ├── index.html       # Landing page
    ├── dashboard.html   # Protected dashboard
    ├── token.html       # JWT token display and API testing
    └── error.html       # Error pages
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google OAuth2 Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" > "Create Credentials" > "OAuth 2.0 Client IDs"
5. Set application type to "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:5000/callback` (for development)
   - Add your production domain when deploying

### 3. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update with your Google OAuth credentials:
   ```env
   SECRET_KEY=your-super-secret-key-change-this-in-production
   JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
   GOOGLE_CLIENT_ID=your-google-client-id-from-console
   GOOGLE_CLIENT_SECRET=your-google-client-secret-from-console
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Application Flow

### Web Authentication (Cookie-based)
1. User clicks "Login with Google"
2. Redirected to Google OAuth consent screen
3. After successful authentication, user returns to `/callback`
4. JWT token is generated and stored in HTTP-only cookie
5. User can access protected web pages like `/dashboard`

### API Authentication (Bearer Token)
1. User must be logged in via web interface first
2. Visit `/get-token` to view JWT token
3. Use the token in API requests:
   ```bash
   curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
        http://localhost:5000/api/profile
   ```

## API Endpoints

All API endpoints require Bearer token authentication:

- `GET /api/profile` - Get user profile information
- `GET /api/data` - Get sample application data
- `GET /api/protected` - Example protected endpoint

## Security Features

- **JWT Tokens**: Stateless authentication with configurable expiration
- **HTTP-only Cookies**: Prevents XSS attacks on web interface
- **Separate Authentication**: Web UI uses cookies, APIs require Bearer tokens
- **Secure Cookie Flags**: HttpOnly, Secure (in production), SameSite
- **OAuth2 Flow**: Secure authentication via Google

## Development Notes

### Key Files

- `app.py`: Main application with routes and authentication logic
- `templates/base.html`: Base template with navigation and common styles
- `templates/dashboard.html`: Protected dashboard with API testing functionality
- `templates/token.html`: JWT token display with usage examples

### Authentication Decorators

- `@login_required_cookie`: For web routes (uses cookie authentication)
- `@login_required_api`: For API routes (requires Bearer token)

### Frontend Features

- Responsive design with Tailwind CSS
- Interactive elements with jQuery
- API testing directly from the web interface
- Copy-to-clipboard functionality for tokens and code examples

## Production Deployment

1. **Security Settings**:
   - Generate strong, unique secret keys
   - Set `FLASK_ENV=production`
   - Enable HTTPS and set `secure=True` for cookies
   - Update CORS settings if needed

2. **Google OAuth**:
   - Add production domain to authorized redirect URIs
   - Update environment variables with production credentials

3. **Server Configuration**:
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Configure reverse proxy (Nginx, Apache)
   - Set up SSL certificates

## Testing the Application

1. **Web Interface**:
   - Visit `/` to see the landing page
   - Login with Google account
   - Access `/dashboard` to see protected content
   - Test API calls from the dashboard

2. **API Testing**:
   - Get your JWT token from `/get-token`
   - Use curl, Postman, or any HTTP client
   - Include `Authorization: Bearer <token>` header

## Troubleshooting

- **OAuth Error**: Check Google Client ID/Secret and redirect URIs
- **JWT Errors**: Verify JWT secret key configuration
- **Cookie Issues**: Check domain settings and HTTPS configuration
- **API 401 Errors**: Ensure Bearer token is correctly formatted in headers

## License

This project is for educational purposes. Modify as needed for your use case.
