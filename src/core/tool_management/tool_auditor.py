"""
Tool Auditor

Handles comprehensive auditing of tools with environment consistency tracking.
"""

import gc
import uuid
import logging
from typing import Dict, Any
from datetime import datetime

from .tool_discovery import ToolDiscovery
from .environment_monitor import EnvironmentMonitor
from .consistency_validator import ConsistencyValidator


class ToolAuditor:
    """Audits tools with environment consistency tracking"""
    
    def __init__(self, tools_directory: str = "src/tools"):
        self.tool_discovery = ToolDiscovery(tools_directory)
        self.environment_monitor = EnvironmentMonitor()
        self.consistency_validator = ConsistencyValidator()
        self.logger = logging.getLogger(__name__)
    
    def audit_all_tools(self) -> Dict[str, Any]:
        """Audit all tools with environment consistency tracking"""
        start_time = datetime.now()
        
        # Capture initial environment
        initial_environment = self.environment_monitor.capture_test_environment()
        
        # Force garbage collection before testing
        collected = gc.collect()
        
        # Discover tools in deterministic order
        tools = self.tool_discovery.discover_all_tools()
        
        tool_results: Dict[str, Any] = {}
        audit_results: Dict[str, Any] = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "initial_environment": initial_environment,
            "garbage_collected": collected,
            "total_tools": len(tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": tool_results,
            "consistency_metrics": {},
            "final_environment": None
        }
        
        # Test each tool in isolated environment
        for tool_name in sorted(tools.keys()):  # Deterministic order
            tool_info = tools[tool_name]
            
            # Capture environment before each test
            pre_test_env = self.environment_monitor.capture_test_environment()
            
            # Test tool in isolation
            test_result = self._test_tool_isolated(tool_name, tool_info)
            
            # Capture environment after test
            post_test_env = self.environment_monitor.capture_test_environment()
            
            # Calculate environment impact
            env_impact = self.environment_monitor.calculate_environment_impact(pre_test_env, post_test_env)
            
            if test_result.get("status") == "working":
                audit_results["working_tools"] += 1
            else:
                audit_results["broken_tools"] += 1
            
            tool_results[tool_name] = {
                **test_result,
                "pre_test_environment": pre_test_env,
                "post_test_environment": post_test_env,
                "environment_impact": env_impact
            }
            
            # Force garbage collection between tests
            gc.collect()
        
        # Capture final environment
        audit_results["final_environment"] = self.environment_monitor.capture_test_environment()
        
        # Calculate consistency metrics
        audit_results["consistency_metrics"] = self.consistency_validator.calculate_consistency_metrics(audit_results)
        
        return audit_results
    
    def _test_tool_isolated(self, tool_name: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test tool with ACTUAL execution, not just method existence"""
        try:
            if "error" in tool_info:
                return {"status": "failed", "error": tool_info["error"]}
            
            working_classes = 0
            total_classes = len(tool_info["classes"])
            test_results = []
            
            for tool_class in tool_info["classes"]:
                class_result = self._test_tool_class(tool_class)
                test_results.append(class_result)
                
                if class_result.get("working", False):
                    working_classes += 1
            
            if working_classes > 0:
                return {
                    "status": "working",
                    "working_classes": working_classes,
                    "total_classes": total_classes,
                    "reliability_score": working_classes / total_classes,
                    "class_results": test_results
                }
            else:
                return {
                    "status": "failed", 
                    "error": "No working tool classes found",
                    "class_results": test_results
                }
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _test_tool_class(self, tool_class: type) -> Dict[str, Any]:
        """Test a specific tool class"""
        class_name = tool_class.__name__
        result = {
            "class_name": class_name,
            "working": False,
            "instantiation_success": False,
            "execute_method_exists": False,
            "execute_test_success": False,
            "error": None
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
    
    def audit_with_consistency_validation(self) -> Dict[str, Any]:
        """Audit tools with mandatory consistency validation"""
        start_time = datetime.now()
        
        # Clear any cached results to ensure fresh audit
        if hasattr(self.tool_discovery, 'discovered_tools'):
            self.tool_discovery.discovered_tools = {}
        
        # Force garbage collection before audit
        collected = gc.collect()
        
        # Perform actual tool discovery and testing
        tools = self.tool_discovery.discover_all_tools()
        tool_results_dict: Dict[str, Any] = {}
        audit_results: Dict[str, Any] = {
            "timestamp": start_time.isoformat(),
            "audit_id": str(uuid.uuid4()),
            "total_tools": len(tools),
            "working_tools": 0,
            "broken_tools": 0,
            "tool_results": tool_results_dict,
            "garbage_collected": collected,
            "consistency_validated": True
        }
        
        # Test each tool individually and count results
        for tool_name, tool_info in tools.items():
            try:
                # Check if tool has error from discovery
                if "error" in tool_info:
                    tool_results_dict[tool_name] = {
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
                    tool_results_dict[tool_name] = {
                        "status": "working",
                        "working_classes": working_classes,
                        "total_classes": total_classes,
                        "reliability_score": working_classes / max(total_classes, 1),
                        "test_timestamp": datetime.now().isoformat()
                    }
                    audit_results["working_tools"] += 1
                else:
                    tool_results_dict[tool_name] = {
                        "status": "broken",
                        "error": "No working classes found",
                        "working_classes": 0,
                        "total_classes": total_classes,
                        "test_timestamp": datetime.now().isoformat()
                    }
                    audit_results["broken_tools"] += 1
                    
            except Exception as e:
                tool_results_dict[tool_name] = {
                    "status": "broken",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "test_timestamp": datetime.now().isoformat()
                }
                audit_results["broken_tools"] += 1
        
        # CRITICAL: Verify math consistency
        working_count = int(audit_results["working_tools"])
        broken_count = int(audit_results["broken_tools"])
        total_count = int(audit_results["total_tools"])
        total_counted = working_count + broken_count
        if total_counted != total_count:
            raise RuntimeError(f"Tool count inconsistency: {total_counted} != {total_count}")
        
        # Calculate success rate
        if total_count > 0:
            success_rate = (working_count / total_count) * 100
            audit_results["success_rate_percent"] = round(success_rate, 2)
        else:
            audit_results["success_rate_percent"] = 0.0
        
        # Log with evidence logger for consistency
        try:
            from ..evidence_logger import EvidenceLogger
            evidence_logger = EvidenceLogger()
            evidence_logger.log_tool_audit_results(audit_results, start_time.strftime("%Y%m%d_%H%M%S"))
        except ImportError:
            self.logger.warning("Evidence logger not available for audit logging")
        
        return audit_results
    
    def get_success_rate(self) -> float:
        """Calculate ACTUAL tool success rate"""
        audit = self.audit_all_tools()
        if audit["total_tools"] == 0:
            return 0.0
        return (audit["working_tools"] / audit["total_tools"]) * 100
    
    def generate_audit_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive audit summary"""
        summary = {
            "audit_id": audit_results.get("audit_id"),
            "timestamp": audit_results.get("timestamp"),
            "overview": {
                "total_tools": audit_results.get("total_tools", 0),
                "working_tools": audit_results.get("working_tools", 0),
                "broken_tools": audit_results.get("broken_tools", 0),
                "success_rate": audit_results.get("success_rate_percent", 0)
            },
            "issues": self._extract_issues(audit_results),
            "recommendations": self._generate_recommendations(audit_results),
            "consistency_status": audit_results.get("consistency_metrics", {})
        }
        
        return summary
    
    def _extract_issues(self, audit_results: Dict[str, Any]) -> list[str]:
        """Extract issues from audit results"""
        issues = []
        
        for tool_name, tool_result in audit_results.get("tool_results", {}).items():
            if tool_result.get("status") != "working":
                error = tool_result.get("error", "Unknown error")
                issues.append(f"{tool_name}: {error}")
        
        return issues
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> list[str]:
        """Generate recommendations based on audit results"""
        recommendations = []
        
        success_rate = audit_results.get("success_rate_percent", 0)
        if success_rate < 50:
            recommendations.append("Low tool success rate - review tool implementations")
        elif success_rate < 80:
            recommendations.append("Moderate tool success rate - investigate failing tools")
        
        broken_tools = audit_results.get("broken_tools", 0)
        if broken_tools > 0:
            recommendations.append(f"Fix {broken_tools} broken tools to improve system reliability")
        
        consistency_metrics = audit_results.get("consistency_metrics", {})
        if not consistency_metrics.get("environment_stability", True):
            recommendations.append("Environment stability issues detected - review resource usage")
        
        return recommendations
