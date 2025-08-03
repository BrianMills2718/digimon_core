"""
Dependency Checking Components

Comprehensive dependency validation for production readiness.
"""

import logging
import time
from typing import Dict, Any, List
from abc import ABC, abstractmethod

from .data_models import DependencyCheckResult

logger = logging.getLogger(__name__)


class DependencyChecker(ABC):
    """Base class for dependency checking"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_dependency(self) -> DependencyCheckResult:
        """Check dependency availability"""
        pass


class Neo4jDependencyChecker(DependencyChecker):
    """Check Neo4j database dependency"""
    
    def check_dependency(self) -> DependencyCheckResult:
        """Check Neo4j manager availability"""
        start_time = time.time()
        
        try:
            from src.core.neo4j_manager import Neo4jDockerManager
            
            # Try to create manager instance
            manager = Neo4jDockerManager()
            
            # Test basic connectivity
            with manager.get_session() as session:
                result = session.run("RETURN 1 as test")
                test_result = result.single()
                
                if test_result["test"] == 1:
                    check_time = time.time() - start_time
                    return DependencyCheckResult(
                        dependency_name="neo4j_manager",
                        available=True,
                        version="4.x",
                        check_time=check_time
                    )
                else:
                    check_time = time.time() - start_time
                    return DependencyCheckResult(
                        dependency_name="neo4j_manager",
                        available=False,
                        error_message="Neo4j query test failed",
                        check_time=check_time
                    )
            
        except ImportError as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="neo4j_manager",
                available=False,
                error_message=f"Import failed: {str(e)}",
                check_time=check_time
            )
        except Exception as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="neo4j_manager",
                available=False,
                error_message=f"Connection failed: {str(e)}",
                check_time=check_time
            )


class ToolFactoryDependencyChecker(DependencyChecker):
    """Check tool factory dependency"""
    
    def check_dependency(self) -> DependencyCheckResult:
        """Check tool factory availability"""
        start_time = time.time()
        
        try:
            from src.core.tool_factory import ToolFactory
            
            # Try to create factory instance
            factory = ToolFactory()
            
            # Test basic functionality
            if hasattr(factory, 'get_available_tools'):
                available_tools = factory.get_available_tools()
                tool_count = len(available_tools) if available_tools else 0
                
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="tool_factory",
                    available=True,
                    version=f"tools_available_{tool_count}",
                    check_time=check_time
                )
            else:
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="tool_factory",
                    available=False,
                    error_message="Tool factory missing required methods",
                    check_time=check_time
                )
            
        except ImportError as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="tool_factory",
                available=False,
                error_message=f"Import failed: {str(e)}",
                check_time=check_time
            )
        except Exception as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="tool_factory",
                available=False,
                error_message=f"Initialization failed: {str(e)}",
                check_time=check_time
            )


class ConfigManagerDependencyChecker(DependencyChecker):
    """Check configuration manager dependency"""
    
    def check_dependency(self) -> DependencyCheckResult:
        """Check config manager availability"""
        start_time = time.time()
        
        try:
            from src.core.config_manager import get_config
            
            # Try to get config instance
            config = get_config()
            
            # Test basic functionality
            if hasattr(config, 'get_config'):
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="config_manager",
                    available=True,
                    version="1.0",
                    check_time=check_time
                )
            else:
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="config_manager",
                    available=False,
                    error_message="Config manager missing required methods",
                    check_time=check_time
                )
            
        except ImportError as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="config_manager",
                available=False,
                error_message=f"Import failed: {str(e)}",
                check_time=check_time
            )
        except Exception as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="config_manager",
                available=False,
                error_message=f"Initialization failed: {str(e)}",
                check_time=check_time
            )


class EvidenceLoggerDependencyChecker(DependencyChecker):
    """Check evidence logger dependency"""
    
    def check_dependency(self) -> DependencyCheckResult:
        """Check evidence logger availability"""
        start_time = time.time()
        
        try:
            from src.core.evidence_logger import EvidenceLogger
            
            # Try to create logger instance
            logger = EvidenceLogger()
            
            # Test basic functionality
            if hasattr(logger, 'log_evidence'):
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="evidence_logger",
                    available=True,
                    version="1.0",
                    check_time=check_time
                )
            else:
                check_time = time.time() - start_time
                return DependencyCheckResult(
                    dependency_name="evidence_logger",
                    available=False,
                    error_message="Evidence logger missing required methods",
                    check_time=check_time
                )
            
        except ImportError as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="evidence_logger",
                available=False,
                error_message=f"Import failed: {str(e)}",
                check_time=check_time
            )
        except Exception as e:
            check_time = time.time() - start_time
            return DependencyCheckResult(
                dependency_name="evidence_logger",
                available=False,
                error_message=f"Initialization failed: {str(e)}",
                check_time=check_time
            )


class ComprehensiveDependencyChecker:
    """Comprehensive dependency checking orchestrator"""
    
    def __init__(self):
        self.dependency_checkers = {
            "neo4j_manager": Neo4jDependencyChecker(),
            "tool_factory": ToolFactoryDependencyChecker(),
            "config_manager": ConfigManagerDependencyChecker(),
            "evidence_logger": EvidenceLoggerDependencyChecker()
        }
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def check_all_dependencies(self) -> Dict[str, Any]:
        """Check all dependencies and return comprehensive results"""
        dependency_results = {}
        all_available = True
        missing_dependencies = []
        
        self.logger.info("Checking all system dependencies")
        
        for name, checker in self.dependency_checkers.items():
            try:
                result = checker.check_dependency()
                dependency_results[name] = result
                
                if not result.available:
                    all_available = False
                    missing_dependencies.append(f"{name}: {result.error_message}")
                    
            except Exception as e:
                self.logger.error(f"Dependency check failed for {name}: {e}")
                dependency_results[name] = DependencyCheckResult(
                    dependency_name=name,
                    available=False,
                    error_message=f"Check failed: {str(e)}"
                )
                all_available = False
                missing_dependencies.append(f"{name}: Check failed - {str(e)}")
        
        return {
            "dependency_results": dependency_results,
            "all_dependencies_available": all_available,
            "missing_dependencies": missing_dependencies,
            "total_dependencies": len(self.dependency_checkers),
            "available_count": sum(1 for result in dependency_results.values() if result.available)
        }