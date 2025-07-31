# SBOMSAAS - Flask OAuth2 Web Application with Stripe Integration

A modern, production-ready Flask web application featuring Google OAuth2 authentication, JWT tokens, Stripe payments, and secure webhook handling. Built with separated architecture for maintainable code and optimal performance.

## ✨ Features

- **🔐 Google OAuth2 Authentication**: Secure login using Google accounts
- **🎫 JWT Tokens**: Stateless authentication with separate cookie and Bearer token support
- **💳 Stripe Integration**: Complete payment processing with secure webhooks
- **🔄 Dual Authentication Modes**:
  - Web UI: JWT stored in HTTP-only cookies
  - API: Bearer tokens in Authorization headers
- **🎨 Modern UI**: Responsive design with Tailwind CSS
- **⚡ Interactive Frontend**: jQuery for enhanced user experience
- **🛡️ Protected Routes**: Both web pages and API endpoints
- **🔒 Security Features**: HTTP-only cookies, CSRF protection, webhook signature verification
- **📱 Mobile Responsive**: Works seamlessly on all device sizes
- **🖼️ Smart Profile Pictures**: Automatic fallback avatars when Google profile pictures fail to load

## 🚀 Quick Start

### Set up development environment
./scripts/dev.sh setup

### Install dependencies
make install

### Run tests
make test

### Start development server
make run

### Code quality checks
make quality