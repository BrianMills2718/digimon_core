"""Centralized Configuration Management System

Provides a unified configuration system to replace hardcoded values throughout
the codebase. Supports YAML configuration files with environment-specific overrides
and runtime validation.

Addresses Configuration Management Debt identified in TECHNICAL_DEBT_AUDIT.md
"""

import os
import yaml
import jsonschema
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
import threading
from .logging_config import get_logger


@dataclass
class EntityProcessingConfig:
    """Configuration for entity processing."""
    confidence_threshold: float = 0.7
    chunk_overlap_size: int = 50
    embedding_batch_size: int = 100
    max_entities_per_chunk: int = 20


@dataclass
class TextProcessingConfig:
    """Configuration for text processing."""
    chunk_size: int = 512
    semantic_similarity_threshold: float = 0.85
    max_chunks_per_document: int = 100


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
    """Configuration for API interactions."""
    retry_attempts: int = 3
    timeout_seconds: int = 30
    batch_processing_size: int = 10
    openai_model: str = "text-embedding-3-small"
    gemini_model: str = "gemini-2.0-flash-exp"
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j database."""
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: float = 30.0
    keep_alive: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for workflow management."""
    storage_dir: str = "./data/workflows"
    checkpoint_interval: int = 10
    max_retries: int = 3
    timeout_seconds: int = 300


@dataclass
class SystemConfig:
    """Complete system configuration."""
    entity_processing: EntityProcessingConfig = field(default_factory=EntityProcessingConfig)
    text_processing: TextProcessingConfig = field(default_factory=TextProcessingConfig)
    graph_construction: GraphConstructionConfig = field(default_factory=GraphConstructionConfig)
    api: APIConfig = field(default_factory=APIConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    
    # Environment settings
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass


class ConfigurationManager:
    """Centralized configuration management with singleton pattern.
    
    Unified configuration manager that combines the best features of both
    ConfigurationManager and ConfigManager for complete system coverage.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._config_path = None
            self._config = None
            self.logger = get_logger("core.config")
    
    def load_config(self, config_path: Optional[str] = None, force_reload: bool = False) -> SystemConfig:
        """Load configuration from file or create default."""
        # Force reload if requested or if config path is different
        if force_reload or (config_path and config_path != self._config_path):
            self._config = None
        
        if config_path is None:
            # Try default locations
            possible_paths = [
                "config/default.yaml",
                "config.yaml",
                os.path.expanduser("~/.graphrag/config.yaml")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            self._config = self._load_from_file(config_path)
            self._config_path = config_path
        else:
            # Use default configuration
            self._config = SystemConfig()
            self._config_path = None
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        return self._config
    
    def _load_from_file(self, config_path: str) -> SystemConfig:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return SystemConfig()
            
            # Convert nested dict to SystemConfig
            return self._dict_to_config(config_data)
            
        except Exception as e:
            self.logger.warning("Failed to load config from %s: %s", config_path, str(e))
            self.logger.info("Using default configuration")
            return SystemConfig()
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> SystemConfig:
        """Convert dictionary to SystemConfig object."""
        config = SystemConfig()
        
        # Entity processing
        if 'entity_processing' in config_dict:
            ep_data = config_dict['entity_processing']
            config.entity_processing = EntityProcessingConfig(
                confidence_threshold=ep_data.get('confidence_threshold', 0.7),
                chunk_overlap_size=ep_data.get('chunk_overlap_size', 50),
                embedding_batch_size=ep_data.get('embedding_batch_size', 100),
                max_entities_per_chunk=ep_data.get('max_entities_per_chunk', 20)
            )
        
        # Text processing
        if 'text_processing' in config_dict:
            tp_data = config_dict['text_processing']
            config.text_processing = TextProcessingConfig(
                chunk_size=tp_data.get('chunk_size', 512),
                semantic_similarity_threshold=tp_data.get('semantic_similarity_threshold', 0.85),
                max_chunks_per_document=tp_data.get('max_chunks_per_document', 100)
            )
        
        # Graph construction
        if 'graph_construction' in config_dict:
            gc_data = config_dict['graph_construction']
            config.graph_construction = GraphConstructionConfig(
                pagerank_iterations=gc_data.get('pagerank_iterations', 100),
                pagerank_damping_factor=gc_data.get('pagerank_damping_factor', 0.85),
                pagerank_tolerance=gc_data.get('pagerank_tolerance', 1e-6),
                pagerank_min_score=gc_data.get('pagerank_min_score', 0.0001),
                max_relationships_per_entity=gc_data.get('max_relationships_per_entity', 50),
                graph_pruning_threshold=gc_data.get('graph_pruning_threshold', 0.1)
            )
        
        # API configuration
        if 'api' in config_dict:
            api_data = config_dict['api']
            config.api = APIConfig(
                retry_attempts=api_data.get('retry_attempts', 3),
                timeout_seconds=api_data.get('timeout_seconds', 30),
                batch_processing_size=api_data.get('batch_processing_size', 10),
                openai_model=api_data.get('openai_model', 'text-embedding-3-small'),
                gemini_model=api_data.get('gemini_model', 'gemini-2.0-flash-exp')
            )
        
        # Neo4j configuration
        if 'neo4j' in config_dict:
            neo4j_data = config_dict['neo4j']
            config.neo4j = Neo4jConfig(
                uri=neo4j_data.get('uri', 'bolt://localhost:7687'),
                user=neo4j_data.get('user', 'neo4j'),
                password=neo4j_data.get('password', 'password'),
                max_connection_pool_size=neo4j_data.get('max_connection_pool_size', 50),
                connection_acquisition_timeout=neo4j_data.get('connection_acquisition_timeout', 30.0),
                keep_alive=neo4j_data.get('keep_alive', True)
            )
        
        # System-level settings
        config.environment = config_dict.get('environment', 'development')
        config.debug = config_dict.get('debug', False)
        config.log_level = config_dict.get('log_level', 'INFO')
        
        return config
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        if not self._config:
            return
        
        # Neo4j overrides (most common)
        if os.getenv('NEO4J_URI'):
            self._config.neo4j.uri = os.getenv('NEO4J_URI')
        if os.getenv('NEO4J_USER'):
            self._config.neo4j.user = os.getenv('NEO4J_USER')
        if os.getenv('NEO4J_PASSWORD'):
            self._config.neo4j.password = os.getenv('NEO4J_PASSWORD')
        
        # API model overrides
        if os.getenv('OPENAI_MODEL'):
            self._config.api.openai_model = os.getenv('OPENAI_MODEL')
        if os.getenv('GEMINI_MODEL'):
            self._config.api.gemini_model = os.getenv('GEMINI_MODEL')
        
        # Environment and debug
        if os.getenv('ENVIRONMENT'):
            self._config.environment = os.getenv('ENVIRONMENT')
        if os.getenv('DEBUG'):
            self._config.debug = os.getenv('DEBUG').lower() in ('true', '1', 'yes')
        if os.getenv('LOG_LEVEL'):
            self._config.log_level = os.getenv('LOG_LEVEL')
    
    def get_config(self) -> SystemConfig:
        """Get current configuration, loading default if not loaded."""
        if self._config is None:
            self.load_config()
        return self._config
    
    def save_config(self, config_path: str = None):
        """Save current configuration to file."""
        if config_path is None:
            config_path = self._config_path or "config/default.yaml"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Convert config to dict
        config_dict = self._config_to_dict(self._config)
        
        # Save to YAML
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """Convert SystemConfig to dictionary for YAML serialization."""
        return {
            'entity_processing': {
                'confidence_threshold': config.entity_processing.confidence_threshold,
                'chunk_overlap_size': config.entity_processing.chunk_overlap_size,
                'embedding_batch_size': config.entity_processing.embedding_batch_size,
                'max_entities_per_chunk': config.entity_processing.max_entities_per_chunk
            },
            'text_processing': {
                'chunk_size': config.text_processing.chunk_size,
                'semantic_similarity_threshold': config.text_processing.semantic_similarity_threshold,
                'max_chunks_per_document': config.text_processing.max_chunks_per_document
            },
            'graph_construction': {
                'pagerank_iterations': config.graph_construction.pagerank_iterations,
                'pagerank_damping_factor': config.graph_construction.pagerank_damping_factor,
                'pagerank_tolerance': config.graph_construction.pagerank_tolerance,
                'pagerank_min_score': config.graph_construction.pagerank_min_score,
                'max_relationships_per_entity': config.graph_construction.max_relationships_per_entity,
                'graph_pruning_threshold': config.graph_construction.graph_pruning_threshold
            },
            'api': {
                'retry_attempts': config.api.retry_attempts,
                'timeout_seconds': config.api.timeout_seconds,
                'batch_processing_size': config.api.batch_processing_size,
                'openai_model': config.api.openai_model,
                'gemini_model': config.api.gemini_model
            },
            'neo4j': {
                'uri': config.neo4j.uri,
                'user': config.neo4j.user,
                'password': config.neo4j.password,
                'max_connection_pool_size': config.neo4j.max_connection_pool_size,
                'connection_acquisition_timeout': config.neo4j.connection_acquisition_timeout,
                'keep_alive': config.neo4j.keep_alive
            },
            'environment': config.environment,
            'debug': config.debug,
            'log_level': config.log_level
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration and return validation results."""
        if not self._config:
            return {"status": "error", "error": "No configuration loaded"}
        
        errors = []
        warnings = []
        
        # Validate ranges and constraints
        ep = self._config.entity_processing
        if not (0.0 <= ep.confidence_threshold <= 1.0):
            errors.append("entity_processing.confidence_threshold must be between 0.0 and 1.0")
        if ep.chunk_overlap_size < 0:
            errors.append("entity_processing.chunk_overlap_size must be >= 0")
        if ep.embedding_batch_size <= 0:
            errors.append("entity_processing.embedding_batch_size must be > 0")
        
        tp = self._config.text_processing
        if tp.chunk_size <= 0:
            errors.append("text_processing.chunk_size must be > 0")
        if not (0.0 <= tp.semantic_similarity_threshold <= 1.0):
            errors.append("text_processing.semantic_similarity_threshold must be between 0.0 and 1.0")
        
        gc = self._config.graph_construction
        if gc.pagerank_iterations <= 0:
            errors.append("graph_construction.pagerank_iterations must be > 0")
        if not (0.0 <= gc.pagerank_damping_factor <= 1.0):
            errors.append("graph_construction.pagerank_damping_factor must be between 0.0 and 1.0")
        
        api = self._config.api
        if api.retry_attempts < 0:
            errors.append("api.retry_attempts must be >= 0")
        if api.timeout_seconds <= 0:
            errors.append("api.timeout_seconds must be > 0")
        
        # Warnings for potentially problematic values
        if tp.chunk_size > 2048:
            warnings.append("text_processing.chunk_size > 2048 may cause issues with some models")
        if gc.pagerank_iterations > 500:
            warnings.append("graph_construction.pagerank_iterations > 500 may be unnecessarily slow")
        
        return {
            "status": "valid" if not errors else "invalid",
            "errors": errors,
            "warnings": warnings,
            "config_path": self._config_path
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'neo4j.uri').
        
        Args:
            key: Configuration key using dot notation
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._config:
            self.load_config()
        
        # Convert SystemConfig to dict for dot notation access
        config_dict = self._config_to_dict(self._config)
        
        keys = key.split('.')
        value = config_dict
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get Neo4j configuration with environment variable overrides."""
        if not self._config:
            self.load_config()
        
        return {
            'uri': os.getenv('NEO4J_URI', self._config.neo4j.uri),
            'user': os.getenv('NEO4J_USER', self._config.neo4j.user),
            'password': os.getenv('NEO4J_PASSWORD', self._config.neo4j.password),
            'max_connection_pool_size': int(os.getenv('NEO4J_MAX_POOL_SIZE', self._config.neo4j.max_connection_pool_size)),
            'connection_acquisition_timeout': float(os.getenv('NEO4J_CONNECTION_TIMEOUT', self._config.neo4j.connection_acquisition_timeout)),
            'keep_alive': os.getenv('NEO4J_KEEP_ALIVE', str(self._config.neo4j.keep_alive)).lower() == 'true'
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration with environment variable overrides."""
        if not self._config:
            self.load_config()
        
        return {
            'retry_attempts': int(os.getenv('API_RETRY_ATTEMPTS', self._config.api.retry_attempts)),
            'timeout_seconds': int(os.getenv('API_TIMEOUT_SECONDS', self._config.api.timeout_seconds)),
            'batch_processing_size': int(os.getenv('API_BATCH_SIZE', self._config.api.batch_processing_size)),
            'openai_model': os.getenv('OPENAI_MODEL', self._config.api.openai_model),
            'gemini_model': os.getenv('GEMINI_MODEL', self._config.api.gemini_model)
        }
    
    def get_entity_processing_config(self) -> Dict[str, Any]:
        """Get entity processing configuration."""
        if not self._config:
            self.load_config()
        
        return {
            'confidence_threshold': self._config.entity_processing.confidence_threshold,
            'chunk_overlap_size': self._config.entity_processing.chunk_overlap_size,
            'embedding_batch_size': self._config.entity_processing.embedding_batch_size,
            'max_entities_per_chunk': self._config.entity_processing.max_entities_per_chunk
        }
    
    def get_text_processing_config(self) -> Dict[str, Any]:
        """Get text processing configuration."""
        if not self._config:
            self.load_config()
        
        return {
            'chunk_size': self._config.text_processing.chunk_size,
            'semantic_similarity_threshold': self._config.text_processing.semantic_similarity_threshold,
            'max_chunks_per_document': self._config.text_processing.max_chunks_per_document
        }
    
    def get_graph_construction_config(self) -> Dict[str, Any]:
        """Get graph construction configuration."""
        if not self._config:
            self.load_config()
        
        return {
            'pagerank_iterations': self._config.graph_construction.pagerank_iterations,
            'pagerank_damping_factor': self._config.graph_construction.pagerank_damping_factor,
            'pagerank_tolerance': self._config.graph_construction.pagerank_tolerance,
            'pagerank_min_score': self._config.graph_construction.pagerank_min_score,
            'max_relationships_per_entity': self._config.graph_construction.max_relationships_per_entity,
            'graph_pruning_threshold': self._config.graph_construction.graph_pruning_threshold
        }
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        if not self._config:
            self.load_config()
        
        return {
            'mode': os.getenv('GRAPHRAG_MODE', self._config.environment),
            'environment': os.getenv('ENVIRONMENT', self._config.environment),
            'debug': os.getenv('DEBUG', str(self._config.debug)).lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', self._config.log_level),
            'strict_schema_validation': self.get('system.strict_schema_validation', False)
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        if not self._config:
            self.load_config()
        return self._config_to_dict(self._config)
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._config = None
        self.load_config()
    
    def validate_config_with_schema(self) -> None:
        """Validate configuration against JSON schema for production readiness.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        schema = {
            "type": "object",
            "properties": {
                "neo4j": {
                    "type": "object",
                    "properties": {
                        "uri": {"type": "string", "pattern": "^bolt://.*"},
                        "user": {"type": "string", "minLength": 1},
                        "password": {"type": "string", "minLength": 1},
                        "max_connection_pool_size": {"type": "number", "minimum": 1},
                        "connection_acquisition_timeout": {"type": "number", "minimum": 0},
                        "keep_alive": {"type": "boolean"}
                    },
                    "required": ["uri", "user", "password"],
                    "additionalProperties": False
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
                    "required": ["openai_model", "gemini_model"],
                    "additionalProperties": False
                },
                "entity_processing": {
                    "type": "object",
                    "properties": {
                        "confidence_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        "chunk_overlap_size": {"type": "number", "minimum": 0},
                        "embedding_batch_size": {"type": "number", "minimum": 1},
                        "max_entities_per_chunk": {"type": "number", "minimum": 1}
                    },
                    "additionalProperties": False
                },
                "text_processing": {
                    "type": "object",
                    "properties": {
                        "chunk_size": {"type": "number", "minimum": 1},
                        "semantic_similarity_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        "max_chunks_per_document": {"type": "number", "minimum": 1}
                    },
                    "additionalProperties": False
                },
                "graph_construction": {
                    "type": "object",
                    "properties": {
                        "pagerank_iterations": {"type": "number", "minimum": 1},
                        "pagerank_damping_factor": {"type": "number", "minimum": 0, "maximum": 1},
                        "pagerank_tolerance": {"type": "number", "minimum": 0},
                        "pagerank_min_score": {"type": "number", "minimum": 0},
                        "max_relationships_per_entity": {"type": "number", "minimum": 1},
                        "graph_pruning_threshold": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "additionalProperties": False
                }
            },
            "required": ["neo4j"],
            "additionalProperties": True
        }
        
        try:
            # Construct config object for validation
            config_for_validation = {
                "neo4j": self.get_neo4j_config(),
                "api": self.get_api_config(),
                "entity_processing": self.get_entity_processing_config(),
                "text_processing": self.get_text_processing_config(),
                "graph_construction": self.get_graph_construction_config()
            }
            
            jsonschema.validate(config_for_validation, schema)
        except jsonschema.ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e.message}")
        except Exception as e:
            raise ConfigurationError(f"Configuration validation error: {str(e)}")
    
    def is_production_ready(self) -> tuple[bool, list[str]]:
        """Check if configuration is production ready.
        
        Returns:
            Tuple of (is_ready: bool, issues: list[str])
        """
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
    
    def is_production_mode(self) -> bool:
        """Determine if system is running in production mode."""
        # Check environment variable first
        env_mode = os.getenv('GRAPHRAG_MODE', '').lower()
        if env_mode in ['production', 'prod']:
            return True
        
        # Check configuration
        system_config = self.get_system_config()
        return system_config.get('mode', 'development').lower() in ['production', 'prod']
    
    def get_theory_config(self) -> Dict[str, Any]:
        """Get theory processing configuration."""
        return self.get('theory', {
            'enabled': False,
            'schema_type': 'MASTER_CONCEPTS',
            'concept_library_path': 'src/ontology_library/master_concepts.py',
            'validation_enabled': True,
            'enhancement_boost': 0.1
        })
    
    def is_theory_enabled(self) -> bool:
        """Check if theory processing is enabled."""
        return self.get_theory_config().get('enabled', False)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        if self._config is None:
            self.load_config()
        
        def update_nested_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = update_nested_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        # Convert current config to dict, update, then convert back
        config_dict = self._config_to_dict(self._config)
        updated_dict = update_nested_dict(config_dict, updates)
        self._config = self._dict_to_config(updated_dict)


# Global configuration instance - use a function to ensure singleton across imports
def _get_global_config_manager():
    """Get or create the global configuration manager instance."""
    if not hasattr(_get_global_config_manager, '_instance'):
        _get_global_config_manager._instance = ConfigurationManager()
    return _get_global_config_manager._instance


def get_config() -> SystemConfig:
    """Get the global configuration instance."""
    return _get_global_config_manager().get_config()


def load_config(config_path: Optional[str] = None, force_reload: bool = False) -> SystemConfig:
    """Load configuration from file."""
    return _get_global_config_manager().load_config(config_path, force_reload)


def validate_config() -> Dict[str, Any]:
    """Validate current configuration."""
    return _get_global_config_manager().validate_config()


# Aliases for backward compatibility and audit tool
Config = ConfigurationManager
ConfigManager = ConfigurationManager  # Alias for merged functionality