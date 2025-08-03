# KGAS Development Makefile
# Provides consistent commands for interface validation and development

.PHONY: help validate-interfaces fix-interfaces install-deps test lint clean

# Default target
help:
	@echo "🔧 KGAS Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Interface Management:"
	@echo "  make validate-interfaces    Run full interface validation pipeline"
	@echo "  make fix-interfaces        Auto-fix interface violations" 
	@echo "  make check-deprecated      Check for deprecated patterns only"
	@echo ""
	@echo "Development:"
	@echo "  make install-deps          Install required dependencies"
	@echo "  make test                  Run test suite"
	@echo "  make lint                  Run linting and formatting"
	@echo "  make clean                 Clean temporary files"
	@echo ""
	@echo "CI/CD:"
	@echo "  make ci-validate           Run CI-style validation (strict)"
	@echo "  make pre-commit            Run all pre-commit checks"

# Interface validation pipeline
validate-interfaces:
	@echo "🔍 Running interface validation pipeline..."
	@./scripts/validate-interfaces.sh

# Auto-fix interface violations
fix-interfaces:
	@echo "🔧 Auto-fixing interface violations..."
	@python fix_toolresult_interfaces.py
	@python fix_interface_contracts.py
	@echo "✅ Interface fixes complete. Run 'make validate-interfaces' to verify."

# Check for deprecated patterns only
check-deprecated:
	@echo "🕵️ Checking for deprecated interface patterns..."
	@echo "Checking for ToolResult(success=...):"
	@grep -r "ToolResult.*success\s*=" src/tools/ || echo "  ✅ None found"
	@echo ""
	@echo "Checking for ToolResult(error=...):"
	@grep -r "ToolResult.*\berror\s*=" src/tools/ | grep -v "error_message\|error_code" || echo "  ✅ None found"

# Install development dependencies
install-deps:
	@echo "📦 Installing development dependencies..."
	@pip install -r requirements.txt
	@pip install spacy==3.7.2 neo4j==5.14.1
	@python -m spacy download en_core_web_sm
	@echo "✅ Dependencies installed"

# Run tests
test:
	@echo "🧪 Running test suite..."
	@python -m pytest tests/ -v

# Linting and formatting
lint:
	@echo "🔍 Running linting..."
	@python -m flake8 src/ --max-line-length=120 --ignore=E203,W503
	@echo "✅ Linting complete"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f /tmp/interface_validation.log
	@echo "✅ Cleanup complete"

# CI-style strict validation
ci-validate:
	@echo "🏗️ Running CI-style validation (strict mode)..."
	@python validate_tool_interfaces.py || (echo "❌ Interface validation failed" && exit 1)
	@echo "✅ CI validation passed"

# Pre-commit hook
pre-commit: clean validate-interfaces
	@echo "🚀 Pre-commit validation complete!"
	@echo "Ready to commit! ✅"

# Quick interface summary
summary:
	@echo "📊 Interface Summary:"
	@echo "Total tool files: $$(find src/tools -name '*.py' | wc -l)"
	@echo "Files with interface issues: $$(python validate_tool_interfaces.py 2>&1 | grep -c '❌\|🚨' || echo 0)"
	@echo "Run 'make validate-interfaces' for detailed analysis"