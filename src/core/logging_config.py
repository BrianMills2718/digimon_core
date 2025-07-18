"""Centralized Logging Configuration - Priority 2 Critical Implementation
Replaces logger.info() statements with proper structured logging.

CRITICAL-3 IMPLEMENTATION: Addresses the 20+ instances of logger.info() statements
identified in the comprehensive analysis that create inconsistent error tracking.

This module provides:
- Centralized logging configuration for all components
- File and console logging with proper formatting
- Logger factory with consistent naming convention
- Support for different log levels and output formats
"""

import logging
import logging.config
from typing import Dict, Any, Optional
from pathlib import Path
import os


def setup_logging(
    log_level: str = "INFO", 
    log_file: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True
) -> None:
    """Setup centralized logging configuration for the entire system
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path (defaults to logs/super_digimon.log)
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file
    """
    
    # Default log file location
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "super_digimon.log"
    
    # Ensure log directory exists
    if isinstance(log_file, str):
        log_file = Path(log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Base configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "[%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {},
        "loggers": {
            "super_digimon": {
                "level": log_level,
                "handlers": [],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": []
        }
    }
    
    # Add console handler if requested
    if console_output:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        }
        config["loggers"]["super_digimon"]["handlers"].append("console")
        config["root"]["handlers"].append("console")
    
    # Add file handler if requested
    if file_output and log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file),
            "mode": "a",
            "encoding": "utf-8"
        }
        config["loggers"]["super_digimon"]["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    # Add rotating file handler for production use
    if file_output and log_file:
        config["handlers"]["rotating_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file.with_suffix(".rotating.log")),
            "mode": "a",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        }
        # Note: Not adding to default loggers, can be used explicitly
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log the configuration setup
    logger = get_logger("core.logging")
    logger.info("Logging system initialized - Level: %s, Console: %s, File: %s", 
                log_level, console_output, log_file if file_output else "None")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the super_digimon namespace
    
    Args:
        name: Logger name (will be prefixed with 'super_digimon.')
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger("phase1.workflow")
        # Creates logger named "super_digimon.phase1.workflow"
    """
    return logging.getLogger(f"super_digimon.{name}")


def setup_component_loggers():
    """Setup specific loggers for different system components
    
    This creates specialized loggers for different parts of the system
    with appropriate log levels and formatting.
    """
    # Component-specific logger configurations
    component_configs = {
        "super_digimon.core": {"level": "INFO"},
        "super_digimon.tools.phase1": {"level": "INFO"},
        "super_digimon.tools.phase2": {"level": "INFO"},
        "super_digimon.tools.phase3": {"level": "INFO"},
        "super_digimon.workflows": {"level": "INFO"},
        "super_digimon.services": {"level": "DEBUG"},  # More verbose for services
        "super_digimon.neo4j": {"level": "WARNING"},   # Neo4j can be chatty
        "super_digimon.orchestrator": {"level": "INFO"},
    }
    
    for logger_name, config in component_configs.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(config["level"])


# Auto-initialize logging with sensible defaults
def auto_setup_logging():
    """Automatically setup logging with environment-based configuration"""
    
    # Check for environment variable configuration
    log_level = os.getenv("SUPER_DIGIMON_LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("SUPER_DIGIMON_LOG_FILE")
    console_output = os.getenv("SUPER_DIGIMON_LOG_CONSOLE", "true").lower() == "true"
    file_output = os.getenv("SUPER_DIGIMON_LOG_FILE_ENABLED", "true").lower() == "true"
    
    # Setup with environment configuration
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        console_output=console_output,
        file_output=file_output
    )
    
    # Setup component loggers
    setup_component_loggers()


# Convenience functions for common logging patterns
def log_operation_start(logger: logging.Logger, operation: str, **kwargs):
    """Log the start of an operation with context"""
    context = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info("Starting %s%s", operation, f" ({context})" if context else "")


def log_operation_end(logger: logging.Logger, operation: str, duration: float, success: bool = True, **kwargs):
    """Log the completion of an operation with timing"""
    status = "completed" if success else "failed"
    context = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info("%s %s in %.2fs%s", operation.capitalize(), status, duration, 
                f" ({context})" if context else "")


def log_tool_execution(logger: logging.Logger, tool_name: str, input_summary: str, success: bool, duration: float, error: str = None):
    """Log tool execution with standardized format"""
    if success:
        logger.info("Tool %s executed successfully in %.2fs - %s", tool_name, duration, input_summary)
    else:
        logger.error("Tool %s failed after %.2fs - %s - Error: %s", tool_name, duration, input_summary, error)


class LoggingConfigManager:
    """Wrapper class to make logging_config discoverable by audit system"""
    
    def __init__(self):
        self.tool_id = "LOGGING_CONFIG"
        self._logging_setup = False
        self._initialize_logging()
    
    def _initialize_logging(self):
        """Initialize the logging system"""
        try:
            auto_setup_logging()
            self._logging_setup = True
        except Exception as e:
            # Fallback to basic logging if auto-setup fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            basic_logger = logging.getLogger("super_digimon.logging_fallback")
            basic_logger.warning("Auto logging setup failed, using basic configuration: %s", str(e))
            self._logging_setup = False
    
    def get_tool_info(self):
        """Return tool information for audit system"""
        return {
            "tool_id": self.tool_id,
            "tool_type": "LOGGING_MANAGER",
            "status": "functional" if self._logging_setup else "basic",
            "description": "Centralized logging configuration manager",
            "logging_setup": self._logging_setup
        }
    
    def get_logger(self, name: str) -> logging.Logger:
        """Wrapper for get_logger function"""
        return get_logger(name)
    
    def setup_logging(self, **kwargs):
        """Wrapper for setup_logging function"""
        return setup_logging(**kwargs)
    
    def is_logging_configured(self):
        """Check if logging is properly configured"""
        return self._logging_setup


# Initialize logging system when module is imported
# This ensures logging is available immediately
_logging_manager = LoggingConfigManager()