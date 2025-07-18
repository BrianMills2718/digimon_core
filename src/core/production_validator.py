import logging
import time
import uuid
from typing import Dict, Any, List
from datetime import datetime

class ProductionValidator:
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        # CRITICAL: Ensure neo4j_manager is properly initialized
        self.neo4j_manager = None
        
    def validate_production_readiness(self) -> Dict[str, Any]:
        """Validate production readiness with mandatory stability gating"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validation_id": str(uuid.uuid4()),
            "dependency_checks": {},
            "stability_tests": {},
            "component_tests": {},
            "readiness_percentage": 0.0,
            "overall_status": "failed",
            "critical_issues": [],
            "recommendations": [],
            "stability_gate_passed": False
        }
        
        # CRITICAL: Check all dependencies first
        dependency_results = self._check_all_dependencies()
        validation_results["dependency_checks"] = dependency_results
        
        if not dependency_results["all_dependencies_available"]:
            validation_results["critical_issues"].extend(dependency_results["missing_dependencies"])
            validation_results["recommendations"].append("Fix missing dependencies before proceeding")
            return validation_results
        
        # MANDATORY: Run stability tests with enforcement
        stability_results = self._run_stability_tests()
        validation_results["stability_tests"] = stability_results
        
        # ENFORCE 80% stability threshold
        overall_stability = stability_results.get("overall_stability", 0.0)
        stability_gate_passed = overall_stability >= 0.80
        validation_results["stability_gate_passed"] = stability_gate_passed
        
        if not stability_gate_passed:
            validation_results["critical_issues"].append(
                f"Stability gate FAILED: {overall_stability:.1%} < 80% threshold"
            )
            validation_results["recommendations"].extend([
                "System stability insufficient for production deployment",
                "Address database connectivity issues",
                "Fix tool consistency problems",
                "Resolve memory stability issues"
            ])
            validation_results["overall_status"] = "stability_failed"
            return validation_results
        
        # Only test components if stability gate passes
        component_results = self._test_all_components()
        validation_results["component_tests"] = component_results
        
        # Calculate readiness based on actual component health
        validation_results["readiness_percentage"] = self._calculate_readiness(component_results)
        
        # Set status based on realistic thresholds
        readiness = validation_results["readiness_percentage"]
        if readiness >= 95:
            validation_results["overall_status"] = "production_ready"
        elif readiness >= 85:
            validation_results["overall_status"] = "near_production"
        elif readiness >= 70:
            validation_results["overall_status"] = "development_ready"
        else:
            validation_results["overall_status"] = "development"
        
        return validation_results

    def _run_stability_tests(self) -> Dict[str, Any]:
        """Test system stability over multiple iterations"""
        stability_results = {
            "database_stability": self._test_database_stability(),
            "tool_consistency": self._test_tool_consistency(),
            "memory_stability": self._test_memory_stability(),
            "overall_stability": 0.0
        }
        
        # Calculate overall stability score
        scores = [result.get("stability_score", 0.0) for result in stability_results.values() if isinstance(result, dict)]
        stability_results["overall_stability"] = sum(scores) / len(scores) if scores else 0.0
        
        return stability_results

    def _test_database_stability(self) -> Dict[str, Any]:
        """Test database connection stability with comprehensive validation"""
        stability_tests = 50  # Increased from 20 for better reliability
        successful_connections = 0
        connection_times = []
        error_patterns = {}
        performance_metrics = []
        
        self.logger.info(f"Starting comprehensive database stability test with {stability_tests} iterations")
        
        for attempt in range(stability_tests):
            try:
                start_time = time.time()
                
                # Test full connection lifecycle with multiple operations
                from src.core.neo4j_manager import Neo4jDockerManager
                neo4j_manager = Neo4jDockerManager()
                
                # Test 1: Connection acquisition
                session = neo4j_manager.get_session()
                connection_acquired_time = time.time() - start_time
                
                # Test 2: Basic query execution
                with session:
                    result = session.run("RETURN 1 as test, $timestamp as ts", 
                                       timestamp=datetime.now().isoformat())
                    record = result.single()
                    
                    if record["test"] != 1:
                        raise ValueError(f"Database query returned incorrect result: {record['test']}")
                    
                    query_time = time.time() - start_time
                    
                    # Test 3: Write capability with verification
                    test_id = str(uuid.uuid4())
                    session.run("CREATE (n:StabilityTest {id: $id, attempt: $attempt}) RETURN n.id as created_id",
                               id=test_id, attempt=attempt)
                    
                    # Test 4: Read verification
                    verify_result = session.run("MATCH (n:StabilityTest {id: $id}) RETURN n.id as found_id", 
                                              id=test_id)
                    found_record = verify_result.single()
                    
                    if found_record["found_id"] != test_id:
                        raise ValueError(f"Write verification failed: {found_record['found_id']} != {test_id}")
                    
                    # Test 5: Cleanup
                    session.run("MATCH (n:StabilityTest {id: $id}) DELETE n", id=test_id)
                    
                    write_time = time.time() - start_time
                
                total_time = time.time() - start_time
                connection_times.append(total_time)
                
                performance_metrics.append({
                    "attempt": attempt + 1,
                    "connection_time": connection_acquired_time,
                    "query_time": query_time,
                    "write_time": write_time,
                    "total_time": total_time
                })
                
                successful_connections += 1
                
            except Exception as e:
                error_type = type(e).__name__
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
                self.logger.warning(f"Database stability test {attempt + 1} failed: {e}")
            
            # Brief delay between attempts for realistic testing
            time.sleep(0.1)
        
        # Calculate comprehensive stability metrics
        stability_score = successful_connections / stability_tests
        avg_connection_time = sum(connection_times) / len(connection_times) if connection_times else float('inf')
        max_connection_time = max(connection_times) if connection_times else float('inf')
        min_connection_time = min(connection_times) if connection_times else float('inf')
        connection_variance = self._calculate_variance(connection_times) if connection_times else float('inf')
        
        # Determine stability classification with strict thresholds
        if stability_score >= 0.98:  # 98% minimum for excellent
            stability_class = "excellent"
        elif stability_score >= 0.95:  # 95% minimum for good
            stability_class = "good"
        elif stability_score >= 0.90:  # 90% minimum for acceptable
            stability_class = "acceptable"
        elif stability_score >= 0.80:  # 80% minimum threshold
            stability_class = "marginal"
        else:
            stability_class = "poor"
        
        stability_results = {
            "successful_connections": successful_connections,
            "total_attempts": stability_tests,
            "stability_score": stability_score,
            "stability_class": stability_class,
            "performance_metrics": {
                "average_connection_time": avg_connection_time,
                "max_connection_time": max_connection_time,
                "min_connection_time": min_connection_time,
                "connection_time_variance": connection_variance
            },
            "error_analysis": {
                "error_patterns": error_patterns,
                "total_errors": stability_tests - successful_connections,
                "error_rate": (stability_tests - successful_connections) / stability_tests
            },
            "detailed_performance": performance_metrics,
            "meets_threshold": stability_score >= 0.80,
            "meets_production_threshold": stability_score >= 0.95
        }
        
        self.logger.info(f"Database stability test completed: {stability_score:.1%} success rate ({stability_class})")
        return stability_results

    def _test_tool_consistency(self) -> Dict[str, Any]:
        """Test tool auditing consistency over multiple runs"""
        consistency_runs = 5
        run_results = []
        
        for run in range(consistency_runs):
            try:
                from src.core.tool_factory import ToolFactory
                factory = ToolFactory()
                
                # Run audit with environment capture
                audit_result = factory.audit_all_tools()
                
                run_results.append({
                    "run_number": run + 1,
                    "total_tools": audit_result.get("total_tools", 0),
                    "working_tools": audit_result.get("working_tools", 0),
                    "success_rate": (audit_result.get("working_tools", 0) / 
                                   max(audit_result.get("total_tools", 1), 1)) * 100,
                    "environment_stable": audit_result.get("consistency_metrics", {}).get("environment_stability", False),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                run_results.append({
                    "run_number": run + 1,
                    "error": str(e),
                    "success_rate": 0,
                    "timestamp": datetime.now().isoformat()
                })
            
            time.sleep(1.0)  # Delay between runs
        
        # Calculate consistency metrics
        success_rates = [r.get("success_rate", 0) for r in run_results if "error" not in r]
        
        if success_rates:
            avg_success_rate = sum(success_rates) / len(success_rates)
            success_variance = self._calculate_variance(success_rates)
            max_deviation = max(abs(rate - avg_success_rate) for rate in success_rates)
            
            # Consistency criteria: variance < 5% and max deviation < 10%
            is_consistent = success_variance < 25 and max_deviation < 10
        else:
            avg_success_rate = 0
            success_variance = float('inf')
            max_deviation = float('inf')
            is_consistent = False
        
        return {
            "runs_completed": len([r for r in run_results if "error" not in r]),
            "total_runs": consistency_runs,
            "run_results": run_results,
            "average_success_rate": avg_success_rate,
            "success_rate_variance": success_variance,
            "max_deviation": max_deviation,
            "is_consistent": is_consistent,
            "stability_score": 0.8 if is_consistent else 0.0
        }

    def _test_memory_stability(self) -> Dict[str, Any]:
        """Monitor memory usage during operations"""
        import psutil
        import gc
        
        # Baseline memory measurement
        gc.collect()
        initial_memory = psutil.virtual_memory()
        process = psutil.Process()
        initial_process_memory = process.memory_info()
        
        memory_samples = []
        operations = 10
        
        for i in range(operations):
            # Perform memory-intensive operations
            try:
                # Tool auditing
                from src.core.tool_factory import ToolFactory
                factory = ToolFactory()
                audit = factory.audit_all_tools()
                
                # Database operations
                from src.core.neo4j_manager import Neo4jDockerManager
                neo4j = Neo4jDockerManager()
                with neo4j.get_session() as session:
                    session.run("MATCH (n) RETURN count(n) LIMIT 1")
                
                # Memory measurement
                current_memory = psutil.virtual_memory()
                current_process_memory = process.memory_info()
                
                memory_samples.append({
                    "operation": i + 1,
                    "system_memory_percent": current_memory.percent,
                    "system_memory_available": current_memory.available,
                    "process_memory_rss": current_process_memory.rss,
                    "process_memory_vms": current_process_memory.vms,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                memory_samples.append({
                    "operation": i + 1,
                    "error": str(e),
                    "timestamp": time.time()
                })
            
            time.sleep(0.5)
        
        # Final memory measurement
        gc.collect()
        final_memory = psutil.virtual_memory()
        final_process_memory = process.memory_info()
        
        # Calculate memory stability metrics
        successful_samples = [s for s in memory_samples if "error" not in s]
        
        if successful_samples:
            memory_growth = (final_process_memory.rss - initial_process_memory.rss) / 1024 / 1024  # MB
            max_memory_usage = max(s["process_memory_rss"] for s in successful_samples) / 1024 / 1024  # MB
            
            # Stability criteria: < 100MB growth and < 1GB peak usage
            is_stable = memory_growth < 100 and max_memory_usage < 1024
            stability_score = max(0.0, 1.0 - (memory_growth / 100) - (max_memory_usage / 1024))
        else:
            memory_growth = float('inf')
            max_memory_usage = float('inf')
            is_stable = False
            stability_score = 0.0
        
        return {
            "initial_memory": {
                "system_percent": initial_memory.percent,
                "system_available": initial_memory.available,
                "process_rss": initial_process_memory.rss,
                "process_vms": initial_process_memory.vms
            },
            "final_memory": {
                "system_percent": final_memory.percent,
                "system_available": final_memory.available,
                "process_rss": final_process_memory.rss,
                "process_vms": final_process_memory.vms
            },
            "memory_samples": memory_samples,
            "memory_growth_mb": memory_growth,
            "max_memory_usage_mb": max_memory_usage,
            "is_stable": is_stable,
            "stability_score": min(stability_score, 1.0)
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance

    def _test_all_components(self) -> Dict[str, Any]:
        """Test all system components"""
        return {
            "database": self._test_database_connectivity(),
            "tools": self._test_tool_functionality(),
            "services": self._test_core_services(),
            "configuration": self._test_configuration_system()
        }

    def _calculate_stable_readiness(self, stability_results: Dict[str, Any], component_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate production readiness based on stable metrics"""
        # Weight stability heavily in the calculation
        stability_weight = 0.4
        component_weight = 0.6
        
        # Calculate component readiness
        component_readiness = self._calculate_readiness(component_results)
        
        # Calculate stability readiness
        stability_readiness = stability_results["overall_stability"] * 100
        
        # Combined readiness score
        overall_readiness = (stability_weight * stability_readiness) + (component_weight * component_readiness)
        
        # Determine status
        if overall_readiness >= 85:
            status = "production_ready"
        elif overall_readiness >= 70:
            status = "near_production"
        else:
            status = "development"
        
        return {
            "readiness_percentage": overall_readiness,
            "overall_status": status,
            "stability_contribution": stability_readiness,
            "component_contribution": component_readiness
        }
        
    def _test_database_connectivity(self) -> Dict[str, Any]:
        """Test ACTUAL Neo4j database connectivity and operations"""
        try:
            from src.core.neo4j_manager import Neo4jManager
            neo4j_manager = Neo4jManager()
            
            # Test actual connection with real query
            with neo4j_manager.get_session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                # Test actual write operation
                session.run("CREATE (n:ProductionTest {timestamp: $timestamp})", 
                           timestamp=str(datetime.now()))
                
                # Test actual read operation
                read_result = session.run("MATCH (n:ProductionTest) RETURN count(n) as count")
                count = read_result.single()["count"]
                
                # Clean up
                session.run("MATCH (n:ProductionTest) DELETE n")
                
            return {
                "status": "working",
                "connection": True,
                "write_test": True,
                "read_test": True,
                "test_count": count
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
            
    def _test_tool_functionality(self) -> Dict[str, Any]:
        """Test ACTUAL tool discovery and functionality - NO MOCKS"""
        try:
            from src.core.tool_factory import ToolFactory
            tool_factory = ToolFactory()
            audit_results = tool_factory.audit_all_tools()
            success_rate = tool_factory.get_success_rate()
            
            # Additional real functionality tests
            tool_instantiation_tests = {}
            for tool_name, tool_info in tool_factory.discovered_tools.items():
                if "classes" in tool_info:
                    try:
                        # Actually instantiate and test each tool
                        for tool_class in tool_info["classes"]:
                            instance = tool_class()
                            # Test that execute method signature is valid
                            import inspect
                            sig = inspect.signature(instance.execute)
                            tool_instantiation_tests[f"{tool_name}.{tool_class.__name__}"] = "working"
                    except Exception as e:
                        tool_instantiation_tests[tool_name] = f"failed: {str(e)}"
            
            return {
                "status": "working" if success_rate >= 60 else "failed",
                "success_rate": success_rate,
                "total_tools": audit_results["total_tools"],
                "working_tools": audit_results["working_tools"],
                "broken_tools": audit_results["broken_tools"],
                "instantiation_tests": tool_instantiation_tests
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
            
    def _test_core_services(self) -> Dict[str, Any]:
        """Test ACTUAL core service functionality"""
        services = {
            "evidence_logger": self._test_evidence_logger_service(),
            "quality_service": self._test_quality_service(),
            "ontology_validator": self._test_ontology_validator_service()
        }
        
        working_services = sum(1 for s in services.values() if s.get("status") == "working")
        
        return {
            "status": "working" if working_services >= 2 else "failed",
            "services": services,
            "working_count": working_services,
            "total_count": len(services)
        }
        
    def _test_configuration_system(self) -> Dict[str, Any]:
        """Test configuration system functionality"""
        try:
            if self.config_manager:
                # Test actual configuration loading
                config_data = self.config_manager.get_config()
                return {
                    "status": "working",
                    "config_loaded": True,
                    "config_keys": len(config_data) if isinstance(config_data, dict) else 0
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "No config manager provided"
                }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    def _test_evidence_logger_service(self) -> Dict[str, Any]:
        """Test ACTUAL evidence logger functionality"""
        try:
            from src.core.evidence_logger import EvidenceLogger
            logger = EvidenceLogger()
            
            # Test actual logging
            test_hash = logger.log_with_verification("PRODUCTION_VALIDATION_TEST", 
                                                   {"test": True, "timestamp": datetime.now().isoformat()})
            
            # Test actual verification
            verification_result = logger.verify_evidence_integrity()
            
            return {
                "status": "working",
                "test_hash": test_hash,
                "verification_working": verification_result.get("status") == "completed"
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    def _test_quality_service(self) -> Dict[str, Any]:
        """Test ACTUAL quality service functionality"""
        try:
            from src.core.quality_service import QualityService
            quality_service = QualityService()
            
            check_result = quality_service.run_comprehensive_quality_check()
            
            return {
                "status": "working" if check_result.get("service_status") == "working" else "failed",
                "check_result": check_result
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    def _test_ontology_validator_service(self) -> Dict[str, Any]:
        """Test ACTUAL ontology validator functionality"""
        try:
            from src.core.ontology_validator import OntologyValidator
            validator = OntologyValidator()
            
            # Test actual concept loading
            concepts = validator.list_all_concepts()
            
            return {
                "status": "working",
                "concept_count": len(concepts),
                "has_dolce_concepts": len(concepts) >= 10
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
            
    def _calculate_readiness(self, component_status: Dict[str, Any]) -> float:
        """Calculate ACTUAL production readiness percentage"""
        total_weight = 0
        achieved_weight = 0
        
        # Realistic weight distribution
        weights = {
            "database": 25,
            "tools": 35,
            "services": 25,
            "configuration": 15
        }
        
        for component, weight in weights.items():
            total_weight += weight
            if component in component_status:
                status = component_status[component]
                if status.get("status") == "working":
                    achieved_weight += weight
                elif "success_rate" in status:
                    achieved_weight += weight * (status["success_rate"] / 100)
                elif status.get("status") == "skipped":
                    achieved_weight += weight * 0.5  # Partial credit for skipped
                    
        return (achieved_weight / total_weight) * 100 if total_weight > 0 else 0
        
    def _identify_critical_issues(self, component_status: Dict[str, Any]) -> List[str]:
        """Identify ACTUAL critical issues"""
        issues = []
        
        for component, status in component_status.items():
            if status.get("status") == "failed":
                issues.append(f"{component}: {status.get('error', 'Unknown failure')}")
            elif component == "tools" and status.get("success_rate", 0) < 50:
                issues.append(f"Tool success rate too low: {status.get('success_rate', 0):.1f}%")
                
        return issues

    def _check_all_dependencies(self) -> Dict[str, Any]:
        """Check all system dependencies before testing"""
        dependencies = {
            "neo4j_manager": self._check_neo4j_manager(),
            "tool_factory": self._check_tool_factory(),
            "evidence_logger": self._check_evidence_logger(),
            "config_manager": self._check_config_manager()
        }
        
        missing = [name for name, available in dependencies.items() if not available]
        
        return {
            "all_dependencies_available": len(missing) == 0,
            "missing_dependencies": missing,
            "dependency_details": dependencies
        }

    def _check_neo4j_manager(self) -> bool:
        """Check if Neo4j manager is available and functional"""
        try:
            from src.core.neo4j_manager import Neo4jDockerManager
            manager = Neo4jDockerManager()
            
            # CRITICAL: Test that get_session method exists and works
            if not hasattr(manager, 'get_session'):
                return False
                
            session = manager.get_session()
            if session is None:
                return False
                
            with session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
                
        except Exception:
            return False

    def _check_tool_factory(self) -> bool:
        """Check if tool factory is available"""
        try:
            from src.core.tool_factory import ToolFactory
            factory = ToolFactory()
            return hasattr(factory, 'audit_all_tools')
        except Exception:
            return False

    def _check_evidence_logger(self) -> bool:
        """Check if evidence logger is available"""
        try:
            from src.core.evidence_logger import EvidenceLogger
            logger = EvidenceLogger()
            return hasattr(logger, 'log_with_verification')
        except Exception:
            return False

    def _check_config_manager(self) -> bool:
        """Check if config manager is available"""
        try:
            if self.config_manager is not None:
                return True
            from src.core.config import ConfigurationManager
            manager = ConfigurationManager()
            return hasattr(manager, 'get_config')
        except Exception:
            return False

    def _test_database_connectivity_with_stability(self) -> Dict[str, Any]:
        """Test database connectivity with proper error handling"""
        try:
            if self.neo4j_manager is None:
                from src.core.neo4j_manager import Neo4jDockerManager
                self.neo4j_manager = Neo4jDockerManager()
            
            # Test connection multiple times for stability
            successful_tests = 0
            total_tests = 5
            
            for i in range(total_tests):
                try:
                    with self.neo4j_manager.get_session() as session:
                        result = session.run("RETURN 1 as test")
                        if result.single()["test"] == 1:
                            successful_tests += 1
                except Exception:
                    pass
                
                time.sleep(0.1)
            
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
                "error": str(e)
            }