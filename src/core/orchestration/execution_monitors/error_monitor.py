"""Error Monitor (<150 lines)

Monitors and handles errors during pipeline execution.
Provides error classification, recovery suggestions, and error aggregation.
"""

from typing import Dict, Any, List, Optional
import time
from datetime import datetime
from collections import defaultdict
from ...logging_config import get_logger

logger = get_logger("core.orchestration.error_monitor")


class ErrorMonitor:
    """Monitor and track errors during pipeline execution"""
    
    def __init__(self):
        self.logger = get_logger("core.orchestration.error_monitor")
        self.errors = []
        self.error_counts = defaultdict(int)
        self.error_patterns = defaultdict(list)
        self.start_time = None
        
    def record_error(self, error: Exception, tool_name: str = None, context: Dict[str, Any] = None):
        """Record an error that occurred during execution"""
        if self.start_time is None:
            self.start_time = time.time()
            
        error_info = {
            "timestamp": time.time(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "tool_name": tool_name,
            "context": context or {},
            "severity": self._classify_error_severity(error),
            "category": self._classify_error_category(error),
            "recovery_suggestion": self._get_recovery_suggestion(error)
        }
        
        self.errors.append(error_info)
        self.error_counts[error_info["error_type"]] += 1
        self.error_patterns[error_info["category"]].append(error_info)
        
        # Log based on severity
        if error_info["severity"] == "critical":
            self.logger.critical(f"Critical error in {tool_name}: {str(error)}")
        elif error_info["severity"] == "high":
            self.logger.error(f"High severity error in {tool_name}: {str(error)}")
        elif error_info["severity"] == "medium":
            self.logger.warning(f"Medium severity error in {tool_name}: {str(error)}")
        else:
            self.logger.info(f"Low severity error in {tool_name}: {str(error)}")
            
    def _classify_error_severity(self, error: Exception) -> str:
        """Classify error severity based on error type and message"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Critical errors that should stop execution
        if error_type in ["SystemError", "MemoryError", "RuntimeError"]:
            return "critical"
            
        if any(keyword in error_msg for keyword in ["cannot connect", "database error", "authentication failed"]):
            return "critical"
            
        # High severity errors that may cause significant issues
        if error_type in ["ValueError", "TypeError", "ImportError"]:
            return "high"
            
        if any(keyword in error_msg for keyword in ["validation failed", "missing required", "permission denied"]):
            return "high"
            
        # Medium severity errors that may cause partial failures
        if error_type in ["FileNotFoundError", "KeyError", "AttributeError"]:
            return "medium"
            
        if any(keyword in error_msg for keyword in ["timeout", "rate limit", "temporary failure"]):
            return "medium"
            
        # Low severity errors that are often recoverable
        return "low"
        
    def _classify_error_category(self, error: Exception) -> str:
        """Classify error into functional categories"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        if any(keyword in error_msg for keyword in ["file", "path", "directory", "read", "write"]):
            return "file_system"
            
        if any(keyword in error_msg for keyword in ["database", "neo4j", "connection", "query"]):
            return "database"
            
        if any(keyword in error_msg for keyword in ["api", "http", "network", "timeout", "connection"]):
            return "network"
            
        if any(keyword in error_msg for keyword in ["validation", "schema", "format", "type"]):
            return "validation"
            
        if any(keyword in error_msg for keyword in ["memory", "resource", "limit", "capacity"]):
            return "resource"
            
        if error_type in ["ImportError", "ModuleNotFoundError", "AttributeError"]:
            return "dependency"
            
        return "general"
        
    def _get_recovery_suggestion(self, error: Exception) -> str:
        """Provide recovery suggestions based on error type"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        if "file not found" in error_msg:
            return "Check if the file path is correct and the file exists"
            
        if "permission denied" in error_msg:
            return "Check file/directory permissions or run with appropriate privileges"
            
        if "connection" in error_msg and "refused" in error_msg:
            return "Check if the service is running and accessible"
            
        if "timeout" in error_msg:
            return "Increase timeout settings or check network connectivity"
            
        if "memory" in error_msg:
            return "Reduce memory usage or increase available memory"
            
        if "import" in error_msg.lower() or error_type == "ImportError":
            return "Install missing dependencies or check Python path"
            
        if "validation failed" in error_msg:
            return "Check input data format and ensure all required fields are present"
            
        if "rate limit" in error_msg:
            return "Reduce request frequency or implement exponential backoff"
            
        return "Review error details and check system logs for more information"
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error summary"""
        if not self.errors:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "severity_distribution": {},
                "category_distribution": {},
                "top_errors": [],
                "recovery_suggestions": []
            }
            
        total_time = time.time() - self.start_time if self.start_time else 1
        
        # Calculate severity distribution
        severity_counts = defaultdict(int)
        for error in self.errors:
            severity_counts[error["severity"]] += 1
            
        # Calculate category distribution
        category_counts = defaultdict(int)
        for error in self.errors:
            category_counts[error["category"]] += 1
            
        # Get top error types
        top_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Collect unique recovery suggestions
        recovery_suggestions = list(set([error["recovery_suggestion"] for error in self.errors]))
        
        return {
            "total_errors": len(self.errors),
            "error_rate": len(self.errors) / total_time,  # errors per second
            "severity_distribution": dict(severity_counts),
            "category_distribution": dict(category_counts),
            "top_errors": top_errors,
            "recovery_suggestions": recovery_suggestions,
            "recent_errors": self.errors[-5:] if len(self.errors) > 5 else self.errors  # Last 5 errors
        }
        
    def get_error_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get errors grouped by patterns/categories"""
        return dict(self.error_patterns)
        
    def has_critical_errors(self) -> bool:
        """Check if any critical errors have been recorded"""
        return any(error["severity"] == "critical" for error in self.errors)
        
    def get_error_trend(self) -> Dict[str, Any]:
        """Get error trend over time"""
        if len(self.errors) < 2:
            return {"trend": "insufficient_data"}
            
        # Calculate errors in recent vs earlier periods
        current_time = time.time()
        midpoint = self.start_time + (current_time - self.start_time) / 2
        
        recent_errors = len([e for e in self.errors if e["timestamp"] > midpoint])
        earlier_errors = len([e for e in self.errors if e["timestamp"] <= midpoint])
        
        if earlier_errors == 0:
            trend = "increasing"
        else:
            ratio = recent_errors / earlier_errors
            if ratio > 1.5:
                trend = "increasing"
            elif ratio < 0.5:
                trend = "decreasing"
            else:
                trend = "stable"
                
        return {
            "trend": trend,
            "recent_errors": recent_errors,
            "earlier_errors": earlier_errors,
            "ratio": recent_errors / earlier_errors if earlier_errors > 0 else float('inf')
        }
        
    def reset(self):
        """Reset error monitoring state"""
        self.errors.clear()
        self.error_counts.clear()
        self.error_patterns.clear()
        self.start_time = None
        
    def health_check(self) -> bool:
        """Check if error monitor is healthy"""
        return True  # Error monitor is always healthy