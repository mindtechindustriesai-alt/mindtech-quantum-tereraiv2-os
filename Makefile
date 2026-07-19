.PHONY: help install dev test lint format clean docker-build verify

help:
	@echo "Available commands:"
	@echo "  install       Install dependencies"
	@echo "  dev           Install development dependencies"
	@echo "  test          Run tests"
	@echo "  lint          Run linting"
	@echo "  format        Format code"
	@echo "  clean         Clean temporary files"
	@echo "  docker-build  Build Docker image"
	@echo "  verify        Run CHSH verification"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=mqos --cov-report=html

lint:
	ruff check mqos/ tests/

format:
	black mqos/ tests/
	isort mqos/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov

docker-build:
	docker build -t mqos-tererai .

verify:
	python scripts/verify_ibm.py
