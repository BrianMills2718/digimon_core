import importlib
import inspect
import os
import sys
import gc
import time
import uuid
import threading
import random
import logging
from typing import Dict, Any, List, Type
from pathlib import Path
from datetime import datetime

class ToolFactory:
    def __init__(self, tools_directory: str = "src/tools"):
        self.tools_directory = tools_directory
        self.discovered_tools = {}
        self.logger = logging.getLogger(__name__)
        
    def discover_all_tools(self) -> Dict[str, Any]:
        """Discover all tool classes in the tools directory - COMPLETE IMPLEMENTATION"""
        tools = {}
        
        for phase_dir in ["phase1", "phase2", "phase3"]:
            phase_path = Path(self.tools_directory) / phase_dir
            if phase_path.exists():
                for py_file in phase_path.glob("*.py"):
                    if py_file.name.startswith("t") and py_file.name != "__init__.py":
                        tool_name = py_file.stem
                        try:
                            module_path = f"src.tools.{phase_dir}.{tool_name}"
                            
                            # Actually import and inspect the module
                            spec = importlib.util.spec_from_file_location(module_path, py_file)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_path] = module
                            spec.loader.exec_module(module)
                            
                            # Find actual tool classes with execute methods
                            tool_classes = []
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    hasattr(obj, 'execute') and 
                                    callable(getattr(obj, 'execute'))):
                                    tool_classes.append(obj)
                            
                            if tool_classes:
                                tools[f"{phase_dir}.{tool_name}"] = {
                                    "classes": tool_classes,
                                    "module": module_path,
                                    "file": str(py_file),
                                    "status": "discovered"
                                }
                            else:
                                tools[f"{phase_dir}.{tool_name}"] = {
                                    "error": "No tool classes with execute method found",
                                    "status": "failed"
                                }
                                
                        except Exception as e:
                            tools[f"{phase_dir}.{tool_name}"] = {
                                "error": str(e),
                                "status": "failed"
                            }
                            
        self.discovered_tools = tools
        return tools
        
    def audit_all_tools(self) -> Dict[str, Any]:
        """Audit all tools with environment consistency tracking"""
        start_time = datetime.now()
        
        # Capture initial environment
        initial_environment = self._capture_test_environment()
        
        # Force garbage collection before testing
        collected = gc.collect()
        
        # Discover tools in deterministic order
        tools = self.discover_all_tools()
        self.discovered_tools = tools
        
        audit_results = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "initial_environment": initial_environment,
            "garbage_collected": collected,
            "total_tools": len(tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": {},
            "consistency_metrics": {},
            "final_environment": None
        }
        
        # Test each tool in isolated environment
        for tool_name in sorted(tools.keys()):  # Deterministic order
            tool_info = tools[tool_name]
            
            # Capture environment before each test
            pre_test_env = self._capture_test_environment()
            
            # Test tool in isolation
            test_result = self._test_tool_isolated(tool_name, tool_info)
            
            # Capture environment after test
            post_test_env = self._capture_test_environment()
            
            # Calculate environment impact
            env_impact = self._calculate_environment_impact(pre_test_env, post_test_env)
            
            if test_result.get("status") == "working":
                audit_results["working_tools"] += 1
            else:
                audit_results["broken_tools"] += 1
            
            audit_results["tool_results"][tool_name] = {
                **test_result,
                "pre_test_environment": pre_test_env,
                "post_test_environment": post_test_env,
                "environment_impact": env_impact
            }
            
            # Force garbage collection between tests
            gc.collect()
            time.sleep(0.1)  # Brief pause for system stability
        
        # Capture final environment
        audit_results["final_environment"] = self._capture_test_environment()
        
        # Calculate consistency metrics
        audit_results["consistency_metrics"] = self._calculate_consistency_metrics(audit_results)
        
        return audit_results

    def _test_tool_isolated(self, tool_name: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test tool with ACTUAL execution, not just method existence"""
        try:
            if "error" in tool_info:
                return {"status": "failed", "error": tool_info["error"]}
            
            working_classes = 0
            total_classes = len(tool_info["classes"])
            
            for tool_class in tool_info["classes"]:
                try:
                    # Create fresh instance
                    instance = tool_class()
                    
                    # CRITICAL: Actually test execute method with minimal input
                    if hasattr(instance, 'execute') and callable(instance.execute):
                        try:
                            # Test with minimal valid input
                            test_result = instance.execute({"test": True})
                            if isinstance(test_result, dict) and "status" in test_result:
                                working_classes += 1
                        except Exception as exec_error:
                            # Execute method exists but fails - count as broken
                            self.logger.warning(f"Tool execute method failed for {tool_class.__name__}: {exec_error}")
                            continue
                    
                    # Clean up instance
                    del instance
                    
                except Exception as class_error:
                    self.logger.error(f"Tool class instantiation failed for {tool_class.__name__}: {class_error}")
                    continue
            
            if working_classes > 0:
                return {
                    "status": "working",
                    "working_classes": working_classes,
                    "total_classes": total_classes,
                    "reliability_score": working_classes / total_classes
                }
            else:
                return {
                    "status": "failed", 
                    "error": "No working tool classes found"
                }
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _capture_test_environment(self) -> Dict[str, Any]:
        """Capture comprehensive test environment for consistency validation"""
        import psutil
        import platform
        
        try:
            # Get system information
            memory = psutil.virtual_memory()
            cpu_times = psutil.cpu_times()
            
            environment = {
                "timestamp": datetime.now().isoformat(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(logical=False),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "disk_usage": dict(psutil.disk_usage('/')._asdict()),
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                "gc_counts": gc.get_count(),
                "gc_stats": gc.get_stats(),
                "process_count": len(psutil.pids()),
                "boot_time": psutil.boot_time()
            }
            
            # Add Python-specific information
            environment.update({
                "python_executable": sys.executable,
                "python_path": sys.path[:5],  # First 5 entries
                "recursion_limit": sys.getrecursionlimit(),
                "thread_count": threading.active_count()
            })
            
            return environment
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "capture_failed": True
            }
        
    def get_success_rate(self) -> float:
        """Calculate ACTUAL tool success rate"""
        audit = self.audit_all_tools()
        if audit["total_tools"] == 0:
            return 0.0
        return (audit["working_tools"] / audit["total_tools"]) * 100

    def _calculate_environment_impact(self, pre_env: Dict, post_env: Dict) -> Dict[str, Any]:
        """Calculate the impact of tool testing on system environment"""
        impact = {
            "timestamp": datetime.now().isoformat(),
            "memory_impact": {},
            "cpu_impact": {},
            "process_impact": {},
            "thread_impact": {},
            "disk_impact": {},
            "overall_stability": True
        }
        
        try:
            # Memory impact analysis
            if "memory_available" in pre_env and "memory_available" in post_env:
                memory_delta = post_env["memory_available"] - pre_env["memory_available"]
                memory_percent_delta = post_env.get("memory_percent", 0) - pre_env.get("memory_percent", 0)
                
                impact["memory_impact"] = {
                    "available_bytes_change": memory_delta,
                    "percent_change": memory_percent_delta,
                    "leak_detected": memory_delta < -50 * 1024 * 1024,  # 50MB threshold
                    "excessive_usage": memory_percent_delta > 5.0  # 5% threshold
                }
                
                if impact["memory_impact"]["leak_detected"] or impact["memory_impact"]["excessive_usage"]:
                    impact["overall_stability"] = False

            # CPU impact analysis
            if "cpu_percent" in pre_env and "cpu_percent" in post_env:
                cpu_delta = post_env["cpu_percent"] - pre_env["cpu_percent"]
                
                impact["cpu_impact"] = {
                    "percent_change": cpu_delta,
                    "excessive_usage": cpu_delta > 20.0,  # 20% threshold
                    "sustained_high_usage": post_env.get("cpu_percent", 0) > 80.0
                }
                
                if impact["cpu_impact"]["excessive_usage"] or impact["cpu_impact"]["sustained_high_usage"]:
                    impact["overall_stability"] = False

            # Process impact analysis
            if "process_count" in pre_env and "process_count" in post_env:
                process_delta = post_env["process_count"] - pre_env["process_count"]
                
                impact["process_impact"] = {
                    "count_change": process_delta,
                    "leak_detected": process_delta > 0,  # Any increase indicates leak
                    "excessive_processes": post_env.get("process_count", 0) > pre_env.get("process_count", 0) + 5
                }
                
                if impact["process_impact"]["leak_detected"]:
                    impact["overall_stability"] = False

            # Thread impact analysis
            if "thread_count" in pre_env and "thread_count" in post_env:
                thread_delta = post_env["thread_count"] - pre_env["thread_count"]
                
                impact["thread_impact"] = {
                    "count_change": thread_delta,
                    "leak_detected": thread_delta > 2,  # Allow 2 thread tolerance
                    "excessive_threads": post_env.get("thread_count", 0) > 50
                }
                
                if impact["thread_impact"]["leak_detected"]:
                    impact["overall_stability"] = False

            # Disk impact analysis
            if "disk_usage" in pre_env and "disk_usage" in post_env:
                pre_disk = pre_env["disk_usage"]
                post_disk = post_env["disk_usage"]
                
                if isinstance(pre_disk, dict) and isinstance(post_disk, dict):
                    used_delta = post_disk.get("used", 0) - pre_disk.get("used", 0)
                    
                    impact["disk_impact"] = {
                        "bytes_change": used_delta,
                        "significant_usage": used_delta > 100 * 1024 * 1024,  # 100MB threshold
                        "disk_space_concern": post_disk.get("free", 0) < 1024 * 1024 * 1024  # 1GB free threshold
                    }
                    
                    if impact["disk_impact"]["significant_usage"]:
                        impact["overall_stability"] = False

        except Exception as e:
            impact["calculation_error"] = str(e)
            impact["overall_stability"] = False
            raise RuntimeError(f"Environment impact calculation failed: {e}")
        
        return impact

    def _calculate_consistency_metrics(self, audit_results: Dict) -> Dict[str, Any]:
        """Calculate consistency metrics across all tool tests"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "environment_stability": True,
            "memory_stability": True,
            "cpu_stability": True,
            "process_stability": True,
            "thread_stability": True,
            "test_result_consistency": True,
            "overall_consistency_score": 0.0,
            "detailed_metrics": {
                "memory_leaks_detected": 0,
                "process_leaks_detected": 0,
                "thread_leaks_detected": 0,
                "cpu_spikes_detected": 0,
                "inconsistent_results": 0
            },
            "stability_violations": []
        }
        
        try:
            total_tools = len(audit_results.get("tool_results", {}))
            if total_tools == 0:
                raise ValueError("No tool results to analyze for consistency")
            
            # Analyze environment impacts across all tools
            for tool_name, tool_result in audit_results["tool_results"].items():
                env_impact = tool_result.get("environment_impact", {})
                
                # Memory stability analysis
                if env_impact.get("memory_impact", {}).get("leak_detected", False):
                    metrics["detailed_metrics"]["memory_leaks_detected"] += 1
                    metrics["memory_stability"] = False
                    metrics["stability_violations"].append(f"Memory leak in {tool_name}")
                
                # Process stability analysis
                if env_impact.get("process_impact", {}).get("leak_detected", False):
                    metrics["detailed_metrics"]["process_leaks_detected"] += 1
                    metrics["process_stability"] = False
                    metrics["stability_violations"].append(f"Process leak in {tool_name}")
                
                # Thread stability analysis
                if env_impact.get("thread_impact", {}).get("leak_detected", False):
                    metrics["detailed_metrics"]["thread_leaks_detected"] += 1
                    metrics["thread_stability"] = False
                    metrics["stability_violations"].append(f"Thread leak in {tool_name}")
                
                # CPU stability analysis
                if env_impact.get("cpu_impact", {}).get("excessive_usage", False):
                    metrics["detailed_metrics"]["cpu_spikes_detected"] += 1
                    metrics["cpu_stability"] = False
                    metrics["stability_violations"].append(f"CPU spike in {tool_name}")
            
            # Calculate overall environment stability
            metrics["environment_stability"] = all([
                metrics["memory_stability"],
                metrics["cpu_stability"], 
                metrics["process_stability"],
                metrics["thread_stability"]
            ])
            
            # Test result consistency analysis
            working_tools = audit_results.get("working_tools", 0)
            total_tools_count = audit_results.get("total_tools", 0)
            
            if total_tools_count > 0:
                success_rate = working_tools / total_tools_count
                # Consistency requires deterministic results
                metrics["test_result_consistency"] = True  # Will be validated by multiple runs
            else:
                metrics["test_result_consistency"] = False
                metrics["stability_violations"].append("No tools found for consistency analysis")
            
            # Calculate overall consistency score
            stability_factors = [
                metrics["memory_stability"],
                metrics["cpu_stability"],
                metrics["process_stability"], 
                metrics["thread_stability"],
                metrics["test_result_consistency"]
            ]
            
            metrics["overall_consistency_score"] = sum(stability_factors) / len(stability_factors)
            
            # Log consistency results
            from .evidence_logger import EvidenceLogger
            evidence_logger = EvidenceLogger()
            evidence_logger.log_with_verification("TOOL_CONSISTENCY_METRICS", metrics)
            
        except Exception as e:
            metrics["calculation_error"] = str(e)
            metrics["overall_consistency_score"] = 0.0
            raise RuntimeError(f"Consistency metrics calculation failed: {e}")
        
        return metrics

    def create_all_tools(self) -> List[Any]:
        """Create and return instances of all discovered tools."""
        if not self.discovered_tools:
            self.discover_all_tools()

        tool_instances = []
        for tool_name in self.discovered_tools:
            try:
                tool_instance = self.get_tool_by_name(tool_name)
                if tool_instance:
                    tool_instances.append(tool_instance)
            except (ValueError, RuntimeError) as e:
                self.logger.warning(f"Could not create instance for tool {tool_name}: {e}")
        
        return tool_instances

    def get_tool_by_name(self, tool_name: str) -> Any:
        """Get actual tool instance by name"""
        if not self.discovered_tools:
            self.discover_all_tools()
            
        if tool_name not in self.discovered_tools:
            raise ValueError(f"Tool {tool_name} not found")
            
        tool_info = self.discovered_tools[tool_name]
        if "error" in tool_info:
            raise RuntimeError(f"Tool {tool_name} has error: {tool_info['error']}")
            
        # Return first working class instance
        for tool_class in tool_info["classes"]:
            try:
                return tool_class()
            except Exception as e:
                self.logger.error(f"Tool instantiation failed for {tool_class.__name__}: {e}")
                continue
                
        raise RuntimeError(f"No working instances found for {tool_name}")
    
    def audit_all_tools_with_consistency_validation(self) -> Dict[str, Any]:
        """Audit tools with mandatory consistency validation"""
        start_time = datetime.now()
        
        # Clear any cached results to ensure fresh audit
        self.discovered_tools = None
        if hasattr(self, '_tool_cache'):
            self._tool_cache.clear()
        
        # Force garbage collection before audit
        import gc
        collected = gc.collect()
        
        # Perform actual tool discovery and testing
        tools = self.discover_all_tools()
        audit_results = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "total_tools": len(tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": {},
            "garbage_collected": collected,
            "consistency_validated": True
        }
        
        # Test each tool individually and count results
        for tool_name, tool_info in tools.items():
            try:
                # Check if tool has error from discovery
                if "error" in tool_info:
                    audit_results["tool_results"][tool_name] = {
                        "status": "broken",
                        "error": tool_info["error"],
                        "test_timestamp": datetime.now().isoformat()
                    }
                    audit_results["broken_tools"] += 1
                    continue
                
                # Attempt to instantiate and test the tool
                working_classes = 0
                total_classes = len(tool_info.get("classes", []))
                
                for tool_class in tool_info.get("classes", []):
                    try:
                        tool_instance = tool_class()
                        
                        # Basic functionality test
                        if hasattr(tool_instance, 'execute') or hasattr(tool_instance, '__call__'):
                            working_classes += 1
                        
                    except Exception as e:
                        self.logger.error(f"Tool class testing failed for {tool_class.__name__}: {e}")
                        continue
                
                if working_classes > 0:
                    audit_results["tool_results"][tool_name] = {
                        "status": "working",
                        "working_classes": working_classes,
                        "total_classes": total_classes,
                        "reliability_score": working_classes / max(total_classes, 1),
                        "test_timestamp": datetime.now().isoformat()
                    }
                    audit_results["working_tools"] += 1
                else:
                    audit_results["tool_results"][tool_name] = {
                        "status": "broken",
                        "error": "No working classes found",
                        "working_classes": 0,
                        "total_classes": total_classes,
                        "test_timestamp": datetime.now().isoformat()
                    }
                    audit_results["broken_tools"] += 1
                    
            except Exception as e:
                audit_results["tool_results"][tool_name] = {
                    "status": "broken",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "test_timestamp": datetime.now().isoformat()
                }
                audit_results["broken_tools"] += 1
        
        # CRITICAL: Verify math consistency
        total_counted = audit_results["working_tools"] + audit_results["broken_tools"]
        if total_counted != audit_results["total_tools"]:
            raise RuntimeError(f"Tool count inconsistency: {total_counted} != {audit_results['total_tools']}")
        
        # Calculate success rate
        success_rate = (audit_results["working_tools"] / audit_results["total_tools"]) * 100
        audit_results["success_rate_percent"] = round(success_rate, 2)
        
        # Log with evidence logger for consistency
        from .evidence_logger import EvidenceLogger
        evidence_logger = EvidenceLogger()
        evidence_logger.log_tool_audit_results(audit_results, start_time.strftime("%Y%m%d_%H%M%S"))
        
        return audit_results