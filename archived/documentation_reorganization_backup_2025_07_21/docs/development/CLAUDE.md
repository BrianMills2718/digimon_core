# Development Documentation - CLAUDE.md

## Overview
The `docs/development/` directory contains guides, standards, and best practices for developers working on KGAS. This documentation ensures consistent development practices, quality standards, and efficient workflows across the project.

## Directory Structure

### Current Files
- **`DEPLOYMENT.md`**: Production deployment procedures and configuration
- **Standards and guides**: Development standards, coding practices, testing procedures
- **Contributing guidelines**: How to contribute to the project effectively

### Expected Development Documentation
- **`contributing/`**: Contribution guidelines and workflow processes
- **`guides/`**: Development guides for specific areas (setup, debugging, etc.)
- **`standards/`**: Coding standards, logging practices, error handling standards
- **`testing/`**: Testing procedures, evaluation methods, verification standards

## Development Philosophy

### Academic Research Tool Focus
- **Correctness over performance**: Prioritize accurate results and reproducibility
- **Flexibility over optimization**: Support diverse research needs and methods
- **Evidence-based development**: All claims backed by actual implementation and testing
- **Theory-aware architecture**: Support domain-specific analysis and ontologies

### Quality Standards
- **Fail-fast architecture**: Expose problems immediately rather than masking them
- **Zero tolerance for deceptive practices**: No mocks, stubs, or fabricated evidence
- **Contract-first design**: All components interact via defined, verifiable contracts
- **Comprehensive testing**: Unit, integration, and adversarial testing for critical components

## Development Workflow

### Setup and Environment
```bash
# Initial setup
git clone https://github.com/your-org/KGAS.git
cd KGAS

# Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .

# Install development dependencies
pip install -r requirements/dev.txt

# Database setup
docker-compose up -d neo4j

# Verify installation
python scripts/verify_system.py
```

### Development Cycle
1. **Create feature branch**: `git checkout -b feature/description`
2. **Write contract**: Create or update tool contract if applicable
3. **Implement feature**: Follow coding standards and patterns
4. **Write tests**: Unit tests minimum, integration tests for critical path
5. **Validate quality**: Run linting, type checking, and testing
6. **Document changes**: Update relevant documentation
7. **Create pull request**: Include evidence of testing and validation

### Code Quality Gates
```bash
# Run before committing
make lint          # Code linting and formatting
make typecheck     # Type checking with mypy
make test-unit     # Unit tests
make test-integration  # Integration tests (if applicable)
make validate-contracts  # Contract validation
```

## Coding Standards

### Python Style Guidelines
- **Follow PEP 8**: Use black formatter and flake8 linter
- **Type hints**: All functions should have comprehensive type hints
- **Docstrings**: Use Google-style docstrings for all public functions
- **Error handling**: Implement fail-fast error handling with recovery guidance
- **Logging**: Use structured logging with appropriate levels

### Code Organization
```python
# Standard module structure
"""
Module docstring describing purpose and usage.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Local imports after standard library and third-party
from src.core.service_manager import ServiceManager
from src.utils.validation import validate_input

logger = logging.getLogger(__name__)

class ComponentName:
    """
    Class docstring with purpose, usage, and examples.
    
    Args:
        service_manager: Dependency injection for core services
        
    Example:
        >>> component = ComponentName(service_manager)
        >>> result = component.process(data)
        >>> assert result["status"] == "success"
    """
    
    def __init__(self, service_manager: ServiceManager) -> None:
        self.services = service_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data with comprehensive error handling.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Result dictionary with status and data/error
            
        Raises:
            ValueError: If input data is invalid
            RuntimeError: If processing fails
        """
        try:
            # Input validation
            validate_input(data, self._get_input_schema())
            
            # Processing with logging
            self.logger.info(f"Processing started for {len(data)} items")
            result = self._core_processing(data)
            self.logger.info("Processing completed successfully")
            
            return {"status": "success", "data": result}
            
        except ValueError as e:
            self.logger.error(f"Input validation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "error_type": "validation",
                "recovery": "Check input format and required fields"
            }
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "error_type": "processing",
                "recovery": "Review logs and retry with valid data"
            }
```

### Error Handling Standards
```python
# Fail-fast with informative errors
def robust_function(param: str) -> Dict[str, Any]:
    """Example of robust error handling pattern."""
    
    # Input validation - fail fast
    if not param:
        raise ValueError("Parameter cannot be empty")
    
    if not isinstance(param, str):
        raise TypeError(f"Expected string, got {type(param)}")
    
    # Processing with try-catch
    try:
        result = risky_operation(param)
        return {"status": "success", "data": result}
        
    except SpecificError as e:
        # Log error with context
        logger.error(f"Operation failed for param='{param}': {e}")
        
        # Return structured error
        return {
            "status": "error",
            "error": str(e),
            "context": {"param": param},
            "recovery": "Try with different input or check configuration"
        }
```

### Testing Standards
```python
# Comprehensive testing pattern
import pytest
from unittest.mock import Mock, patch

class TestComponentName:
    """Test class following standard patterns."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.service_manager = Mock()
        self.component = ComponentName(self.service_manager)
    
    def test_successful_processing(self):
        """Test normal operation."""
        # Arrange
        input_data = {"key": "value"}
        expected_result = {"processed": "data"}
        
        # Act
        result = self.component.process(input_data)
        
        # Assert
        assert result["status"] == "success"
        assert result["data"] == expected_result
    
    def test_input_validation_error(self):
        """Test input validation."""
        # Arrange
        invalid_data = {}
        
        # Act
        result = self.component.process(invalid_data)
        
        # Assert
        assert result["status"] == "error"
        assert result["error_type"] == "validation"
        assert "recovery" in result
    
    def test_processing_error_handling(self):
        """Test error handling during processing."""
        # Arrange
        input_data = {"key": "value"}
        
        # Mock to raise exception
        with patch.object(self.component, '_core_processing') as mock_process:
            mock_process.side_effect = RuntimeError("Processing failed")
            
            # Act
            result = self.component.process(input_data)
            
            # Assert
            assert result["status"] == "error"
            assert result["error_type"] == "processing"
    
    @pytest.mark.integration
    def test_integration_with_services(self):
        """Integration test with real services."""
        # Test with actual service manager
        from src.core.service_manager import ServiceManager
        real_services = ServiceManager()
        component = ComponentName(real_services)
        
        # Test real integration
        result = component.process({"real": "data"})
        assert result["status"] in ["success", "error"]
```

## Tool Development Standards

### Tool Implementation Pattern
```python
# Standard tool development pattern
from src.tools.base_tool import BaseTool

class ToolImplementation(BaseTool):
    """
    Tool following standard implementation pattern.
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = self.__class__.__name__
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution following standard pattern."""
        try:
            # Contract validation
            self._validate_contract(params)
            
            # Core processing
            result = self._process(params)
            
            # Quality assessment
            confidence = self.quality.assess_confidence(result)
            
            # Provenance logging
            self.provenance.log_execution(
                tool_id=self.tool_id,
                inputs=params,
                outputs=result,
                confidence=confidence
            )
            
            return {
                "status": "success",
                "data": result,
                "confidence": confidence,
                "tool_id": self.tool_id
            }
            
        except Exception as e:
            return self._handle_error(e, params)
```

### MCP Integration Standards
```python
# MCP tool wrapper pattern
from fastmcp import FastMCP

app = FastMCP("Tool Name")

@app.tool()
def tool_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    MCP tool following standard pattern.
    
    Args:
        param1: Required parameter description
        param2: Optional parameter description
        
    Returns:
        Standard result dictionary with status and data/error
    """
    # Get services
    service_manager = ServiceManager()
    
    # Create tool
    tool = ToolImplementation(service_manager)
    
    # Execute with standard error handling
    return tool.execute({"param1": param1, "param2": param2})
```

## Documentation Standards

### Code Documentation
```python
def function_example(param1: str, param2: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    More detailed description if needed, including usage patterns,
    performance considerations, or important notes.
    
    Args:
        param1: Description of param1, including format expectations
        param2: Description of param2, including default behavior
        
    Returns:
        Dictionary containing:
            - status: "success" or "error"
            - data: Result data (if successful)
            - error: Error message (if failed)
            - recovery: Recovery guidance (if failed)
            
    Raises:
        ValueError: If param1 is invalid format
        RuntimeError: If processing fails unexpectedly
        
    Example:
        >>> result = function_example("test", ["option1", "option2"])
        >>> assert result["status"] == "success"
        >>> data = result["data"]
        
    Note:
        This function is thread-safe and can be called concurrently.
    """
```

### README Patterns
```markdown
# Component Name

Brief description of component purpose and role in KGAS.

## Installation

```bash
# Installation commands
```

## Usage

```python
# Basic usage example
```

## Configuration

Description of configuration options.

## Testing

```bash
# How to run tests
```

## Contributing

Link to contribution guidelines.
```

## Environment and Tools

### Development Environment
```bash
# Required tools
python >= 3.8
docker
git
make (optional, for convenience commands)

# IDE recommendations
- VS Code with Python extension
- PyCharm Professional/Community
- Vim/Neovim with appropriate plugins

# Recommended VS Code settings
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

### Git Workflow
```bash
# Branch naming
feature/short-description
bugfix/issue-description
docs/documentation-update

# Commit message format
type(scope): brief description

Longer description if needed explaining the change and why it was made.

# Examples
feat(tools): add T02 Word document loader
fix(core): resolve PipelineOrchestrator import error
docs(architecture): update cross-modal analysis documentation
test(integration): add end-to-end workflow testing
```

### Continuous Integration
```yaml
# .github/workflows/test.yml pattern
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements/dev.txt
      - name: Lint
        run: make lint
      - name: Type check
        run: make typecheck
      - name: Test
        run: make test
      - name: Validate contracts
        run: make validate-contracts
```

## Debugging and Troubleshooting

### Common Development Issues

#### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify package installation
pip list | grep kgas

# Install in development mode
pip install -e .
```

#### Database Connection Issues
```bash
# Check Docker containers
docker ps

# Start Neo4j
docker-compose up -d neo4j

# Test connection
python -c "
from src.core.neo4j_manager import Neo4jManager
manager = Neo4jManager()
print(manager.health_check())
"
```

#### Test Failures
```bash
# Run specific test
python -m pytest tests/unit/test_specific.py::test_function -v

# Run with debugging
python -m pytest tests/ --pdb

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Logging and Debugging
```python
# Development logging configuration
import logging

# Set up debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use in development
logger = logging.getLogger(__name__)
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning about potential issues")
logger.error("Error that needs attention")
```

## Performance and Optimization

### Development Performance
- **Use profiling tools**: cProfile, memory_profiler for performance analysis
- **Cache expensive operations**: Use functools.lru_cache appropriately
- **Monitor resource usage**: Track memory and CPU usage during development
- **Optimize imports**: Use lazy imports for heavy dependencies

### Database Performance
```python
# Efficient Neo4j queries
def efficient_query_pattern(driver, entity_ids: List[str]):
    """Example of efficient batch querying."""
    with driver.session() as session:
        # Batch query instead of individual queries
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.id IN $entity_ids
            RETURN e.id, e.name, e.confidence
        """, entity_ids=entity_ids)
        
        return [record.data() for record in result]

# Avoid N+1 query problems
# Use batching for multiple operations
# Use parameterized queries for security and performance
```

## Contributing Guidelines

### Code Review Standards
- **Review for correctness**: Does the code do what it claims?
- **Review for quality**: Follows coding standards and patterns?
- **Review for testing**: Adequate test coverage and quality?
- **Review for documentation**: Clear documentation and examples?
- **Review for integration**: Works with existing system?

### Pull Request Template
```markdown
## Description
Brief description of changes and motivation.

## Changes Made
- Specific change 1
- Specific change 2

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed
- [ ] Contract validation passes (if applicable)

## Documentation
- [ ] Code documentation updated
- [ ] README updated (if needed)
- [ ] Architecture docs updated (if applicable)

## Evidence
Include evidence of testing, performance measurements, or validation results.
```

The development documentation ensures consistent, high-quality development practices that support KGAS's academic research focus and cross-modal analysis capabilities.