from src.core.standard_config import get_database_uri
"""
Testing Framework Configuration

Centralized configuration management for the testing framework with
environment variable support and validation.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration for testing"""
    uri: str = field(default_factory=lambda: os.getenv('TEST_NEO4J_URI', get_database_uri()))
    username: str = field(default_factory=lambda: os.getenv('TEST_NEO4J_USER', 'neo4j'))
    password: str = field(default_factory=lambda: os.getenv('TEST_NEO4J_PASSWORD', 'neo4j'))
    database: str = field(default_factory=lambda: os.getenv('TEST_NEO4J_DATABASE', 'test'))


@dataclass
class PerformanceConfig:
    """Performance testing configuration"""
    default_iterations: int = field(default_factory=lambda: int(os.getenv('TEST_PERFORMANCE_ITERATIONS', '10')))
    warmup_iterations: int = field(default_factory=lambda: int(os.getenv('TEST_WARMUP_ITERATIONS', '3')))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv('TEST_TIMEOUT_SECONDS', '30')))
    baseline_tolerance_percent: float = field(default_factory=lambda: float(os.getenv('TEST_BASELINE_TOLERANCE', '10.0')))
    concurrent_calls: int = field(default_factory=lambda: int(os.getenv('TEST_CONCURRENT_CALLS', '10')))
    stress_duration_seconds: int = field(default_factory=lambda: int(os.getenv('TEST_STRESS_DURATION', '30')))


@dataclass
class MockConfig:
    """Mock service configuration"""
    default_delay_ms: float = field(default_factory=lambda: float(os.getenv('TEST_MOCK_DELAY_MS', '10.0')))
    success_rate: float = field(default_factory=lambda: float(os.getenv('TEST_MOCK_SUCCESS_RATE', '0.9')))
    failure_modes: List[str] = field(default_factory=lambda: os.getenv('TEST_MOCK_FAILURE_MODES', 'timeout,connection_error,invalid_input').split(','))


@dataclass
class IntegrationConfig:
    """Integration testing configuration"""
    use_real_services: bool = field(default_factory=lambda: os.getenv('TEST_USE_REAL_SERVICES', 'false').lower() == 'true')
    mock_external_services: bool = field(default_factory=lambda: os.getenv('TEST_MOCK_EXTERNAL', 'true').lower() == 'true')
    use_in_memory_storage: bool = field(default_factory=lambda: os.getenv('TEST_IN_MEMORY_STORAGE', 'true').lower() == 'true')
    similarity_threshold: float = field(default_factory=lambda: float(os.getenv('TEST_SIMILARITY_THRESHOLD', '0.8')))


@dataclass
class TestDataConfig:
    """Test data generation configuration"""
    small_dataset_size: Dict[str, int] = field(default_factory=lambda: {
        'docs': int(os.getenv('TEST_SMALL_DOCS', '10')),
        'entities': int(os.getenv('TEST_SMALL_ENTITIES', '50')),
        'mentions': int(os.getenv('TEST_SMALL_MENTIONS', '100')),
        'relationships': int(os.getenv('TEST_SMALL_RELATIONSHIPS', '75'))
    })
    medium_dataset_size: Dict[str, int] = field(default_factory=lambda: {
        'docs': int(os.getenv('TEST_MEDIUM_DOCS', '100')),
        'entities': int(os.getenv('TEST_MEDIUM_ENTITIES', '500')),
        'mentions': int(os.getenv('TEST_MEDIUM_MENTIONS', '1000')),
        'relationships': int(os.getenv('TEST_MEDIUM_RELATIONSHIPS', '750'))
    })
    large_dataset_size: Dict[str, int] = field(default_factory=lambda: {
        'docs': int(os.getenv('TEST_LARGE_DOCS', '1000')),
        'entities': int(os.getenv('TEST_LARGE_ENTITIES', '5000')),
        'mentions': int(os.getenv('TEST_LARGE_MENTIONS', '10000')),
        'relationships': int(os.getenv('TEST_LARGE_RELATIONSHIPS', '7500'))
    })


@dataclass
class TestingConfig:
    """Complete testing framework configuration"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    mock: MockConfig = field(default_factory=MockConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    test_data: TestDataConfig = field(default_factory=TestDataConfig)
    
    # Logging configuration
    log_level: str = field(default_factory=lambda: os.getenv('TEST_LOG_LEVEL', 'DEBUG'))
    log_file: Optional[str] = field(default_factory=lambda: os.getenv('TEST_LOG_FILE'))
    
    # Discovery configuration
    test_directories: list = field(default_factory=lambda: os.getenv('TEST_DIRECTORIES', 'tests,src/testing/tests').split(','))
    test_patterns: list = field(default_factory=lambda: os.getenv('TEST_PATTERNS', 'test_*.py').split(','))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format for legacy compatibility"""
        return {
            'neo4j': {
                'uri': self.database.uri,
                'username': self.database.username,
                'password': self.database.password,
                'database': self.database.database
            },
            'identity': {
                'use_embeddings': False,
                'similarity_threshold': self.integration.similarity_threshold
            },
            'testing': {
                'mock_external_services': self.integration.mock_external_services,
                'use_in_memory_storage': self.integration.use_in_memory_storage,
                'timeout_seconds': self.performance.timeout_seconds
            },
            'performance': {
                'default_iterations': self.performance.default_iterations,
                'warmup_iterations': self.performance.warmup_iterations,
                'timeout_seconds': self.performance.timeout_seconds,
                'baseline_tolerance_percent': self.performance.baseline_tolerance_percent
            },
            'mock': {
                'default_delay_ms': self.mock.default_delay_ms,
                'success_rate': self.mock.success_rate,
                'failure_modes': self.mock.failure_modes
            }
        }


# Global configuration instance
_config: Optional[TestingConfig] = None


def get_testing_config(reload: bool = False) -> TestingConfig:
    """Get the global testing configuration instance"""
    global _config
    
    if _config is None or reload:
        _config = TestingConfig()
    
    return _config


def load_config_from_file(config_file: str) -> TestingConfig:
    """Load configuration from a file (JSON or YAML)"""
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    if config_path.suffix.lower() in ['.yaml', '.yml']:
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
    elif config_path.suffix.lower() == '.json':
        import json
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    else:
        raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    # Update environment variables with config file values
    _update_env_from_config(config_data)
    
    # Return new configuration instance
    return TestingConfig()


def _update_env_from_config(config_data: Dict[str, Any]) -> None:
    """Update environment variables from configuration data"""
    mapping = {
        'database.uri': 'TEST_NEO4J_URI',
        'database.username': 'TEST_NEO4J_USER',
        'database.password': 'TEST_NEO4J_PASSWORD',
        'database.database': 'TEST_NEO4J_DATABASE',
        'performance.default_iterations': 'TEST_PERFORMANCE_ITERATIONS',
        'performance.warmup_iterations': 'TEST_WARMUP_ITERATIONS',
        'performance.timeout_seconds': 'TEST_TIMEOUT_SECONDS',
        'mock.default_delay_ms': 'TEST_MOCK_DELAY_MS',
        'mock.success_rate': 'TEST_MOCK_SUCCESS_RATE'
    }
    
    for config_path, env_var in mapping.items():
        keys = config_path.split('.')
        value = config_data
        
        try:
            for key in keys:
                value = value[key]
            os.environ[env_var] = str(value)
        except (KeyError, TypeError):
            continue  # Skip missing configuration values


def save_config_template(output_file: str = "testing_config_template.yaml") -> None:
    """Save a configuration template file with all available options"""
    template = {
        'database': {
            'uri': get_database_uri(),
            'username': 'neo4j',
            'password': 'neo4j',
            'database': 'test'
        },
        'performance': {
            'default_iterations': 10,
            'warmup_iterations': 3,
            'timeout_seconds': 30,
            'baseline_tolerance_percent': 10.0,
            'concurrent_calls': 10,
            'stress_duration_seconds': 30
        },
        'mock': {
            'default_delay_ms': 10.0,
            'success_rate': 0.9,
            'failure_modes': ['timeout', 'connection_error', 'invalid_input']
        },
        'integration': {
            'use_real_services': False,
            'mock_external_services': True,
            'use_in_memory_storage': True,
            'similarity_threshold': 0.8
        },
        'test_data': {
            'small_dataset_size': {'docs': 10, 'entities': 50, 'mentions': 100, 'relationships': 75},
            'medium_dataset_size': {'docs': 100, 'entities': 500, 'mentions': 1000, 'relationships': 750},
            'large_dataset_size': {'docs': 1000, 'entities': 5000, 'mentions': 10000, 'relationships': 7500}
        },
        'logging': {
            'log_level': 'DEBUG',
            'log_file': None
        },
        'discovery': {
            'test_directories': ['tests', 'src/testing/tests'],
            'test_patterns': ['test_*.py']
        }
    }
    
    try:
        import yaml
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)
        print(f"Configuration template saved to: {output_file}")
    except ImportError:
        import json
        json_file = output_file.replace('.yaml', '.json')
        with open(json_file, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"Configuration template saved to: {json_file} (YAML not available)")


# Environment variable documentation
ENV_VARS_HELP = """
Testing Framework Environment Variables:

Database Configuration:
  TEST_NEO4J_URI              - Neo4j connection URI (default: bolt://localhost:7687)
  TEST_NEO4J_USER             - Neo4j username (default: neo4j)
  TEST_NEO4J_PASSWORD         - Neo4j password (default: neo4j)
  TEST_NEO4J_DATABASE         - Neo4j database name (default: test)

Performance Configuration:
  TEST_PERFORMANCE_ITERATIONS - Default test iterations (default: 10)
  TEST_WARMUP_ITERATIONS      - Warmup iterations (default: 3)
  TEST_TIMEOUT_SECONDS        - Test timeout in seconds (default: 30)
  TEST_BASELINE_TOLERANCE     - Performance baseline tolerance % (default: 10.0)
  TEST_CONCURRENT_CALLS       - Concurrent calls for stress tests (default: 10)
  TEST_STRESS_DURATION        - Stress test duration in seconds (default: 30)

Mock Configuration:
  TEST_MOCK_DELAY_MS          - Mock service delay in milliseconds (default: 10.0)
  TEST_MOCK_SUCCESS_RATE      - Mock service success rate (default: 0.9)
  TEST_MOCK_FAILURE_MODES     - Comma-separated failure modes (default: timeout,connection_error,invalid_input)

Integration Configuration:
  TEST_USE_REAL_SERVICES      - Use real services instead of mocks (default: false)
  TEST_MOCK_EXTERNAL          - Mock external services (default: true)
  TEST_IN_MEMORY_STORAGE      - Use in-memory storage (default: true)
  TEST_SIMILARITY_THRESHOLD   - Entity similarity threshold (default: 0.8)

Test Data Configuration:
  TEST_SMALL_DOCS             - Small dataset document count (default: 10)
  TEST_SMALL_ENTITIES         - Small dataset entity count (default: 50)
  TEST_MEDIUM_DOCS            - Medium dataset document count (default: 100)
  TEST_LARGE_DOCS             - Large dataset document count (default: 1000)
  (similar pattern for entities, mentions, relationships)

General Configuration:
  TEST_LOG_LEVEL              - Logging level (default: DEBUG)
  TEST_LOG_FILE               - Log file path (default: None - stdout)
  TEST_DIRECTORIES            - Comma-separated test directories (default: tests,src/testing/tests)
  TEST_PATTERNS               - Comma-separated test file patterns (default: test_*.py)
"""


def print_env_help() -> None:
    """Print environment variable documentation"""
    print(ENV_VARS_HELP)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "template":
            save_config_template()
        elif sys.argv[1] == "help":
            print_env_help()
        elif sys.argv[1] == "show":
            config = get_testing_config()
            print("Current Testing Configuration:")
            print("=" * 40)
            import json
            print(json.dumps(config.to_dict(), indent=2))
    else:
        print("Usage: python config.py [template|help|show]")
        print("  template - Generate configuration template file")
        print("  help     - Show environment variable documentation")
        print("  show     - Show current configuration")