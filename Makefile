.PHONY: help install run test lint format clean docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the Streamlit app"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean up temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Run the Streamlit app
run:
	streamlit run app.py

# Run tests
test:
	pytest

# Run linting
lint:
	flake8 src tests app.py
	mypy src app.py

# Format code
format:
	black src tests app.py
	isort src tests app.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

# Docker commands
docker-build:
	docker build -t university-performance-analyzer .

docker-run:
	docker run -p 8501:8501 university-performance-analyzer

# Development setup
dev-setup: install
	pip install -r requirements-optional.txt
	pre-commit install

# Full CI pipeline
ci: lint test
