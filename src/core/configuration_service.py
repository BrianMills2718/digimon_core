"""
Configuration Service
====================

Unified configuration service that integrates the ProductionConfigManager
and SecureCredentialManager to provide a complete configuration solution
for KGAS.

Features:
- Single entry point for all configuration needs
- Automatic credential management integration
- Runtime configuration updates
- Health checking and validation
- Configuration monitoring and alerts

Usage:
    config_service = ConfigurationService()
    
    # Get database connection
    neo4j_config = config_service.get_database_config('neo4j')
    
    # Get API key (automatically decrypted)
    openai_key = config_service.get_api_key('openai')
    
    # Get schema settings
    schema_config = config_service.get_schema_config()
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass

from .production_config_manager import (
    ProductionConfigManager, 
    DatabaseConfig, 
    LLMConfig, 
    SchemaConfig,
    ErrorHandlingConfig,
    SecurityConfig,
    Environment
)
from .secure_credential_manager import SecureCredentialManager


@dataclass
class ConfigurationHealth:
    """Configuration health status."""
    overall_status: str
    issues: List[str]
    warnings: List[str]
    last_check: float
    
    def is_healthy(self) -> bool:
        """Check if configuration is healthy."""
        return self.overall_status == "healthy" and not self.issues


class ConfigurationService:
    """
    Unified configuration service for KGAS.
    
    Provides a single interface for all configuration needs, integrating
    the production configuration manager with secure credential management.
    """
    
    def __init__(self, config_dir: Optional[str] = None, environment: Optional[str] = None):
        """Initialize configuration service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize component managers
        self.config_manager = ProductionConfigManager(config_dir, environment)
        self.credential_manager = SecureCredentialManager(
            credentials_dir=str(self.config_manager.config_dir / "credentials"),
            encrypt_by_default=self.config_manager.security_config.encrypt_credentials
        )
        
        # Configuration cache for performance
        self._config_cache: Dict[str, Any] = {}
        self._cache_expiry: float = 0
        self._cache_ttl: int = 300  # 5 minutes
        
        # Health monitoring
        self._last_health_check: float = 0
        self._health_check_interval: int = 60  # 1 minute
        self._health_status: Optional[ConfigurationHealth] = None
        
        # Setup initial configuration
        self._setup_initial_configuration()
        
        self.logger.info("Configuration service initialized successfully")
    
    def _setup_initial_configuration(self) -> None:
        """Set up initial configuration from environment variables."""
        # Import credentials from environment variables
        self._import_credentials_from_env()
        
        # Validate initial configuration
        self._validate_configuration()
    
    def _import_credentials_from_env(self) -> None:
        """Import API keys from environment variables if not already stored."""
        providers = {
            'openai': ['KGAS_OPENAI_API_KEY', 'OPENAI_API_KEY'],
            'anthropic': ['KGAS_ANTHROPIC_API_KEY', 'ANTHROPIC_API_KEY'],
            'google': ['KGAS_GOOGLE_API_KEY', 'GOOGLE_API_KEY'],
        }
        
        for provider, env_vars in providers.items():
            # Skip if credential already exists
            try:
                self.credential_manager.get_credential(provider)
                continue
            except ValueError:
                pass
            
            # Try to import from environment variables
            for env_var in env_vars:
                api_key = os.getenv(env_var)
                if api_key:
                    self.credential_manager.store_credential(
                        provider=provider,
                        credential=api_key,
                        expires_days=90,
                        description=f"Auto-imported from {env_var}"
                    )
                    self.logger.info(f"Imported {provider} credential from {env_var}")
                    break
    
    def _validate_configuration(self) -> None:
        """Validate configuration and log issues."""
        issues = self.config_manager.validate_configuration()
        
        if issues:
            self.logger.warning(f"Configuration validation found {len(issues)} issues:")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
        else:
            self.logger.info("Configuration validation passed")
    
    def get_database_config(self, database: str = "neo4j") -> DatabaseConfig:
        """Get database configuration."""
        return self.config_manager.get_database_config(database)
    
    def get_llm_config(self, provider: str) -> LLMConfig:
        """Get LLM configuration with integrated credential."""
        config = self.config_manager.get_llm_config(provider)
        
        # Override API key with securely stored credential
        try:
            config.api_key = self.credential_manager.get_credential(provider)
        except ValueError as e:
            self.logger.error(f"Failed to get credential for {provider}: {e}")
            raise
        
        return config
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for provider."""
        return self.credential_manager.get_credential(provider)
    
    def set_api_key(self, provider: str, api_key: str, expires_days: int = 90) -> None:
        """Set API key for provider."""
        self.credential_manager.store_credential(
            provider=provider,
            credential=api_key,
            expires_days=expires_days,
            description="Set via configuration service"
        )
        
        # Clear cache to force reload
        self._clear_cache()
    
    def get_schema_config(self) -> SchemaConfig:
        """Get schema framework configuration."""
        return self.config_manager.get_schema_config()
    
    def get_error_config(self) -> ErrorHandlingConfig:
        """Get error handling configuration."""
        return self.config_manager.get_error_config()
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.config_manager.get_security_config()
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.config_manager.is_development()
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.config_manager.is_production()
    
    def get_environment(self) -> str:
        """Get current environment name."""
        return self.config_manager.environment.value
    
    def check_health(self, force_check: bool = False) -> ConfigurationHealth:
        """Check configuration health."""
        now = time.time()
        
        # Use cached result if recent enough
        if (not force_check and 
            self._health_status and 
            now - self._last_health_check < self._health_check_interval):
            return self._health_status
        
        issues = []
        warnings = []
        
        # Check configuration validation
        config_issues = self.config_manager.validate_configuration()
        issues.extend(config_issues)
        
        # Check credential expiry
        expiring_credentials = self.credential_manager.check_expiring_credentials(days_threshold=30)
        for provider in expiring_credentials:
            status = self.credential_manager.get_credential_status(provider)
            days_left = status['days_until_expiry']
            if days_left == 0:
                issues.append(f"Credential for {provider} has expired")
            elif days_left <= 7:
                issues.append(f"Credential for {provider} expires in {days_left} days")
            else:
                warnings.append(f"Credential for {provider} expires in {days_left} days")
        
        # Check database connectivity (basic validation)
        try:
            db_config = self.get_database_config('neo4j')
            if not db_config.host:
                issues.append("Neo4j host not configured")
            if not db_config.password and not self.is_development():
                issues.append("Neo4j password not set for production")
        except Exception as e:
            issues.append(f"Database configuration error: {e}")
        
        # Check LLM configurations
        llm_providers = ['openai', 'anthropic', 'google']
        working_providers = 0
        
        for provider in llm_providers:
            try:
                config = self.get_llm_config(provider)
                if config.is_valid():
                    working_providers += 1
            except Exception as e:
                warnings.append(f"LLM provider {provider} not configured: {e}")
        
        if working_providers == 0:
            issues.append("No LLM providers configured")
        elif working_providers < 2:
            warnings.append("Only one LLM provider configured (no fallback)")
        
        # Determine overall status
        if issues:
            overall_status = "unhealthy"
        elif warnings:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Create health status
        self._health_status = ConfigurationHealth(
            overall_status=overall_status,
            issues=issues,
            warnings=warnings,
            last_check=now
        )
        
        self._last_health_check = now
        
        return self._health_status
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get comprehensive configuration summary."""
        health = self.check_health()
        
        return {
            "environment": self.get_environment(),
            "config_dir": str(self.config_manager.config_dir),
            "health": {
                "status": health.overall_status,
                "issues": len(health.issues),
                "warnings": len(health.warnings),
                "last_check": health.last_check,
            },
            "database": {
                "neo4j_host": self.get_database_config('neo4j').host,
                "neo4j_port": self.get_database_config('neo4j').port,
            },
            "credentials": self.credential_manager.list_credentials(),
            "schema": {
                "enabled_paradigms": self.get_schema_config().enabled_paradigms,
                "default_paradigm": self.get_schema_config().default_paradigm,
            },
            "error_handling": {
                "circuit_breaker_enabled": self.get_error_config().circuit_breaker_enabled,
                "max_retries": self.get_error_config().max_retries,
            },
            "security": {
                "encrypt_credentials": self.get_security_config().encrypt_credentials,
                "pii_encryption": self.get_security_config().pii_encryption,
            }
        }
    
    def rotate_credential(self, provider: str, new_credential: str, expires_days: int = 90) -> None:
        """Rotate credential for provider."""
        self.credential_manager.rotate_credential(
            provider=provider,
            new_credential=new_credential,
            expires_days=expires_days
        )
        
        # Clear cache
        self._clear_cache()
        
        self.logger.info(f"Rotated credential for {provider}")
    
    def validate_api_key(self, provider: str) -> bool:
        """Validate that API key exists and is accessible."""
        try:
            api_key = self.get_api_key(provider)
            return bool(api_key and len(api_key) > 10)
        except Exception:
            return False
    
    def get_active_llm_providers(self) -> List[str]:
        """Get list of active LLM providers with valid credentials."""
        providers = []
        
        for provider in ['openai', 'anthropic', 'google']:
            if self.validate_api_key(provider):
                providers.append(provider)
        
        return providers
    
    def _clear_cache(self) -> None:
        """Clear configuration cache."""
        self._config_cache.clear()
        self._cache_expiry = 0
    
    def reload_configuration(self) -> None:
        """Reload configuration from files."""
        self.config_manager._load_configuration()
        self.config_manager._initialize_configurations()
        self.credential_manager._load_credentials()
        
        self._clear_cache()
        self._validate_configuration()
        
        self.logger.info("Configuration reloaded")
    
    def export_configuration(self, include_credentials: bool = False) -> Dict[str, Any]:
        """Export configuration for backup or migration."""
        export_data = {
            "environment": self.get_environment(),
            "config_summary": self.config_manager.get_config_summary(),
            "credential_metadata": self.credential_manager.list_credentials(),
            "export_timestamp": time.time(),
        }
        
        if include_credentials:
            self.logger.warning("Exporting configuration with credentials - handle securely!")
            # Note: This would need additional security measures in production
            export_data["credentials"] = "*** REDACTED FOR SECURITY ***"
        
        return export_data


# Global configuration service instance
_config_service: Optional[ConfigurationService] = None


def get_config_service(config_dir: Optional[str] = None, environment: Optional[str] = None) -> ConfigurationService:
    """Get or create global configuration service instance."""
    global _config_service
    
    if _config_service is None:
        _config_service = ConfigurationService(config_dir, environment)
    
    return _config_service


def initialize_configuration() -> ConfigurationService:
    """Initialize configuration service and return it."""
    config_service = get_config_service()
    
    # Perform initial health check
    health = config_service.check_health()
    
    if not health.is_healthy():
        logging.warning(f"Configuration service started with {len(health.issues)} issues")
        for issue in health.issues:
            logging.warning(f"  - {issue}")
    
    return config_service


if __name__ == "__main__":
    # Test configuration service
    import tempfile
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Test configuration summary
        summary = config_service.get_configuration_summary()
        print("Configuration Summary:")
        import json
        print(json.dumps(summary, indent=2, default=str))
        
        # Test health check
        health = config_service.check_health()
        print(f"\nHealth Status: {health.overall_status}")
        if health.issues:
            print("Issues:")
            for issue in health.issues:
                print(f"  - {issue}")
        if health.warnings:
            print("Warnings:")
            for warning in health.warnings:
                print(f"  - {warning}")
        
        print("\n✅ Configuration service test completed")