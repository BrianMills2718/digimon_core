"""
Factory for creating orchestrators - enables easy pivoting between strategies.

This factory pattern allows switching between different orchestration approaches
without changing the calling code, supporting our "easy to pivot" design goal.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .base import Orchestrator
from .simple_orchestrator import SimpleSequentialOrchestrator

logger = logging.getLogger(__name__)


# Registry of available orchestrator types
ORCHESTRATOR_REGISTRY = {
    "simple": SimpleSequentialOrchestrator,
    "simple_sequential": SimpleSequentialOrchestrator,
    "sequential": SimpleSequentialOrchestrator,
    # Future orchestrators can be added here:
    # "parallel": ParallelOrchestrator,
    # "llm_planned": LLMPlannedOrchestrator,
    # "langchain": LangChainOrchestrator,
    # "crewai": CrewAIOrchestrator,
    # "autogen": AutoGenOrchestrator,
}


def create_orchestrator(strategy: str = "simple", config_path: str = None) -> Orchestrator:
    """
    Factory for creating orchestrators - easy to extend.
    
    This is the main pivot point for changing orchestration strategies.
    Just add new orchestrator classes to ORCHESTRATOR_REGISTRY and they
    become available without changing any other code.
    
    Args:
        strategy: Orchestration strategy to use
        config_path: Optional path to configuration file
        
    Returns:
        Orchestrator instance
        
    Raises:
        ValueError: If strategy is not recognized
        RuntimeError: If orchestrator creation fails
    """
    logger.info(f"Creating orchestrator with strategy: {strategy}")
    
    # Normalize strategy name
    strategy = strategy.lower()
    
    # Check if strategy is registered
    if strategy not in ORCHESTRATOR_REGISTRY:
        available = ", ".join(ORCHESTRATOR_REGISTRY.keys())
        raise ValueError(
            f"Unknown orchestration strategy: '{strategy}'. "
            f"Available strategies: {available}"
        )
    
    # Get orchestrator class
    orchestrator_class = ORCHESTRATOR_REGISTRY[strategy]
    
    try:
        # Create orchestrator instance
        if config_path:
            orchestrator = orchestrator_class(config_path)
        else:
            orchestrator = orchestrator_class()
        
        logger.info(f"Created {orchestrator_class.__name__} successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to create orchestrator: {e}")
        raise RuntimeError(f"Orchestrator creation failed: {str(e)}")


async def initialize_orchestration_system(
    strategy: str = "simple",
    config_path: str = None,
    config_dict: Dict[str, Any] = None
) -> Orchestrator:
    """
    Initialize complete orchestration system.
    
    This is a convenience function that creates and initializes an orchestrator
    in one step, handling all the setup required for immediate use.
    
    Args:
        strategy: Orchestration strategy to use
        config_path: Optional path to configuration file
        config_dict: Optional configuration dictionary (overrides file)
        
    Returns:
        Initialized orchestrator ready for use
        
    Raises:
        RuntimeError: If initialization fails
    """
    logger.info("Initializing orchestration system")
    
    try:
        # Create orchestrator
        orchestrator = create_orchestrator(strategy, config_path)
        
        # Apply config dict if provided
        if config_dict and hasattr(orchestrator, 'config'):
            orchestrator.config.update(config_dict)
            logger.debug("Applied configuration dictionary")
        
        # Initialize orchestrator
        success = await orchestrator.initialize()
        
        if not success:
            raise RuntimeError("Orchestrator initialization returned False")
        
        logger.info(f"Orchestration system initialized with {strategy} strategy")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to initialize orchestration system: {e}")
        raise RuntimeError(f"Orchestration system initialization failed: {str(e)}")


def register_orchestrator(name: str, orchestrator_class: type) -> None:
    """
    Register a new orchestrator type.
    
    This allows dynamic registration of orchestrator implementations,
    supporting plugin-style extensions without modifying this file.
    
    Args:
        name: Name for the orchestrator strategy
        orchestrator_class: Class implementing Orchestrator interface
        
    Raises:
        ValueError: If name already registered or class invalid
    """
    # Validate name
    if not name or not isinstance(name, str):
        raise ValueError("Orchestrator name must be a non-empty string")
    
    name = name.lower()
    
    # Check if already registered
    if name in ORCHESTRATOR_REGISTRY:
        raise ValueError(f"Orchestrator '{name}' is already registered")
    
    # Validate class
    if not isinstance(orchestrator_class, type):
        raise ValueError("Orchestrator class must be a type")
    
    # Check if it's a subclass of Orchestrator
    if not issubclass(orchestrator_class, Orchestrator):
        raise ValueError("Orchestrator class must inherit from Orchestrator base class")
    
    # Register
    ORCHESTRATOR_REGISTRY[name] = orchestrator_class
    logger.info(f"Registered orchestrator: {name} -> {orchestrator_class.__name__}")


def get_available_strategies() -> Dict[str, str]:
    """
    Get available orchestration strategies.
    
    Returns:
        Dictionary mapping strategy names to class names
    """
    return {
        name: cls.__name__ 
        for name, cls in ORCHESTRATOR_REGISTRY.items()
    }


def load_config_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Supports JSON and YAML formats based on file extension.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file format not supported
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Determine format from extension
    extension = config_path.suffix.lower()
    
    try:
        if extension == '.json':
            import json
            with open(config_path) as f:
                return json.load(f)
                
        elif extension in ['.yml', '.yaml']:
            try:
                import yaml
                with open(config_path) as f:
                    return yaml.safe_load(f)
            except ImportError:
                logger.warning("PyYAML not installed, cannot load YAML config")
                raise ValueError("YAML support requires PyYAML: pip install pyyaml")
                
        else:
            raise ValueError(f"Unsupported configuration format: {extension}")
            
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Example usage patterns for future orchestrators
"""
Future orchestrator implementations can be added easily:

1. Parallel Orchestrator:
   ```python
   class ParallelOrchestrator(Orchestrator):
       # Executes independent steps in parallel
       pass
   
   register_orchestrator("parallel", ParallelOrchestrator)
   ```

2. LLM-Planned Orchestrator:
   ```python
   class LLMPlannedOrchestrator(Orchestrator):
       # Uses LLM to dynamically plan workflows
       pass
   
   register_orchestrator("llm_planned", LLMPlannedOrchestrator)
   ```

3. External Framework Integration:
   ```python
   class LangChainOrchestrator(Orchestrator):
       # Wraps LangChain for orchestration
       pass
   
   register_orchestrator("langchain", LangChainOrchestrator)
   ```

Usage remains the same regardless of implementation:
   ```python
   orchestrator = await initialize_orchestration_system("parallel")
   result = await orchestrator.process_request("Analyze these documents")
   ```
"""