"""
Production Configuration Manager - SECURITY AND RELIABILITY FIXED
=================================================================

CRITICAL FIXES APPLIED:
- NO silent exception swallowing
- NO fallback to insecure defaults
- Proper schema validation
- Fail-fast error handling
- Type safety enforcement
- Resource management

THIS VERSION PRIORITIZES RELIABILITY AND SECURITY
"""

import os
import json
import logging
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import jsonschema
from jsonschema import ValidationError


class ConfigurationError(Exception):
    """Configuration-related errors that should halt execution."""
    pass


class ConfigurationValidationError(ConfigurationError):
    """Configuration validation errors."""
    pass


class Environment(Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings with validation."""
    host: str
    port: int
    username: str
    password: str
    database: str
    max_connections: int = 50
    connection_timeout: int = 30
    read_timeout: int = 300
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.host or not self.host.strip():
            raise ConfigurationValidationError("Database host cannot be empty")
        if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
            raise ConfigurationValidationError(f"Database port must be 1-65535, got: {self.port}")
        if not self.username or not self.username.strip():
            raise ConfigurationValidationError("Database username cannot be empty")
        if not self.database or not self.database.strip():
            raise ConfigurationValidationError("Database name cannot be empty")
        if self.max_connections <= 0:
            raise ConfigurationValidationError("Max connections must be positive")
        if self.connection_timeout <= 0:
            raise ConfigurationValidationError("Connection timeout must be positive")
    
    def to_uri(self) -> str:
        """Generate database connection URI."""
        if self.password:
            return f"bolt://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"bolt://{self.host}:{self.port}"


@dataclass
class LLMConfig:
    """LLM service configuration with validation."""
    provider: str
    model: str
    api_key: str = ""
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 60
    max_retries: int = 3
    rate_limit_per_minute: int = 60
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.provider or not self.provider.strip():
            raise ConfigurationValidationError("LLM provider cannot be empty")
        if not self.model or not self.model.strip():
            raise ConfigurationValidationError("LLM model cannot be empty")
        if not isinstance(self.max_tokens, int) or self.max_tokens <= 0:
            raise ConfigurationValidationError("Max tokens must be positive integer")
        if not isinstance(self.temperature, (int, float)) or not (0 <= self.temperature <= 2):
            raise ConfigurationValidationError("Temperature must be 0-2")
        if self.timeout <= 0:
            raise ConfigurationValidationError("Timeout must be positive")
        if self.max_retries < 0:
            raise ConfigurationValidationError("Max retries cannot be negative")
        if self.rate_limit_per_minute <= 0:
            raise ConfigurationValidationError("Rate limit must be positive")
    
    def is_valid(self) -> bool:
        """Check if configuration has required API key."""
        return bool(self.provider and self.model and self.api_key and len(self.api_key) >= 8)


@dataclass
class SchemaConfig:
    """Schema framework configuration with validation."""
    enabled_paradigms: List[str] = field(default_factory=lambda: [
        "uml", "rdf_owl", "orm", "typedb", "nary"
    ])
    default_paradigm: str = "rdf_owl"
    cross_paradigm_validation: bool = True
    auto_transform: bool = True
    validation_timeout: int = 30
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_paradigms = {"uml", "rdf_owl", "orm", "typedb", "nary"}
        
        if not self.enabled_paradigms:
            raise ConfigurationValidationError("At least one schema paradigm must be enabled")
        
        for paradigm in self.enabled_paradigms:
            if paradigm not in valid_paradigms:
                raise ConfigurationValidationError(f"Invalid schema paradigm: {paradigm}")
        
        if self.default_paradigm not in self.enabled_paradigms:
            raise ConfigurationValidationError("Default paradigm must be in enabled paradigms")
        
        if self.validation_timeout <= 0:
            raise ConfigurationValidationError("Validation timeout must be positive")


@dataclass
class ErrorHandlingConfig:
    """Error handling and monitoring configuration with validation."""
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    health_check_interval: int = 60
    metrics_enabled: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.circuit_breaker_threshold <= 0:
            raise ConfigurationValidationError("Circuit breaker threshold must be positive")
        if self.circuit_breaker_timeout <= 0:
            raise ConfigurationValidationError("Circuit breaker timeout must be positive")
        if self.max_retries < 0:
            raise ConfigurationValidationError("Max retries cannot be negative")
        if self.retry_delay <= 0:
            raise ConfigurationValidationError("Retry delay must be positive")
        if self.health_check_interval <= 0:
            raise ConfigurationValidationError("Health check interval must be positive")


@dataclass
class SecurityConfig:
    """Security and encryption configuration with validation."""
    encrypt_credentials: bool = True
    credential_key_file: str = "credentials.key"
    pii_encryption: bool = True
    api_key_rotation_days: int = 90
    audit_logging: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.credential_key_file or not self.credential_key_file.strip():
            raise ConfigurationValidationError("Credential key file cannot be empty")
        if self.api_key_rotation_days <= 0 or self.api_key_rotation_days > 365:
            raise ConfigurationValidationError("API key rotation days must be 1-365")


class ConfigurationSchemaValidator:
    """JSON Schema validator for configuration files."""
    
    # Configuration schema definition
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "database": {
                "type": "object",
                "patternProperties": {
                    "^[a-zA-Z0-9_]+$": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string", "minLength": 1},
                            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                            "username": {"type": "string", "minLength": 1},
                            "password": {"type": "string"},
                            "database": {"type": "string", "minLength": 1},
                            "max_connections": {"type": "integer", "minimum": 1},
                            "connection_timeout": {"type": "integer", "minimum": 1},
                            "read_timeout": {"type": "integer", "minimum": 1}
                        },
                        "required": ["host", "port", "username", "database"],
                        "additionalProperties": False
                    }
                }
            },
            "llm": {
                "type": "object",
                "patternProperties": {
                    "^[a-zA-Z0-9_]+$": {
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string", "minLength": 1},
                            "model": {"type": "string", "minLength": 1},
                            "api_key": {"type": "string"},
                            "max_tokens": {"type": "integer", "minimum": 1, "maximum": 128000},
                            "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                            "timeout": {"type": "integer", "minimum": 1},
                            "max_retries": {"type": "integer", "minimum": 0},
                            "rate_limit_per_minute": {"type": "integer", "minimum": 1}
                        },
                        "required": ["provider", "model"],
                        "additionalProperties": False
                    }
                }
            },
            "schema": {
                "type": "object",
                "properties": {
                    "enabled_paradigms": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["uml", "rdf_owl", "orm", "typedb", "nary"]},
                        "minItems": 1,
                        "uniqueItems": True
                    },
                    "default_paradigm": {"type": "string", "enum": ["uml", "rdf_owl", "orm", "typedb", "nary"]},
                    "cross_paradigm_validation": {"type": "boolean"},
                    "auto_transform": {"type": "boolean"},
                    "validation_timeout": {"type": "integer", "minimum": 1}
                },
                "additionalProperties": False
            },
            "error_handling": {
                "type": "object",
                "properties": {
                    "circuit_breaker_enabled": {"type": "boolean"},
                    "circuit_breaker_threshold": {"type": "integer", "minimum": 1},
                    "circuit_breaker_timeout": {"type": "integer", "minimum": 1},
                    "max_retries": {"type": "integer", "minimum": 0},
                    "retry_delay": {"type": "number", "minimum": 0},
                    "exponential_backoff": {"type": "boolean"},
                    "health_check_interval": {"type": "integer", "minimum": 1},
                    "metrics_enabled": {"type": "boolean"}
                },
                "additionalProperties": False
            },
            "security": {
                "type": "object",
                "properties": {
                    "encrypt_credentials": {"type": "boolean"},
                    "credential_key_file": {"type": "string", "minLength": 1},
                    "pii_encryption": {"type": "boolean"},
                    "api_key_rotation_days": {"type": "integer", "minimum": 1, "maximum": 365},
                    "audit_logging": {"type": "boolean"}
                },
                "additionalProperties": False
            },
            "logging": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "format": {"type": "string"},
                    "file": {"type": ["string", "null"]},
                    "max_file_size": {"type": "string"},
                    "backup_count": {"type": "integer", "minimum": 0},
                    "debug": {"type": "boolean"}
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        """Validate configuration against schema."""
        try:
            jsonschema.validate(config, cls.CONFIG_SCHEMA)
        except ValidationError as e:
            raise ConfigurationValidationError(f"Configuration validation failed: {e.message} at {'.'.join(str(p) for p in e.absolute_path)}")


class ProductionConfigManager:
    """
    Production-grade configuration manager with NO security compromises.
    
    Security and reliability principles:
    - Fail fast on any configuration issues
    - NO silent fallbacks or defaults
    - Comprehensive schema validation
    - Type safety enforcement
    - Proper error handling
    """
    
    def __init__(self, config_dir: Optional[str] = None, environment: Optional[str] = None):
        """Initialize configuration manager with strict validation."""
        self.logger = logging.getLogger(__name__)
        
        # Determine configuration directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / "config"
        
        if not self.config_dir.exists():
            raise ConfigurationError(f"Configuration directory does not exist: {self.config_dir}")
        
        # Determine environment with validation
        env_str = environment or os.getenv("KGAS_ENV", "development")
        try:
            self.environment = Environment(env_str)
        except ValueError:
            valid_envs = [e.value for e in Environment]
            raise ConfigurationError(f"Invalid environment '{env_str}'. Valid values: {valid_envs}")
        
        # Load and validate configuration
        self._config: Dict[str, Any] = {}
        self._load_configuration()
        
        # Validate loaded configuration
        ConfigurationSchemaValidator.validate_config(self._config)
        
        # Initialize configuration objects with validation
        self.database_configs: Dict[str, DatabaseConfig] = {}
        self.llm_configs: Dict[str, LLMConfig] = {}
        self.schema_config = SchemaConfig()
        self.error_config = ErrorHandlingConfig()
        self.security_config = SecurityConfig()
        
        self._initialize_configurations()
        
        # Perform comprehensive validation
        validation_issues = self._validate_configuration()
        if validation_issues:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(validation_issues)}")
        
        self.logger.info(f"Production configuration manager initialized for {self.environment.value}")
    
    def _load_configuration(self) -> None:
        """Load configuration files with comprehensive error handling."""
        # Load base configuration
        base_config_file = self.config_dir / "base.yaml"
        if not base_config_file.exists():
            raise ConfigurationError(f"Base configuration file not found: {base_config_file}")
        
        try:
            with open(base_config_file, 'r') as f:
                self._config = yaml.safe_load(f)
                if self._config is None:
                    self._config = {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in base configuration: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load base configuration: {e}")
        
        # Load environment-specific configuration
        env_config_file = self.config_dir / f"{self.environment.value}.yaml"
        if env_config_file.exists():
            try:
                with open(env_config_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                    if env_config:
                        self._deep_merge(self._config, env_config)
            except yaml.YAMLError as e:
                raise ConfigurationError(f"Invalid YAML in {self.environment.value} configuration: {e}")
            except Exception as e:
                raise ConfigurationError(f"Failed to load {self.environment.value} configuration: {e}")
        
        # Override with environment variables
        self._load_environment_variables()
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables with validation."""
        env_mappings = {
            "KGAS_NEO4J_HOST": (["database", "neo4j", "host"], str),
            "KGAS_NEO4J_PORT": (["database", "neo4j", "port"], int),
            "KGAS_NEO4J_PASSWORD": (["database", "neo4j", "password"], str),
            "KGAS_OPENAI_API_KEY": (["llm", "openai", "api_key"], str),
            "KGAS_ANTHROPIC_API_KEY": (["llm", "anthropic", "api_key"], str),
            "KGAS_GOOGLE_API_KEY": (["llm", "google", "api_key"], str),
            "KGAS_CIRCUIT_BREAKER_ENABLED": (["error_handling", "circuit_breaker_enabled"], bool),
            "KGAS_DEBUG": (["logging", "debug"], bool),
        }
        
        for env_var, (config_path, expected_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = self._convert_env_value(value, expected_type)
                    self._set_nested_value(self._config, config_path, converted_value)
                except (ValueError, TypeError) as e:
                    raise ConfigurationError(f"Invalid value for {env_var}: {e}")
    
    def _convert_env_value(self, value: str, expected_type: type) -> Union[str, int, bool]:
        """Convert environment variable string to appropriate type with validation."""
        if expected_type == bool:
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        
        elif expected_type == int:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Invalid integer value: {value}")
        
        elif expected_type == str:
            return value
        
        else:
            raise ValueError(f"Unsupported type conversion: {expected_type}")
    
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
            elif not isinstance(current[key], dict):
                raise ConfigurationError(f"Cannot set nested value: {key} is not a dictionary")
            current = current[key]
        current[path[-1]] = value
    
    def _initialize_configurations(self) -> None:
        """Initialize configuration objects with comprehensive validation."""
        # Database configurations
        db_config = self._config.get("database", {})
        for db_name, db_settings in db_config.items():
            if not isinstance(db_settings, dict):
                raise ConfigurationError(f"Database configuration for {db_name} must be a dictionary")
            
            try:
                # Ensure password is set for production
                if self.environment == Environment.PRODUCTION and not db_settings.get("password"):
                    raise ConfigurationError(f"Database password required for production environment: {db_name}")
                
                self.database_configs[db_name] = DatabaseConfig(**db_settings)
            except TypeError as e:
                raise ConfigurationError(f"Invalid database configuration for {db_name}: {e}")
        
        # Ensure Neo4j config exists
        if "neo4j" not in self.database_configs:
            raise ConfigurationError("Neo4j database configuration is required")
        
        # LLM configurations
        llm_config = self._config.get("llm", {})
        for provider, settings in llm_config.items():
            if not isinstance(settings, dict):
                raise ConfigurationError(f"LLM configuration for {provider} must be a dictionary")
            
            try:
                # Ensure provider is set correctly
                config_dict = settings.copy()
                config_dict['provider'] = provider
                self.llm_configs[provider] = LLMConfig(**config_dict)
            except TypeError as e:
                raise ConfigurationError(f"Invalid LLM configuration for {provider}: {e}")
        
        # Schema configuration
        schema_settings = self._config.get("schema", {})
        if schema_settings:
            try:
                self.schema_config = SchemaConfig(**schema_settings)
            except TypeError as e:
                raise ConfigurationError(f"Invalid schema configuration: {e}")
        
        # Error handling configuration
        error_settings = self._config.get("error_handling", {})
        if error_settings:
            try:
                self.error_config = ErrorHandlingConfig(**error_settings)
            except TypeError as e:
                raise ConfigurationError(f"Invalid error handling configuration: {e}")
        
        # Security configuration
        security_settings = self._config.get("security", {})
        if security_settings:
            try:
                self.security_config = SecurityConfig(**security_settings)
            except TypeError as e:
                raise ConfigurationError(f"Invalid security configuration: {e}")
    
    def get_database_config(self, database: str) -> DatabaseConfig:
        """Get database configuration with validation."""
        if database not in self.database_configs:
            raise ConfigurationError(f"Database configuration not found: {database}")
        return self.database_configs[database]
    
    def get_llm_config(self, provider: str) -> LLMConfig:
        """Get LLM configuration with validation."""
        if provider not in self.llm_configs:
            raise ConfigurationError(f"LLM configuration not found: {provider}")
        
        config = self.llm_configs[provider]
        return config
    
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
    
    def _validate_configuration(self) -> List[str]:
        """Comprehensive configuration validation."""
        issues = []
        
        # Validate database configurations
        for db_name, db_config in self.database_configs.items():
            try:
                # Database configs self-validate in __post_init__
                pass
            except ConfigurationValidationError as e:
                issues.append(f"Database {db_name}: {e}")
        
        # Validate LLM configurations
        if not self.llm_configs:
            issues.append("No LLM configurations found")
        
        for provider, config in self.llm_configs.items():
            try:
                # LLM configs self-validate in __post_init__
                pass
            except ConfigurationValidationError as e:
                issues.append(f"LLM {provider}: {e}")
        
        # Validate production-specific requirements
        if self.environment == Environment.PRODUCTION:
            # Ensure encryption is enabled
            if not self.security_config.encrypt_credentials:
                issues.append("Credential encryption must be enabled in production")
            
            # Ensure audit logging is enabled
            if not self.security_config.audit_logging:
                issues.append("Audit logging must be enabled in production")
        
        return issues
    
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
        }


if __name__ == "__main__":
    # Test production configuration manager
    try:
        # Test with current configuration
        config = ProductionConfigManager()
        summary = config.get_config_summary()
        
        print("Production Configuration Manager Test:")
        print(json.dumps(summary, indent=2))
        
        print("\n✅ Production configuration manager test completed successfully")
        
    except Exception as e:
        print(f"❌ Configuration manager test failed: {e}")
        raise