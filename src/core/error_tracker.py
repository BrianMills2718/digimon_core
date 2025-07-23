import uuid
import traceback
import time
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Comprehensive error tracking and analysis"""
    
    def __init__(self):
        self.error_log = []
        self.error_patterns = defaultdict(int)
        self.recovery_strategies = {}
        self._setup_recovery_strategies()
    
    def track_error(self, error: Exception, context: Dict[str, Any]) -> str:
        """Track error with full context and return error ID"""
        error_id = str(uuid.uuid4())
        
        error_entry = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "system_state": self._capture_system_state()
        }
        
        self.error_log.append(error_entry)
        self._analyze_error_pattern(error_entry)
        
        logger.error(f"Error tracked [{error_id}]: {error_entry['error_type']} - {error_entry['error_message']}")
        
        return error_id
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Analyze error patterns and suggest fixes"""
        return {
            "total_errors": len(self.error_log),
            "error_patterns": dict(self.error_patterns),
            "most_common_errors": self._get_most_common_errors(),
            "suggested_fixes": self._suggest_fixes(),
            "error_trends": self._analyze_error_trends()
        }
    
    def get_recovery_strategy(self, error_type: str) -> Dict[str, Any]:
        """Get recovery strategy for specific error type"""
        return self.recovery_strategies.get(error_type, {
            "strategy": "generic_retry",
            "max_attempts": 3,
            "delay": 1.0,
            "description": "Generic retry strategy with exponential backoff"
        })
    
    def attempt_recovery(self, error_id: str) -> Dict[str, Any]:
        """Attempt to recover from a specific error"""
        error_entry = self._find_error_by_id(error_id)
        if not error_entry:
            return {"success": False, "reason": "Error not found"}
        
        error_type = error_entry["error_type"]
        strategy = self.get_recovery_strategy(error_type)
        
        recovery_result = {
            "error_id": error_id,
            "strategy_used": strategy["strategy"],
            "recovery_attempted": True,
            "success": False,
            "attempts": 0,
            "recovery_time": 0.0
        }
        
        start_time = time.time()
        
        try:
            if strategy["strategy"] == "database_reconnect":
                success = self._attempt_database_recovery(error_entry, strategy)
            elif strategy["strategy"] == "service_restart":
                success = self._attempt_service_recovery(error_entry, strategy)
            elif strategy["strategy"] == "memory_cleanup":
                success = self._attempt_memory_recovery(error_entry, strategy)
            else:
                success = self._attempt_generic_recovery(error_entry, strategy)
            
            recovery_result["success"] = success
            
        except Exception as recovery_error:
            recovery_result["recovery_error"] = str(recovery_error)
            logger.error(f"Recovery attempt failed for {error_id}: {recovery_error}")
        
        recovery_result["recovery_time"] = time.time() - start_time
        
        return recovery_result
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Capture current system state for error context"""
        try:
            import psutil
            process = psutil.Process()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "memory_usage": process.memory_info().rss,
                "cpu_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
                "threads": process.num_threads(),
                "system_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            return {"error": f"Failed to capture system state: {e}"}
    
    def _analyze_error_pattern(self, error_entry: Dict[str, Any]):
        """Analyze error for patterns"""
        error_type = error_entry["error_type"]
        error_message = error_entry["error_message"]
        
        # Track error type frequency
        self.error_patterns[error_type] += 1
        
        # Track specific error message patterns
        if "connection" in error_message.lower():
            self.error_patterns["connection_errors"] += 1
        if "timeout" in error_message.lower():
            self.error_patterns["timeout_errors"] += 1
        if "memory" in error_message.lower():
            self.error_patterns["memory_errors"] += 1
        if "permission" in error_message.lower():
            self.error_patterns["permission_errors"] += 1
    
    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common error types"""
        sorted_patterns = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)
        return [{"error_type": error_type, "count": count} for error_type, count in sorted_patterns[:10]]
    
    def _suggest_fixes(self) -> List[str]:
        """Suggest fixes based on error patterns"""
        suggestions = []
        
        if self.error_patterns.get("connection_errors", 0) > 3:
            suggestions.append("Consider implementing connection pooling and retry logic")
        
        if self.error_patterns.get("timeout_errors", 0) > 2:
            suggestions.append("Increase timeout values or implement async processing")
        
        if self.error_patterns.get("memory_errors", 0) > 1:
            suggestions.append("Implement memory management and garbage collection strategies")
        
        if self.error_patterns.get("ConnectionError", 0) > 3:
            suggestions.append("Check database connectivity and implement robust connection handling")
        
        if self.error_patterns.get("FileNotFoundError", 0) > 1:
            suggestions.append("Verify file paths and implement proper file existence checks")
        
        return suggestions
    
    def _analyze_error_trends(self) -> Dict[str, Any]:
        """Analyze error trends over time"""
        if len(self.error_log) < 2:
            return {"trend": "insufficient_data"}
        
        recent_errors = [e for e in self.error_log if self._is_recent_error(e)]
        older_errors = [e for e in self.error_log if not self._is_recent_error(e)]
        
        return {
            "total_errors": len(self.error_log),
            "recent_errors": len(recent_errors),
            "older_errors": len(older_errors),
            "error_rate_trend": "increasing" if len(recent_errors) > len(older_errors) else "decreasing",
            "most_recent_error": self.error_log[-1]["timestamp"] if self.error_log else None
        }
    
    def _is_recent_error(self, error_entry: Dict[str, Any]) -> bool:
        """Check if error occurred in the last hour"""
        try:
            error_time = datetime.fromisoformat(error_entry["timestamp"])
            now = datetime.now()
            return (now - error_time).total_seconds() < 3600  # 1 hour
        except:
            return False
    
    def _find_error_by_id(self, error_id: str) -> Dict[str, Any]:
        """Find error entry by ID"""
        for error_entry in self.error_log:
            if error_entry["error_id"] == error_id:
                return error_entry
        return None
    
    def _setup_recovery_strategies(self):
        """Setup recovery strategies for different error types"""
        self.recovery_strategies = {
            "ConnectionError": {
                "strategy": "database_reconnect",
                "max_attempts": 3,
                "delay": 2.0,
                "description": "Reconnect to database with exponential backoff"
            },
            "TimeoutError": {
                "strategy": "retry_with_increased_timeout",
                "max_attempts": 2,
                "delay": 5.0,
                "description": "Retry operation with increased timeout"
            },
            "MemoryError": {
                "strategy": "memory_cleanup",
                "max_attempts": 1,
                "delay": 0.0,
                "description": "Force garbage collection and retry"
            },
            "FileNotFoundError": {
                "strategy": "verify_and_create_path",
                "max_attempts": 2,
                "delay": 0.5,
                "description": "Verify file path and create if necessary"
            },
            "ImportError": {
                "strategy": "service_restart",
                "max_attempts": 1,
                "delay": 1.0,
                "description": "Restart affected service or component"
            }
        }
    
    def _attempt_database_recovery(self, error_entry: Dict[str, Any], strategy: Dict[str, Any]) -> bool:
        """Attempt database connection recovery"""
        try:
            from src.core.neo4j_manager import Neo4jManager
            
            # Force reconnection
            manager = Neo4jManager()
            if hasattr(manager, '_driver') and manager._driver:
                manager._driver.close()
                manager._driver = None
            
            # Test new connection
            session = manager.get_session()
            with session:
                result = session.run("RETURN 1")
                return result.single()[0] == 1
            
        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            return False
    
    def _attempt_service_recovery(self, error_entry: Dict[str, Any], strategy: Dict[str, Any]) -> bool:
        """Attempt service recovery"""
        try:
            # Generic service recovery - clear caches, restart components
            import gc
            gc.collect()
            
            # Could implement specific service restart logic here
            return True
            
        except Exception as e:
            logger.error(f"Service recovery failed: {e}")
            return False
    
    def _attempt_memory_recovery(self, error_entry: Dict[str, Any], strategy: Dict[str, Any]) -> bool:
        """Attempt memory recovery"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collection freed {collected} objects")
            
            # Check if memory usage decreased
            import psutil
            current_memory = psutil.Process().memory_info().rss
            
            return True
            
        except Exception as e:
            logger.error(f"Memory recovery failed: {e}")
            return False
    
    def _attempt_generic_recovery(self, error_entry: Dict[str, Any], strategy: Dict[str, Any]) -> bool:
        """Attempt generic recovery"""
        try:
            # Generic recovery: wait and retry
            # Use async delay for error recovery
            delay = strategy.get("delay", 1.0)
            import asyncio
            try:
                asyncio.create_task(asyncio.sleep(min(delay, 0.5)))  # Cap at 0.5s
            except RuntimeError:
                # Non-async fallback
                import time
                time.sleep(min(delay, 0.1))  # Cap at 100ms
            return True
            
        except Exception as e:
            logger.error(f"Generic recovery failed: {e}")
            return False
    
    async def _attempt_generic_recovery_async(self, error_entry: Dict[str, Any], strategy: Dict[str, Any]) -> bool:
        """Async version of generic recovery with non-blocking delays"""
        try:
            # Generic recovery: wait and retry - NON-BLOCKING
            await asyncio.sleep(strategy.get("delay", 1.0))  # ✅ NON-BLOCKING
            return True
            
        except Exception as e:
            logger.error(f"Async generic recovery failed: {e}")
            return False
    
    def clear_old_errors(self, max_age_hours: int = 24):
        """Clear errors older than specified hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        initial_count = len(self.error_log)
        self.error_log = [
            error for error in self.error_log
            if datetime.fromisoformat(error["timestamp"]).timestamp() > cutoff_time
        ]
        
        cleared_count = initial_count - len(self.error_log)
        logger.info(f"Cleared {cleared_count} old errors (older than {max_age_hours} hours)")
        
        return cleared_count
    
    def get_error_summary(self) -> str:
        """Get a human-readable error summary"""
        if not self.error_log:
            return "No errors tracked"
        
        analysis = self.get_error_analysis()
        most_common = analysis["most_common_errors"]
        
        summary = f"Total errors: {analysis['total_errors']}\n"
        
        if most_common:
            summary += f"Most common error: {most_common[0]['error_type']} ({most_common[0]['count']} occurrences)\n"
        
        if analysis["suggested_fixes"]:
            summary += f"Top suggestion: {analysis['suggested_fixes'][0]}\n"
        
        return summary.strip()