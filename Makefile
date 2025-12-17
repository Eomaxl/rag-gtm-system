# RAG System Development Makefile

.PHONY: help install dev-install lint format type-check test test-unit test-property test-integration clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies and setup pre-commit
	pip install -r requirements.txt
	pre-commit install

lint:  ## Run linting checks
	flake8 src tests
	isort --check-only src tests
	black --check src tests

format:  ## Format code with black and isort
	isort src tests
	black src tests

type-check:  ## Run type checking with mypy
	mypy src

test:  ## Run all tests
	pytest tests/ -v

test-unit:  ## Run unit tests only
	pytest tests/ -v -m "unit"

test-property:  ## Run property-based tests only
	pytest tests/ -v -m "property"

test-integration:  ## Run integration tests only
	pytest tests/ -v -m "integration"

clean:  ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

run:  ## Run the development server
	python main.py

docker-build:  ## Build Docker image
	docker build -t rag-system:latest .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 rag-system:latest