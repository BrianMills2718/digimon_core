# Utils Module - CLAUDE.md

## Overview
The `src/utils/` directory contains utility functions, helper modules, and common functionality shared across the KGAS system. These utilities provide foundational support for database operations, file handling, data processing, and system integration.

## Directory Structure

### Current State
The utils directory is currently minimal but should contain:
- **Database utilities**: Connection helpers, query builders, transaction management
- **File handling**: Safe file operations, path utilities, format detection
- **Data processing**: Serialization, validation, transformation utilities
- **System integration**: Service discovery, health checks, configuration helpers
- **Cross-modal utilities**: Format conversion helpers, reference resolution

## Expected Utility Categories

### Database Utilities
```python
# src/utils/database.py
class DatabaseManager:
    """Unified database connection and operation management"""
    def get_neo4j_connection(self) -> neo4j.Driver
    def get_sqlite_connection(self) -> sqlite3.Connection
    def execute_transaction(self, operations: List[DatabaseOp]) -> Result
    def health_check(self) -> Dict[str, bool]

# src/utils/references.py
class ReferenceManager:
    """Universal reference system for cross-modal data"""
    def create_reference(self, storage: str, type: str, id: str) -> str
    def resolve_reference(self, reference: str) -> Optional[Dict]
    def validate_reference(self, reference: str) -> bool
```

### File and Data Utilities
```python
# src/utils/file_operations.py
def safe_file_read(path: Path, encoding: str = 'utf-8') -> str
def detect_file_format(path: Path) -> str
def ensure_directory(path: Path) -> None
def secure_temp_file() -> Path

# src/utils/serialization.py
def serialize_with_provenance(data: Any, metadata: Dict) -> str
def deserialize_with_validation(data: str, schema: Dict) -> Any
def compress_large_data(data: str, threshold: int = 1000000) -> str
```

### Cross-Modal Utilities
```python
# src/utils/format_conversion.py
class FormatConverter:
    """Convert between graph, table, and vector representations"""
    def graph_to_table(self, graph_data: Dict) -> pd.DataFrame
    def table_to_graph(self, df: pd.DataFrame) -> Dict
    def extract_vectors(self, data: Any) -> np.ndarray
    def vectors_to_similarity_graph(self, vectors: np.ndarray) -> Dict

# src/utils/cross_modal.py
def suggest_optimal_format(analysis_type: str, data_size: int) -> str
def validate_cross_modal_conversion(source: Any, target: Any) -> bool
def maintain_provenance_chain(operation: str, source_ref: str) -> str
```

### System Integration Utilities
```python
# src/utils/service_discovery.py
def discover_available_services() -> List[str]
def check_service_health(service_name: str) -> bool
def get_service_endpoint(service_name: str) -> str

# src/utils/configuration.py
def load_environment_config() -> Dict
def validate_configuration(config: Dict) -> List[str]
def merge_configurations(base: Dict, override: Dict) -> Dict
```

## Common Patterns

### Error Handling
```python
# All utilities should use consistent error handling
try:
    result = risky_operation()
    return {"status": "success", "data": result}
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return {"status": "error", "error": str(e), "recovery": "suggested_action"}
```

### Logging and Monitoring
```python
# All utilities should include proper logging
import logging
logger = logging.getLogger(__name__)

def utility_function(params):
    logger.info(f"Starting operation with params: {params}")
    # ... operation ...
    logger.info(f"Operation completed successfully")
    return result
```

### Input Validation
```python
# All utilities should validate inputs
from typing import Union, Optional
from pathlib import Path

def safe_file_operation(file_path: Union[str, Path]) -> Optional[str]:
    """Safe file operation with comprehensive validation"""
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    # ... rest of operation ...
```

## Development Guidelines

### Creating New Utilities
1. **Single Responsibility**: Each utility should have one clear purpose
2. **Type Hints**: Use comprehensive type hints for all functions
3. **Documentation**: Include docstrings with examples
4. **Error Handling**: Implement consistent error handling patterns
5. **Testing**: Create unit tests for all utilities
6. **Integration**: Ensure utilities work with core services

### Naming Conventions
- **Files**: Use descriptive names (e.g., `database_operations.py`, `file_validators.py`)
- **Functions**: Use verb_noun pattern (e.g., `validate_file`, `convert_format`)
- **Classes**: Use noun pattern (e.g., `ReferenceManager`, `FormatConverter`)
- **Constants**: Use UPPER_CASE (e.g., `DEFAULT_TIMEOUT`, `MAX_FILE_SIZE`)

### Performance Considerations
- **Caching**: Use appropriate caching for expensive operations
- **Lazy Loading**: Load resources only when needed
- **Memory Management**: Be mindful of memory usage for large data
- **Connection Pooling**: Reuse database connections efficiently

## Common Commands

### Testing Utilities
```bash
# Run all utility tests
python -m pytest src/utils/

# Test specific utility
python -m pytest src/utils/test_database.py

# Test with coverage
python -m pytest src/utils/ --cov=src/utils --cov-report=html
```

### Import Patterns
```python
# Import utilities in tool implementations
from src.utils.database import DatabaseManager
from src.utils.references import ReferenceManager
from src.utils.format_conversion import FormatConverter

# Use dependency injection pattern
class Tool:
    def __init__(self, db_manager: DatabaseManager, ref_manager: ReferenceManager):
        self.db = db_manager
        self.refs = ref_manager
```

### Configuration Usage
```python
# Load configuration in utilities
from src.utils.configuration import load_environment_config

config = load_environment_config()
timeout = config.get('DATABASE_TIMEOUT', 30)
max_retries = config.get('MAX_RETRIES', 3)
```

## Integration Points

### Core Services
- **ServiceManager**: Utilities should be available through service manager
- **ConfigManager**: Use unified configuration system
- **ErrorHandler**: Integrate with system-wide error handling
- **LoggingConfig**: Use consistent logging configuration

### Tool Integration
- **Tool Base Classes**: Utilities should be available to all tools
- **Contract Compliance**: Utilities should support contract validation
- **Quality Services**: Integrate with confidence scoring and quality metrics
- **Provenance Tracking**: All utilities should support provenance

### Cross-Modal Analysis
- **AnalyticsService**: Utilities should support analytics orchestration
- **Format Conversion**: Enable seamless format transitions
- **Reference System**: Support universal reference resolution
- **Source Linking**: Maintain traceability to original sources

## Best Practices

### Code Organization
```python
# Organize utilities by functionality
src/utils/
├── __init__.py           # Export main utilities
├── database/             # Database utilities
│   ├── __init__.py
│   ├── connections.py
│   ├── operations.py
│   └── references.py
├── files/               # File handling utilities
│   ├── __init__.py
│   ├── operations.py
│   ├── validation.py
│   └── formats.py
├── cross_modal/         # Cross-modal utilities
│   ├── __init__.py
│   ├── conversion.py
│   ├── validation.py
│   └── orchestration.py
└── system/              # System utilities
    ├── __init__.py
    ├── configuration.py
    ├── health.py
    └── discovery.py
```

### Testing Strategy
```python
# Create comprehensive tests for utilities
import pytest
from unittest.mock import Mock, patch

def test_utility_success_case():
    """Test normal operation"""
    result = utility_function(valid_input)
    assert result["status"] == "success"

def test_utility_error_handling():
    """Test error scenarios"""
    with pytest.raises(SpecificError):
        utility_function(invalid_input)

def test_utility_edge_cases():
    """Test boundary conditions"""
    # Test empty input, large input, etc.
```

### Documentation Standards
```python
def utility_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of what the utility does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Dict containing result with status and data/error
    
    Raises:
        ValueError: If param1 is invalid
        RuntimeError: If operation fails
    
    Example:
        >>> result = utility_function("test", 42)
        >>> assert result["status"] == "success"
    """
```

## Future Expansion

### Planned Utilities
- **Theory Integration**: Utilities for theory-aware processing
- **LLM Operations**: Common LLM interaction patterns
- **Vector Operations**: Vector search and similarity utilities
- **Graph Operations**: Graph traversal and analysis utilities
- **Statistical Analysis**: Statistical processing utilities
- **Export Utilities**: Data export and format conversion

### Performance Monitoring
- **Metrics Collection**: Utility performance metrics
- **Resource Usage**: Memory and CPU monitoring
- **Cache Performance**: Cache hit rates and efficiency
- **Error Rates**: Track utility failure rates

The utils module provides the foundational layer that enables all other components to work together efficiently and reliably. Focus on creating robust, well-tested utilities that support the cross-modal analysis vision.