"""Centralized Configuration Management System

Provides a unified configuration system to replace hardcoded values throughout
the codebase. Supports YAML configuration files with environment-specific overrides
and runtime validation.

Addresses Configuration Management Debt identified in TECHNICAL_DEBT_AUDIT.md
"""

import os
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
import threading


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
class SystemConfig:
    """Complete system configuration."""
    entity_processing: EntityProcessingConfig = field(default_factory=EntityProcessingConfig)
    text_processing: TextProcessingConfig = field(default_factory=TextProcessingConfig)
    graph_construction: GraphConstructionConfig = field(default_factory=GraphConstructionConfig)
    api: APIConfig = field(default_factory=APIConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    
    # Environment settings
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"


class ConfigurationManager:
    """Centralized configuration management with singleton pattern."""
    
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
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration")
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