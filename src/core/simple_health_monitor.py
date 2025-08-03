"""
Simple Health Monitor - Production Health Monitoring for TD.5

Simple and effective health monitoring for production deployment.
Focuses on essential system health without complex dependencies.
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SimpleHealthMonitor:
    """Simple production health monitoring"""
    
    def __init__(self):
        self.enabled = True
        self._initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize health monitoring"""
        try:
            self.enabled = config.get('health_checks_enabled', True)
            self._initialized = True
            logger.info("SimpleHealthMonitor initialized")
            return True
        except Exception as e:
            logger.error(f"SimpleHealthMonitor initialization failed: {e}")
            return False
    
    def health_check(self) -> bool:
        """Basic health check for service status"""
        return self._initialized and self.enabled
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get basic system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'disk_usage_percent': (disk.used / disk.total) * 100,
                'memory_total_gb': memory.total / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'disk_used_gb': disk.used / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        self._initialized = False
        logger.info("SimpleHealthMonitor cleanup completed")


# Create global instance
_global_health_monitor = SimpleHealthMonitor()


def get_health_monitor() -> SimpleHealthMonitor:
    """Get global health monitor instance"""
    return _global_health_monitor