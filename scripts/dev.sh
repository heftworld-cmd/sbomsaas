#!/bin/bash
# Development and testing scripts for SBOM SaaS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to project root
cd "$(dirname "$0")/.."

case "$1" in
    "install")
        print_status "Installing dependencies..."
        pip install -r requirements/requirements.txt
        pip install -r requirements/requirements-dev.txt
        print_success "Dependencies installed successfully!"
        ;;
    
    "test")
        print_status "Running tests..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term
        print_success "Tests completed!"
        ;;
    
    "test-unit")
        print_status "Running unit tests..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        python -m pytest tests/unit/ -v
        print_success "Unit tests completed!"
        ;;
    
    "test-integration")
        print_status "Running integration tests..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        python -m pytest tests/integration/ -v
        print_success "Integration tests completed!"
        ;;
    
    "test-api")
        print_status "Running API tests..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        python -m pytest tests/api/ -v
        print_success "API tests completed!"
        ;;
    
    "test-stripe")
        print_status "Running Stripe webhook tests..."
        python tests/integration/test_stripe_webhook.py
        print_success "Stripe webhook tests completed!"
        ;;
    
    "lint")
        print_status "Running code linting..."
        flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503
        print_success "Linting completed!"
        ;;
    
    "format")
        print_status "Formatting code with black..."
        black src/ tests/ --line-length=100
        print_success "Code formatting completed!"
        ;;
    
    "type-check")
        print_status "Running type checking..."
        mypy src/ --ignore-missing-imports
        print_success "Type checking completed!"
        ;;
    
    "quality")
        print_status "Running all quality checks..."
        ./scripts/dev.sh format
        ./scripts/dev.sh lint
        ./scripts/dev.sh type-check
        print_success "Quality checks completed!"
        ;;
    
    "run")
        print_status "Starting development server..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        export FLASK_ENV=development
        export FLASK_DEBUG=1
        cd src/app && python app.py
        ;;
    
    "run-prod")
        print_status "Starting production server..."
        export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
        export FLASK_ENV=production
        cd src/app && python app.py
        ;;
    
    "clean")
        print_status "Cleaning up cache files..."
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name ".coverage" -delete 2>/dev/null || true
        print_success "Cleanup completed!"
        ;;
    
    "setup")
        print_status "Setting up development environment..."
        ./scripts/dev.sh install
        ./scripts/dev.sh clean
        print_status "Creating .env file from template..."
        if [ ! -f config/.env ]; then
            cp config/.env.example config/.env
            print_warning "Please edit config/.env file with your configuration!"
        fi
        print_success "Development environment setup completed!"
        ;;
    
    "docs")
        print_status "Generating documentation..."
        cd docs/
        make html
        print_success "Documentation generated in docs/_build/html/"
        ;;
    
    *)
        echo "SBOM SaaS Development Scripts"
        echo "Usage: $0 {command}"
        echo ""
        echo "Available commands:"
        echo "  setup          - Set up development environment"
        echo "  install        - Install dependencies"
        echo "  run            - Start development server"
        echo "  run-prod       - Start production server"
        echo "  test           - Run all tests with coverage"
        echo "  test-unit      - Run unit tests only"
        echo "  test-integration - Run integration tests only"
        echo "  test-api       - Run API tests only"
        echo "  test-stripe    - Run Stripe webhook tests"
        echo "  lint           - Run code linting"
        echo "  format         - Format code with black"
        echo "  type-check     - Run type checking"
        echo "  quality        - Run all quality checks"
        echo "  clean          - Clean cache files"
        echo "  docs           - Generate documentation"
        echo ""
        echo "Examples:"
        echo "  $0 setup       # First-time setup"
        echo "  $0 test        # Run tests"
        echo "  $0 run         # Start dev server"
        exit 1
        ;;
esac
