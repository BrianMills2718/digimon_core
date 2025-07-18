"""
Configuration Loader for KGAS
Provides centralized configuration management and environment-specific settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfigurationSettings:
    """Configuration settings for KGAS system."""
    
    # Environment settings
    environment: str = "development"
    docker_compose_path: str = ""
    database_url: str = ""
    llm_provider: str = "openai"
    log_level: str = "INFO"
    
    # Monitoring settings
    prometheus_config: str = ""
    grafana_datasources: str = ""
    monitoring_docker_compose: str = ""
    
    # Contract settings
    tool_contract_schema: str = ""
    phase1_to_phase2_adapter: str = ""
    
    # Core settings
    max_concurrent_documents: int = 10
    backup_retention_days: int = 30
    metrics_collection_interval: int = 30
    
    # Security settings
    encrypt_backups: bool = True
    require_pii_encryption: bool = True
    max_api_rate_limit: int = 100
    
    # Performance settings
    memory_limit_gb: int = 8
    processing_timeout_seconds: int = 300
    parallel_processing_enabled: bool = True

class ConfigurationLoader:
    """Centralized configuration loader for KGAS system."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration loader.
        
        Args:
            config_path: Optional path to configuration file. Defaults to config/config.yaml
        """
        if config_path is None:
            self.config_path = Path(__file__).parent / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        self.config_dir = self.config_path.parent
        self._config_data = None
        self._settings = None
        
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self._config_data = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise
    
    def get_settings(self, environment: Optional[str] = None) -> ConfigurationSettings:
        """Get configuration settings for specified environment.
        
        Args:
            environment: Environment name. Defaults to KGAS_ENV environment variable or 'development'
            
        Returns:
            ConfigurationSettings object with environment-specific settings
        """
        if environment is None:
            environment = os.environ.get('KGAS_ENV', 'development')
        
        if self._settings is None or self._settings.environment != environment:
            self._settings = self._build_settings(environment)
        
        return self._settings
    
    def _build_settings(self, environment: str) -> ConfigurationSettings:
        """Build configuration settings for specified environment."""
        
        # Get environment-specific settings
        env_config = self._config_data.get('environments', {}).get(environment, {})
        
        # Get other configuration sections
        monitoring_config = self._config_data.get('monitoring', {})
        contracts_config = self._config_data.get('contracts', {})
        core_config = self._config_data.get('core', {})
        security_config = self._config_data.get('security', {})
        performance_config = self._config_data.get('performance', {})
        
        # Resolve relative paths
        def resolve_path(path: str) -> str:
            if path.startswith('./'):
                return str(self.config_dir / path[2:])
            return path
        
        # Build settings object
        settings = ConfigurationSettings(
            environment=environment,
            docker_compose_path=resolve_path(env_config.get('docker_compose', '')),
            database_url=self._resolve_env_var(env_config.get('database_url', '')),
            llm_provider=self._resolve_env_var(env_config.get('llm_provider', 'openai')),
            log_level=env_config.get('log_level', 'INFO'),
            
            prometheus_config=resolve_path(monitoring_config.get('prometheus', {}).get('config', '')),
            grafana_datasources=resolve_path(monitoring_config.get('grafana', {}).get('datasources', '')),
            monitoring_docker_compose=resolve_path(monitoring_config.get('docker_compose', '')),
            
            tool_contract_schema=resolve_path(contracts_config.get('tool_contract_schema', '')),
            phase1_to_phase2_adapter=resolve_path(contracts_config.get('phase1_to_phase2_adapter', '')),
            
            max_concurrent_documents=core_config.get('max_concurrent_documents', 10),
            backup_retention_days=core_config.get('backup_retention_days', 30),
            metrics_collection_interval=core_config.get('metrics_collection_interval', 30),
            
            encrypt_backups=security_config.get('encrypt_backups', True),
            require_pii_encryption=security_config.get('require_pii_encryption', True),
            max_api_rate_limit=security_config.get('max_api_rate_limit', 100),
            
            memory_limit_gb=performance_config.get('memory_limit_gb', 8),
            processing_timeout_seconds=performance_config.get('processing_timeout_seconds', 300),
            parallel_processing_enabled=performance_config.get('parallel_processing_enabled', True)
        )
        
        logger.info(f"Built configuration settings for environment: {environment}")
        return settings
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variable references in configuration values."""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.environ.get(env_var, value)
        return value
    
    def get_config_path(self, relative_path: str) -> Path:
        """Get absolute path for a configuration file relative to config directory."""
        if relative_path.startswith('./'):
            return self.config_dir / relative_path[2:]
        return Path(relative_path)

# Global configuration loader instance
_config_loader = None

def get_config_loader() -> ConfigurationLoader:
    """Get global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader()
    return _config_loader

def get_settings(environment: Optional[str] = None) -> ConfigurationSettings:
    """Get configuration settings for specified environment."""
    return get_config_loader().get_settings(environment)