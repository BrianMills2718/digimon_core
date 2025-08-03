"""
Centralized Model Configuration for Development

This module provides a single source of truth for LLM model configuration across
the entire codebase. During development, this locks in gemini-2.5-flash everywhere.
After development, simply change DEVELOPMENT_MODEL to switch the entire system.
"""

import os
import yaml
from typing import Optional, Dict, Any
from pathlib import Path

# =============================================================================
# DEVELOPMENT MODEL LOCK-IN
# =============================================================================
# Change this single line to switch the entire codebase to a different model
DEVELOPMENT_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-lite"

# Set to True to override ALL model settings during development
DEVELOPMENT_MODE = True

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

class ModelConfig:
    """Centralized model configuration"""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception:
            # Fallback configuration
            self.config = {
                'llm': {'default_model': DEVELOPMENT_MODEL},
                'api': {
                    'gemini_model': DEVELOPMENT_MODEL,
                    'fallback_model': FALLBACK_MODEL
                }
            }
    
    def get_model(self, component: str = "default", fallback: Optional[str] = None) -> str:
        """
        Get the model for a specific component
        
        Args:
            component: Component name (e.g., 'algorithm_generator', 'extractor')
            fallback: Fallback model if not found in config
            
        Returns:
            Model name to use
        """
        # During development, always return the development model
        if DEVELOPMENT_MODE:
            return DEVELOPMENT_MODEL
        
        # Production logic - check config
        if component == "default":
            return self.config.get('llm', {}).get('default_model', fallback or DEVELOPMENT_MODEL)
        elif component == "gemini":
            return self.config.get('api', {}).get('gemini_model', fallback or DEVELOPMENT_MODEL)
        else:
            # Check for component-specific config
            component_config = self.config.get('llm', {}).get('component_models', {})
            return component_config.get(component, self.get_model("default"))
    
    def get_provider(self, model: Optional[str] = None) -> str:
        """Get the provider for a model"""
        model = model or self.get_model()
        
        if 'gemini' in model.lower():
            return 'google'
        elif 'gpt' in model.lower() or 'openai' in model.lower():
            return 'openai'
        elif 'claude' in model.lower():
            return 'anthropic'
        else:
            return 'google'  # Default to google for gemini models
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for the provider"""
        provider = provider or self.get_provider()
        
        if provider == 'google':
            return os.getenv("GOOGLE_API_KEY") or self.config.get('api', {}).get('google_api_key')
        elif provider == 'openai':
            return os.getenv("OPENAI_API_KEY") or self.config.get('api', {}).get('openai_api_key')
        elif provider == 'anthropic':
            return os.getenv("ANTHROPIC_API_KEY") or self.config.get('api', {}).get('anthropic_api_key')
        else:
            return None
    
    def get_litellm_model(self, component: str = "default") -> str:
        """Get model in LiteLLM format (provider/model)"""
        model = self.get_model(component)
        provider = self.get_provider(model)
        
        # LiteLLM format
        if provider == 'google':
            return f"gemini/{model}"
        elif provider == 'openai':
            return model  # OpenAI models don't need prefix
        elif provider == 'anthropic':
            return f"anthropic/{model}"
        else:
            return model

# Global instance
_model_config = ModelConfig()

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_model(component: str = "default", fallback: Optional[str] = None) -> str:
    """Get model for a component"""
    return _model_config.get_model(component, fallback)

def get_litellm_model(component: str = "default") -> str:
    """Get model in LiteLLM format"""
    return _model_config.get_litellm_model(component)

def get_provider(model: Optional[str] = None) -> str:
    """Get provider for a model"""
    return _model_config.get_provider(model)

def get_api_key(provider: Optional[str] = None) -> Optional[str]:
    """Get API key for provider"""
    return _model_config.get_api_key(provider)

def is_development_mode() -> bool:
    """Check if in development mode"""
    return DEVELOPMENT_MODE

def get_development_model() -> str:
    """Get the current development model"""
    return DEVELOPMENT_MODEL

# =============================================================================
# ENVIRONMENT VARIABLE OVERRIDES
# =============================================================================

def set_development_model_env():
    """Set environment variables to lock in development model"""
    os.environ["LLM_MODEL"] = DEVELOPMENT_MODEL
    os.environ["DEFAULT_MODEL"] = DEVELOPMENT_MODEL
    os.environ["DEVELOPMENT_MODEL"] = DEVELOPMENT_MODEL

def clear_model_env_overrides():
    """Clear potentially conflicting environment variables"""
    conflicting_vars = [
        "OPENAI_MODEL", "GPT_MODEL", "GEMINI_MODEL", 
        "CLAUDE_MODEL", "ANTHROPIC_MODEL"
    ]
    
    for var in conflicting_vars:
        if var in os.environ:
            del os.environ[var]

# Auto-set environment variables when imported
if DEVELOPMENT_MODE:
    set_development_model_env()
    clear_model_env_overrides()

# =============================================================================
# DEVELOPMENT UTILITIES
# =============================================================================

def print_model_status():
    """Print current model configuration status"""
    print("=" * 60)
    print("MODEL CONFIGURATION STATUS")
    print("=" * 60)
    print(f"Development Mode: {DEVELOPMENT_MODE}")
    print(f"Development Model: {DEVELOPMENT_MODEL}")
    print(f"Default Model: {get_model()}")
    print(f"LiteLLM Format: {get_litellm_model()}")
    print(f"Provider: {get_provider()}")
    print("=" * 60)

def verify_model_lock():
    """Verify that the model is locked in correctly"""
    issues = []
    
    # Check if development mode is active
    if not DEVELOPMENT_MODE:
        issues.append("Development mode is disabled")
    
    # Check if model is set correctly
    if get_model() != DEVELOPMENT_MODEL:
        issues.append(f"Model mismatch: expected {DEVELOPMENT_MODEL}, got {get_model()}")
    
    # Check environment variables
    if os.getenv("LLM_MODEL") != DEVELOPMENT_MODEL:
        issues.append("LLM_MODEL environment variable not set correctly")
    
    if issues:
        print("❌ Model lock verification failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Model lock verified successfully")
        return True

if __name__ == "__main__":
    print_model_status()
    verify_model_lock()