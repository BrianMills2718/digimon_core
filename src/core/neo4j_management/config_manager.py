"""
Config Manager

Handles Neo4j configuration management and validation.
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .neo4j_types import Neo4jConfig, ValidationError

logger = logging.getLogger(__name__)


class Neo4jConfigManager:
    """Manages Neo4j configuration creation and validation."""
    
    def __init__(self):
        self._default_config = {
            "host": "localhost",
            "port": 7687,
            "username": "neo4j",
            "password": "password",
            "container_name": "neo4j-graphrag",
            "max_retries": 3,
            "retry_delay": 1.0,
            "connection_timeout": 30,
            "max_connection_lifetime": 3600,
            "max_connection_pool_size": 10,
            "connection_acquisition_timeout": 60,
            "keep_alive": True
        }
    
    def create_config_from_uri(self, bolt_uri: str, username: str, password: str, 
                              container_name: str = "neo4j-graphrag", **kwargs) -> Neo4jConfig:
        """Create Neo4j configuration from bolt URI and credentials."""
        try:
            # Parse the bolt URI
            parsed_uri = urlparse(bolt_uri)
            
            if parsed_uri.scheme not in ["bolt", "bolt+s", "bolt+ssc"]:
                raise ValidationError(f"Invalid bolt URI scheme: {parsed_uri.scheme}")
            
            host = parsed_uri.hostname or "localhost"
            port = parsed_uri.port or 7687
            
            # Create configuration with defaults and overrides
            config_dict = self._default_config.copy()
            config_dict.update({
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "bolt_uri": bolt_uri,
                "container_name": container_name
            })
            config_dict.update(kwargs)
            
            # Validate configuration
            self._validate_config_dict(config_dict)
            
            return Neo4jConfig(**config_dict)
            
        except Exception as e:
            logger.error(f"Failed to create Neo4j config from URI: {e}")
            raise ValidationError(f"Invalid Neo4j configuration: {e}")
    
    def create_config_from_components(self, host: str, port: int, username: str, password: str,
                                    container_name: str = "neo4j-graphrag", **kwargs) -> Neo4jConfig:
        """Create Neo4j configuration from individual components."""
        try:
            # Build bolt URI
            bolt_uri = f"bolt://{host}:{port}"
            
            # Create configuration with defaults and overrides
            config_dict = self._default_config.copy()
            config_dict.update({
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "bolt_uri": bolt_uri,
                "container_name": container_name
            })
            config_dict.update(kwargs)
            
            # Validate configuration
            self._validate_config_dict(config_dict)
            
            return Neo4jConfig(**config_dict)
            
        except Exception as e:
            logger.error(f"Failed to create Neo4j config from components: {e}")
            raise ValidationError(f"Invalid Neo4j configuration: {e}")
    
    def create_config_from_external_config(self, external_config: Dict[str, Any]) -> Neo4jConfig:
        """Create Neo4j configuration from external configuration manager."""
        try:
            # Extract Neo4j configuration from external config
            neo4j_config = external_config.get('neo4j', {})
            
            if not neo4j_config:
                logger.warning("No Neo4j configuration found in external config, using defaults")
                neo4j_config = {}
            
            # Extract required fields
            uri = neo4j_config.get('uri', f"bolt://{self._default_config['host']}:{self._default_config['port']}")
            username = neo4j_config.get('user', self._default_config['username'])
            password = neo4j_config.get('password', self._default_config['password'])
            
            # Parse URI for host and port
            parsed_uri = urlparse(uri)
            host = parsed_uri.hostname or self._default_config['host']
            port = parsed_uri.port or self._default_config['port']
            
            # Build full configuration
            config_dict = self._default_config.copy()
            config_dict.update({
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "bolt_uri": uri
            })
            
            # Override with any additional Neo4j-specific settings
            for key, value in neo4j_config.items():
                if key in config_dict and key not in ['uri', 'user', 'password']:
                    config_dict[key] = value
            
            # Validate configuration
            self._validate_config_dict(config_dict)
            
            return Neo4jConfig(**config_dict)
            
        except Exception as e:
            logger.error(f"Failed to create Neo4j config from external config: {e}")
            raise ValidationError(f"Invalid external Neo4j configuration: {e}")
    
    def _validate_config_dict(self, config_dict: Dict[str, Any]) -> None:
        """Validate configuration dictionary."""
        # Required fields
        required_fields = ["host", "port", "username", "password", "bolt_uri"]
        for field in required_fields:
            if field not in config_dict or config_dict[field] is None:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate types and ranges
        if not isinstance(config_dict["port"], int) or config_dict["port"] <= 0 or config_dict["port"] > 65535:
            raise ValidationError("Port must be a positive integer between 1 and 65535")
        
        if not isinstance(config_dict["max_retries"], int) or config_dict["max_retries"] < 0:
            raise ValidationError("Max retries must be a non-negative integer")
        
        if not isinstance(config_dict["retry_delay"], (int, float)) or config_dict["retry_delay"] < 0:
            raise ValidationError("Retry delay must be a non-negative number")
        
        if not isinstance(config_dict["connection_timeout"], int) or config_dict["connection_timeout"] <= 0:
            raise ValidationError("Connection timeout must be a positive integer")
        
        if not isinstance(config_dict["max_connection_lifetime"], int) or config_dict["max_connection_lifetime"] <= 0:
            raise ValidationError("Max connection lifetime must be a positive integer")
        
        if not isinstance(config_dict["max_connection_pool_size"], int) or config_dict["max_connection_pool_size"] <= 0:
            raise ValidationError("Max connection pool size must be a positive integer")
        
        if not isinstance(config_dict["connection_acquisition_timeout"], int) or config_dict["connection_acquisition_timeout"] <= 0:
            raise ValidationError("Connection acquisition timeout must be a positive integer")
        
        # Validate string fields
        string_fields = ["host", "username", "password", "bolt_uri", "container_name"]
        for field in string_fields:
            if not isinstance(config_dict[field], str) or not config_dict[field].strip():
                raise ValidationError(f"{field} must be a non-empty string")
        
        # Validate boolean fields
        if not isinstance(config_dict["keep_alive"], bool):
            raise ValidationError("Keep alive must be a boolean")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return self._default_config.copy()
    
    def validate_connection_parameters(self, config: Neo4jConfig) -> Dict[str, Any]:
        """Validate that connection parameters are reasonable for production use."""
        warnings = []
        recommendations = []
        
        # Check connection pool size
        if config.max_connection_pool_size < 5:
            warnings.append("Connection pool size is very small, may impact performance")
            recommendations.append("Consider increasing max_connection_pool_size to at least 10")
        elif config.max_connection_pool_size > 50:
            warnings.append("Connection pool size is very large, may consume excessive resources")
            recommendations.append("Consider reducing max_connection_pool_size to 20-30 for most use cases")
        
        # Check connection lifetime
        if config.max_connection_lifetime < 300:  # 5 minutes
            warnings.append("Connection lifetime is very short, may cause frequent reconnections")
            recommendations.append("Consider increasing max_connection_lifetime to at least 1800 (30 minutes)")
        elif config.max_connection_lifetime > 86400:  # 24 hours
            warnings.append("Connection lifetime is very long, connections may become stale")
            recommendations.append("Consider reducing max_connection_lifetime to 3600-7200 (1-2 hours)")
        
        # Check timeouts
        if config.connection_timeout < 5:
            warnings.append("Connection timeout is very short, may cause premature failures")
            recommendations.append("Consider increasing connection_timeout to at least 10 seconds")
        elif config.connection_timeout > 60:
            warnings.append("Connection timeout is very long, may cause slow failure detection")
            recommendations.append("Consider reducing connection_timeout to 30-45 seconds")
        
        # Check retry settings
        if config.max_retries > 5:
            warnings.append("Max retries is high, may cause long delays on persistent failures")
            recommendations.append("Consider reducing max_retries to 3-5")
        
        if config.retry_delay > 5.0:
            warnings.append("Retry delay is high, may cause long recovery times")
            recommendations.append("Consider reducing retry_delay to 1.0-2.0 seconds")
        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": recommendations,
            "config_summary": {
                "pool_size": config.max_connection_pool_size,
                "connection_lifetime": config.max_connection_lifetime,
                "connection_timeout": config.connection_timeout,
                "max_retries": config.max_retries,
                "retry_delay": config.retry_delay
            }
        }
    
    def create_optimized_config(self, bolt_uri: str, username: str, password: str,
                               use_case: str = "production") -> Neo4jConfig:
        """Create optimized configuration for specific use cases."""
        
        base_config = self.create_config_from_uri(bolt_uri, username, password)
        
        if use_case == "development":
            # Development settings - faster timeouts, smaller pools
            optimizations = {
                "max_connection_pool_size": 5,
                "connection_timeout": 15,
                "max_connection_lifetime": 1800,  # 30 minutes
                "max_retries": 2,
                "retry_delay": 0.5
            }
        elif use_case == "testing":
            # Testing settings - minimal resources, fast failures
            optimizations = {
                "max_connection_pool_size": 2,
                "connection_timeout": 10,
                "max_connection_lifetime": 600,  # 10 minutes
                "max_retries": 1,
                "retry_delay": 0.1
            }
        elif use_case == "high_performance":
            # High performance settings - larger pools, longer lifetimes
            optimizations = {
                "max_connection_pool_size": 20,
                "connection_timeout": 45,
                "max_connection_lifetime": 7200,  # 2 hours
                "max_retries": 5,
                "retry_delay": 1.0
            }
        else:  # production (default)
            # Production settings - balanced performance and reliability
            optimizations = {
                "max_connection_pool_size": 10,
                "connection_timeout": 30,
                "max_connection_lifetime": 3600,  # 1 hour
                "max_retries": 3,
                "retry_delay": 1.0
            }
        
        # Create new config with optimizations
        return Neo4jConfig(
            host=base_config.host,
            port=base_config.port,
            username=base_config.username,
            password=base_config.password,
            bolt_uri=base_config.bolt_uri,
            container_name=base_config.container_name,
            **optimizations
        )
    
    def export_config_summary(self, config: Neo4jConfig) -> Dict[str, Any]:
        """Export configuration summary for logging or debugging."""
        return {
            "connection": {
                "host": config.host,
                "port": config.port,
                "bolt_uri": config.bolt_uri,
                "username": config.username,
                "password_set": bool(config.password)  # Don't expose actual password
            },
            "container": {
                "name": config.container_name
            },
            "connection_pooling": {
                "max_pool_size": config.max_connection_pool_size,
                "connection_lifetime": config.max_connection_lifetime,
                "keep_alive": config.keep_alive
            },
            "timeouts": {
                "connection_timeout": config.connection_timeout,
                "acquisition_timeout": config.connection_acquisition_timeout
            },
            "retry_policy": {
                "max_retries": config.max_retries,
                "retry_delay": config.retry_delay
            }
        }