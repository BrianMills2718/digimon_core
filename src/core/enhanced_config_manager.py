from src.core.standard_config import get_database_uri
from src.core.standard_config import get_file_path
"""
Enhanced Configuration Manager for KGAS

Provides easy configuration management with environment variable support,
validation, and sensible defaults. Designed for production use with
security best practices.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", get_database_uri()))
    username: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", ""))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))
    
    def __post_init__(self):
        if not self.password:
            logger.warning("NEO4J_PASSWORD not set - database connections may fail")

@dataclass
class APIConfig:
    """API configuration for LLM providers"""
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    max_retries: int = field(default_factory=lambda: int(os.getenv("KGAS_API_MAX_RETRIES", "3")))
    timeout: int = field(default_factory=lambda: int(os.getenv("KGAS_API_TIMEOUT", "30")))

@dataclass
class SystemConfig:
    """System configuration"""
    log_level: str = field(default_factory=lambda: os.getenv("KGAS_LOG_LEVEL", "INFO"))
    max_workers: int = field(default_factory=lambda: int(os.getenv("KGAS_MAX_WORKERS", "4")))
    debug_mode: bool = field(default_factory=lambda: os.getenv("KGAS_DEBUG", "false").lower() == "true")
    metrics_enabled: bool = field(default_factory=lambda: os.getenv("KGAS_METRICS_ENABLED", "true").lower() == "true")
    backup_enabled: bool = field(default_factory=lambda: os.getenv("KGAS_BACKUP_ENABLED", "false").lower() == "true")
    encryption_enabled: bool = field(default_factory=lambda: os.getenv("KGAS_ENCRYPTION_ENABLED", "false").lower() == "true")

@dataclass
class SecurityConfig:
    """Security configuration"""
    pii_password: str = field(default_factory=lambda: os.getenv("KGAS_PII_PASSWORD", ""))
    pii_salt: str = field(default_factory=lambda: os.getenv("KGAS_PII_SALT", ""))
    enable_auth: bool = field(default_factory=lambda: os.getenv("KGAS_ENABLE_AUTH", "false").lower() == "true")
    
    def __post_init__(self):
        if self.enable_auth and (not self.pii_password or not self.pii_salt):
            logger.warning("Authentication enabled but PII credentials not set")

@dataclass
class EnhancedKGASConfig:
    """Complete KGAS configuration"""
    environment: Environment = field(default_factory=lambda: Environment(os.getenv("KGAS_ENV", "development")))
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Additional paths
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("KGAS_DATA_DIR", get_file_path("data_dir"))))
    logs_dir: Path = field(default_factory=lambda: Path(os.getenv("KGAS_LOGS_DIR", get_file_path("logs_dir"))))
    config_dir: Path = field(default_factory=lambda: Path(os.getenv("KGAS_CONFIG_DIR", get_file_path("config_dir"))))
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Log configuration status
        logger.info(f"KGAS configured for {self.environment.value} environment")
        
        # Validate critical settings
        if not self.database.password and self.environment != Environment.TESTING:
            logger.error("Database password not configured - system may not function properly")
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get Neo4j configuration dictionary"""
        return {
            "uri": self.database.uri,
            "user": self.database.username,
            "password": self.database.password,
            "database": self.database.database
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM API configuration"""
        return {
            "openai_api_key": self.api.openai_api_key,
            "anthropic_api_key": self.api.anthropic_api_key,
            "google_api_key": self.api.google_api_key,
            "max_retries": self.api.max_retries,
            "timeout": self.api.timeout
        }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.environment == Environment.TESTING
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key is available for provider"""
        provider_map = {
            "openai": self.api.openai_api_key,
            "anthropic": self.api.anthropic_api_key,
            "google": self.api.google_api_key
        }
        
        key = provider_map.get(provider.lower(), "")
        return bool(key and key != "test-key")

class EnhancedConfigManager:
    """Enhanced configuration manager with validation and caching"""
    
    def __init__(self):
        self._config: Optional[EnhancedKGASConfig] = None
        self._config_file_path: Optional[Path] = None
        
    def load_config(self, config_file: Optional[Union[str, Path]] = None) -> EnhancedKGASConfig:
        """Load configuration from environment and optional YAML file"""
        
        # Load environment variables from .env if available
        self._load_env_file()
        
        # Create base config from environment variables
        config = EnhancedKGASConfig()
        
        # Override with YAML file if provided
        if config_file:
            config = self._merge_yaml_config(config, config_file)
        else:
            # Try default config files
            config_dir = get_file_path("config_dir")
            default_files = [
                f"{config_dir}/{config.environment.value}.yaml",
                f"{config_dir}/config.yaml",
                f"{config_dir}/default.yaml"
            ]
            
            for file_path in default_files:
                if Path(file_path).exists():
                    config = self._merge_yaml_config(config, file_path)
                    break
        
        self._config = config
        return config
    
    def get_config(self) -> EnhancedKGASConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> EnhancedKGASConfig:
        """Reload configuration from sources"""
        self._config = None
        return self.load_config(self._config_file_path)
    
    def _load_env_file(self):
        """Load .env file if available"""
        env_file = Path(".env")
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.debug("Loaded environment variables from .env file")
            except ImportError:
                logger.warning("python-dotenv not available - .env file not loaded")
            except Exception as e:
                logger.error(f"Error loading .env file: {e}")
    
    def _merge_yaml_config(self, config: EnhancedKGASConfig, yaml_file: Union[str, Path]) -> EnhancedKGASConfig:
        """Merge YAML configuration with existing config"""
        try:
            yaml_path = Path(yaml_file)
            if not yaml_path.exists():
                logger.warning(f"Config file not found: {yaml_file}")
                return config
            
            with open(yaml_path, 'r') as f:
                yaml_data = yaml.safe_load(f)
            
            if not yaml_data:
                logger.warning(f"Empty or invalid YAML file: {yaml_file}")
                return config
            
            # Process YAML data and merge with config
            config = self._apply_yaml_overrides(config, yaml_data)
            self._config_file_path = yaml_path
            
            logger.debug(f"Merged configuration from {yaml_file}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading YAML config from {yaml_file}: {e}")
            return config
    
    def _apply_yaml_overrides(self, config: EnhancedKGASConfig, yaml_data: Dict[str, Any]) -> EnhancedKGASConfig:
        """Apply YAML configuration overrides"""
        
        # Database configuration
        if "database" in yaml_data:
            db_config = yaml_data["database"]
            if "uri" in db_config:
                config.database.uri = self._resolve_env_var(db_config["uri"])
            if "username" in db_config:
                config.database.username = self._resolve_env_var(db_config["username"])
            if "password" in db_config:
                config.database.password = self._resolve_env_var(db_config["password"])
        
        # API configuration
        if "api" in yaml_data:
            api_config = yaml_data["api"]
            if "openai_api_key" in api_config:
                config.api.openai_api_key = self._resolve_env_var(api_config["openai_api_key"])
            if "anthropic_api_key" in api_config:
                config.api.anthropic_api_key = self._resolve_env_var(api_config["anthropic_api_key"])
            if "google_api_key" in api_config:
                config.api.google_api_key = self._resolve_env_var(api_config["google_api_key"])
            if "max_retries" in api_config:
                config.api.max_retries = int(api_config["max_retries"])
            if "timeout" in api_config:
                config.api.timeout = int(api_config["timeout"])
        
        # System configuration
        if "system" in yaml_data:
            sys_config = yaml_data["system"]
            if "log_level" in sys_config:
                config.system.log_level = self._resolve_env_var(sys_config["log_level"])
            if "max_workers" in sys_config:
                config.system.max_workers = int(self._resolve_env_var(sys_config["max_workers"]))
            if "debug_mode" in sys_config:
                config.system.debug_mode = bool(sys_config["debug_mode"])
            if "metrics_enabled" in sys_config:
                config.system.metrics_enabled = bool(sys_config["metrics_enabled"])
            if "backup_enabled" in sys_config:
                config.system.backup_enabled = bool(sys_config["backup_enabled"])
            if "encryption_enabled" in sys_config:
                config.system.encryption_enabled = bool(sys_config["encryption_enabled"])
        
        return config
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variable references in configuration values"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            # Extract variable name and default value
            var_expr = value[2:-1]  # Remove ${ and }
            
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, "")
        
        return str(value)
    
    def validate_config(self, config: Optional[EnhancedKGASConfig] = None) -> bool:
        """Validate configuration completeness and consistency"""
        if config is None:
            config = self.get_config()
        
        issues = []
        
        # Check database configuration
        if not config.database.password and not config.is_testing():
            issues.append("Database password not configured")
        
        # Check production requirements
        if config.is_production():
            if not config.system.backup_enabled:
                issues.append("Backups should be enabled in production")
            if not config.system.encryption_enabled:
                issues.append("Encryption should be enabled in production")
            if config.system.debug_mode:
                issues.append("Debug mode should be disabled in production")
        
        # Check API keys (warnings only)
        if not any([config.api.openai_api_key, config.api.anthropic_api_key, config.api.google_api_key]):
            logger.warning("No LLM API keys configured - some features may not work")
        
        if issues:
            for issue in issues:
                logger.error(f"Configuration issue: {issue}")
            return False
        
        return True

# Global instance for easy access
_config_manager = EnhancedConfigManager()

def get_config() -> EnhancedKGASConfig:
    """Get global configuration instance"""
    return _config_manager.get_config()

def reload_config() -> EnhancedKGASConfig:
    """Reload global configuration"""
    return _config_manager.reload_config()

def validate_config() -> bool:
    """Validate global configuration"""
    return _config_manager.validate_config()

# Backward compatibility aliases
get_settings = get_config
ConfigurationSettings = EnhancedKGASConfig