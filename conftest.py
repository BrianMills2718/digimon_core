"""
Global pytest configuration for KGAS test suite

This file provides standardized test environment setup across all test suites,
ensuring consistent behavior for mock-free testing and service integration.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Set test environment
os.environ["KGAS_ENVIRONMENT"] = "test"
os.environ["KGAS_LOG_LEVEL"] = "WARNING"  # Reduce test noise

# Set default PII service values for testing to suppress warnings
os.environ.setdefault("KGAS_PII_PASSWORD", "test_password_not_for_production")
os.environ.setdefault("KGAS_PII_SALT", "test_salt_not_for_production")

# Set test database paths
os.environ.setdefault("KGAS_TEST_DB_PATH", ":memory:")
os.environ.setdefault("KGAS_TEST_DATA_DIR", str(Path(__file__).parent / "test_data"))

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables"""
    original_env = dict(os.environ)
    
    # Test environment configuration
    test_env = {
        "KGAS_ENVIRONMENT": "test",
        "KGAS_LOG_LEVEL": "WARNING",
        "KGAS_PII_PASSWORD": "test_password_not_for_production",
        "KGAS_PII_SALT": "test_salt_not_for_production",
        "KGAS_TEST_MODE": "true",
        # Disable external services in tests
        "KGAS_DISABLE_OPENAI": "true",
        "KGAS_DISABLE_NEO4J": "true",
        "KGAS_DISABLE_EXTERNAL_APIS": "true"
    }
    
    # Apply test environment
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture(scope="function")
def temp_test_dir():
    """Create temporary directory for test files"""
    temp_dir = Path(tempfile.mkdtemp(prefix="kgas_test_"))
    yield temp_dir
    
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def mock_free_service_manager():
    """Provide real ServiceManager for mock-free testing"""
    from src.core.service_manager import ServiceManager
    
    # Use real service manager with test configuration
    service_manager = ServiceManager()
    
    yield service_manager
    
    # Cleanup
    if hasattr(service_manager, 'cleanup'):
        service_manager.cleanup()

@pytest.fixture(scope="function")
def sample_test_data():
    """Provide sample test data for consistent testing"""
    return {
        "simple_text": "This is a simple test document with entities like Apple Inc. and Microsoft Corporation.",
        "unicode_text": "Test with Unicode: café, naïve, 你好世界, こんにちは, 🚀 ✨",
        "csv_data": "name,age,city\nJohn,25,New York\nJane,30,San Francisco\nBob,35,Chicago",
        "json_data": {
            "employees": [
                {"name": "John", "age": 25, "department": "Engineering"},
                {"name": "Jane", "age": 30, "department": "Marketing"}
            ],
            "company": "Test Corp"
        },
        "markdown_content": """# Test Document

## Overview
This is a **test document** for testing markdown parsing.

### Features
- Lists
- *Emphasis*
- `Code`

## Table
| Name | Role |
|------|------|
| John | Dev  |
| Jane | PM   |
""",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Document</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Test Document</h1>
    <p>This is a <strong>test document</strong> for HTML parsing.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</body>
</html>"""
    }

@pytest.fixture(autouse=True)
def suppress_external_warnings():
    """Suppress warnings from external libraries during testing"""
    import warnings
    
    # Suppress specific warnings that are common in tests
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", message=".*PytestUnknownMarkWarning.*", category=UserWarning)
    
    # Suppress Neo4j driver warnings in test mode
    warnings.filterwarnings("ignore", message=".*neo4j.*", category=UserWarning)
    
    # Suppress OpenAI API warnings in test mode
    warnings.filterwarnings("ignore", message=".*openai.*", category=UserWarning)
    
    yield
    
    # Reset warnings
    warnings.resetwarnings()

# Configure pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest markers and settings"""
    # Register custom markers
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "mock_free: mark test as mock-free implementation test")
    
    # Set test collection patterns
    config.option.python_files = ["test_*.py", "*_test.py"]
    config.option.python_classes = ["Test*", "*Test", "*Tests"]
    config.option.python_functions = ["test_*"]

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test path
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add mock_free marker for unified test files
        if "unified" in item.name and "mock_free" in str(item.fspath).lower():
            item.add_marker(pytest.mark.mock_free)
        
        # Add performance marker for performance tests
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory"""
    test_data_path = Path(__file__).parent / "test_data"
    test_data_path.mkdir(exist_ok=True)
    return test_data_path

# Test configuration complete