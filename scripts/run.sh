#!/bin/bash

# Flask OAuth2 Web Application Startup Script

echo "🚀 Starting Flask OAuth2 Web Application..."
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your Google OAuth2 credentials:"
    echo "   - GOOGLE_CLIENT_ID"
    echo "   - GOOGLE_CLIENT_SECRET"
    echo ""
fi

# Activate virtual environment and run the app
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo "🌐 Starting Flask application on http://localhost:5000"
echo "📱 Access the app at: http://localhost:5000"
echo "🔑 Dashboard (requires login): http://localhost:5000/dashboard"
echo "🛠️  API token page: http://localhost:5000/get-token"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python src/app/app.py
