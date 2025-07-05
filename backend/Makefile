# Ultra Civic Backend - Development Makefile
# Provides convenient commands for common development tasks

.PHONY: help install format lint check test clean pre-commit-install pre-commit-run

# Default target
help:
	@echo "Ultra Civic Backend Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install           Install dependencies with Poetry"
	@echo "  pre-commit-install Install pre-commit hooks"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  format            Format code with Black and Ruff"
	@echo "  lint              Run linting checks"
	@echo "  check             Run comprehensive quality checks"
	@echo "  test              Run test suite"
	@echo ""
	@echo "Pre-commit Commands:"
	@echo "  pre-commit-run    Run pre-commit hooks manually"
	@echo "  pre-commit-all    Run pre-commit hooks on all files"
	@echo ""
	@echo "Database Commands:"
	@echo "  migrate           Run database migrations"
	@echo "  migrate-auto      Generate and run auto migration"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean             Clean temporary files and caches"
	@echo "  dev               Start development server"

# Setup commands
install:
	poetry install
	@echo "✅ Dependencies installed"

pre-commit-install:
	poetry run pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Code quality commands
format:
	@echo "🎨 Formatting code..."
	poetry run python scripts/format.py

lint:
	@echo "🔍 Running linting checks..."
	poetry run python scripts/lint.py

check:
	@echo "🔬 Running comprehensive quality checks..."
	poetry run python scripts/check.py

test:
	@echo "🧪 Running test suite..."
	poetry run pytest tests/ -v

# Pre-commit commands
pre-commit-run:
	poetry run pre-commit run

pre-commit-all:
	poetry run pre-commit run --all-files

# Database commands
migrate:
	@echo "🗄️  Running database migrations..."
	poetry run alembic upgrade head

migrate-auto:
	@echo "🗄️  Generating auto migration..."
	poetry run alembic revision --autogenerate -m "Auto migration"
	poetry run alembic upgrade head

# Development commands
dev:
	@echo "🚀 Starting development server..."
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Utility commands
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -f bandit-report.json
	@echo "✅ Cleanup completed"

# Quality assurance pipeline
qa: format lint test
	@echo "🎉 Quality assurance pipeline completed!"

# Complete development setup
setup: install pre-commit-install
	@echo "🎯 Development environment setup completed!"
	@echo "💡 Run 'make help' to see available commands"