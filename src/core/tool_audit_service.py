import asyncio
import gc
import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Lock

from src.core.tool_registry_service import ToolRegistryService
from src.core.config_manager import get_config


class ToolAuditService:
    """
    Service responsible for tool validation and audit operations.
    
    Handles comprehensive testing of tools with environment consistency
    tracking, performance monitoring, and detailed audit reporting.
    """
    
    def __init__(self, registry_service: Optional[ToolRegistryService] = None):
        """
        Initialize the tool audit service.
        
        Args:
            registry_service: ToolRegistryService for accessing registered tools
        """
        self.registry_service = registry_service or ToolRegistryService()
        self.audit_results: Dict[str, Dict[str, Any]] = {}
        self.audit_lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        # Get configuration
        self.config = get_config()
        
        # Audit configuration
        self.max_test_retries = 3
        self.test_timeout = 30.0
        self.stability_check_enabled = True
        
    def audit_tool(self, tool_name: str, test_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Audit a single tool with comprehensive validation.
        
        Args:
            tool_name: Name of the tool to audit
            test_data: Optional test data for the tool
            
        Returns:
            Dictionary containing audit results
        """
        audit_start = datetime.now()
        audit_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting audit for tool: {tool_name} (audit_id: {audit_id})")
        
        # Initialize audit result
        audit_result = {
            "tool_name": tool_name,
            "audit_id": audit_id,
            "start_time": audit_start.isoformat(),
            "status": "unknown",
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": [],
            "environment_impact": {},
            "performance_metrics": {}
        }
        
        try:
            # Check if tool is registered
            if not self.registry_service.is_tool_registered(tool_name):
                audit_result["status"] = "not_registered"
                audit_result["errors"].append(f"Tool {tool_name} is not registered")
                return audit_result
            
            # Capture initial environment
            initial_env = self._capture_test_environment()
            
            # Run comprehensive audit tests
            audit_result.update(self._run_audit_tests(tool_name, test_data, initial_env))
            
            # Calculate final status
            if audit_result["tests_failed"] == 0 and len(audit_result["errors"]) == 0:
                audit_result["status"] = "working"
            elif audit_result["tests_passed"] > 0:
                audit_result["status"] = "partial"
            else:
                audit_result["status"] = "broken"
            
        except Exception as e:
            self.logger.error(f"Audit failed for tool {tool_name}: {e}")
            audit_result["status"] = "error"
            audit_result["errors"].append(f"Audit exception: {str(e)}")
        
        finally:
            # Record completion time
            audit_result["end_time"] = datetime.now().isoformat()
            audit_result["duration"] = (datetime.now() - audit_start).total_seconds()
            
            # Store audit result
            with self.audit_lock:
                self.audit_results[tool_name] = audit_result
        
        self.logger.info(f"Audit completed for {tool_name}: {audit_result['status']} "
                        f"({audit_result['tests_passed']}/{audit_result['tests_passed'] + audit_result['tests_failed']} tests passed)")
        
        return audit_result
    
    async def audit_tool_async(self, tool_name: str, test_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Asynchronous version of tool audit.
        
        Args:
            tool_name: Name of the tool to audit
            test_data: Optional test data for the tool
            
        Returns:
            Dictionary containing audit results
        """
        audit_start = datetime.now()
        audit_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting async audit for tool: {tool_name} (audit_id: {audit_id})")
        
        # Initialize audit result
        audit_result = {
            "tool_name": tool_name,
            "audit_id": audit_id,
            "start_time": audit_start.isoformat(),
            "status": "unknown",
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": [],
            "environment_impact": {},
            "performance_metrics": {}
        }
        
        try:
            # Check if tool is registered
            if not self.registry_service.is_tool_registered(tool_name):
                audit_result["status"] = "not_registered"
                audit_result["errors"].append(f"Tool {tool_name} is not registered")
                return audit_result
            
            # Capture initial environment
            initial_env = self._capture_test_environment()
            
            # Run async audit tests
            audit_result.update(await self._run_audit_tests_async(tool_name, test_data, initial_env))
            
            # Calculate final status
            if audit_result["tests_failed"] == 0 and len(audit_result["errors"]) == 0:
                audit_result["status"] = "working"
            elif audit_result["tests_passed"] > 0:
                audit_result["status"] = "partial"
            else:
                audit_result["status"] = "broken"
            
        except Exception as e:
            self.logger.error(f"Async audit failed for tool {tool_name}: {e}")
            audit_result["status"] = "error"
            audit_result["errors"].append(f"Async audit exception: {str(e)}")
        
        finally:
            # Record completion time
            audit_result["end_time"] = datetime.now().isoformat()
            audit_result["duration"] = (datetime.now() - audit_start).total_seconds()
            
            # Store audit result
            with self.audit_lock:
                self.audit_results[tool_name] = audit_result
        
        return audit_result
    
    def audit_all_tools(self) -> Dict[str, Any]:
        """
        Audit all registered tools with comprehensive validation.
        
        Returns:
            Dictionary containing complete audit results
        """
        audit_start = datetime.now()
        audit_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting comprehensive tool audit (audit_id: {audit_id})")
        
        # Capture initial environment
        initial_environment = self._capture_test_environment()
        
        # Force garbage collection before testing
        collected = gc.collect()
        
        # Get all registered tools
        tool_names = self.registry_service.list_registered_tools()
        
        # Initialize audit summary
        audit_summary = {
            "audit_id": audit_id,
            "timestamp": audit_start.isoformat(),
            "initial_environment": initial_environment,
            "garbage_collected": collected,
            "total_tools": len(tool_names),
            "working_tools": 0,
            "broken_tools": 0,
            "partial_tools": 0,
            "not_registered_tools": 0,
            "tool_results": {},
            "consistency_metrics": {},
            "final_environment": None
        }
        
        # Audit each tool
        for tool_name in sorted(tool_names):  # Deterministic order
            self.logger.debug(f"Auditing tool: {tool_name}")
            
            # Capture environment before test
            pre_test_env = self._capture_test_environment()
            
            # Audit the tool
            tool_audit_result = self.audit_tool(tool_name)
            
            # Capture environment after test
            post_test_env = self._capture_test_environment()
            
            # Calculate environment impact
            env_impact = self._calculate_environment_impact(pre_test_env, post_test_env)
            tool_audit_result["environment_impact"] = env_impact
            
            # Update summary counters
            status = tool_audit_result["status"]
            if status == "working":
                audit_summary["working_tools"] += 1
            elif status == "broken" or status == "error":
                audit_summary["broken_tools"] += 1
            elif status == "partial":
                audit_summary["partial_tools"] += 1
            elif status == "not_registered":
                audit_summary["not_registered_tools"] += 1
            
            audit_summary["tool_results"][tool_name] = tool_audit_result
            
            # Force garbage collection between tests
            gc.collect()
        
        # Capture final environment
        audit_summary["final_environment"] = self._capture_test_environment()
        
        # Calculate consistency metrics
        audit_summary["consistency_metrics"] = self._calculate_consistency_metrics(audit_summary)
        
        # Record completion
        audit_summary["end_time"] = datetime.now().isoformat()
        audit_summary["duration"] = (datetime.now() - audit_start).total_seconds()
        
        self.logger.info(f"Comprehensive audit completed: {audit_summary['working_tools']}/{audit_summary['total_tools']} tools working")
        
        return audit_summary
    
    async def audit_all_tools_async(self) -> Dict[str, Any]:
        """
        Asynchronous version of comprehensive tool audit.
        
        Returns:
            Dictionary containing complete audit results
        """
        audit_start = datetime.now()
        audit_id = str(uuid.uuid4())
        
        self.logger.info(f"Starting async comprehensive tool audit (audit_id: {audit_id})")
        
        # Capture initial environment
        initial_environment = self._capture_test_environment()
        
        # Force garbage collection before testing
        collected = gc.collect()
        
        # Get all registered tools
        tool_names = self.registry_service.list_registered_tools()
        
        # Initialize audit summary
        audit_summary = {
            "audit_id": audit_id,
            "timestamp": audit_start.isoformat(),
            "initial_environment": initial_environment,
            "garbage_collected": collected,
            "total_tools": len(tool_names),
            "working_tools": 0,
            "broken_tools": 0,
            "partial_tools": 0,
            "not_registered_tools": 0,
            "tool_results": {},
            "consistency_metrics": {},
            "final_environment": None
        }
        
        # Audit each tool
        for tool_name in sorted(tool_names):  # Deterministic order
            self.logger.debug(f"Auditing tool: {tool_name}")
            
            # Capture environment before test
            pre_test_env = self._capture_test_environment()
            
            # Audit the tool asynchronously
            tool_audit_result = await self.audit_tool_async(tool_name)
            
            # Capture environment after test
            post_test_env = self._capture_test_environment()
            
            # Calculate environment impact
            env_impact = self._calculate_environment_impact(pre_test_env, post_test_env)
            tool_audit_result["environment_impact"] = env_impact
            
            # Update summary counters
            status = tool_audit_result["status"]
            if status == "working":
                audit_summary["working_tools"] += 1
            elif status == "broken" or status == "error":
                audit_summary["broken_tools"] += 1
            elif status == "partial":
                audit_summary["partial_tools"] += 1
            elif status == "not_registered":
                audit_summary["not_registered_tools"] += 1
            
            audit_summary["tool_results"][tool_name] = tool_audit_result
            
            # Force garbage collection between tests
            gc.collect()
            await asyncio.sleep(0.1)  # Brief pause for system stability
        
        # Capture final environment
        audit_summary["final_environment"] = self._capture_test_environment()
        
        # Calculate consistency metrics
        audit_summary["consistency_metrics"] = self._calculate_consistency_metrics(audit_summary)
        
        # Record completion
        audit_summary["end_time"] = datetime.now().isoformat()
        audit_summary["duration"] = (datetime.now() - audit_start).total_seconds()
        
        self.logger.info(f"Async comprehensive audit completed: {audit_summary['working_tools']}/{audit_summary['total_tools']} tools working")
        
        return audit_summary
    
    def get_success_rate(self, tool_name: Optional[str] = None) -> float:
        """
        Calculate tool success rate from audit history.
        
        Args:
            tool_name: Specific tool name, or None for overall rate
            
        Returns:
            Success rate as percentage (0.0 to 100.0)
        """
        if tool_name:
            # Get success rate for specific tool
            if tool_name in self.audit_results:
                result = self.audit_results[tool_name]
                total_tests = result["tests_passed"] + result["tests_failed"]
                if total_tests > 0:
                    return (result["tests_passed"] / total_tests) * 100.0
            return 0.0
        else:
            # Calculate overall success rate
            total_working = 0
            total_tools = 0
            
            for audit_result in self.audit_results.values():
                total_tools += 1
                if audit_result["status"] == "working":
                    total_working += 1
            
            if total_tools > 0:
                return (total_working / total_tools) * 100.0
            return 0.0
    
    def get_audit_history(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get audit history for tools.
        
        Args:
            tool_name: Specific tool name, or None for all tools
            
        Returns:
            Dictionary containing audit history
        """
        if tool_name:
            return self.audit_results.get(tool_name, {})
        else:
            return dict(self.audit_results)
    
    def clear_audit_history(self, tool_name: Optional[str] = None) -> None:
        """
        Clear audit history.
        
        Args:
            tool_name: Specific tool name, or None to clear all
        """
        with self.audit_lock:
            if tool_name:
                if tool_name in self.audit_results:
                    del self.audit_results[tool_name]
                    self.logger.info(f"Cleared audit history for tool: {tool_name}")
            else:
                self.audit_results.clear()
                self.logger.info("Cleared all audit history")
    
    def _run_audit_tests(self, tool_name: str, test_data: Optional[Dict[str, Any]], 
                        initial_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive audit tests for a tool.
        
        Args:
            tool_name: Name of the tool to test
            test_data: Optional test data
            initial_env: Initial environment state
            
        Returns:
            Dictionary containing test results
        """
        test_results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": [],
            "performance_metrics": {}
        }
        
        try:
            # Test 1: Tool instantiation
            test_start = datetime.now()
            tool_instance = self.registry_service.get_tool_instance(tool_name, force_new=True)
            instantiation_time = (datetime.now() - test_start).total_seconds()
            
            if tool_instance is None:
                test_results["tests_failed"] += 1
                test_results["errors"].append("Failed to instantiate tool")
                return test_results
            else:
                test_results["tests_passed"] += 1
                test_results["performance_metrics"]["instantiation_time"] = instantiation_time
            
            # Test 2: Tool info method
            if hasattr(tool_instance, 'get_tool_info'):
                try:
                    tool_info = tool_instance.get_tool_info()
                    if isinstance(tool_info, dict):
                        test_results["tests_passed"] += 1
                    else:
                        test_results["tests_failed"] += 1
                        test_results["errors"].append("get_tool_info did not return dict")
                except Exception as e:
                    test_results["tests_failed"] += 1
                    test_results["errors"].append(f"get_tool_info failed: {str(e)}")
            
            # Test 3: Tool execution
            try:
                # Use provided test data or create minimal test data
                if test_data is None:
                    test_data = {"test": True}
                
                execution_start = datetime.now()
                result = tool_instance.execute(test_data)
                execution_time = (datetime.now() - execution_start).total_seconds()
                
                if isinstance(result, dict) and "status" in result:
                    test_results["tests_passed"] += 1
                    test_results["performance_metrics"]["execution_time"] = execution_time
                else:
                    test_results["tests_failed"] += 1
                    test_results["errors"].append("Tool execution did not return proper result format")
                    
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["errors"].append(f"Tool execution failed: {str(e)}")
            
            # Test 4: Memory stability (if enabled)
            if self.stability_check_enabled:
                try:
                    pre_memory = self._get_memory_usage()
                    # Run tool multiple times to check for memory leaks
                    for _ in range(3):
                        tool_instance.execute(test_data)
                    post_memory = self._get_memory_usage()
                    
                    memory_growth = post_memory - pre_memory
                    test_results["performance_metrics"]["memory_growth_mb"] = memory_growth
                    
                    if memory_growth < 50:  # Less than 50MB growth is acceptable
                        test_results["tests_passed"] += 1
                    else:
                        test_results["tests_failed"] += 1
                        test_results["warnings"].append(f"Potential memory leak: {memory_growth:.1f}MB growth")
                        
                except Exception as e:
                    test_results["warnings"].append(f"Memory stability test failed: {str(e)}")
            
        except Exception as e:
            test_results["errors"].append(f"Audit test exception: {str(e)}")
        
        return test_results
    
    async def _run_audit_tests_async(self, tool_name: str, test_data: Optional[Dict[str, Any]], 
                                   initial_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous version of audit tests.
        
        Args:
            tool_name: Name of the tool to test
            test_data: Optional test data
            initial_env: Initial environment state
            
        Returns:
            Dictionary containing test results
        """
        # For now, run the sync version but with async yields
        test_results = self._run_audit_tests(tool_name, test_data, initial_env)
        
        # Add brief async yield to prevent blocking
        await asyncio.sleep(0.01)
        
        return test_results
    
    def _capture_test_environment(self) -> Dict[str, Any]:
        """
        Capture comprehensive test environment state.
        
        Returns:
            Dictionary containing environment metrics
        """
        import psutil
        import threading
        
        try:
            process = psutil.Process()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "thread_count": threading.active_count(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
                "gc_stats": {
                    "collections": gc.get_count(),
                    "collected_objects": gc.collect()
                }
            }
        except Exception as e:
            self.logger.warning(f"Failed to capture environment: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _calculate_environment_impact(self, pre_env: Dict[str, Any], 
                                    post_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate environmental impact of tool testing.
        
        Args:
            pre_env: Environment state before test
            post_env: Environment state after test
            
        Returns:
            Dictionary containing impact metrics
        """
        try:
            impact = {
                "memory_delta_mb": post_env.get("memory_mb", 0) - pre_env.get("memory_mb", 0),
                "thread_delta": post_env.get("thread_count", 0) - pre_env.get("thread_count", 0),
                "file_delta": post_env.get("open_files", 0) - pre_env.get("open_files", 0),
                "connection_delta": post_env.get("connections", 0) - pre_env.get("connections", 0)
            }
            
            # Calculate severity
            severity = "low"
            if abs(impact["memory_delta_mb"]) > 10 or abs(impact["thread_delta"]) > 2:
                severity = "medium"
            if abs(impact["memory_delta_mb"]) > 50 or abs(impact["thread_delta"]) > 5:
                severity = "high"
            
            impact["severity"] = severity
            return impact
            
        except Exception as e:
            return {"error": str(e), "severity": "unknown"}
    
    def _calculate_consistency_metrics(self, audit_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate consistency metrics across all tool tests.
        
        Args:
            audit_summary: Complete audit summary
            
        Returns:
            Dictionary containing consistency metrics
        """
        try:
            total_tools = audit_summary["total_tools"]
            if total_tools == 0:
                return {"error": "No tools to analyze"}
            
            # Calculate environment consistency
            initial_env = audit_summary.get("initial_environment", {})
            final_env = audit_summary.get("final_environment", {})
            
            overall_impact = self._calculate_environment_impact(initial_env, final_env)
            
            # Calculate success rates
            success_rate = (audit_summary["working_tools"] / total_tools) * 100
            
            return {
                "success_rate_percent": success_rate,
                "tools_working": audit_summary["working_tools"],
                "tools_broken": audit_summary["broken_tools"],
                "tools_partial": audit_summary["partial_tools"],
                "overall_environment_impact": overall_impact,
                "consistency_level": "high" if success_rate > 80 else "medium" if success_rate > 50 else "low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0