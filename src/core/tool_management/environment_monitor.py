"""
Environment Monitor

Monitors system environment during tool operations for consistency validation.
"""

import gc
import sys
import threading
import platform
from typing import Dict, Any
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class EnvironmentMonitor:
    """Monitors system environment for consistency validation"""
    
    def __init__(self):
        self.psutil_available = PSUTIL_AVAILABLE
    
    def capture_test_environment(self) -> Dict[str, Any]:
        """Capture comprehensive test environment for consistency validation"""
        try:
            environment = {
                "timestamp": datetime.now().isoformat(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "gc_counts": gc.get_count(),
                "gc_stats": gc.get_stats(),
                "python_executable": sys.executable,
                "python_path": sys.path[:5],  # First 5 entries
                "recursion_limit": sys.getrecursionlimit(),
                "thread_count": threading.active_count()
            }
            
            # Add system information if psutil is available
            if self.psutil_available:
                environment.update(self._capture_system_info())
            else:
                environment["system_info_unavailable"] = "psutil not installed"
            
            return environment
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "capture_failed": True
            }
    
    def _capture_system_info(self) -> Dict[str, Any]:
        """Capture system information using psutil"""
        info: Dict[str, Any] = {}
        
        try:
            # Memory information
            memory = psutil.virtual_memory()
            info.update({
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent
            })
            
            # CPU information
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            info.update({
                "cpu_count": cpu_count if cpu_count is not None else 0,
                "cpu_count_logical": cpu_count_logical if cpu_count_logical is not None else 0,
                "cpu_percent": psutil.cpu_percent(interval=1)
            })
            
            # Disk information
            disk_usage = psutil.disk_usage('/')
            info["disk_usage"] = {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent
            }
            
            # Process information
            info.update({
                "process_count": len(psutil.pids()),
                "boot_time": psutil.boot_time()
            })
            
            # Load average (if available)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
                info["load_average"] = {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                }
            
        except Exception as e:
            info["system_info_error"] = str(e)
        
        return info
    
    def calculate_environment_impact(self, pre_env: Dict[str, Any], post_env: Dict[str, Any]) -> Dict[str, Any]:
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
                pre_mem_available = float(pre_env["memory_available"])
                post_mem_available = float(post_env["memory_available"])
                memory_delta = post_mem_available - pre_mem_available
                
                pre_mem_percent = float(pre_env.get("memory_percent", 0.0))
                post_mem_percent = float(post_env.get("memory_percent", 0.0))
                memory_percent_delta = post_mem_percent - pre_mem_percent
                
                memory_impact = {
                    "available_bytes_change": memory_delta,
                    "percent_change": memory_percent_delta,
                    "leak_detected": memory_delta < -50 * 1024 * 1024,  # 50MB threshold
                    "excessive_usage": memory_percent_delta > 5.0  # 5% threshold
                }
                impact["memory_impact"] = memory_impact
                
                if memory_impact["leak_detected"] or memory_impact["excessive_usage"]:
                    impact["overall_stability"] = False

            # CPU impact analysis
            if "cpu_percent" in pre_env and "cpu_percent" in post_env:
                pre_cpu = float(pre_env["cpu_percent"])
                post_cpu = float(post_env["cpu_percent"])
                cpu_delta = post_cpu - pre_cpu
                
                cpu_impact = {
                    "percent_change": cpu_delta,
                    "excessive_usage": cpu_delta > 20.0,  # 20% threshold
                    "sustained_high_usage": post_cpu > 80.0
                }
                impact["cpu_impact"] = cpu_impact
                
                if cpu_impact["excessive_usage"] or cpu_impact["sustained_high_usage"]:
                    impact["overall_stability"] = False

            # Process impact analysis
            if "process_count" in pre_env and "process_count" in post_env:
                pre_process = int(pre_env["process_count"])
                post_process = int(post_env["process_count"])
                process_delta = post_process - pre_process
                
                process_impact = {
                    "count_change": process_delta,
                    "leak_detected": process_delta > 0,  # Any increase indicates leak
                    "excessive_processes": post_process > pre_process + 5
                }
                impact["process_impact"] = process_impact
                
                if process_impact["leak_detected"]:
                    impact["overall_stability"] = False

            # Thread impact analysis
            if "thread_count" in pre_env and "thread_count" in post_env:
                pre_thread = int(pre_env["thread_count"])
                post_thread = int(post_env["thread_count"])
                thread_delta = post_thread - pre_thread
                
                thread_impact = {
                    "count_change": thread_delta,
                    "leak_detected": thread_delta > 2,  # Allow 2 thread tolerance
                    "excessive_threads": post_thread > 50
                }
                impact["thread_impact"] = thread_impact
                
                if thread_impact["leak_detected"]:
                    impact["overall_stability"] = False

            # Disk impact analysis
            if "disk_usage" in pre_env and "disk_usage" in post_env:
                pre_disk = pre_env["disk_usage"]
                post_disk = post_env["disk_usage"]
                
                if isinstance(pre_disk, dict) and isinstance(post_disk, dict):
                    pre_used = float(pre_disk.get("used", 0))
                    post_used = float(post_disk.get("used", 0))
                    used_delta = post_used - pre_used
                    
                    post_free = float(post_disk.get("free", 0))
                    
                    disk_impact = {
                        "bytes_change": used_delta,
                        "significant_usage": used_delta > 100 * 1024 * 1024,  # 100MB threshold
                        "disk_space_concern": post_free < 1024 * 1024 * 1024  # 1GB free threshold
                    }
                    impact["disk_impact"] = disk_impact
                    
                    if disk_impact["significant_usage"]:
                        impact["overall_stability"] = False

        except Exception as e:
            impact["calculation_error"] = str(e)
            impact["overall_stability"] = False
            raise RuntimeError(f"Environment impact calculation failed: {e}")
        
        return impact
    
    def analyze_stability_trends(self, impact_history: list) -> Dict[str, Any]:
        """Analyze stability trends across multiple impact measurements"""
        recommendations: list[str] = []
        trends: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "measurements_analyzed": len(impact_history),
            "memory_trend": self._analyze_memory_trend(impact_history),
            "cpu_trend": self._analyze_cpu_trend(impact_history),
            "stability_trend": self._analyze_stability_trend(impact_history),
            "recommendations": recommendations
        }
        
        # Generate recommendations based on trends
        memory_trend = trends["memory_trend"]
        if isinstance(memory_trend, dict) and memory_trend.get("declining", False):
            recommendations.append("Memory usage trending upward - investigate memory leaks")
        
        cpu_trend = trends["cpu_trend"]
        if isinstance(cpu_trend, dict) and cpu_trend.get("high_usage_count", 0) > len(impact_history) * 0.3:
            recommendations.append("Frequent CPU spikes detected - optimize tool performance")
        
        stability_trend = trends["stability_trend"]
        if isinstance(stability_trend, dict) and not stability_trend.get("improving", False):
            recommendations.append("System stability not improving - review tool implementations")
        
        return trends
    
    def _analyze_memory_trend(self, impact_history: list) -> Dict[str, Any]:
        """Analyze memory usage trends"""
        memory_changes = []
        leak_count = 0
        
        for impact in impact_history:
            memory_impact = impact.get("memory_impact", {})
            if "available_bytes_change" in memory_impact:
                memory_changes.append(memory_impact["available_bytes_change"])
            if memory_impact.get("leak_detected", False):
                leak_count += 1
        
        trend: Dict[str, Any] = {
            "total_changes": len(memory_changes),
            "leak_count": leak_count,
            "declining": False,
            "average_change": 0.0
        }
        
        if memory_changes:
            trend["average_change"] = sum(memory_changes) / len(memory_changes)
            trend["declining"] = trend["average_change"] < -10 * 1024 * 1024  # 10MB threshold
        
        return trend
    
    def _analyze_cpu_trend(self, impact_history: list) -> Dict[str, Any]:
        """Analyze CPU usage trends"""
        cpu_changes = []
        high_usage_count = 0
        
        for impact in impact_history:
            cpu_impact = impact.get("cpu_impact", {})
            if "percent_change" in cpu_impact:
                cpu_changes.append(cpu_impact["percent_change"])
            if cpu_impact.get("excessive_usage", False):
                high_usage_count += 1
        
        trend: Dict[str, Any] = {
            "total_changes": len(cpu_changes),
            "high_usage_count": high_usage_count,
            "average_change": 0.0
        }
        
        if cpu_changes:
            trend["average_change"] = sum(cpu_changes) / len(cpu_changes)
        
        return trend
    
    def _analyze_stability_trend(self, impact_history: list) -> Dict[str, Any]:
        """Analyze overall stability trends"""
        stability_scores = []
        
        for impact in impact_history:
            stable = impact.get("overall_stability", True)
            stability_scores.append(1 if stable else 0)
        
        trend: Dict[str, Any] = {
            "total_measurements": len(stability_scores),
            "stable_count": sum(stability_scores),
            "stability_rate": 0.0,
            "improving": False
        }
        
        if stability_scores:
            trend["stability_rate"] = sum(stability_scores) / len(stability_scores)
            
            # Check if stability is improving (last half better than first half)
            if len(stability_scores) >= 4:
                mid_point = len(stability_scores) // 2
                first_half = stability_scores[:mid_point]
                second_half = stability_scores[mid_point:]
                
                first_rate = sum(first_half) / len(first_half)
                second_rate = sum(second_half) / len(second_half)
                
                trend["improving"] = second_rate > first_rate
        
        return trend
