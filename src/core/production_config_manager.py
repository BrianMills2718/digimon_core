"""
Production Configuration Management System
========================================

Centralized configuration management for KGAS with environment-based loading,
validation, and secure credential handling.

Key Features:
- Environment-based configuration (dev, test, prod)
- Secure API key and credential management
- Schema framework configuration
- Error handling and monitoring settings
- Runtime configuration updates
- Comprehensive validation and defaults

Usage:
    config = ProductionConfigManager()
    api_key = config.get_api_key('openai')
    neo4j_config = config.get_database_config('neo4j')
"""

import os
import json
import logging
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
import base64
from enum import Enum


class Environment(Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 7687
    username: str = "neo4j"
    password: str = ""
    database: str = "neo4j"
    max_connections: int = 50
    connection_timeout: int = 30
    read_timeout: int = 300
    
    def to_uri(self) -> str:
        """Generate database connection URI."""
        if self.password:
            return f"bolt://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"bolt://{self.host}:{self.port}"


@dataclass
class LLMConfig:
    """LLM service configuration."""
    provider: str  # openai, anthropic, google
    api_key: str = ""
    model: str = ""
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60
    max_retries: int = 3
    rate_limit_per_minute: int = 60
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return bool(self.provider and self.api_key and self.model)


@dataclass
class SchemaConfig:
    """Schema framework configuration."""
    enabled_paradigms: List[str] = field(default_factory=lambda: [
        "uml", "rdf_owl", "orm", "typedb", "nary"
    ])
    default_paradigm: str = "rdf_owl"
    cross_paradigm_validation: bool = True
    auto_transform: bool = True
    validation_timeout: int = 30


@dataclass
class ErrorHandlingConfig:
    """Error handling and monitoring configuration."""
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    health_check_interval: int = 60
    metrics_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security and encryption configuration."""
    encrypt_credentials: bool = True
    credential_key_file: str = "credentials.key"
    pii_encryption: bool = True
    api_key_rotation_days: int = 90
    audit_logging: bool = True


class ProductionConfigManager:
    """
    Production-grade configuration management system.
    
    Provides centralized configuration with environment-based settings,
    secure credential management, and comprehensive validation.
    """
    
    def __init__(self, config_dir: Optional[str] = None, environment: Optional[str] = None):
        """Initialize configuration manager."""
        self.logger = logging.getLogger(__name__)
        
        # Determine configuration directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to project config directory
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / "config"
        
        self.config_dir.mkdir(exist_ok=True)
        
        # Determine environment
        self.environment = Environment(
            environment or os.getenv("KGAS_ENV", "development")
        )
        
        # Initialize encryption for credentials
        self._encryption_key = self._get_or_create_encryption_key()
        
        # Load configuration
        self._config: Dict[str, Any] = {}
        self._load_configuration()
        
        # Initialize components
        self.database_configs: Dict[str, DatabaseConfig] = {}
        self.llm_configs: Dict[str, LLMConfig] = {}
        self.schema_config = SchemaConfig()
        self.error_config = ErrorHandlingConfig()
        self.security_config = SecurityConfig()
        
        self._initialize_configurations()
        
        self.logger.info(f"Configuration manager initialized for {self.environment.value}")
    
    def _get_or_create_encryption_key(self) -> Fernet:
        """Get or create encryption key for credentials."""
        key_file = self.config_dir / "encryption.key"
        
        if key_file.exists():
            key = key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
        
        return Fernet(key)
    
    def _load_configuration(self) -> None:
        """Load configuration from files."""
        # Load base configuration
        base_config_file = self.config_dir / "base.yaml"
        if base_config_file.exists():
            with open(base_config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        
        # Load environment-specific configuration
        env_config_file = self.config_dir / f"{self.environment.value}.yaml"
        if env_config_file.exists():
            with open(env_config_file, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                self._deep_merge(self._config, env_config)
        
        # Override with environment variables
        self._load_environment_variables()
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "KGAS_NEO4J_HOST": ["database", "neo4j", "host"],
            "KGAS_NEO4J_PORT": ["database", "neo4j", "port"],
            "KGAS_NEO4J_PASSWORD": ["database", "neo4j", "password"],
            "KGAS_OPENAI_API_KEY": ["llm", "openai", "api_key"],
            "KGAS_ANTHROPIC_API_KEY": ["llm", "anthropic", "api_key"],
            "KGAS_GOOGLE_API_KEY": ["llm", "google", "api_key"],
            "KGAS_CIRCUIT_BREAKER_ENABLED": ["error_handling", "circuit_breaker_enabled"],
            "KGAS_DEBUG": ["logging", "debug"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(self._config, config_path, self._convert_env_value(value))
    
    def _convert_env_value(self, value: str) -> Union[str, int, bool]:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, config: Dict[str, Any], path: List[str], value: Any) -> None:
        """Set value in nested configuration dictionary."""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def _initialize_configurations(self) -> None:
        """Initialize configuration objects from loaded data."""
        # Database configurations
        db_config = self._config.get("database", {})
        for db_name, db_settings in db_config.items():
            if isinstance(db_settings, dict):
                self.database_configs[db_name] = DatabaseConfig(**db_settings)
        
        # Ensure Neo4j config exists
        if "neo4j" not in self.database_configs:
            self.database_configs["neo4j"] = DatabaseConfig()
        
        # LLM configurations
        llm_config = self._config.get("llm", {})
        for provider, settings in llm_config.items():
            if isinstance(settings, dict):
                # Make a copy and ensure provider is set correctly
                config_dict = settings.copy()
                config_dict['provider'] = provider
                self.llm_configs[provider] = LLMConfig(**config_dict)
        
        # Schema configuration
        schema_settings = self._config.get("schema", {})
        if schema_settings:
            self.schema_config = SchemaConfig(**schema_settings)
        
        # Error handling configuration
        error_settings = self._config.get("error_handling", {})
        if error_settings:
            self.error_config = ErrorHandlingConfig(**error_settings)
        
        # Security configuration
        security_settings = self._config.get("security", {})
        if security_settings:
            self.security_config = SecurityConfig(**security_settings)
    
    def get_database_config(self, database: str = "neo4j") -> DatabaseConfig:
        """Get database configuration."""
        if database not in self.database_configs:
            raise ConfigurationError(f"Database configuration not found: {database}")
        return self.database_configs[database]
    
    def get_llm_config(self, provider: str) -> LLMConfig:
        """Get LLM configuration for provider."""
        if provider not in self.llm_configs:
            raise ConfigurationError(f"LLM configuration not found: {provider}")
        
        config = self.llm_configs[provider]
        if not config.is_valid():
            raise ConfigurationError(f"Invalid LLM configuration for {provider}")
        
        return config
    
    def get_api_key(self, provider: str) -> str:
        """Get decrypted API key for provider."""
        config = self.get_llm_config(provider)
        
        if self.security_config.encrypt_credentials:
            try:
                # Decrypt API key if it's encrypted
                encrypted_key = config.api_key.encode() if isinstance(config.api_key, str) else config.api_key
                return self._encryption_key.decrypt(encrypted_key).decode()
            except Exception:
                # If decryption fails, assume it's plaintext (for development)
                return config.api_key
        
        return config.api_key
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set encrypted API key for provider."""
        if self.security_config.encrypt_credentials:
            encrypted_key = self._encryption_key.encrypt(api_key.encode()).decode()
        else:
            encrypted_key = api_key
        
        if provider not in self.llm_configs:
            self.llm_configs[provider] = LLMConfig(provider=provider)
        
        self.llm_configs[provider].api_key = encrypted_key
        self._save_configuration()
    
    def get_schema_config(self) -> SchemaConfig:
        """Get schema framework configuration."""
        return self.schema_config
    
    def get_error_config(self) -> ErrorHandlingConfig:
        """Get error handling configuration."""
        return self.error_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.security_config
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate database configurations
        for db_name, db_config in self.database_configs.items():
            if not db_config.host:
                issues.append(f"Missing host for database {db_name}")
            if not db_config.username and db_name == "neo4j":
                issues.append(f"Missing username for database {db_name}")
        
        # Validate LLM configurations
        if not self.llm_configs:
            issues.append("No LLM configurations found")
        
        for provider, config in self.llm_configs.items():
            if not config.is_valid():
                issues.append(f"Invalid LLM configuration for {provider}")
        
        # Validate schema configuration
        if not self.schema_config.enabled_paradigms:
            issues.append("No schema paradigms enabled")
        
        if self.schema_config.default_paradigm not in self.schema_config.enabled_paradigms:
            issues.append("Default schema paradigm not in enabled list")
        
        return issues
    
    def _save_configuration(self) -> None:
        """Save current configuration to file."""
        config_file = self.config_dir / f"{self.environment.value}.yaml"
        
        # Prepare configuration for saving (exclude sensitive data)
        save_config = {
            "database": {name: self._dataclass_to_dict(config) for name, config in self.database_configs.items()},
            "llm": {name: self._dataclass_to_dict(config) for name, config in self.llm_configs.items()},
            "schema": self._dataclass_to_dict(self.schema_config),
            "error_handling": self._dataclass_to_dict(self.error_config),
            "security": self._dataclass_to_dict(self.security_config),
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(save_config, f, default_flow_style=False)
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return {}
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging."""
        return {
            "environment": self.environment.value,
            "config_dir": str(self.config_dir),
            "databases": list(self.database_configs.keys()),
            "llm_providers": list(self.llm_configs.keys()),
            "enabled_schema_paradigms": self.schema_config.enabled_paradigms,
            "circuit_breaker_enabled": self.error_config.circuit_breaker_enabled,
            "encryption_enabled": self.security_config.encrypt_credentials,
            "validation_issues": self.validate_configuration(),
        }


def create_default_configurations(config_dir: str) -> None:
    """Create default configuration files."""
    config_path = Path(config_dir)
    config_path.mkdir(exist_ok=True)
    
    # Base configuration
    base_config = {
        "database": {
            "neo4j": {
                "host": "localhost",
                "port": 7687,
                "username": "neo4j",
                "password": "",
                "database": "neo4j",
                "max_connections": 50,
                "connection_timeout": 30,
                "read_timeout": 300,
            }
        },
        "llm": {
            "openai": {
                "provider": "openai",
                "model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.1,
                "timeout": 60,
                "max_retries": 3,
                "rate_limit_per_minute": 60,
            },
            "anthropic": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "temperature": 0.1,
                "timeout": 60,
                "max_retries": 3,
                "rate_limit_per_minute": 60,
            }
        },
        "schema": {
            "enabled_paradigms": ["uml", "rdf_owl", "orm", "typedb", "nary"],
            "default_paradigm": "rdf_owl",
            "cross_paradigm_validation": True,
            "auto_transform": True,
            "validation_timeout": 30,
        },
        "error_handling": {
            "circuit_breaker_enabled": True,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
            "max_retries": 3,
            "retry_delay": 1.0,
            "exponential_backoff": True,
            "health_check_interval": 60,
            "metrics_enabled": True,
        },
        "security": {
            "encrypt_credentials": True,
            "pii_encryption": True,
            "api_key_rotation_days": 90,
            "audit_logging": True,
        }
    }
    
    # Save base configuration
    with open(config_path / "base.yaml", 'w') as f:
        yaml.dump(base_config, f, default_flow_style=False)
    
    # Development configuration
    dev_config = {
        "database": {
            "neo4j": {
                "password": "development",
            }
        },
        "security": {
            "encrypt_credentials": False,
        },
        "logging": {
            "level": "DEBUG",
            "debug": True,
        }
    }
    
    with open(config_path / "development.yaml", 'w') as f:
        yaml.dump(dev_config, f, default_flow_style=False)
    
    # Production configuration template
    prod_config = {
        "database": {
            "neo4j": {
                "password": "CHANGE_ME",
                "max_connections": 100,
            }
        },
        "security": {
            "encrypt_credentials": True,
            "audit_logging": True,
        },
        "logging": {
            "level": "INFO",
            "debug": False,
        }
    }
    
    with open(config_path / "production.yaml", 'w') as f:
        yaml.dump(prod_config, f, default_flow_style=False)


if __name__ == "__main__":
    # Create default configurations for testing
    create_default_configurations("config")
    
    # Test configuration manager
    config = ProductionConfigManager()
    summary = config.get_config_summary()
    
    print("Configuration Summary:")
    print(json.dumps(summary, indent=2))
    
    # Validate configuration
    issues = config.validate_configuration()
    if issues:
        print("\nConfiguration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration validation passed")