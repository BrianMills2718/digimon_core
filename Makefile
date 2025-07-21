# KGAS Makefile
# Common development tasks and verification

.PHONY: help verify-docs test clean install

help:
	@echo "Available targets:"
	@echo "  verify-docs    - Verify documentation claims and consistency"
	@echo "  test          - Run all tests"
	@echo "  clean         - Clean build artifacts"
	@echo "  install       - Install dependencies"

verify-docs:
	@echo "🔍 Verifying documentation claims..."
	@scripts/verify_all_documentation_claims.sh
	@echo "🔍 Checking documentation drift..."
	@scripts/check_doc_drift.py
	@echo "✅ Documentation verification complete"

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=src --cov-report=term-missing

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

install:
	@echo "📦 Installing base dependencies..."
	pip install -r requirements/base.txt

install-llm:
	@echo "📦 Installing LLM dependencies..."
	pip install -r requirements/llm.txt

install-ui:
	@echo "📦 Installing UI dependencies..."
	pip install -r requirements/ui.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements/dev.txt

format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	isort src/ tests/

lint:
	@echo "🔍 Linting code..."
	flake8 src/ tests/
	mypy src/

check: format lint test verify-docs
	@echo "✅ All checks passed"

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t kgas .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8501:8501 kgas

neo4j-start:
	@echo "🗄️ Starting Neo4j..."
	docker-compose up -d neo4j

neo4j-stop:
	@echo "🗄️ Stopping Neo4j..."
	docker-compose down

ui-start:
	@echo "��️ Starting UI..."
	python -m src.cli ui

mcp-start:
	@echo "🔌 Starting MCP server..."
	python -m src.cli mcp 