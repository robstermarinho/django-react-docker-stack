.PHONY: help up up-d poetry-add poetry-add-dev poetry-update poetry-remove poetry-show-outdated poetry-export clean test lint format backend-shell warp-shell frontend-install frontend-build frontend-restart backend-restart

# Default target
help:
	@echo "Available commands:"
	@echo "  up            - Start development environment"
	@echo "  up-d          - Start development environment (detached)"
	@echo "  poetry-add    - Add production dependency (usage: make poetry-add PACKAGE=requests)"
	@echo "  poetry-add-dev- Add dev dependency (usage: make poetry-add-dev PACKAGE=pytest)"
	@echo "  poetry-update - Update dependencies"
	@echo "  poetry-remove - Remove dependency (usage: make poetry-remove PACKAGE=requests)"
	@echo "  poetry-show-outdated - Show outdated dependencies"
	@echo "  poetry-export - Export Poetry deps to requirements.txt"
	@echo "  clean         - Clean up containers and volumes"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  format        - Format code"
	@echo "  backend-shell - Open shell in backend container"
	@echo "  warp-shell    - Open warpified shell in backend container (auto-detects container)"
	@echo "  frontend-install - Install frontend dependencies"
	@echo "  frontend-build   - Build frontend"
	@echo "  frontend-restart - Restart frontend container"
	@echo "  backend-restart  - Restart backend container"

# Development environment
up:
	@echo "🚀 Starting development environment..."
	docker compose up --build

up-d:
	@echo "🚀 Starting development environment (detached)..."
	docker compose up --build -d

# Poetry commands (local machine)
poetry-add:
	@if [ -z "$(PACKAGE)" ]; then echo "❌ Usage: make poetry-add PACKAGE=package-name"; exit 1; fi
	@echo "📦 Adding production dependency: $(PACKAGE)"
	cd backend && poetry add $(PACKAGE)
	@echo "📋 Locking and exporting updated requirements..."
	cd backend && poetry lock
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes
	cd backend && poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
	@echo "✅ Dependency $(PACKAGE) added! Don't forget to commit the changes."

poetry-add-dev:
	@if [ -z "$(PACKAGE)" ]; then echo "❌ Usage: make poetry-add-dev PACKAGE=package-name"; exit 1; fi
	@echo "🛠️ Adding dev dependency: $(PACKAGE)"
	cd backend && poetry add --group dev $(PACKAGE)
	@echo "📋 Locking and exporting updated requirements..."
	cd backend && poetry lock
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes
	cd backend && poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
	@echo "✅ Dev dependency $(PACKAGE) added! Don't forget to commit the changes."

poetry-update:
	@echo "🔄 Updating Poetry dependencies..."
	cd backend && poetry update
	@echo "📋 Locking and exporting updated requirements..."
	cd backend && poetry lock
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes
	cd backend && poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
	@echo "✅ Dependencies updated! Don't forget to commit the changes."

poetry-remove:
	@if [ -z "$(PACKAGE)" ]; then echo "❌ Usage: make poetry-remove PACKAGE=package-name"; exit 1; fi
	@echo "🗑️ Removing dependency: $(PACKAGE)"
	cd backend && poetry remove $(PACKAGE)
	@echo "📋 Locking and exporting updated requirements..."
	cd backend && poetry lock
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes
	cd backend && poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
	@echo "✅ Dependency $(PACKAGE) removed! Don't forget to commit the changes."

# Show outdated dependencies
poetry-show-outdated:
	@echo "📊 Checking outdated dependencies..."
	cd backend && poetry show --outdated

# Export dependencies
poetry-export:
	@echo "📋 Locking and exporting Poetry dependencies to requirements files..."
	cd backend && poetry lock
	cd backend && poetry export -f requirements.txt --output requirements.txt --without-hashes
	cd backend && poetry export -f requirements.txt --output requirements-dev.txt --without-hashes --with dev
	@echo "✅ Requirements.txt and requirements-dev.txt updated!"

# Install dependencies locally
poetry-install:
	@echo "📦 Installing Poetry dependencies locally..."
	cd backend && poetry install
	@echo "✅ Dependencies installed!"

# Open shell in backend container
backend-shell:
	@echo "🐚 Opening shell in backend container..."
	docker compose exec api /bin/bash

# Open warpified shell in backend container (auto-detects container)
warp-shell:
	@echo "🌟 Opening warpified shell in backend container..."
	./scripts/warp-shell.sh


# Open local Poetry shell
poetry-shell:
	@echo "🐚 Opening Poetry shell..."
	cd backend && poetry shell

# Clean up
clean:
	@echo "🧹 Cleaning up Docker containers and volumes..."
	docker compose down -v
	docker builder prune -f

# Run tests in Docker
test:
	@echo "🧪 Running tests..."
	docker compose exec api pytest

# Run linting locally
lint:
	@echo "🔍 Running linting locally..."
	cd backend && poetry run flake8 .
	cd backend && poetry run black --check .
	cd backend && poetry run isort --check-only .

# Format code locally
format:
	@echo "✨ Formatting code locally..."
	cd backend && poetry run black .
	cd backend && poetry run isort .

# Frontend commands
frontend-install:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

frontend-build:
	@echo "🏗️ Building frontend..."
	docker compose exec web npm run build

frontend-restart:
	@echo "🔄 Restarting frontend container..."
	docker compose restart web

backend-restart:
	@echo "🔄 Restarting backend container..."
	docker compose restart api