"""
Consolidated Configuration Management System

Single authoritative configuration manager combining features from both
unified_config.py and config.py systems. Eliminates redundancy and provides
comprehensive configuration management for production deployment.
"""

import os
import yaml
import jsonschema
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import time
import threading


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 7687
    username: str = "neo4j"
    password: str = ""
    database: str = "neo4j"
    uri: str = ""
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: float = 30.0
    keep_alive: bool = True
    
    def __post_init__(self):
        if not self.uri:
            self.uri = f"bolt://{self.host}:{self.port}"


@dataclass
class TextProcessingConfig:
    """Configuration for text processing."""
    chunk_size: int = 512
    semantic_similarity_threshold: float = 0.85
    max_chunks_per_document: int = 100
    chunk_overlap_size: int = 50


@dataclass
class EntityProcessingConfig:
    """Configuration for entity processing."""
    confidence_threshold: float = 0.7
    chunk_overlap_size: int = 50
    embedding_batch_size: int = 100
    max_entities_per_chunk: int = 20


@dataclass
class GraphConstructionConfig:
    """Configuration for graph construction."""
    pagerank_iterations: int = 100
    pagerank_damping_factor: float = 0.85
    pagerank_tolerance: float = 1e-6
    pagerank_min_score: float = 0.0001
    max_relationships_per_entity: int = 50
    graph_pruning_threshold: float = 0.1


@dataclass
class APIConfig:
    """API configuration for external services."""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "text-embedding-3-small"
    gemini_model: str = "gemini-2.0-flash-exp"
    timeout: int = 30
    max_retries: int = 3
    retry_attempts: int = 3
    timeout_seconds: int = 30
    batch_processing_size: int = 10


@dataclass
class SystemConfig:
    """System-level configuration."""
    log_level: str = "INFO"
    max_workers: int = 4
    backup_enabled: bool = True
    encryption_enabled: bool = True
    metrics_enabled: bool = True
    health_check_interval: int = 60
    environment: str = "development"
    debug: bool = False


@dataclass
class WorkflowConfig:
    """Configuration for workflow management."""
    storage_dir: str = "./data/workflows"
    checkpoint_interval: int = 10
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class TheoryConfig:
    """Configuration for theory processing."""
    enabled: bool = False
    schema_type: str = "MASTER_CONCEPTS"
    concept_library_path: str = "src/ontology_library/master_concepts.py"
    validation_enabled: bool = True
    enhancement_boost: float = 0.1


class ConfigurationError(Exception):
    """Configuration-related error."""
    pass


class ConfigurationManager:
    """
    Consolidated configuration management system.
    
    Combines and replaces both ConfigurationManager and the legacy ConfigurationManager.
    Provides comprehensive configuration management with validation and production readiness.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config_path: Optional[str] = None):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        if not getattr(self, '_initialized', False):
            self._initialized = True
            self.config_path = Path(config_path) if config_path else Path("config/default.yaml")
            self.config_data: Dict[str, Any] = {}
            self.environment_vars: Dict[str, str] = {}
            
            # Configuration objects
            self.database: DatabaseConfig = DatabaseConfig()
            self.api: APIConfig = APIConfig()
            self.system: SystemConfig = SystemConfig()
            self.text_processing: TextProcessingConfig = TextProcessingConfig()
            self.entity_processing: EntityProcessingConfig = EntityProcessingConfig()
            self.graph_construction: GraphConstructionConfig = GraphConstructionConfig()
            self.workflow: WorkflowConfig = WorkflowConfig()
            self.theory: TheoryConfig = TheoryConfig()
            
            # Load configuration
            self._load_config()
            self._load_environment_variables()
            self._validate_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                
                # Populate configuration objects
                self._populate_config_objects()
            else:
                # Create default config file
                self._create_default_config()
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def _populate_config_objects(self) -> None:
        """Populate configuration objects from loaded data."""
        if 'database' in self.config_data:
            self.database = DatabaseConfig(**self.config_data['database'])
        
        if 'api' in self.config_data:
            self.api = APIConfig(**self.config_data['api'])
        
        if 'system' in self.config_data:
            self.system = SystemConfig(**self.config_data['system'])
        
        if 'text_processing' in self.config_data:
            self.text_processing = TextProcessingConfig(**self.config_data['text_processing'])
        
        if 'entity_processing' in self.config_data:
            self.entity_processing = EntityProcessingConfig(**self.config_data['entity_processing'])
        
        if 'graph_construction' in self.config_data:
            self.graph_construction = GraphConstructionConfig(**self.config_data['graph_construction'])
        
        if 'workflow' in self.config_data:
            self.workflow = WorkflowConfig(**self.config_data['workflow'])
        
        if 'theory' in self.config_data:
            self.theory = TheoryConfig(**self.config_data['theory'])
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'NEO4J_HOST': ('database', 'host'),
            'NEO4J_PORT': ('database', 'port'),
            'NEO4J_USERNAME': ('database', 'username'),
            'NEO4J_USER': ('database', 'username'),
            'NEO4J_PASSWORD': ('database', 'password'),
            'NEO4J_DATABASE': ('database', 'database'),
            'NEO4J_URI': ('database', 'uri'),
            'NEO4J_MAX_POOL_SIZE': ('database', 'max_connection_pool_size'),
            'NEO4J_CONNECTION_TIMEOUT': ('database', 'connection_acquisition_timeout'),
            'NEO4J_KEEP_ALIVE': ('database', 'keep_alive'),
            
            'OPENAI_API_KEY': ('api', 'openai_api_key'),
            'ANTHROPIC_API_KEY': ('api', 'anthropic_api_key'),
            'GOOGLE_API_KEY': ('api', 'google_api_key'),
            'OPENAI_MODEL': ('api', 'openai_model'),
            'GEMINI_MODEL': ('api', 'gemini_model'),
            'API_TIMEOUT_SECONDS': ('api', 'timeout_seconds'),
            'API_RETRY_ATTEMPTS': ('api', 'retry_attempts'),
            'API_BATCH_SIZE': ('api', 'batch_processing_size'),
            
            'LOG_LEVEL': ('system', 'log_level'),
            'MAX_WORKERS': ('system', 'max_workers'),
            'BACKUP_ENABLED': ('system', 'backup_enabled'),
            'ENCRYPTION_ENABLED': ('system', 'encryption_enabled'),
            'METRICS_ENABLED': ('system', 'metrics_enabled'),
            'ENVIRONMENT': ('system', 'environment'),
            'DEBUG': ('system', 'debug'),
            'HEALTH_CHECK_INTERVAL': ('system', 'health_check_interval'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                self.environment_vars[env_var] = value
                
                # Apply to configuration objects
                config_obj = getattr(self, section)
                target_type = type(getattr(config_obj, key))
                converted_value = self._convert_type(value, target_type)
                setattr(config_obj, key, converted_value)
    
    def _convert_type(self, value: str, target_type: type) -> Any:
        """Convert string value to target type."""
        if target_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        else:
            return value
    
    def _validate_config(self) -> None:
        """Validate configuration completeness and fail fast on critical issues."""
        # Only perform strict validation in production mode
        if self.is_production_mode():
            required_fields = {
                'database.password': self.database.password,
                'database.uri': self.database.uri,
            }
            
            missing_fields = []
            for field_name, field_value in required_fields.items():
                if not field_value:
                    missing_fields.append(field_name)
            
            if missing_fields:
                raise ConfigurationError(
                    f"Missing required configuration in production mode: {', '.join(missing_fields)}"
                )
            
            # Validate database connectivity requirements
            if self.database.uri == "bolt://localhost:7687" and self.system.environment == "production":
                raise ConfigurationError("Production mode cannot use localhost database URI")
            
            if self.database.username == "neo4j" and self.database.password == "password":
                raise ConfigurationError("Production mode cannot use default database credentials")
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        default_config = {
            'database': {
                'host': 'localhost',
                'port': 7687,
                'username': 'neo4j',
                'password': '',
                'database': 'neo4j',
                'max_connection_pool_size': 50,
                'connection_acquisition_timeout': 30.0,
                'keep_alive': True
            },
            'api': {
                'openai_api_key': '',
                'anthropic_api_key': '',
                'google_api_key': '',
                'openai_model': 'text-embedding-3-small',
                'gemini_model': 'gemini-2.0-flash-exp',
                'timeout': 30,
                'max_retries': 3,
                'batch_processing_size': 10
            },
            'system': {
                'log_level': 'INFO',
                'max_workers': 4,
                'backup_enabled': True,
                'encryption_enabled': True,
                'metrics_enabled': True,
                'environment': 'development',
                'debug': False,
                'health_check_interval': 60
            },
            'text_processing': {
                'chunk_size': 512,
                'semantic_similarity_threshold': 0.85,
                'max_chunks_per_document': 100,
                'chunk_overlap_size': 50
            },
            'entity_processing': {
                'confidence_threshold': 0.7,
                'chunk_overlap_size': 50,
                'embedding_batch_size': 100,
                'max_entities_per_chunk': 20
            },
            'graph_construction': {
                'pagerank_iterations': 100,
                'pagerank_damping_factor': 0.85,
                'pagerank_tolerance': 1e-6,
                'pagerank_min_score': 0.0001,
                'max_relationships_per_entity': 50,
                'graph_pruning_threshold': 0.1
            },
            'workflow': {
                'storage_dir': './data/workflows',
                'checkpoint_interval': 10,
                'max_retries': 3,
                'timeout_seconds': 300
            },
            'theory': {
                'enabled': False,
                'schema_type': 'MASTER_CONCEPTS',
                'concept_library_path': 'src/ontology_library/master_concepts.py',
                'validation_enabled': True,
                'enhancement_boost': 0.1
            }
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key using dot notation."""
        keys = key.split('.')
        
        # Map to configuration objects
        if keys[0] == 'database':
            obj = self.database
        elif keys[0] == 'api':
            obj = self.api
        elif keys[0] == 'system':
            obj = self.system
        elif keys[0] == 'text_processing':
            obj = self.text_processing
        elif keys[0] == 'entity_processing':
            obj = self.entity_processing
        elif keys[0] == 'graph_construction':
            obj = self.graph_construction
        elif keys[0] == 'workflow':
            obj = self.workflow
        elif keys[0] == 'theory':
            obj = self.theory
        else:
            return default
        
        # Navigate remaining keys
        for key in keys[1:]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                return default
        
        return obj
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get Neo4j configuration with environment variable overrides."""
        return {
            'uri': os.getenv('NEO4J_URI', self.database.uri),
            'username': os.getenv('NEO4J_USER', self.database.username),
            'user': os.getenv('NEO4J_USER', self.database.username),  # Support both patterns
            'password': os.getenv('NEO4J_PASSWORD', self.database.password),
            'database': os.getenv('NEO4J_DATABASE', self.database.database),
            'max_connection_pool_size': int(os.getenv('NEO4J_MAX_POOL_SIZE', self.database.max_connection_pool_size)),
            'connection_acquisition_timeout': float(os.getenv('NEO4J_CONNECTION_TIMEOUT', self.database.connection_acquisition_timeout)),
            'keep_alive': os.getenv('NEO4J_KEEP_ALIVE', str(self.database.keep_alive)).lower() == 'true'
        }
    
    def get_api_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get API configuration for specific provider or general config."""
        base_config = {
            'retry_attempts': int(os.getenv('API_RETRY_ATTEMPTS', self.api.retry_attempts)),
            'timeout_seconds': int(os.getenv('API_TIMEOUT_SECONDS', self.api.timeout_seconds)),
            'timeout': int(os.getenv('API_TIMEOUT_SECONDS', self.api.timeout)),
            'batch_processing_size': int(os.getenv('API_BATCH_SIZE', self.api.batch_processing_size)),
            'max_retries': int(os.getenv('API_RETRY_ATTEMPTS', self.api.max_retries)),
            'openai_model': os.getenv('OPENAI_MODEL', self.api.openai_model),
            'gemini_model': os.getenv('GEMINI_MODEL', self.api.gemini_model)
        }
        
        if provider == 'openai':
            return {
                **base_config,
                'api_key': os.getenv('OPENAI_API_KEY', self.api.openai_api_key),
                'base_url': self.api.openai_base_url,
            }
        elif provider == 'anthropic':
            return {
                **base_config,
                'api_key': os.getenv('ANTHROPIC_API_KEY', self.api.anthropic_api_key),
            }
        elif provider == 'google':
            return {
                **base_config,
                'api_key': os.getenv('GOOGLE_API_KEY', self.api.google_api_key),
            }
        else:
            return {
                **base_config,
                'openai_api_key': os.getenv('OPENAI_API_KEY', self.api.openai_api_key),
                'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', self.api.anthropic_api_key),
                'google_api_key': os.getenv('GOOGLE_API_KEY', self.api.google_api_key),
            }
    
    def get_entity_processing_config(self) -> Dict[str, Any]:
        """Get entity processing configuration."""
        return {
            'confidence_threshold': self.entity_processing.confidence_threshold,
            'chunk_overlap_size': self.entity_processing.chunk_overlap_size,
            'embedding_batch_size': self.entity_processing.embedding_batch_size,
            'max_entities_per_chunk': self.entity_processing.max_entities_per_chunk
        }
    
    def get_text_processing_config(self) -> Dict[str, Any]:
        """Get text processing configuration."""
        return {
            'chunk_size': self.text_processing.chunk_size,
            'semantic_similarity_threshold': self.text_processing.semantic_similarity_threshold,
            'max_chunks_per_document': self.text_processing.max_chunks_per_document,
            'chunk_overlap_size': self.text_processing.chunk_overlap_size
        }
    
    def get_graph_construction_config(self) -> Dict[str, Any]:
        """Get graph construction configuration."""
        return {
            'pagerank_iterations': self.graph_construction.pagerank_iterations,
            'pagerank_damping_factor': self.graph_construction.pagerank_damping_factor,
            'pagerank_tolerance': self.graph_construction.pagerank_tolerance,
            'pagerank_min_score': self.graph_construction.pagerank_min_score,
            'max_relationships_per_entity': self.graph_construction.max_relationships_per_entity,
            'graph_pruning_threshold': self.graph_construction.graph_pruning_threshold
        }
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        return {
            'mode': os.getenv('GRAPHRAG_MODE', self.system.environment),
            'environment': os.getenv('ENVIRONMENT', self.system.environment),
            'debug': os.getenv('DEBUG', str(self.system.debug)).lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', self.system.log_level),
            'max_workers': self.system.max_workers,
            'backup_enabled': self.system.backup_enabled,
            'encryption_enabled': self.system.encryption_enabled,
            'metrics_enabled': self.system.metrics_enabled,
            'health_check_interval': self.system.health_check_interval
        }
    
    def get_theory_config(self) -> Dict[str, Any]:
        """Get theory processing configuration."""
        return {
            'enabled': self.theory.enabled,
            'schema_type': self.theory.schema_type,
            'concept_library_path': self.theory.concept_library_path,
            'validation_enabled': self.theory.validation_enabled,
            'enhancement_boost': self.theory.enhancement_boost
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        feature_map = {
            'backup': self.system.backup_enabled,
            'encryption': self.system.encryption_enabled,
            'metrics': self.system.metrics_enabled,
            'theory': self.theory.enabled
        }
        
        return feature_map.get(feature, False)
    
    def is_theory_enabled(self) -> bool:
        """Check if theory processing is enabled."""
        return self.theory.enabled
    
    def is_production_mode(self) -> bool:
        """Determine if system is running in production mode."""
        # Check environment variable first
        env_mode = os.getenv('GRAPHRAG_MODE', '').lower()
        if env_mode in ['production', 'prod']:
            return True
        
        env_env = os.getenv('ENVIRONMENT', '').lower()
        if env_env in ['production', 'prod']:
            return True
        
        # Check configuration
        return self.system.environment.lower() in ['production', 'prod']
    
    def is_production_ready(self) -> Tuple[bool, List[str]]:
        """Check if configuration is production ready."""
        issues = []
        
        try:
            self.validate_config_with_schema()
        except ConfigurationError as e:
            issues.append(f"Schema validation failed: {e}")
        
        # Check for production-specific requirements
        neo4j_config = self.get_neo4j_config()
        if neo4j_config['uri'] == 'bolt://localhost:7687':
            issues.append("Neo4j URI should not use localhost in production")
        
        if neo4j_config['user'] == 'neo4j' and neo4j_config['password'] == 'password':
            issues.append("Neo4j credentials should not use default values in production")
        
        system_config = self.get_system_config()
        if system_config['environment'] == 'development':
            issues.append("Environment should be set to 'production'")
        
        if system_config['debug']:
            issues.append("Debug mode should be disabled in production")
        
        # Check for required environment variables
        required_env_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                issues.append(f"Required environment variable {env_var} not set")
        
        return len(issues) == 0, issues
    
    def validate_config_with_schema(self) -> None:
        """Validate configuration against JSON schema for production readiness."""
        schema = {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "pattern": "^bolt://.*"},
                        "username": {"type": "string", "minLength": 1},
                        "password": {"type": "string", "minLength": 1},
                        "max_connection_pool_size": {"type": "number", "minimum": 1},
                        "connection_acquisition_timeout": {"type": "number", "minimum": 0},
                        "keep_alive": {"type": "boolean"}
                    },
                    "required": ["uri", "username", "password"],
                    "additionalProperties": True
                },
                "api": {
                    "type": "object",
                    "properties": {
                        "retry_attempts": {"type": "number", "minimum": 0, "maximum": 10},
                        "timeout_seconds": {"type": "number", "minimum": 1, "maximum": 300},
                        "batch_processing_size": {"type": "number", "minimum": 1, "maximum": 1000},
                        "openai_model": {"type": "string", "minLength": 1},
                        "gemini_model": {"type": "string", "minLength": 1}
                    },
                    "additionalProperties": True
                }
            },
            "required": ["database"],
            "additionalProperties": True
        }
        
        try:
            config_for_validation = {
                "database": {
                    "uri": self.database.uri,
                    "username": self.database.username,
                    "password": self.database.password,
                    "max_connection_pool_size": self.database.max_connection_pool_size,
                    "connection_acquisition_timeout": self.database.connection_acquisition_timeout,
                    "keep_alive": self.database.keep_alive
                },
                "api": {
                    "retry_attempts": self.api.retry_attempts,
                    "timeout_seconds": self.api.timeout_seconds,
                    "batch_processing_size": self.api.batch_processing_size,
                    "openai_model": self.api.openai_model,
                    "gemini_model": self.api.gemini_model
                }
            }
            
            jsonschema.validate(config_for_validation, schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e.message}")
        except Exception as e:
            raise ConfigurationError(f"Configuration validation error: {str(e)}")
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get summary of environment configuration."""
        return {
            'config_file': str(self.config_path),
            'config_exists': self.config_path.exists(),
            'environment_vars_loaded': len(self.environment_vars),
            'database_configured': bool(self.database.password),
            'api_keys_configured': {
                'openai': bool(self.api.openai_api_key),
                'anthropic': bool(self.api.anthropic_api_key),
                'google': bool(self.api.google_api_key)
            },
            'features_enabled': {
                'backup': self.system.backup_enabled,
                'encryption': self.system.encryption_enabled,
                'metrics': self.system.metrics_enabled,
                'theory': self.theory.enabled
            },
            'production_mode': self.is_production_mode(),
            'production_ready': self.is_production_ready()[0]
        }


# Global configuration instance
_config_instance: Optional[ConfigurationManager] = None
_config_lock = threading.Lock()


def get_config() -> ConfigurationManager:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:
                _config_instance = ConfigurationManager()
    return _config_instance


def load_config(config_path: Optional[str] = None, force_reload: bool = False) -> ConfigurationManager:
    """Load configuration from file."""
    global _config_instance
    if force_reload or _config_instance is None:
        with _config_lock:
            _config_instance = ConfigurationManager(config_path)
    return _config_instance


def validate_config() -> Dict[str, Any]:
    """Validate current configuration."""
    config = get_config()
    try:
        config.validate_config_with_schema()
        return {"status": "valid", "errors": [], "warnings": []}
    except ConfigurationError as e:
        return {"status": "invalid", "errors": [str(e)], "warnings": []}


# Backward compatibility aliases
UnifiedConfigManager = ConfigurationManager
ConfigManager = ConfigurationManager