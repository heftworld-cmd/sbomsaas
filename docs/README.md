# SBOMSAAS - Flask OAuth2 Web Application with Stripe Integration

A modern, production-ready Flask web application featuring Google OAuth2 authentication, JWT tokens, Stripe payments with secure webhooks, and a beautiful responsive UI. Built with separated CSS/JavaScript architecture for maintainable code and optimal performance.

## ✨ Features

- **🔐 Google OAuth2 Authentication**: Secure login using Google accounts
- **🎫 JWT Tokens**: Stateless authentication with separate cookie and Bearer token support
- **� Stripe Integration**: Complete payment processing with pricing tables and secure webhooks
- **�🔄 Dual Authentication Modes**:
  - Web UI: JWT stored in HTTP-only cookies
  - API: Bearer tokens in Authorization headers
- **🎨 Modern UI**: Responsive design with Tailwind CSS
- **⚡ Interactive Frontend**: jQuery for enhanced user experience
- **🛡️ Protected Routes**: Both web pages and API endpoints
- **🔒 Security Features**: HTTP-only cookies, CSRF protection, webhook signature verification
- **📱 Mobile Responsive**: Works seamlessly on all device sizes
- **🖼️ Smart Profile Pictures**: Automatic fallback avatars when Google profile pictures fail to load
- **🔗 Kong API Gateway Integration**: Optional Kong integration for advanced API management
- **📊 Webhook Processing**: Secure handling of Stripe payment events

## 📁 Project Structure

```
sbomsaas/
├── src/                       # Source code
│   ├── app/
│   │   └── app.py            # Main Flask application
│   ├── api/
│   │   └── api_routes.py     # API endpoints
│   ├── auth/
│   │   └── auth_utils.py     # Authentication utilities
│   ├── config/
│   │   └── config.py         # Configuration settings
│   ├── kong/
│   │   ├── kong_admin_api.py # Kong API integration
│   │   └── kong_utils.py     # Kong utilities
│   ├── stripe_integration/
│   │   ├── stripe_service.py # Stripe webhook service
│   │   └── webhook_routes.py # Stripe webhook routes
│   ├── static/               # Static assets
│   │   ├── css/
│   │   │   └── styles.css    # Custom styles and utilities
│   │   └── js/
│   │       ├── main.js       # Common JavaScript functionality
│   │       ├── dashboard.js  # Dashboard-specific features
│   │       ├── index.js      # Home page functionality
│   │       └── token.js      # Token page functionality
│   └── templates/            # HTML templates
│       ├── base.html         # Base template with navigation
│       ├── index.html        # Landing page with pricing
│       ├── pricing.html      # Dedicated pricing page
│       ├── dashboard.html    # Protected dashboard
│       ├── token.html        # JWT token display and API testing
│       └── error.html        # Error pages
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   │   └── test_stripe_webhook.py # Stripe webhook tests
│   └── api/                  # API tests
├── docs/                     # Documentation
│   └── STRIPE_WEBHOOK_GUIDE.md # Stripe integration guide
├── scripts/                  # Development scripts
│   ├── run.sh               # Application startup script
│   └── dev.sh               # Development utilities
├── requirements/            # Dependencies
│   ├── requirements.txt     # Production dependencies
│   └── requirements-dev.txt # Development dependencies
├── test_stripe_webhook.py   # Stripe webhook testing utility
├── .env.example             # Environment variables template
└── README.md                # Project documentation
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

### Stripe Integration
- `stripe_service.py`: Core webhook processing service
- `webhook_routes.py`: Flask routes for webhook endpoints
- Secure signature verification for all webhook events
- Comprehensive event handling for payments and subscriptions

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/heftworld-cmd/sbomsaas.git
cd sbomsaas
./scripts/dev.sh setup  # Sets up virtual environment and dependencies
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your credentials:
# - Google OAuth2 credentials
# - Stripe API keys and webhook secret
```

### 3. Run the Application
```bash
# Using the startup script (recommended)
./scripts/run.sh

# Or using development script
./scripts/dev.sh run
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

2. Edit `.env` and update with your credentials:
   ```env
   # Application Security
   SECRET_KEY=your-super-secret-key-change-this-in-production
   JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
   
   # Google OAuth2 Settings
   GOOGLE_CLIENT_ID=your-google-client-id-from-console
   GOOGLE_CLIENT_SECRET=your-google-client-secret-from-console
   
   # Stripe Settings
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   
   # Application Settings
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

### 4. Stripe Setup (Optional)

1. **Create Stripe Account**: Sign up at [Stripe Dashboard](https://dashboard.stripe.com/)
2. **Configure Pricing Table**: Create your pricing table in Stripe Dashboard
3. **Set up Webhooks**:
   - Go to Webhooks section in Stripe Dashboard
   - Add endpoint: `https://yourdomain.com/stripe/webhook`
   - Select events: `payment_intent.succeeded`, `customer.subscription.*`, `invoice.payment.*`
   - Copy webhook secret to your `.env` file

### 5. Run the Application

```bash
# Using the startup script (recommended)
./scripts/run.sh

# Or using development utilities
./scripts/dev.sh run
```

The application will be available at `http://localhost:5000`

## 💳 Stripe Integration Features

### Payment Processing
- **No-Code Pricing Tables**: Embedded Stripe pricing tables for seamless checkout
- **Secure Webhooks**: Real-time payment event processing with signature verification
- **Customer Management**: Automatic linking of Stripe customers to user accounts
- **Billing Portal**: Direct access to Stripe's customer portal for subscription management

### Supported Events
- Payment success/failure notifications
- Subscription creation, updates, and cancellations
- Invoice payment processing
- Customer data synchronization

### Webhook Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stripe/webhook` | POST | Main webhook for Stripe events |
| `/stripe/webhook/test` | GET | Configuration test endpoint |
| `/stripe/events` | GET | List recent events (dev only) |

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
- Visit `/` to see the landing page with pricing integration
- Click "Login with Google" to test OAuth flow
- Access `/dashboard` to see protected content
- Visit `/pricing` to view Stripe pricing tables
- Test the "Billing" link in navigation for authenticated users
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

### 3. Stripe Webhook Testing
```bash
# Test webhook configuration
curl http://localhost:5000/stripe/webhook/test

# Run automated webhook tests
python tests/integration/test_stripe_webhook.py

# Test with Stripe CLI (after installation)
stripe listen --forward-to localhost:5000/stripe/webhook
stripe trigger payment_intent.succeeded
```

### 4. Using Test Scripts
```bash
# Run the included API test script
python3 test_api.py YOUR_JWT_TOKEN

# Run the full test suite
./scripts/dev.sh test

# Run specific test categories
./scripts/dev.sh test-unit
./scripts/dev.sh test-integration
```

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
| **Stripe Webhook 400 Error** | Invalid webhook signature | Verify `STRIPE_WEBHOOK_SECRET` in `.env` |
| **Pricing Table Not Loading** | Incorrect Stripe keys | Check `STRIPE_PUBLISHABLE_KEY` configuration |
| **Webhook Events Not Processing** | Wrong endpoint URL | Verify webhook URL in Stripe Dashboard |
| **Billing Link Not Working** | Missing user email | Ensure user is logged in with valid email |

### Debug Mode
```bash
# Enable debug mode for detailed error messages
export FLASK_DEBUG=True
./scripts/run.sh

# Test webhook configuration
curl http://localhost:5000/stripe/webhook/test

# Check webhook logs
tail -f logs/app.log  # if logging to file
```

### Stripe Testing
```bash
# Test webhook endpoint
python test_stripe_webhook.py

# Use Stripe test cards
# Visa: 4242424242424242
# Visa (declined): 4000000000000002
# Mastercard: 5555555555554444
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
- [ ] Use production Stripe keys (replace test keys)
- [ ] Configure production webhook endpoint with HTTPS
- [ ] Set up webhook monitoring and alerting
- [ ] Implement proper logging for payment events
- [ ] Test webhook delivery in production environment

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
