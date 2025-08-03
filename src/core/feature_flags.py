#!/usr/bin/env python3
"""
Feature Flags Service - Structured Output Migration

Manages feature flags for gradual rollout of structured output with Pydantic schemas.
Provides centralized control over which components use structured output vs manual parsing.
"""

import logging
import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StructuredOutputConfig:
    """Configuration for structured output feature flags."""
    
    # Component-specific flags
    llm_reasoning: bool = True
    entity_extraction: bool = False
    mcp_adapter: bool = False
    llm_integration: bool = False
    
    # Global settings
    fail_fast: bool = True
    log_failures: bool = True
    
    # Token limits
    default_tokens: int = 32000
    complex_reasoning_tokens: int = 65000
    simple_extraction_tokens: int = 16000


class FeatureFlagsService:
    """
    Service for managing structured output feature flags.
    
    Loads configuration from config/default.yaml and provides
    typed access to feature flags and settings.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize feature flags service.
        
        Args:
            config_path: Path to config file (defaults to config/default.yaml)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Default config path
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'default.yaml'
            )
        
        self.config_path = config_path
        self.config = self._load_config()
        self.structured_output = self._parse_structured_output_config()
        
        self.logger.info(f"Feature flags loaded from {config_path}")
        self.logger.debug(f"Structured output config: {self.structured_output}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                self.logger.debug(f"Loaded config from {self.config_path}")
                return config
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def _parse_structured_output_config(self) -> StructuredOutputConfig:
        """Parse structured output configuration section."""
        
        so_config = self.config.get('structured_output', {})
        enabled_components = so_config.get('enabled_components', {})
        token_limits = so_config.get('token_limits', {})
        
        return StructuredOutputConfig(
            # Component flags
            llm_reasoning=enabled_components.get('llm_reasoning', True),
            entity_extraction=enabled_components.get('entity_extraction', False),
            mcp_adapter=enabled_components.get('mcp_adapter', False),
            llm_integration=enabled_components.get('llm_integration', False),
            
            # Global settings
            fail_fast=so_config.get('fail_fast', True),
            log_failures=so_config.get('log_failures', True),
            
            # Token limits
            default_tokens=token_limits.get('default', 32000),
            complex_reasoning_tokens=token_limits.get('complex_reasoning', 65000),
            simple_extraction_tokens=token_limits.get('simple_extraction', 16000)
        )
    
    def is_structured_output_enabled(self, component: str) -> bool:
        """
        Check if structured output is enabled for a specific component.
        
        Args:
            component: Component name ('llm_reasoning', 'entity_extraction', etc.)
            
        Returns:
            True if structured output is enabled for the component
        """
        return getattr(self.structured_output, component, False)
    
    def get_token_limit(self, usage_type: str = "default") -> int:
        """
        Get token limit for specific usage type.
        
        Args:
            usage_type: Type of usage ('default', 'complex_reasoning', 'simple_extraction')
            
        Returns:
            Token limit for the usage type
        """
        if usage_type == "complex_reasoning":
            return self.structured_output.complex_reasoning_tokens
        elif usage_type == "simple_extraction":
            return self.structured_output.simple_extraction_tokens
        else:
            return self.structured_output.default_tokens
    
    def should_fail_fast(self) -> bool:
        """Check if fail-fast behavior is enabled."""
        return self.structured_output.fail_fast
    
    def should_log_failures(self) -> bool:
        """Check if failure logging is enabled."""
        return self.structured_output.log_failures
    
    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags as dictionary."""
        return {
            'structured_output': {
                'llm_reasoning': self.structured_output.llm_reasoning,
                'entity_extraction': self.structured_output.entity_extraction,
                'mcp_adapter': self.structured_output.mcp_adapter,
                'llm_integration': self.structured_output.llm_integration,
                'fail_fast': self.structured_output.fail_fast,
                'log_failures': self.structured_output.log_failures,
                'token_limits': {
                    'default': self.structured_output.default_tokens,
                    'complex_reasoning': self.structured_output.complex_reasoning_tokens,
                    'simple_extraction': self.structured_output.simple_extraction_tokens
                }
            }
        }
    
    def enable_component(self, component: str) -> None:
        """
        Enable structured output for a component.
        
        Args:
            component: Component name to enable
        """
        if hasattr(self.structured_output, component):
            setattr(self.structured_output, component, True)
            self.logger.info(f"Enabled structured output for {component}")
        else:
            self.logger.warning(f"Unknown component: {component}")
    
    def disable_component(self, component: str) -> None:
        """
        Disable structured output for a component.
        
        Args:
            component: Component name to disable
        """
        if hasattr(self.structured_output, component):
            setattr(self.structured_output, component, False)
            self.logger.info(f"Disabled structured output for {component}")
        else:
            self.logger.warning(f"Unknown component: {component}")
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()
        self.structured_output = self._parse_structured_output_config()
        self.logger.info("Configuration reloaded")


# Global service instance
_feature_flags_service: Optional[FeatureFlagsService] = None

def get_feature_flags() -> FeatureFlagsService:
    """Get global feature flags service instance."""
    global _feature_flags_service
    
    if _feature_flags_service is None:
        _feature_flags_service = FeatureFlagsService()
    
    return _feature_flags_service


# Convenience functions
def is_structured_output_enabled(component: str) -> bool:
    """Check if structured output is enabled for component."""
    return get_feature_flags().is_structured_output_enabled(component)


def get_token_limit(usage_type: str = "default") -> int:
    """Get token limit for usage type."""
    return get_feature_flags().get_token_limit(usage_type)


def should_fail_fast() -> bool:
    """Check if fail-fast behavior is enabled."""
    return get_feature_flags().should_fail_fast()


def should_log_failures() -> bool:
    """Check if failure logging is enabled."""
    return get_feature_flags().should_log_failures()


if __name__ == "__main__":
    # Test the feature flags service
    flags = FeatureFlagsService()
    
    print("Feature Flags Test:")
    print("-" * 30)
    print(f"LLM Reasoning enabled: {flags.is_structured_output_enabled('llm_reasoning')}")
    print(f"Entity Extraction enabled: {flags.is_structured_output_enabled('entity_extraction')}")
    print(f"MCP Adapter enabled: {flags.is_structured_output_enabled('mcp_adapter')}")
    print(f"LLM Integration enabled: {flags.is_structured_output_enabled('llm_integration')}")
    print()
    print(f"Fail fast: {flags.should_fail_fast()}")
    print(f"Log failures: {flags.should_log_failures()}")
    print()
    print(f"Default token limit: {flags.get_token_limit('default')}")
    print(f"Complex reasoning tokens: {flags.get_token_limit('complex_reasoning')}")
    print(f"Simple extraction tokens: {flags.get_token_limit('simple_extraction')}")
    print()
    print("All flags:")
    import json
    print(json.dumps(flags.get_all_flags(), indent=2))