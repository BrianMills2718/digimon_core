"""
Consistency Validator

Validates consistency of tool operations and environment state.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime


class ConsistencyValidator:
    """Validates consistency of tool operations and environment state"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_consistency_metrics(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate consistency metrics from audit results"""
        metrics: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "environment_stability": True,
            "memory_consistency": True,
            "thread_consistency": True,
            "process_consistency": True,
            "tool_behavior_consistency": True,
            "overall_consistency_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Analyze environment stability
            if "tool_results" in audit_results:
                metrics.update(self._analyze_environment_stability(audit_results["tool_results"]))
            
            # Calculate overall consistency score
            consistency_factors = [
                metrics["environment_stability"],
                metrics["memory_consistency"],
                metrics["thread_consistency"],
                metrics["process_consistency"],
                metrics["tool_behavior_consistency"]
            ]
            
            metrics["overall_consistency_score"] = sum(consistency_factors) / len(consistency_factors)
            
            # Generate recommendations based on issues
            if metrics["overall_consistency_score"] < 0.8:
                metrics["recommendations"].append("System consistency below 80% - investigate environmental issues")
            
            if not metrics["environment_stability"]:
                metrics["recommendations"].append("Environment instability detected - review resource cleanup")
            
        except Exception as e:
            self.logger.error(f"Consistency metrics calculation failed: {e}")
            metrics["calculation_error"] = str(e)
            metrics["overall_consistency_score"] = 0.0
        
        return metrics
    
    def _analyze_environment_stability(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environment stability across tool executions"""
        stability_metrics: Dict[str, Any] = {
            "environment_stability": True,
            "memory_consistency": True,
            "thread_consistency": True,
            "process_consistency": True,
            "tool_behavior_consistency": True,
            "issues": []
        }
        
        memory_leaks = 0
        thread_leaks = 0
        process_changes = 0
        inconsistent_behaviors = 0
        
        for tool_name, tool_result in tool_results.items():
            try:
                # Check environment impact
                env_impact = tool_result.get("environment_impact", {})
                
                # Memory leak detection
                memory_impact = env_impact.get("memory_impact", {})
                if memory_impact.get("leak_detected", False):
                    memory_leaks += 1
                    stability_metrics["issues"].append(f"Memory leak detected in {tool_name}")
                
                # Thread leak detection
                thread_impact = env_impact.get("thread_impact", {})
                if thread_impact.get("leak_detected", False):
                    thread_leaks += 1
                    stability_metrics["issues"].append(f"Thread leak detected in {tool_name}")
                
                # Process changes
                process_impact = env_impact.get("process_impact", {})
                if process_impact.get("leak_detected", False):
                    process_changes += 1
                    stability_metrics["issues"].append(f"Process count changed in {tool_name}")
                
                # Tool behavior consistency
                if tool_result.get("status") not in ["working", "failed"]:
                    inconsistent_behaviors += 1
                    stability_metrics["issues"].append(f"Inconsistent behavior in {tool_name}")
                
            except Exception as e:
                self.logger.warning(f"Could not analyze stability for {tool_name}: {e}")
                inconsistent_behaviors += 1
        
        # Set consistency flags based on thresholds
        total_tools = len(tool_results)
        if total_tools > 0:
            if memory_leaks > total_tools * 0.1:  # More than 10% have memory leaks
                stability_metrics["memory_consistency"] = False
                stability_metrics["environment_stability"] = False
            
            if thread_leaks > total_tools * 0.1:  # More than 10% have thread leaks
                stability_metrics["thread_consistency"] = False
                stability_metrics["environment_stability"] = False
            
            if process_changes > total_tools * 0.05:  # More than 5% change process count
                stability_metrics["process_consistency"] = False
                stability_metrics["environment_stability"] = False
            
            if inconsistent_behaviors > total_tools * 0.15:  # More than 15% inconsistent
                stability_metrics["tool_behavior_consistency"] = False
        
        return stability_metrics
    
    def validate_tool_consistency(self, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate consistency across multiple tool execution results"""
        validation: Dict[str, Any] = {
            "consistent": True,
            "total_executions": len(tool_results),
            "consistent_executions": 0,
            "inconsistent_executions": 0,
            "consistency_score": 0.0,
            "issues": [],
            "patterns": {
                "success_rate_variance": 0.0,
                "execution_time_variance": 0.0,
                "memory_usage_variance": 0.0
            }
        }
        
        if not tool_results:
            return validation
        
        try:
            # Analyze execution patterns
            success_rates = []
            execution_times = []
            memory_usages = []
            
            for result in tool_results:
                # Success rate analysis
                total_tools = result.get("total_tools", 0)
                working_tools = result.get("working_tools", 0)
                if total_tools > 0:
                    success_rate = working_tools / total_tools
                    success_rates.append(success_rate)
                
                # Execution time analysis (if available)
                if "execution_time" in result:
                    execution_times.append(result["execution_time"])
                
                # Memory usage analysis (if available)
                final_env = result.get("final_environment", {})
                if "memory_percent" in final_env:
                    memory_usages.append(final_env["memory_percent"])
            
            # Calculate variances
            if success_rates:
                avg_success = sum(success_rates) / len(success_rates)
                validation["patterns"]["success_rate_variance"] = sum(
                    (rate - avg_success) ** 2 for rate in success_rates
                ) / len(success_rates)
            
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                validation["patterns"]["execution_time_variance"] = sum(
                    (time - avg_time) ** 2 for time in execution_times
                ) / len(execution_times)
            
            if memory_usages:
                avg_memory = sum(memory_usages) / len(memory_usages)
                validation["patterns"]["memory_usage_variance"] = sum(
                    (mem - avg_memory) ** 2 for mem in memory_usages
                ) / len(memory_usages)
            
            # Determine consistency based on variance thresholds
            high_variance_count = 0
            
            if validation["patterns"]["success_rate_variance"] > 0.01:  # 1% variance threshold
                validation["issues"].append("High variance in success rates across executions")
                high_variance_count += 1
            
            if validation["patterns"]["execution_time_variance"] > 100:  # 100 second variance threshold
                validation["issues"].append("High variance in execution times")
                high_variance_count += 1
            
            if validation["patterns"]["memory_usage_variance"] > 25:  # 25% memory variance threshold
                validation["issues"].append("High variance in memory usage")
                high_variance_count += 1
            
            # Calculate consistency metrics
            validation["consistent_executions"] = max(0, len(tool_results) - high_variance_count)
            validation["inconsistent_executions"] = high_variance_count
            
            if len(tool_results) > 0:
                validation["consistency_score"] = validation["consistent_executions"] / len(tool_results)
                validation["consistent"] = validation["consistency_score"] >= 0.8
            
        except Exception as e:
            self.logger.error(f"Tool consistency validation failed: {e}")
            validation["validation_error"] = str(e)
            validation["consistent"] = False
        
        return validation
    
    def generate_consistency_report(self, consistency_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive consistency report"""
        report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "CONSISTENT" if consistency_metrics.get("overall_consistency_score", 0) >= 0.8 else "INCONSISTENT",
            "consistency_score": consistency_metrics.get("overall_consistency_score", 0.0),
            "summary": {
                "environment_stable": consistency_metrics.get("environment_stability", False),
                "memory_consistent": consistency_metrics.get("memory_consistency", False),
                "thread_consistent": consistency_metrics.get("thread_consistency", False),
                "process_consistent": consistency_metrics.get("process_consistency", False),
                "tool_behavior_consistent": consistency_metrics.get("tool_behavior_consistency", False)
            },
            "issues_found": len(consistency_metrics.get("issues", [])),
            "critical_issues": [],
            "recommendations": consistency_metrics.get("recommendations", []),
            "detailed_analysis": consistency_metrics
        }
        
        # Categorize critical issues
        issues = consistency_metrics.get("issues", [])
        for issue in issues:
            if any(keyword in issue.lower() for keyword in ["leak", "crash", "timeout", "failure"]):
                report["critical_issues"].append(issue)
        
        # Add severity assessment
        if report["consistency_score"] < 0.5:
            report["severity"] = "CRITICAL"
            report["recommendations"].insert(0, "Immediate action required - system consistency critically compromised")
        elif report["consistency_score"] < 0.7:
            report["severity"] = "HIGH"
            report["recommendations"].insert(0, "High priority fixes needed for system stability")
        elif report["consistency_score"] < 0.9:
            report["severity"] = "MEDIUM"
        else:
            report["severity"] = "LOW"
        
        return report