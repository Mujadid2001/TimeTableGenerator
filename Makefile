# TimeTable Generator Makefile

.PHONY: help install install-dev test lint format type-check clean build docs serve-docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docs         - Build documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  all-checks   - Run all checks (test, lint, format, type)"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	pytest

test-cov:
	pytest --cov=src/timetable_generator --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/

format:
	black src/ tests/

format-check:
	black --check src/ tests/

type-check:
	mypy src/timetable_generator/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	python -m build

# Documentation
docs:
	cd docs && make html

serve-docs:
	cd docs/_build/html && python -m http.server 8000

# All checks
all-checks: test lint format-check type-check
	@echo "All checks passed!"

# Development setup
setup-dev: install-dev
	mkdir -p data exports logs templates
	cp .env.example .env
	@echo "Development environment set up!"
	@echo "Edit .env file to customize settings."