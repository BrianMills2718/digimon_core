# Testing Framework Configuration Guide

This guide explains how to configure the testing framework using the centralized configuration system.

## Overview

The testing framework now uses a centralized configuration system that:
- Eliminates hardcoded values throughout the codebase
- Supports environment variable overrides
- Provides sensible defaults for all settings
- Supports configuration files (YAML/JSON)
- Ensures consistent configuration across all testing components

## Quick Start

### Using Environment Variables

```bash
# Database configuration
export TEST_NEO4J_URI="bolt://localhost:7687"
export TEST_NEO4J_USER="neo4j"
export TEST_NEO4J_PASSWORD="your_password"
export TEST_NEO4J_DATABASE="test"

# Performance testing
export TEST_PERFORMANCE_ITERATIONS="20"
export TEST_TIMEOUT_SECONDS="60"
export TEST_BASELINE_TOLERANCE="15.0"

# Mock services
export TEST_MOCK_SUCCESS_RATE="0.95"
export TEST_MOCK_DELAY_MS="5.0"

# Run tests
python -m pytest src/testing/
```

### Using Configuration Files

1. Generate a template:
```bash
cd src/testing
python config.py template
```

2. Edit the generated `testing_config_template.yaml`:
```yaml
database:
  uri: bolt://localhost:7687
  username: neo4j
  password: your_password
  database: test

performance:
  default_iterations: 20
  warmup_iterations: 5
  timeout_seconds: 60
  baseline_tolerance_percent: 15.0
```

3. Load the configuration:
```python
from testing.config import load_config_from_file
config = load_config_from_file("my_test_config.yaml")
```

## Configuration Categories

### Database Configuration

Controls Neo4j database connections for testing.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `uri` | `TEST_NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `username` | `TEST_NEO4J_USER` | `neo4j` | Database username |
| `password` | `TEST_NEO4J_PASSWORD` | `neo4j` | Database password |
| `database` | `TEST_NEO4J_DATABASE` | `test` | Database name |

### Performance Configuration

Controls performance testing behavior.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `default_iterations` | `TEST_PERFORMANCE_ITERATIONS` | `10` | Default test iterations |
| `warmup_iterations` | `TEST_WARMUP_ITERATIONS` | `3` | Warmup iterations |
| `timeout_seconds` | `TEST_TIMEOUT_SECONDS` | `30` | Test timeout in seconds |
| `baseline_tolerance_percent` | `TEST_BASELINE_TOLERANCE` | `10.0` | Performance tolerance % |
| `concurrent_calls` | `TEST_CONCURRENT_CALLS` | `10` | Concurrent calls for stress tests |
| `stress_duration_seconds` | `TEST_STRESS_DURATION` | `30` | Stress test duration |

### Mock Configuration

Controls mock service behavior.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `default_delay_ms` | `TEST_MOCK_DELAY_MS` | `10.0` | Mock service delay in ms |
| `success_rate` | `TEST_MOCK_SUCCESS_RATE` | `0.9` | Mock success rate (0.0-1.0) |
| `failure_modes` | `TEST_MOCK_FAILURE_MODES` | `timeout,connection_error,invalid_input` | Comma-separated failure modes |

### Integration Configuration

Controls integration testing behavior.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `use_real_services` | `TEST_USE_REAL_SERVICES` | `false` | Use real services vs mocks |
| `mock_external_services` | `TEST_MOCK_EXTERNAL` | `true` | Mock external dependencies |
| `use_in_memory_storage` | `TEST_IN_MEMORY_STORAGE` | `true` | Use in-memory storage |
| `similarity_threshold` | `TEST_SIMILARITY_THRESHOLD` | `0.8` | Entity similarity threshold |

### Test Data Configuration

Controls test data generation sizes.

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| `small_dataset_size.docs` | `TEST_SMALL_DOCS` | `10` | Small dataset document count |
| `small_dataset_size.entities` | `TEST_SMALL_ENTITIES` | `50` | Small dataset entity count |
| `medium_dataset_size.docs` | `TEST_MEDIUM_DOCS` | `100` | Medium dataset document count |
| `large_dataset_size.docs` | `TEST_LARGE_DOCS` | `1000` | Large dataset document count |

*(Similar pattern for entities, mentions, relationships)*

## Programming Interface

### Basic Usage

```python
from testing.config import get_testing_config

# Get current configuration
config = get_testing_config()

# Access configuration values
print(f"Neo4j URI: {config.database.uri}")
print(f"Test iterations: {config.performance.default_iterations}")
print(f"Mock delay: {config.mock.default_delay_ms}ms")

# Convert to dict for legacy compatibility
config_dict = config.to_dict()
container.configure(config_dict)
```

### Reloading Configuration

```python
# Reload configuration (e.g., after changing env vars)
config = get_testing_config(reload=True)
```

### Loading from Files

```python
from testing.config import load_config_from_file

# Load from YAML
config = load_config_from_file("test_config.yaml")

# Load from JSON
config = load_config_from_file("test_config.json")
```

### Creating Custom Configurations

```python
from testing.config import TestingConfig, DatabaseConfig, PerformanceConfig

# Create custom configuration
config = TestingConfig(
    database=DatabaseConfig(
        uri="bolt://custom:7687",
        username="custom_user"
    ),
    performance=PerformanceConfig(
        default_iterations=50,
        timeout_seconds=120
    )
)
```

## Test Environment Setup

### Development Environment

```bash
# .env file for development
TEST_NEO4J_URI=bolt://localhost:7687
TEST_NEO4J_USER=neo4j
TEST_NEO4J_PASSWORD=neo4j
TEST_PERFORMANCE_ITERATIONS=5
TEST_TIMEOUT_SECONDS=15
TEST_MOCK_SUCCESS_RATE=1.0  # No failures during development
```

### CI/CD Environment

```bash
# CI environment variables
TEST_NEO4J_URI=bolt://neo4j-test:7687
TEST_NEO4J_USER=test_user
TEST_NEO4J_PASSWORD=$NEO4J_TEST_PASSWORD
TEST_PERFORMANCE_ITERATIONS=3  # Faster CI runs
TEST_TIMEOUT_SECONDS=10
TEST_USE_REAL_SERVICES=false  # Always use mocks in CI
```

### Production Testing Environment

```bash
# Production-like testing
TEST_NEO4J_URI=bolt://neo4j-staging:7687
TEST_PERFORMANCE_ITERATIONS=20
TEST_TIMEOUT_SECONDS=60
TEST_BASELINE_TOLERANCE=5.0  # Stricter performance requirements
TEST_USE_REAL_SERVICES=true  # Test against real services
```

## Migration from Hardcoded Values

### Before (Hardcoded)

```python
# Old hardcoded approach
test_config = {
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'username': 'neo4j',
        'password': 'testpassword',
        'database': 'test'
    },
    'testing': {
        'timeout_seconds': 30
    }
}
```

### After (Centralized)

```python
# New centralized approach
from testing.config import get_testing_config

config = get_testing_config()
test_config = config.to_dict()
```

## Troubleshooting

### Common Issues

1. **Configuration not updating**: Use `reload=True` to force reload
2. **Environment variables not working**: Check variable names match exactly
3. **Type conversion errors**: Ensure environment variables are valid (e.g., numbers for numeric settings)

### Debugging Configuration

```python
from testing.config import get_testing_config
import os

# Show all environment variables
print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith('TEST_'):
        print(f"  {key}={value}")

# Show current configuration
config = get_testing_config()
print("\nCurrent configuration:")
import json
print(json.dumps(config.to_dict(), indent=2))
```

### Validation

```bash
# Validate current configuration
cd src/testing
python config.py show

# Generate template for reference
python config.py template

# Show environment variable help
python config.py help
```

## Best Practices

1. **Use environment variables** for deployment-specific settings
2. **Use configuration files** for complex test scenarios
3. **Set defaults** that work for typical development
4. **Document** any custom configuration requirements
5. **Validate** configuration in CI/CD pipelines
6. **Use reload=True** when configuration changes during runtime

## Examples

### Example 1: High-Performance Testing

```bash
export TEST_PERFORMANCE_ITERATIONS=100
export TEST_CONCURRENT_CALLS=50
export TEST_STRESS_DURATION=300
export TEST_TIMEOUT_SECONDS=600
python -m pytest src/testing/performance_test.py
```

### Example 2: Quick Development Testing

```bash
export TEST_PERFORMANCE_ITERATIONS=3
export TEST_WARMUP_ITERATIONS=1
export TEST_TIMEOUT_SECONDS=5
export TEST_MOCK_SUCCESS_RATE=1.0
python -m pytest src/testing/ -v
```

### Example 3: Realistic Integration Testing

```bash
export TEST_USE_REAL_SERVICES=true
export TEST_MOCK_EXTERNAL=false
export TEST_BASELINE_TOLERANCE=20.0
python -m pytest src/testing/integration_test.py
```

This centralized configuration system provides flexibility while maintaining simplicity for typical testing scenarios.