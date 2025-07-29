# SBOM SaaS Makefile
# Convenient commands for development

.PHONY: help setup install clean test lint format run docs

# Default target
help:
	@echo "SBOM SaaS Development Commands"
	@echo "============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup     - Set up development environment"
	@echo "  make install   - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run       - Start development server"
	@echo "  make run-prod  - Start production server"
	@echo ""
	@echo "Testing:"
	@echo "  make test      - Run all tests with coverage"
	@echo "  make test-unit - Run unit tests only"
	@echo "  make test-api  - Run API tests only"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint      - Run code linting"
	@echo "  make format    - Format code with black"
	@echo "  make quality   - Run all quality checks"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean     - Clean cache files"
	@echo "  make docs      - Generate documentation"

setup:
	./scripts/dev.sh setup

install:
	./scripts/dev.sh install

run:
	./scripts/dev.sh run

run-prod:
	./scripts/dev.sh run-prod

test:
	./scripts/dev.sh test

test-unit:
	./scripts/dev.sh test-unit

test-integration:
	./scripts/dev.sh test-integration

test-api:
	./scripts/dev.sh test-api

lint:
	./scripts/dev.sh lint

format:
	./scripts/dev.sh format

quality:
	./scripts/dev.sh quality

clean:
	./scripts/dev.sh clean

docs:
	./scripts/dev.sh docs
