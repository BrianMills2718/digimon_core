"""
Async Tool Auditor

Handles asynchronous tool auditing for improved performance.
"""

import asyncio
import gc
import uuid
import logging
from typing import Dict, Any, List
from datetime import datetime

from .tool_discovery import ToolDiscovery
from .environment_monitor import EnvironmentMonitor
from .consistency_validator import ConsistencyValidator


class AsyncToolAuditor:
    """Asynchronous tool auditor for improved performance"""
    
    def __init__(self, tools_directory: str = "src/tools", max_concurrent: int = 3):
        self.tool_discovery = ToolDiscovery(tools_directory)
        self.environment_monitor = EnvironmentMonitor()
        self.consistency_validator = ConsistencyValidator()
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger(__name__)
    
    async def audit_all_tools_async(self) -> Dict[str, Any]:
        """Audit all tools asynchronously with concurrency control"""
        start_time = datetime.now()
        
        # Capture initial environment
        initial_environment = self.environment_monitor.capture_test_environment()
        
        # Force garbage collection before testing
        collected = gc.collect()
        
        # Discover tools
        tools = self.tool_discovery.discover_all_tools()
        
        tool_results_dict: Dict[str, Any] = {}
        audit_results: Dict[str, Any] = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "initial_environment": initial_environment,
            "garbage_collected": collected,
            "total_tools": len(tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": tool_results_dict,
            "consistency_metrics": {},
            "final_environment": None,
            "async_execution": True,
            "max_concurrent": self.max_concurrent
        }
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create tasks for all tool audits
        tasks = []
        for tool_name in sorted(tools.keys()):  # Deterministic order
            tool_info = tools[tool_name]
            task = self._audit_tool_with_semaphore(semaphore, tool_name, tool_info)
            tasks.append(task)
        
        # Execute all audits concurrently with controlled concurrency
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(tool_results):
            tool_name = sorted(tools.keys())[i]
            
            if isinstance(result, Exception):
                tool_results_dict[tool_name] = {
                    "status": "failed",
                    "error": str(result),
                    "error_type": type(result).__name__,
                    "test_timestamp": datetime.now().isoformat()
                }
                audit_results["broken_tools"] += 1
            else:
                tool_results_dict[tool_name] = result
                if isinstance(result, dict) and result.get("status") == "working":
                    audit_results["working_tools"] += 1
                else:
                    audit_results["broken_tools"] += 1
        
        # Capture final environment
        audit_results["final_environment"] = self.environment_monitor.capture_test_environment()
        
        # Calculate consistency metrics
        audit_results["consistency_metrics"] = self.consistency_validator.calculate_consistency_metrics(audit_results)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        audit_results["execution_time_seconds"] = execution_time
        
        return audit_results
    
    async def _audit_tool_with_semaphore(self, semaphore: asyncio.Semaphore, 
                                       tool_name: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Audit a single tool with semaphore-controlled concurrency"""
        async with semaphore:
            return await self._audit_tool_async(tool_name, tool_info)
    
    async def _audit_tool_async(self, tool_name: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Audit a single tool asynchronously"""
        try:
            # Capture environment before test
            pre_test_env = self.environment_monitor.capture_test_environment()
            
            # Run the actual tool test in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            test_result = await loop.run_in_executor(
                None, 
                self._test_tool_isolated_sync, 
                tool_name, 
                tool_info
            )
            
            # Capture environment after test
            post_test_env = self.environment_monitor.capture_test_environment()
            
            # Calculate environment impact
            env_impact = self.environment_monitor.calculate_environment_impact(pre_test_env, post_test_env)
            
            # Add timing information
            test_result.update({
                "pre_test_environment": pre_test_env,
                "post_test_environment": post_test_env,
                "environment_impact": env_impact,
                "async_execution": True
            })
            
            return test_result
            
        except Exception as e:
            self.logger.error(f"Async audit failed for {tool_name}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "test_timestamp": datetime.now().isoformat(),
                "async_execution": True
            }
    
    def _test_tool_isolated_sync(self, tool_name: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous tool testing method (run in thread pool)"""
        try:
            if "error" in tool_info:
                return {"status": "failed", "error": tool_info["error"]}
            
            working_classes = 0
            total_classes = len(tool_info["classes"])
            test_results = []
            
            for tool_class in tool_info["classes"]:
                class_result = self._test_tool_class_sync(tool_class)
                test_results.append(class_result)
                
                if class_result.get("working", False):
                    working_classes += 1
            
            if working_classes > 0:
                return {
                    "status": "working",
                    "working_classes": working_classes,
                    "total_classes": total_classes,
                    "reliability_score": working_classes / total_classes,
                    "class_results": test_results,
                    "test_timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "failed",
                    "error": "No working tool classes found",
                    "class_results": test_results,
                    "test_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "failed", 
                "error": str(e),
                "test_timestamp": datetime.now().isoformat()
            }
    
    def _test_tool_class_sync(self, tool_class: type) -> Dict[str, Any]:
        """Test a specific tool class synchronously"""
        class_name = tool_class.__name__
        result = {
            "class_name": class_name,
            "working": False,
            "instantiation_success": False,
            "execute_method_exists": False,
            "execute_test_success": False,
            "error": None,
            "test_timestamp": datetime.now().isoformat()
        }
        
        try:
            # Create fresh instance
            instance = tool_class()
            result["instantiation_success"] = True
            
            # Check for execute method
            if hasattr(instance, 'execute') and callable(instance.execute):
                result["execute_method_exists"] = True
                
                try:
                    # Test with minimal valid input
                    test_result = instance.execute({"test": True})
                    if isinstance(test_result, dict) and "status" in test_result:
                        result["execute_test_success"] = True
                        result["working"] = True
                    else:
                        result["error"] = f"Execute returned {type(test_result)}, expected dict with 'status'"
                except Exception as exec_error:
                    result["error"] = f"Execute method failed: {exec_error}"
            else:
                result["error"] = "Execute method missing or not callable"
            
            # Clean up instance
            del instance
            
        except Exception as class_error:
            result["error"] = f"Class instantiation failed: {class_error}"
        
        return result
    
    async def audit_tools_by_phase(self, phase: str) -> Dict[str, Any]:
        """Audit tools from a specific phase asynchronously"""
        start_time = datetime.now()
        
        # Discover tools for the specific phase
        tools = self.tool_discovery.discover_all_tools()
        phase_tools = {name: info for name, info in tools.items() if name.startswith(phase)}
        
        if not phase_tools:
            return {
                "timestamp": start_time.isoformat(),
                "phase": phase,
                "total_tools": 0,
                "working_tools": 0,
                "broken_tools": 0,
                "tool_results": {},
                "error": f"No tools found for phase {phase}"
            }
        
        phase_tool_results: Dict[str, Any] = {}
        audit_results: Dict[str, Any] = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "phase": phase,
            "total_tools": len(phase_tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": phase_tool_results,
            "async_execution": True
        }
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Create tasks for phase tools
        tasks = []
        for tool_name, tool_info in phase_tools.items():
            task = self._audit_tool_with_semaphore(semaphore, tool_name, tool_info)
            tasks.append(task)
        
        # Execute audits
        tool_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(tool_results):
            tool_name = list(phase_tools.keys())[i]
            
            if isinstance(result, Exception):
                phase_tool_results[tool_name] = {
                    "status": "failed",
                    "error": str(result),
                    "error_type": type(result).__name__
                }
                audit_results["broken_tools"] += 1
            else:
                phase_tool_results[tool_name] = result
                if isinstance(result, dict) and result.get("status") == "working":
                    audit_results["working_tools"] += 1
                else:
                    audit_results["broken_tools"] += 1
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        audit_results["execution_time_seconds"] = execution_time
        
        return audit_results
    
    async def compare_sync_vs_async_performance(self) -> Dict[str, Any]:
        """Compare synchronous vs asynchronous auditing performance"""
        # Run synchronous audit
        sync_start = datetime.now()
        from .tool_auditor import ToolAuditor
        sync_auditor = ToolAuditor(self.tool_discovery.tools_directory)
        sync_results = sync_auditor.audit_all_tools()
        sync_duration = (datetime.now() - sync_start).total_seconds()
        
        # Run asynchronous audit
        async_start = datetime.now()
        async_results = await self.audit_all_tools_async()
        async_duration = (datetime.now() - async_start).total_seconds()
        
        # Calculate performance comparison
        performance_improvement = ((sync_duration - async_duration) / sync_duration) * 100 if sync_duration > 0 else 0
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "sync_duration_seconds": sync_duration,
            "async_duration_seconds": async_duration,
            "performance_improvement_percent": round(performance_improvement, 2),
            "sync_total_tools": sync_results.get("total_tools", 0),
            "async_total_tools": async_results.get("total_tools", 0),
            "sync_working_tools": sync_results.get("working_tools", 0),
            "async_working_tools": async_results.get("working_tools", 0),
            "results_consistent": (
                sync_results.get("working_tools") == async_results.get("working_tools") and
                sync_results.get("broken_tools") == async_results.get("broken_tools")
            ),
            "max_concurrent": self.max_concurrent,
            "recommendations": []
        }
        
        # Generate performance recommendations
        if performance_improvement > 20:
            comparison["recommendations"].append("Async auditing provides significant performance benefits - recommend for production")
        elif performance_improvement > 0:
            comparison["recommendations"].append("Async auditing provides moderate performance benefits")
        else:
            comparison["recommendations"].append("Sync auditing may be more stable for this workload")
        
        if not comparison["results_consistent"]:
            comparison["recommendations"].append("Results inconsistency detected - investigate async implementation")
        
        return comparison
    
    def set_concurrency_limit(self, max_concurrent: int) -> None:
        """Set the maximum number of concurrent tool audits"""
        if max_concurrent < 1:
            raise ValueError("Max concurrent must be at least 1")
        if max_concurrent > 10:
            self.logger.warning(f"High concurrency limit ({max_concurrent}) may cause resource exhaustion")
        
        self.max_concurrent = max_concurrent
        self.logger.info(f"Concurrency limit set to {max_concurrent}")
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics"""
        audit_results = await self.audit_all_tools_async()
        
        statistics = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_tools": audit_results.get("total_tools", 0),
                "working_tools": audit_results.get("working_tools", 0),
                "broken_tools": audit_results.get("broken_tools", 0),
                "success_rate": 0.0
            },
            "performance": {
                "execution_time": audit_results.get("execution_time_seconds", 0),
                "async_execution": True,
                "max_concurrent": self.max_concurrent
            },
            "environment_impact": audit_results.get("consistency_metrics", {}),
            "phase_breakdown": {},
            "error_categories": {}
        }
        
        # Calculate success rate
        total = statistics["overview"]["total_tools"]
        if total > 0:
            statistics["overview"]["success_rate"] = (statistics["overview"]["working_tools"] / total) * 100
        
        # Analyze by phase
        tool_results = audit_results.get("tool_results", {})
        phase_stats = {"phase1": 0, "phase2": 0, "phase3": 0}
        phase_working = {"phase1": 0, "phase2": 0, "phase3": 0}
        
        for tool_name, result in tool_results.items():
            for phase in phase_stats.keys():
                if tool_name.startswith(phase):
                    phase_stats[phase] += 1
                    if result.get("status") == "working":
                        phase_working[phase] += 1
                    break
        
        for phase, total_count in phase_stats.items():
            if total_count > 0:
                success_rate = (phase_working[phase] / total_count) * 100
                statistics["phase_breakdown"][phase] = {
                    "total": total_count,
                    "working": phase_working[phase],
                    "success_rate": round(success_rate, 2)
                }
        
        # Categorize errors
        error_counts = {}
        for tool_name, result in tool_results.items():
            if result.get("status") == "failed":
                error = result.get("error", "Unknown error")
                error_type = result.get("error_type", "Unknown")
                
                if error_type not in error_counts:
                    error_counts[error_type] = 0
                error_counts[error_type] += 1
        
        statistics["error_categories"] = error_counts
        
        return statistics