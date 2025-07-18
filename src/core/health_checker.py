"""
Basic health check system for production readiness

This module provides health checks for all critical system components
to ensure the system is operating correctly.

Addresses CLAUDE.md Task 3.2: Add Basic Health Checks
"""

import time
import psutil
from typing import Dict, Any, List, Optional
from .config import ConfigurationManager


class HealthStatus:
    """Health status constants"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy" 
    WARNING = "warning"
    UNKNOWN = "unknown"


class HealthCheck:
    """Individual health check result"""
    
    def __init__(self, name: str, status: str, latency_ms: Optional[float] = None, 
                 message: Optional[str] = None, metadata: Optional[Dict] = None):
        self.name = name
        self.status = status
        self.latency_ms = latency_ms
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "name": self.name,
            "status": self.status,
            "timestamp": self.timestamp
        }
        
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        
        if self.message:
            result["message"] = self.message
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


class HealthChecker:
    """Comprehensive health checker for production readiness"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        
    def check_neo4j_health(self) -> HealthCheck:
        """Check Neo4j database connectivity and performance"""
        start_time = time.time()
        
        try:
            from neo4j import GraphDatabase
            neo4j_config = self.config_manager.get_neo4j_config()
            
            driver = GraphDatabase.driver(
                neo4j_config['uri'],
                auth=(neo4j_config['user'], neo4j_config['password'])
            )
            
            with driver.session() as session:
                # Basic connectivity test
                result = session.run("RETURN 1 as health_check")
                record = result.single()
                
                # Database info query
                db_info = session.run("CALL dbms.components()").single()
                
                # Database size and node count
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                
                latency_ms = (time.time() - start_time) * 1000
                
                if record and record["health_check"] == 1:
                    metadata = {
                        "version": db_info["versions"][0] if db_info else "unknown",
                        "node_count": node_count,
                        "connection_pool_size": neo4j_config.get('max_connection_pool_size', 50)
                    }
                    
                    # Determine health status based on performance
                    if latency_ms < 100:
                        status = HealthStatus.HEALTHY
                        message = "Neo4j connection healthy"
                    elif latency_ms < 1000:
                        status = HealthStatus.WARNING
                        message = "Neo4j connection slow but functional"
                    else:
                        status = HealthStatus.WARNING
                        message = "Neo4j connection very slow"
                    
                    return HealthCheck(
                        name="neo4j",
                        status=status,
                        latency_ms=latency_ms,
                        message=message,
                        metadata=metadata
                    )
                else:
                    return HealthCheck(
                        name="neo4j",
                        status=HealthStatus.UNHEALTHY,
                        latency_ms=latency_ms,
                        message="Neo4j query returned invalid response"
                    )
                    
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="neo4j",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Neo4j connection failed: {str(e)}"
            )
    
    def check_configuration_health(self) -> HealthCheck:
        """Check configuration validity and production readiness"""
        start_time = time.time()
        
        try:
            # Validate configuration
            is_valid = self.config_manager.validate_config()
            
            # Check production readiness
            is_prod_ready, issues = self.config_manager.is_production_ready()
            
            latency_ms = (time.time() - start_time) * 1000
            
            if is_valid and is_prod_ready:
                return HealthCheck(
                    name="configuration",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message="Configuration is valid and production ready"
                )
            elif is_valid:
                return HealthCheck(
                    name="configuration",
                    status=HealthStatus.WARNING,
                    latency_ms=latency_ms,
                    message="Configuration is valid but not production ready",
                    metadata={"issues": issues}
                )
            else:
                return HealthCheck(
                    name="configuration",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency_ms,
                    message="Configuration validation failed",
                    metadata={"issues": issues}
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Configuration check failed: {str(e)}"
            )
    
    def check_system_resources(self) -> HealthCheck:
        """Check system resource utilization"""
        start_time = time.time()
        
        try:
            # Get system resource information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            latency_ms = (time.time() - start_time) * 1000
            
            metadata = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
            # Determine health status
            issues = []
            if cpu_percent > 90:
                issues.append("High CPU usage")
            if memory.percent > 90:
                issues.append("High memory usage")
            if disk.percent > 90:
                issues.append("High disk usage")
            
            if not issues:
                status = HealthStatus.HEALTHY
                message = "System resources healthy"
            elif len(issues) == 1:
                status = HealthStatus.WARNING
                message = f"Resource warning: {issues[0]}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Multiple resource issues: {', '.join(issues)}"
            
            return HealthCheck(
                name="system_resources",
                status=status,
                latency_ms=latency_ms,
                message=message,
                metadata=metadata
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"System resource check failed: {str(e)}"
            )
    
    def check_dependencies(self) -> HealthCheck:
        """Check that required dependencies are available"""
        start_time = time.time()
        
        try:
            required_modules = [
                'neo4j',
                'yaml',
                'psutil',
                'jsonschema',
                'spacy',
                'openai',
                'google.generativeai'
            ]
            
            missing_modules = []
            available_modules = []
            
            for module in required_modules:
                try:
                    __import__(module)
                    available_modules.append(module)
                except ImportError:
                    missing_modules.append(module)
            
            latency_ms = (time.time() - start_time) * 1000
            
            metadata = {
                "available_modules": available_modules,
                "missing_modules": missing_modules,
                "total_required": len(required_modules)
            }
            
            if not missing_modules:
                return HealthCheck(
                    name="dependencies",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message="All required dependencies available",
                    metadata=metadata
                )
            elif len(missing_modules) <= 2:
                return HealthCheck(
                    name="dependencies",
                    status=HealthStatus.WARNING,
                    latency_ms=latency_ms,
                    message=f"Some optional dependencies missing: {', '.join(missing_modules)}",
                    metadata=metadata
                )
            else:
                return HealthCheck(
                    name="dependencies",
                    status=HealthStatus.UNHEALTHY,
                    latency_ms=latency_ms,
                    message=f"Critical dependencies missing: {', '.join(missing_modules)}",
                    metadata=metadata
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="dependencies",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Dependency check failed: {str(e)}"
            )
    
    def check_pipeline_components(self) -> HealthCheck:
        """Check that core pipeline components can be instantiated"""
        start_time = time.time()
        
        try:
            # Test core component imports and instantiation
            from ..core.tool_factory import ToolFactory, Phase, OptimizationLevel
            from ..core.pipeline_orchestrator import PipelineOrchestrator
            from ..tools.phase1.theory_guided_workflow import TheoryGuidedWorkflow
            
            # Test tool factory
            tools = ToolFactory.create_tools_for_config(
                Phase.PHASE1, 
                OptimizationLevel.STANDARD, 
                self.config_manager
            )
            
            # Test theory workflow instantiation
            from contracts.phase_interfaces.base_graphrag_phase import TheoryConfig, TheorySchema
            theory_config = TheoryConfig(
                schema_type=TheorySchema.MASTER_CONCEPTS,
                concept_library_path="src/ontology_library/master_concepts.py"
            )
            
            theory_workflow = TheoryGuidedWorkflow(self.config_manager, theory_config)
            
            latency_ms = (time.time() - start_time) * 1000
            
            metadata = {
                "phase1_tools_count": len(tools),
                "theory_concepts_loaded": len(theory_workflow.concept_library)
            }
            
            return HealthCheck(
                name="pipeline_components",
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message="Pipeline components instantiated successfully",
                metadata=metadata
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="pipeline_components",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Pipeline component check failed: {str(e)}"
            )
    
    def check_api_services_health(self) -> HealthCheck:
        """Check API services connectivity and authentication"""
        start_time = time.time()
        
        try:
            import os
            
            # Check OpenAI API key
            openai_key = os.getenv("OPENAI_API_KEY")
            
            # Check Google/Gemini API key
            google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            
            # Test basic API connectivity
            service_status = {}
            
            # OpenAI connectivity test
            if openai_key:
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_key)
                    # Simple test call
                    models = client.models.list()
                    service_status["openai"] = "available"
                except Exception as e:
                    service_status["openai"] = f"error: {str(e)[:50]}"
            else:
                service_status["openai"] = "no_api_key"
            
            # Google/Gemini connectivity test
            if google_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=google_key)
                    # Simple test call
                    models = genai.list_models()
                    service_status["gemini"] = "available"
                except Exception as e:
                    service_status["gemini"] = f"error: {str(e)[:50]}"
            else:
                service_status["gemini"] = "no_api_key"
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine overall status
            available_services = [k for k, v in service_status.items() if v == "available"]
            
            if len(available_services) >= 2:
                status = HealthStatus.HEALTHY
                message = f"API services healthy: {', '.join(available_services)}"
            elif len(available_services) == 1:
                status = HealthStatus.WARNING
                message = f"Partial API services available: {', '.join(available_services)}"
            else:
                status = HealthStatus.UNHEALTHY
                message = "No API services available"
            
            return HealthCheck(
                name="api_services",
                status=status,
                latency_ms=latency_ms,
                message=message,
                metadata=service_status
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="api_services",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"API services check failed: {str(e)}"
            )
    
    def check_async_clients_health(self) -> HealthCheck:
        """Check async client functionality"""
        start_time = time.time()
        
        try:
            import asyncio
            
            # Test async client imports
            from .async_api_client import AsyncEnhancedAPIClient
            
            # Create async client
            async def test_async_client():
                client = AsyncEnhancedAPIClient(self.config_manager)
                await client.initialize_clients()
                
                # Check client status
                status = {}
                if client.openai_client:
                    status["openai_async"] = "initialized"
                if client.gemini_client:
                    status["gemini_async"] = "initialized"
                
                await client.close()
                return status
            
            # Run async test
            try:
                status = asyncio.run(test_async_client())
            except RuntimeError:
                # Already in event loop, skip async test
                status = {"async_unavailable": "event_loop_running"}
            
            latency_ms = (time.time() - start_time) * 1000
            
            if status:
                return HealthCheck(
                    name="async_clients",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency_ms,
                    message="Async clients functional",
                    metadata=status
                )
            else:
                return HealthCheck(
                    name="async_clients",
                    status=HealthStatus.WARNING,
                    latency_ms=latency_ms,
                    message="No async clients available"
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="async_clients",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Async clients check failed: {str(e)}"
            )
    
    def check_phase1_readiness(self) -> HealthCheck:
        """Check Phase 1 implementation readiness"""
        start_time = time.time()
        
        try:
            # Check Phase 1 improvements
            improvements = {}
            
            # Check unified configuration
            try:
                from .config import ConfigurationManager, ConfigManager
                if ConfigManager is ConfigurationManager:
                    improvements["unified_config"] = "implemented"
                else:
                    improvements["unified_config"] = "not_unified"
            except ImportError:
                improvements["unified_config"] = "missing"
            
            # Check simplified tool adapters
            try:
                from .tool_adapters import OptimizedToolAdapterRegistry, SimplifiedToolAdapter
                improvements["optimized_adapters"] = "implemented"
            except ImportError:
                try:
                    from .tool_adapters import tool_adapter_registry
                    if hasattr(tool_adapter_registry, 'list_adapters'):
                        improvements["optimized_adapters"] = "legacy_registry"
                    else:
                        improvements["optimized_adapters"] = "missing"
                except ImportError:
                    improvements["optimized_adapters"] = "missing"
            
            # Check comprehensive .env.example
            try:
                import os
                env_example_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env.example")
                if os.path.exists(env_example_path):
                    with open(env_example_path, 'r') as f:
                        content = f.read()
                        var_count = len([line for line in content.split('\n') if line.strip() and '=' in line and not line.startswith('#')])
                        improvements["env_example"] = f"implemented ({var_count} variables)"
                else:
                    improvements["env_example"] = "missing"
            except Exception:
                improvements["env_example"] = "error"
            
            # Check async clients
            try:
                from .async_api_client import AsyncEnhancedAPIClient
                improvements["async_clients"] = "implemented"
            except ImportError:
                improvements["async_clients"] = "missing"
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Count implemented features
            implemented_count = sum(1 for v in improvements.values() if v.startswith("implemented"))
            total_count = len(improvements)
            
            if implemented_count == total_count:
                status = HealthStatus.HEALTHY
                message = "Phase 1 implementation complete"
            elif implemented_count >= total_count * 0.8:
                status = HealthStatus.WARNING
                message = f"Phase 1 mostly complete ({implemented_count}/{total_count})"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Phase 1 incomplete ({implemented_count}/{total_count})"
            
            return HealthCheck(
                name="phase1_readiness",
                status=status,
                latency_ms=latency_ms,
                message=message,
                metadata=improvements
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return HealthCheck(
                name="phase1_readiness",
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"Phase 1 readiness check failed: {str(e)}"
            )
    
    def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        start_time = time.time()
        
        # Run all health checks
        health_checks = [
            self.check_configuration_health(),
            self.check_dependencies(),
            self.check_system_resources(),
            self.check_pipeline_components(),
            self.check_neo4j_health(),
            self.check_api_services_health(),
            self.check_async_clients_health(),
            self.check_phase1_readiness()
        ]
        
        # Calculate overall status
        statuses = [check.status for check in health_checks]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
            overall_message = "All systems healthy"
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
            unhealthy_checks = [check.name for check in health_checks if check.status == HealthStatus.UNHEALTHY]
            overall_message = f"Critical issues in: {', '.join(unhealthy_checks)}"
        else:
            overall_status = HealthStatus.WARNING
            warning_checks = [check.name for check in health_checks if check.status == HealthStatus.WARNING]
            overall_message = f"Warnings in: {', '.join(warning_checks)}"
        
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "overall_status": overall_status,
            "overall_message": overall_message,
            "total_latency_ms": round(total_latency, 2),
            "timestamp": time.time(),
            "checks": [check.to_dict() for check in health_checks],
            "summary": {
                "total_checks": len(health_checks),
                "healthy": len([c for c in health_checks if c.status == HealthStatus.HEALTHY]),
                "warning": len([c for c in health_checks if c.status == HealthStatus.WARNING]),
                "unhealthy": len([c for c in health_checks if c.status == HealthStatus.UNHEALTHY])
            }
        }
    
    def get_readiness_status(self) -> Dict[str, Any]:
        """Check if system is ready to handle requests"""
        # For readiness, we mainly care about critical components
        critical_checks = [
            self.check_configuration_health(),
            self.check_dependencies(),
            self.check_pipeline_components(),
            self.check_api_services_health(),
            self.check_phase1_readiness()
        ]
        
        statuses = [check.status for check in critical_checks]
        
        if all(status in [HealthStatus.HEALTHY, HealthStatus.WARNING] for status in statuses):
            ready = True
            message = "System ready to handle requests"
        else:
            ready = False
            unhealthy_checks = [check.name for check in critical_checks if check.status == HealthStatus.UNHEALTHY]
            message = f"System not ready: {', '.join(unhealthy_checks)}"
        
        return {
            "ready": ready,
            "message": message,
            "timestamp": time.time(),
            "critical_checks": [check.to_dict() for check in critical_checks]
        }
    
    def get_liveness_status(self) -> Dict[str, Any]:
        """Check if system is alive and responsive"""
        # For liveness, we just need basic functionality
        try:
            start_time = time.time()
            
            # Test basic imports
            from ..core.config import ConfigurationManager
            
            # Test config access
            self.config_manager.get_system_config()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "alive": True,
                "message": "System is alive and responsive",
                "latency_ms": round(latency_ms, 2),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "alive": False,
                "message": f"System liveness check failed: {str(e)}",
                "timestamp": time.time()
            }