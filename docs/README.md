# SBOMSAAS - Flask OAuth2 Web Application

A modern, production-ready Flask web application featuring Google OAuth2 authentication, JWT tokens, and a beautiful responsive UI. Built with separated CSS/JavaScript architecture for maintainable code and optimal performance.

## ✨ Features

- **🔐 Google OAuth2 Authentication**: Secure login using Google accounts
- **🎫 JWT Tokens**: Stateless authentication with separate cookie and Bearer token support
- **🔄 Dual Authentication Modes**:
  - Web UI: JWT stored in HTTP-only cookies
  - API: Bearer tokens in Authorization headers
- **🎨 Modern UI**: Responsive design with Tailwind CSS
- **⚡ Interactive Frontend**: jQuery for enhanced user experience
- **🛡️ Protected Routes**: Both web pages and API endpoints
- **🔒 Security Features**: HTTP-only cookies, CSRF protection, fallback handling
- **📱 Mobile Responsive**: Works seamlessly on all device sizes
- **🖼️ Smart Profile Pictures**: Automatic fallback avatars when Google profile pictures fail to load

## 📁 Project Structure

```
sbomsaas/
├── app.py                     # Main Flask application
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── run.sh                     # Application startup script
├── test_api.py               # API testing utility
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css       # Custom styles and utilities
│   └── js/
│       ├── main.js          # Common JavaScript functionality
│       ├── dashboard.js     # Dashboard-specific features
│       ├── index.js         # Home page functionality
│       └── token.js         # Token page functionality
└── templates/               # HTML templates
    ├── base.html            # Base template with navigation
    ├── index.html           # Landing page
    ├── dashboard.html       # Protected dashboard
    ├── token.html           # JWT token display and API testing
    └── error.html           # Error pages
```

## 🏗️ Architecture Highlights

### Separated Assets
- **External CSS**: All styles moved to `static/css/styles.css` for better caching and maintainability
- **Modular JavaScript**: Page-specific functionality split into separate files
- **Clean Templates**: HTML templates now focus purely on structure and content

### Frontend Organization
- `main.js`: Common utilities (alerts, copy functionality, API helpers)
- `dashboard.js`: Dashboard API testing and interactions
- `index.js`: Home page functionality for logged-in users
- `token.js`: Token display and API endpoint testing

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/heftworld-cmd/sbomsaas.git
cd sbomsaas
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your Google OAuth credentials
```

### 3. Run the Application
```bash
# Using the startup script
chmod +x run.sh
./run.sh

# Or directly with Python
python3 app.py
```

Visit `http://localhost:5000` to access the application.

## ⚙️ Detailed Setup Instructions

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
# Option 1: Using the startup script (recommended)
chmod +x run.sh
./run.sh

# Option 2: Direct Python execution
python3 app.py
```

The application will be available at `http://localhost:5000`

## 🔄 Application Flow

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

## 🔗 API Endpoints

All API endpoints require Bearer token authentication:

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/profile` | GET | Get user profile information | User data with picture URL |
| `/api/data` | GET | Get sample application data | Array of sample items |
| `/api/protected` | GET | Example protected endpoint | Timestamp and user info |

### Usage Example
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:5000/api/profile
```

## 🛡️ Security Features

- **JWT Tokens**: Stateless authentication with configurable expiration
- **HTTP-only Cookies**: Prevents XSS attacks on web interface
- **Separate Authentication**: Web UI uses cookies, APIs require Bearer tokens
- **Secure Cookie Flags**: HttpOnly, Secure (in production), SameSite
- **OAuth2 Flow**: Secure authentication via Google

## 💡 Development Notes

### Key Files

- `app.py`: Main application with routes and authentication logic
- `config.py`: Configuration management with environment-based settings
- `static/css/styles.css`: All custom styles, utilities, and responsive design
- `static/js/main.js`: Common JavaScript utilities and helper functions
- `templates/base.html`: Base template with navigation and script loading

### Authentication Decorators

- `@login_required_cookie`: For web routes (uses cookie authentication)
- `@login_required_api`: For API routes (requires Bearer token)

### Frontend Features

- **Separated Assets**: CSS and JavaScript moved to external files for better caching
- **Modular JavaScript**: Page-specific functionality in separate files
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Interactive Elements**: jQuery for enhanced user experience
- **API Testing**: Built-in API testing directly from the web interface
- **Copy Functionality**: One-click copying for tokens and code examples
- **Smart Avatars**: Automatic fallback avatars when profile pictures fail
- **Error Handling**: Graceful handling of missing or broken profile images

### Recent Improvements

- ✅ Fixed profile picture loading issue by including `picture` field in JWT payload
- ✅ Added fallback avatars with user initials for missing profile pictures
- ✅ Separated all inline CSS and JavaScript into external files
- ✅ Improved script loading order and dependency management
- ✅ Enhanced error handling and user experience

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

## 🧪 Testing the Application

### 1. Web Interface Testing
- Visit `/` to see the landing page
- Click "Login with Google" to test OAuth flow
- Access `/dashboard` to see protected content
- Test API calls directly from the dashboard
- Visit `/get-token` to view and copy your JWT token

### 2. API Testing
```bash
# Get your JWT token from the web interface first
TOKEN="your-jwt-token-here"

# Test profile endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/profile

# Test data endpoint  
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/data

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/protected
```

### 3. Using the Test Script
```bash
# Run the included API test script
python3 test_api.py YOUR_JWT_TOKEN
```

## 🔧 Troubleshooting

## 🔧 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **OAuth Error** | Incorrect Google Client ID/Secret | Check credentials in `.env` file |
| **JWT Errors** | Wrong JWT secret key | Verify `JWT_SECRET_KEY` in configuration |
| **Cookie Issues** | Domain/HTTPS settings | Check domain settings and HTTPS config |
| **API 401 Errors** | Invalid Bearer token | Ensure token format: `Authorization: Bearer <token>` |
| **Profile Picture Not Loading** | Missing picture field | Logout and login again to refresh JWT |
| **CSS/JS Not Loading** | Static file path issues | Check `url_for('static', filename='...')` paths |

### Debug Mode
```bash
# Enable debug mode for detailed error messages
export FLASK_DEBUG=True
python3 app.py
```

## 🚀 Production Deployment

### Security Checklist
- [ ] Generate strong, unique secret keys
- [ ] Set `FLASK_ENV=production` 
- [ ] Enable HTTPS and set `secure=True` for cookies
- [ ] Configure CORS settings if needed
- [ ] Add production domain to Google OAuth redirect URIs
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx, Apache)
- [ ] Configure SSL certificates

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/heftworld-cmd/sbomsaas/issues) on GitHub.

---

**Built with ❤️ for modern web authentication**
