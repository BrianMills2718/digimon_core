#!/usr/bin/env python3
"""
Standard Configuration Utility

Single source of truth for all configuration access across the codebase.
All modules should use this instead of hardcoding values or reading config directly.
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StandardConfig:
    """
    Singleton configuration loader that provides standardized access
    to configuration values across all modules.
    """
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config_data is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from standard location"""
        try:
            # Find config directory relative to this file
            current_dir = Path(__file__).parent.parent.parent  # src/core/../.. = project root
            config_path = current_dir / "config" / "default.yaml"
            
            with open(config_path, 'r') as f:
                self._config_data = yaml.safe_load(f)
                
            logger.debug(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Fallback minimal config
            self._config_data = {
                'llm': {
                    'default_model': 'gemini-2.5-flash',
                    'fallback_model': 'gemini-2.5-flash-lite'
                },
                'api': {
                    'gemini_model': 'gemini-2.5-flash',
                    'fallback_model': 'gemini-2.5-flash-lite'
                }
            }
    
    def get_model(self, component: str = "default") -> str:
        """
        Get the model for a specific component.
        
        Args:
            component: Component name (optional, defaults to "default")
            
        Returns:
            Model name to use
        """
        # Always return the default model from config
        return self._config_data.get('llm', {}).get('default_model', 'gemini-2.5-flash')
    
    def get_api_model(self, provider: str = "gemini") -> str:
        """Get model for specific API provider"""
        if provider == "gemini":
            return self._config_data.get('api', {}).get('gemini_model', 'gemini-2.5-flash')
        elif provider == "openai":
            return self._config_data.get('api', {}).get('openai_model', 'gpt-4-turbo')
        else:
            return self.get_model()
    
    def get_database_uri(self) -> str:
        """Get database URI from config"""
        db_config = self._config_data.get('database', {})
        return db_config.get('uri') or f"bolt://{db_config.get('host', 'localhost')}:{db_config.get('port', 7687)}"
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get complete database configuration"""
        return self._config_data.get('database', {
            'host': 'localhost',
            'port': 7687,
            'username': 'neo4j',
            'password': '',
            'database': 'neo4j',
            'uri': 'bolt://localhost:7687'
        })
    
    def get_api_endpoint(self, provider: str) -> str:
        """Get API endpoint for provider"""
        endpoints = {
            'openai': "https://api.openai.com/v1",
            'anthropic': "https://api.anthropic.com/v1",
            'google': "https://generativelanguage.googleapis.com/v1beta"
        }
        
        # Check config first, then fallback to defaults
        api_config = self._config_data.get('api', {})
        if provider == 'openai':
            return api_config.get('openai_base_url', endpoints['openai'])
        elif provider == 'anthropic':
            return api_config.get('anthropic_base_url', endpoints['anthropic'])
        elif provider == 'google':
            return api_config.get('google_base_url', endpoints['google'])
        else:
            return endpoints.get(provider, '')
    
    def get_storage_path(self, storage_type: str = "workflows") -> str:
        """Get storage path for different data types"""
        storage_config = self._config_data.get('storage', {})
        
        if storage_type == "workflows":
            return storage_config.get('workflow_dir', './data/workflows')
        elif storage_type == "ontology":
            return storage_config.get('ontology_dir', './data/ontology')
        elif storage_type == "logs":
            return storage_config.get('logs_dir', get_file_path("logs_dir"))
        elif storage_type == "temp":
            return storage_config.get('temp_dir', '/tmp')
        else:
            return storage_config.get(f'{storage_type}_dir', f'./data/{storage_type}')
    
    def get_port(self, service: str) -> int:
        """Get port for service"""
        ports = self._config_data.get('ports', {})
        default_ports = {
            'neo4j': 7687,
            'web': 8000,
            'api': 5000,
            'prometheus': 9090,
            'grafana': 3000
        }
        return ports.get(service, default_ports.get(service, 8000))
    
    def get_config_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config_data.get(section, {})
    
    def get_config_value(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Configuration path like "llm.default_model"
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        keys = path.split('.')
        value = self._config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value

# Global instance
_config = StandardConfig()

# Convenience functions that all modules should use
def get_model(component: str = "default") -> str:
    """Get the model for a component. USE THIS INSTEAD OF HARDCODING."""
    return _config.get_model(component)

def get_api_model(provider: str = "gemini") -> str:
    """Get model for specific API provider"""
    return _config.get_api_model(provider)

def get_config_section(section: str) -> Dict[str, Any]:
    """Get entire configuration section"""
    return _config.get_config_section(section)

def get_config_value(path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation like 'llm.default_model'"""
    return _config.get_config_value(path, default)

# Additional convenience functions for all configuration types
def get_database_uri() -> str:
    """Get database URI"""
    return _config.get_database_uri()

def get_database_config() -> Dict[str, Any]:
    """Get database configuration section"""
    return _config.get_database_config()

def get_api_endpoint(provider: str) -> str:
    """Get API endpoint for provider"""
    return _config.get_api_endpoint(provider)

def get_storage_path(storage_type: str = "workflows") -> str:
    """Get storage path for data type"""
    return _config.get_storage_path(storage_type)

def get_port(service: str) -> int:
    """Get port for service"""
    return _config.get_port(service)

# For backwards compatibility with modules expecting these functions
def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration section"""
    return get_config_section('llm')

def get_api_config() -> Dict[str, Any]:
    """Get API configuration section"""
    return get_config_section('api')

if __name__ == "__main__":
    # Test the configuration system
    print("=== COMPREHENSIVE STANDARD CONFIG TEST ===")
    print(f"Default model: {get_model()}")
    print(f"Gemini model: {get_api_model('gemini')}")
    print(f"OpenAI model: {get_api_model('openai')}")
    print(f"Database URI: {get_database_uri()}")
    print(f"OpenAI endpoint: {get_api_endpoint('openai')}")
    print(f"Anthropic endpoint: {get_api_endpoint('anthropic')}")
    print(f"Workflows path: {get_storage_path('workflows')}")
    print(f"Logs path: {get_storage_path('logs')}")
    print(f"Neo4j port: {get_port('neo4j')}")
    print(f"Web port: {get_port('web')}")
    print(f"Direct path access: {get_config_value('llm.default_model')}")
def get_file_path(path_type: str) -> str:
    """Get file path with centralized configuration."""
    config = StandardConfig()
    
    defaults = {
        "data_dir": "./data",
        "logs_dir": "./logs", 
        "config_dir": "./config",
        "temp_dir": "./temp",
        "cache_dir": "./cache"
    }
    
    # Check for environment variable override
    env_key = f"KGAS_{path_type.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Check configuration file
    file_path = config._config_data.get('file_paths', {}).get(path_type)
    if file_path:
        return file_path
        
    # Return default
    return defaults.get(path_type, f"./{path_type}")
