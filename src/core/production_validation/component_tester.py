"""
Component Testing Components

Comprehensive testing for individual system components.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from .data_models import ComponentTestResult, ComponentStatus

logger = logging.getLogger(__name__)


class ComponentTester(ABC):
    """Base class for component testing"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def test_component(self) -> ComponentTestResult:
        """Test component and return results"""
        pass
    
    def _measure_response_time(self, operation_func, *args, **kwargs) -> float:
        """Measure response time of an operation"""
        start_time = time.time()
        try:
            result = operation_func(*args, **kwargs)
            return time.time() - start_time
        except Exception:
            return time.time() - start_time


class DatabaseComponentTester(ComponentTester):
    """Test database component functionality"""
    
    async def test_component(self) -> ComponentTestResult:
        """Test database component with connectivity and stability checks"""
        component_name = "database"
        start_time = time.time()
        
        try:
            # Test database availability and connectivity
            stability_result = await self._test_database_connectivity_with_stability()
            response_time = time.time() - start_time
            
            if stability_result["status"] == "working":
                status = ComponentStatus.WORKING
                stability_score = stability_result["stability_score"]
                error_message = None
            elif stability_result["status"] == "unstable":
                status = ComponentStatus.UNSTABLE
                stability_score = stability_result["stability_score"]
                error_message = "Database connection unstable"
            else:
                status = ComponentStatus.FAILED
                stability_score = 0.0
                error_message = stability_result.get("error", "Database connection failed")
            
            return ComponentTestResult(
                component_name=component_name,
                status=status,
                stability_score=stability_score,
                response_time=response_time,
                error_message=error_message,
                metadata=stability_result
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Database component test failed: {e}")
            
            return ComponentTestResult(
                component_name=component_name,
                status=ComponentStatus.FAILED,
                stability_score=0.0,
                response_time=response_time,
                error_message=str(e)
            )
    
    async def _test_database_connectivity_with_stability(self) -> Dict[str, Any]:
        """Test database connectivity with stability checks"""
        try:
            from src.core.neo4j_manager import Neo4jDockerManager
            neo4j_manager = Neo4jDockerManager()
            
            # Test connection multiple times for stability
            successful_tests = 0
            total_tests = 5
            
            for i in range(total_tests):
                try:
                    with neo4j_manager.get_session() as session:
                        result = session.run("RETURN 1 as test")
                        if result.single()["test"] == 1:
                            successful_tests += 1
                except Exception:
                    pass
                
                await asyncio.sleep(0.1)
            
            stability_score = successful_tests / total_tests
            
            return {
                "status": "working" if stability_score >= 0.8 else "unstable",
                "stability_score": stability_score,
                "successful_tests": successful_tests,
                "total_tests": total_tests
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "stability_score": 0.0,
                "error": str(e)
            }


class ToolComponentTester(ComponentTester):
    """Test tool component functionality"""
    
    async def test_component(self) -> ComponentTestResult:
        """Test tool functionality and availability"""
        component_name = "tools"
        start_time = time.time()
        
        try:
            from src.core.tool_factory import ToolFactory
            tool_factory = ToolFactory()
            
            # Test tool availability
            available_tools = tool_factory.get_available_tools()
            tool_count = len(available_tools)
            
            if tool_count == 0:
                response_time = time.time() - start_time
                return ComponentTestResult(
                    component_name=component_name,
                    status=ComponentStatus.FAILED,
                    stability_score=0.0,
                    response_time=response_time,
                    error_message="No tools available",
                    metadata={"tool_count": 0}
                )
            
            # Test tool creation
            successful_creations = 0
            total_tools = min(3, tool_count)  # Test up to 3 tools
            
            for tool_name in list(available_tools.keys())[:total_tools]:
                try:
                    tool_instance = tool_factory.create_tool(tool_name)
                    if tool_instance and hasattr(tool_instance, 'get_tool_info'):
                        tool_info = tool_instance.get_tool_info()
                        if isinstance(tool_info, dict):
                            successful_creations += 1
                except Exception as e:
                    self.logger.warning(f"Tool {tool_name} creation failed: {e}")
            
            response_time = time.time() - start_time
            stability_score = successful_creations / total_tools if total_tools > 0 else 0.0
            
            if stability_score >= 0.8:
                status = ComponentStatus.WORKING
            elif stability_score >= 0.5:
                status = ComponentStatus.UNSTABLE
            else:
                status = ComponentStatus.FAILED
            
            return ComponentTestResult(
                component_name=component_name,
                status=status,
                stability_score=stability_score,
                response_time=response_time,
                metadata={
                    "tool_count": tool_count,
                    "successful_creations": successful_creations,
                    "total_tested": total_tools
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Tool component test failed: {e}")
            
            return ComponentTestResult(
                component_name=component_name,
                status=ComponentStatus.FAILED,
                stability_score=0.0,
                response_time=response_time,
                error_message=str(e)
            )


class ServiceComponentTester(ComponentTester):
    """Test core service components"""
    
    def __init__(self):
        super().__init__()
        self.services_to_test = [
            "config_manager",
            "evidence_logger",
            "quality_service",
            "ontology_validator"
        ]
    
    async def test_component(self) -> ComponentTestResult:
        """Test core services functionality"""
        component_name = "services"
        start_time = time.time()
        
        service_results = {}
        successful_services = 0
        
        for service_name in self.services_to_test:
            try:
                service_result = await self._test_individual_service(service_name)
                service_results[service_name] = service_result
                if service_result.get("status") == "working":
                    successful_services += 1
            except Exception as e:
                service_results[service_name] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        response_time = time.time() - start_time
        total_services = len(self.services_to_test)
        stability_score = successful_services / total_services if total_services > 0 else 0.0
        
        if stability_score >= 0.8:
            status = ComponentStatus.WORKING
        elif stability_score >= 0.5:
            status = ComponentStatus.UNSTABLE
        else:
            status = ComponentStatus.FAILED
        
        return ComponentTestResult(
            component_name=component_name,
            status=status,
            stability_score=stability_score,
            response_time=response_time,
            metadata={
                "service_results": service_results,
                "successful_services": successful_services,
                "total_services": total_services
            }
        )
    
    async def _test_individual_service(self, service_name: str) -> Dict[str, Any]:
        """Test individual service"""
        try:
            if service_name == "config_manager":
                return await self._test_config_manager()
            elif service_name == "evidence_logger":
                return await self._test_evidence_logger()
            elif service_name == "quality_service":
                return await self._test_quality_service()
            elif service_name == "ontology_validator":
                return await self._test_ontology_validator()
            else:
                return {"status": "failed", "error": f"Unknown service: {service_name}"}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_config_manager(self) -> Dict[str, Any]:
        """Test configuration manager"""
        try:
            from src.core.config_manager import get_config
            config = get_config()
            
            if hasattr(config, 'get_config'):
                return {"status": "working", "info": "Config manager available"}
            else:
                return {"status": "failed", "error": "Config manager missing required methods"}
                
        except ImportError:
            return {"status": "failed", "error": "Config manager not available"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_evidence_logger(self) -> Dict[str, Any]:
        """Test evidence logger service"""
        try:
            from src.core.evidence_logger import EvidenceLogger
            logger = EvidenceLogger()
            
            if hasattr(logger, 'log_evidence'):
                return {"status": "working", "info": "Evidence logger available"}
            else:
                return {"status": "failed", "error": "Evidence logger missing required methods"}
                
        except ImportError:
            return {"status": "failed", "error": "Evidence logger not available"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_quality_service(self) -> Dict[str, Any]:
        """Test quality service"""
        try:
            from src.core.quality_service import QualityService
            service = QualityService()
            
            if hasattr(service, 'calculate_confidence'):
                return {"status": "working", "info": "Quality service available"}
            else:
                return {"status": "failed", "error": "Quality service missing required methods"}
                
        except ImportError:
            return {"status": "failed", "error": "Quality service not available"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_ontology_validator(self) -> Dict[str, Any]:
        """Test ontology validator service"""
        try:
            from src.core.ontology_validator import OntologyValidator
            validator = OntologyValidator()
            
            if hasattr(validator, 'validate_entity'):
                return {"status": "working", "info": "Ontology validator available"}
            else:
                return {"status": "failed", "error": "Ontology validator missing required methods"}
                
        except ImportError:
            return {"status": "failed", "error": "Ontology validator not available"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}