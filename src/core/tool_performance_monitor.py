import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from threading import Lock
from collections import defaultdict, deque

from src.core.config_manager import get_config


class ToolPerformanceMonitor:
    """
    Service responsible for tracking and caching tool performance metrics.
    
    Monitors execution times, success rates, resource usage, and provides
    performance-based recommendations for tool optimization.
    """
    
    def __init__(self, max_history_size: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history_size: Maximum number of performance records to keep per tool
        """
        self.max_history_size = max_history_size
        self.performance_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history_size))
        self.performance_cache: Dict[str, Dict[str, Any]] = {}
        self.success_rates: Dict[str, float] = {}
        self.cache_lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        # Get configuration
        self.config = get_config()
        
        # Performance thresholds
        self.slow_execution_threshold = 5.0  # seconds
        self.high_memory_threshold = 100.0   # MB
        self.low_success_threshold = 80.0    # percentage
        
    def track_tool_performance(self, tool_name: str, execution_time: float, 
                             memory_usage: Optional[float] = None,
                             success: bool = True,
                             error_message: Optional[str] = None,
                             additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Record performance metrics for a tool execution.
        
        Args:
            tool_name: Name of the tool
            execution_time: Execution time in seconds
            memory_usage: Memory usage in MB (optional)
            success: Whether the execution was successful
            error_message: Error message if execution failed
            additional_metrics: Additional performance metrics
        """
        timestamp = datetime.now()
        
        performance_record = {
            "timestamp": timestamp.isoformat(),
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "success": success,
            "error_message": error_message,
            "additional_metrics": additional_metrics or {}
        }
        
        with self.cache_lock:
            # Add to performance history
            self.performance_data[tool_name].append(performance_record)
            
            # Update cached success rate
            self._update_success_rate(tool_name)
            
            # Update performance cache
            self._update_performance_cache(tool_name)
        
        self.logger.debug(f"Tracked performance for {tool_name}: {execution_time:.2f}s, success={success}")
    
    def get_tool_performance_summary(self, tool_name: str) -> Dict[str, Any]:
        """
        Get comprehensive performance summary for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary containing performance summary
        """
        with self.cache_lock:
            if tool_name not in self.performance_data or not self.performance_data[tool_name]:
                return {
                    "tool_name": tool_name,
                    "status": "no_data",
                    "total_executions": 0
                }
            
            records = list(self.performance_data[tool_name])
            
            # Calculate basic statistics
            execution_times = [r["execution_time"] for r in records]
            successful_executions = [r for r in records if r["success"]]
            failed_executions = [r for r in records if not r["success"]]
            
            summary = {
                "tool_name": tool_name,
                "total_executions": len(records),
                "successful_executions": len(successful_executions),
                "failed_executions": len(failed_executions),
                "success_rate": self.success_rates.get(tool_name, 0.0),
                "execution_time_stats": self._calculate_time_stats(execution_times),
                "memory_usage_stats": self._calculate_memory_stats(records),
                "recent_performance": self._get_recent_performance(tool_name),
                "performance_trend": self._calculate_performance_trend(tool_name),
                "recommendations": self._generate_performance_recommendations(tool_name, records)
            }
            
            return summary
    
    def get_success_rate(self, tool_name: str) -> float:
        """
        Calculate tool success rate.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Success rate as percentage (0.0 to 100.0)
        """
        with self.cache_lock:
            return self.success_rates.get(tool_name, 0.0)
    
    def get_all_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance statistics for all monitored tools.
        
        Returns:
            Dictionary mapping tool names to their performance stats
        """
        stats = {}
        
        for tool_name in self.performance_data.keys():
            stats[tool_name] = self.get_tool_performance_summary(tool_name)
        
        return stats
    
    def get_top_performers(self, metric: str = "success_rate", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing tools based on specified metric.
        
        Args:
            metric: Metric to sort by ('success_rate', 'avg_execution_time', 'total_executions')
            limit: Maximum number of tools to return
            
        Returns:
            List of top performing tools with their metrics
        """
        all_stats = self.get_all_performance_stats()
        
        # Filter tools with sufficient data
        valid_tools = {name: stats for name, stats in all_stats.items() 
                      if stats.get("total_executions", 0) > 0}
        
        # Sort by specified metric
        if metric == "success_rate":
            sorted_tools = sorted(valid_tools.items(), 
                                key=lambda x: x[1].get("success_rate", 0), 
                                reverse=True)
        elif metric == "avg_execution_time":
            sorted_tools = sorted(valid_tools.items(), 
                                key=lambda x: x[1].get("execution_time_stats", {}).get("mean", float('inf')))
        elif metric == "total_executions":
            sorted_tools = sorted(valid_tools.items(), 
                                key=lambda x: x[1].get("total_executions", 0), 
                                reverse=True)
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        return [{"tool_name": name, "stats": stats} for name, stats in sorted_tools[:limit]]
    
    def get_performance_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify tools with performance issues.
        
        Returns:
            Dictionary categorizing performance issues
        """
        issues = {
            "slow_tools": [],
            "high_memory_tools": [],
            "unreliable_tools": [],
            "error_prone_tools": []
        }
        
        all_stats = self.get_all_performance_stats()
        
        for tool_name, stats in all_stats.items():
            if stats.get("total_executions", 0) == 0:
                continue
            
            # Check for slow execution
            avg_time = stats.get("execution_time_stats", {}).get("mean", 0)
            if avg_time > self.slow_execution_threshold:
                issues["slow_tools"].append({
                    "tool_name": tool_name,
                    "avg_execution_time": avg_time,
                    "threshold": self.slow_execution_threshold
                })
            
            # Check for high memory usage
            avg_memory = stats.get("memory_usage_stats", {}).get("mean", 0)
            if avg_memory > self.high_memory_threshold:
                issues["high_memory_tools"].append({
                    "tool_name": tool_name,
                    "avg_memory_usage": avg_memory,
                    "threshold": self.high_memory_threshold
                })
            
            # Check for low success rate
            success_rate = stats.get("success_rate", 100)
            if success_rate < self.low_success_threshold:
                issues["unreliable_tools"].append({
                    "tool_name": tool_name,
                    "success_rate": success_rate,
                    "threshold": self.low_success_threshold
                })
            
            # Check for high error rate
            failed_executions = stats.get("failed_executions", 0)
            total_executions = stats.get("total_executions", 1)
            error_rate = (failed_executions / total_executions) * 100
            if error_rate > 20:  # More than 20% errors
                issues["error_prone_tools"].append({
                    "tool_name": tool_name,
                    "error_rate": error_rate,
                    "failed_executions": failed_executions,
                    "total_executions": total_executions
                })
        
        return issues
    
    def cache_performance_data(self, tool_name: str, cache_key: str, data: Any, 
                             ttl_seconds: int = 3600) -> None:
        """
        Cache performance-related data with TTL.
        
        Args:
            tool_name: Name of the tool
            cache_key: Key for the cached data
            data: Data to cache
            ttl_seconds: Time to live in seconds
        """
        expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
        
        with self.cache_lock:
            if tool_name not in self.performance_cache:
                self.performance_cache[tool_name] = {}
            
            self.performance_cache[tool_name][cache_key] = {
                "data": data,
                "expiry": expiry_time.isoformat(),
                "cached_at": datetime.now().isoformat()
            }
        
        self.logger.debug(f"Cached performance data for {tool_name}:{cache_key}")
    
    def get_cached_data(self, tool_name: str, cache_key: str) -> Optional[Any]:
        """
        Retrieve cached performance data.
        
        Args:
            tool_name: Name of the tool
            cache_key: Key for the cached data
            
        Returns:
            Cached data or None if expired/not found
        """
        with self.cache_lock:
            if tool_name not in self.performance_cache:
                return None
            
            if cache_key not in self.performance_cache[tool_name]:
                return None
            
            cache_entry = self.performance_cache[tool_name][cache_key]
            expiry_time = datetime.fromisoformat(cache_entry["expiry"])
            
            if datetime.now() > expiry_time:
                # Cache expired, remove it
                del self.performance_cache[tool_name][cache_key]
                return None
            
            return cache_entry["data"]
    
    def clear_performance_data(self, tool_name: Optional[str] = None) -> None:
        """
        Clear performance data for a specific tool or all tools.
        
        Args:
            tool_name: Name of the tool, or None to clear all data
        """
        with self.cache_lock:
            if tool_name:
                if tool_name in self.performance_data:
                    self.performance_data[tool_name].clear()
                if tool_name in self.performance_cache:
                    del self.performance_cache[tool_name]
                if tool_name in self.success_rates:
                    del self.success_rates[tool_name]
                self.logger.info(f"Cleared performance data for tool: {tool_name}")
            else:
                self.performance_data.clear()
                self.performance_cache.clear()
                self.success_rates.clear()
                self.logger.info("Cleared all performance data")
    
    def export_performance_data(self, tool_name: Optional[str] = None, 
                               format: str = "json") -> Dict[str, Any]:
        """
        Export performance data for analysis.
        
        Args:
            tool_name: Specific tool name, or None for all tools
            format: Export format ('json', 'csv_ready')
            
        Returns:
            Exported performance data
        """
        with self.cache_lock:
            if tool_name:
                if tool_name not in self.performance_data:
                    return {"error": f"No data for tool: {tool_name}"}
                
                data = {
                    "tool_name": tool_name,
                    "records": list(self.performance_data[tool_name]),
                    "summary": self.get_tool_performance_summary(tool_name),
                    "export_timestamp": datetime.now().isoformat()
                }
            else:
                data = {
                    "all_tools": {name: list(records) for name, records in self.performance_data.items()},
                    "summaries": self.get_all_performance_stats(),
                    "export_timestamp": datetime.now().isoformat()
                }
            
            if format == "csv_ready":
                # Convert to CSV-friendly format
                return self._convert_to_csv_ready(data)
            
            return data
    
    def _update_success_rate(self, tool_name: str) -> None:
        """Update cached success rate for a tool."""
        if tool_name not in self.performance_data or not self.performance_data[tool_name]:
            self.success_rates[tool_name] = 0.0
            return
        
        records = list(self.performance_data[tool_name])
        successful = sum(1 for r in records if r["success"])
        total = len(records)
        
        self.success_rates[tool_name] = (successful / total * 100) if total > 0 else 0.0
    
    def _update_performance_cache(self, tool_name: str) -> None:
        """Update cached performance metrics for a tool."""
        if tool_name not in self.performance_data or not self.performance_data[tool_name]:
            return
        
        records = list(self.performance_data[tool_name])
        execution_times = [r["execution_time"] for r in records]
        
        # Cache basic statistics
        if tool_name not in self.performance_cache:
            self.performance_cache[tool_name] = {}
        
        self.performance_cache[tool_name]["basic_stats"] = {
            "data": {
                "total_executions": len(records),
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "success_rate": self.success_rates[tool_name],
                "last_updated": datetime.now().isoformat()
            },
            "expiry": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "cached_at": datetime.now().isoformat()
        }
    
    def _calculate_time_stats(self, execution_times: List[float]) -> Dict[str, float]:
        """Calculate execution time statistics."""
        if not execution_times:
            return {"mean": 0, "min": 0, "max": 0, "median": 0}
        
        sorted_times = sorted(execution_times)
        n = len(sorted_times)
        
        return {
            "mean": sum(execution_times) / n,
            "min": min(execution_times),
            "max": max(execution_times),
            "median": sorted_times[n // 2] if n % 2 == 1 else (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2,
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0,
            "p99": sorted_times[int(n * 0.99)] if n > 0 else 0
        }
    
    def _calculate_memory_stats(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate memory usage statistics."""
        memory_values = [r["memory_usage"] for r in records if r["memory_usage"] is not None]
        
        if not memory_values:
            return {"mean": 0, "min": 0, "max": 0, "median": 0}
        
        sorted_memory = sorted(memory_values)
        n = len(sorted_memory)
        
        return {
            "mean": sum(memory_values) / n,
            "min": min(memory_values),
            "max": max(memory_values),
            "median": sorted_memory[n // 2] if n % 2 == 1 else (sorted_memory[n // 2 - 1] + sorted_memory[n // 2]) / 2
        }
    
    def _get_recent_performance(self, tool_name: str, window_minutes: int = 30) -> Dict[str, Any]:
        """Get performance metrics for recent executions."""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        if tool_name not in self.performance_data:
            return {"recent_executions": 0}
        
        recent_records = [
            r for r in self.performance_data[tool_name]
            if datetime.fromisoformat(r["timestamp"]) > cutoff_time
        ]
        
        if not recent_records:
            return {"recent_executions": 0}
        
        successful = sum(1 for r in recent_records if r["success"])
        execution_times = [r["execution_time"] for r in recent_records]
        
        return {
            "recent_executions": len(recent_records),
            "recent_success_rate": (successful / len(recent_records)) * 100,
            "recent_avg_time": sum(execution_times) / len(execution_times),
            "window_minutes": window_minutes
        }
    
    def _calculate_performance_trend(self, tool_name: str) -> str:
        """Calculate performance trend (improving, stable, degrading)."""
        if tool_name not in self.performance_data or len(self.performance_data[tool_name]) < 10:
            return "insufficient_data"
        
        records = list(self.performance_data[tool_name])
        
        # Compare first half vs second half
        mid_point = len(records) // 2
        first_half = records[:mid_point]
        second_half = records[mid_point:]
        
        first_half_avg = sum(r["execution_time"] for r in first_half) / len(first_half)
        second_half_avg = sum(r["execution_time"] for r in second_half) / len(second_half)
        
        improvement_threshold = 0.1  # 10% improvement
        degradation_threshold = 0.1  # 10% degradation
        
        if second_half_avg < first_half_avg * (1 - improvement_threshold):
            return "improving"
        elif second_half_avg > first_half_avg * (1 + degradation_threshold):
            return "degrading"
        else:
            return "stable"
    
    def _generate_performance_recommendations(self, tool_name: str, 
                                            records: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations for a tool."""
        recommendations = []
        
        if not records:
            return ["No performance data available for analysis"]
        
        # Analyze execution times
        execution_times = [r["execution_time"] for r in records]
        avg_time = sum(execution_times) / len(execution_times)
        
        if avg_time > self.slow_execution_threshold:
            recommendations.append(f"Tool is slow (avg: {avg_time:.2f}s). Consider optimization.")
        
        # Analyze success rate
        successful = sum(1 for r in records if r["success"])
        success_rate = (successful / len(records)) * 100
        
        if success_rate < self.low_success_threshold:
            recommendations.append(f"Low success rate ({success_rate:.1f}%). Investigate error patterns.")
        
        # Analyze memory usage
        memory_values = [r["memory_usage"] for r in records if r["memory_usage"] is not None]
        if memory_values:
            avg_memory = sum(memory_values) / len(memory_values)
            if avg_memory > self.high_memory_threshold:
                recommendations.append(f"High memory usage (avg: {avg_memory:.1f}MB). Consider memory optimization.")
        
        # Analyze error patterns
        error_messages = [r["error_message"] for r in records if r["error_message"]]
        if error_messages:
            # Find most common errors
            error_counts = defaultdict(int)
            for error in error_messages:
                error_counts[error] += 1
            
            most_common_error = max(error_counts.items(), key=lambda x: x[1])
            if most_common_error[1] > len(records) * 0.1:  # More than 10% of executions
                recommendations.append(f"Common error pattern: '{most_common_error[0]}' ({most_common_error[1]} occurrences)")
        
        if not recommendations:
            recommendations.append("Performance looks good. No specific recommendations.")
        
        return recommendations
    
    def _convert_to_csv_ready(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert performance data to CSV-friendly format."""
        # This is a simplified version - could be expanded for full CSV export
        csv_data = {
            "format": "csv_ready",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        return csv_data