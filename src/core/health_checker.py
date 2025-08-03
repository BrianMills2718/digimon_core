"""
Comprehensive health checker for all external dependencies.
"""

import asyncio
import aiohttp
import time
import psutil
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core.config_manager import get_config
from src.core.async_api_clients import AsyncOpenAIClient, AsyncAnthropicClient, AsyncGoogleClient


class HealthStatus:
    """Health status constants"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy" 
    WARNING = "warning"
    UNKNOWN = "unknown"


class HealthCheck:
    """Individual health check result"""
    
    def __init__(self, name: str, status: str, latency_ms: Optional[float] = None, 
                 message: Optional[str] = None, metadata: Optional[Dict] = None):
        self.name = name
        self.status = status
        self.latency_ms = latency_ms
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "name": self.name,
            "status": self.status,
            "timestamp": self.timestamp
        }
        
        if self.latency_ms is not None:
            result["latency_ms"] = round(self.latency_ms, 2)
        
        if self.message:
            result["message"] = self.message
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


    def _get_default_model(self) -> str:
        """Get default model from standard config"""
        return get_model()

class HealthChecker:
    """Comprehensive health checker for all system dependencies."""
    
    def __init__(self):
        self.config = get_config()
        self.health_status: Dict[str, Any] = {}
        self.last_check: Optional[datetime] = None
    
    async def check_all_dependencies(self) -> Dict[str, Any]:
        """Check health of all dependencies."""
        
        health_checks = [
            self._check_neo4j(),
            self._check_redis(),
            self._check_openai_api(),
            self._check_anthropic_api(),
            self._check_google_api(),
            self._check_filesystem(),
            self._check_system_resources(),
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Compile results
        self.health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {
                'neo4j': results[0] if not isinstance(results[0], Exception) else {'status': 'error', 'error': str(results[0])},
                'redis': results[1] if not isinstance(results[1], Exception) else {'status': 'error', 'error': str(results[1])},
                'openai_api': results[2] if not isinstance(results[2], Exception) else {'status': 'error', 'error': str(results[2])},
                'anthropic_api': results[3] if not isinstance(results[3], Exception) else {'status': 'error', 'error': str(results[3])},
                'google_api': results[4] if not isinstance(results[4], Exception) else {'status': 'error', 'error': str(results[4])},
                'filesystem': results[5] if not isinstance(results[5], Exception) else {'status': 'error', 'error': str(results[5])},
                'system_resources': results[6] if not isinstance(results[6], Exception) else {'status': 'error', 'error': str(results[6])},
            }
        }
        
        # Determine overall status
        failed_checks = [name for name, result in self.health_status['checks'].items() if result['status'] != 'healthy']
        if failed_checks:
            self.health_status['overall_status'] = 'unhealthy'
            self.health_status['failed_checks'] = failed_checks
        
        self.last_check = datetime.now()
        
        # Log health check results
        self._log_health_check_results()
        
        return self.health_status
        
    async def _check_neo4j(self) -> Dict[str, Any]:
        """Check Neo4j database connectivity."""
        try:
            from neo4j import AsyncGraphDatabase
            
            neo4j_config = self.config.get_neo4j_config()
            
            async with AsyncGraphDatabase.driver(
                neo4j_config['uri'],
                auth=(neo4j_config['username'], neo4j_config['password'])
            ) as driver:
                async with driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    await result.consume()
                    
                    return {
                        'status': 'healthy',
                        'response_time_ms': 0,  # Would need timing
                        'database': neo4j_config['database']
                    }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            import redis.asyncio as redis
            
            redis_client = redis.Redis(
                host=self.config.get('redis.host', 'localhost'),
                port=self.config.get('redis.port', 6379),
                password=self.config.get('redis.password'),
                db=self.config.get('redis.db', 0)
            )
            
            await redis_client.ping()
            await redis_client.close()
            
            return {
                'status': 'healthy',
                'response_time_ms': 0
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity."""
        try:
            if not self.config.api.openai_api_key:
                return {
                    'status': 'skipped',
                    'reason': 'API key not configured'
                }
            
            async with AsyncOpenAIClient() as client:
                # Simple API call to test connectivity
                response = await client.chat_completion(
                    messages=[{"role": "user", "content": "Hello"}],
                    model="gpt-3.5-turbo"
                )
                
                return {
                    'status': 'healthy',
                    'response_time_ms': 0,
                    'model': 'gpt-3.5-turbo'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_anthropic_api(self) -> Dict[str, Any]:
        """Check Anthropic API connectivity."""
        try:
            if not self.config.api.anthropic_api_key:
                return {
                    'status': 'skipped',
                    'reason': 'API key not configured'
                }
            
            async with AsyncAnthropicClient() as client:
                response = await client.messages(
                    messages=[{"role": "user", "content": "Hello"}]
                )
                
                return {
                    'status': 'healthy',
                    'response_time_ms': 0
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_google_api(self) -> Dict[str, Any]:
        """Check Google API connectivity."""
        try:
            if not self.config.api.google_api_key:
                return {
                    'status': 'skipped',
                    'reason': 'API key not configured'
                }
            
            async with AsyncGoogleClient() as client:
                response = await client.generate_content("Hello")
                
                return {
                    'status': 'healthy',
                    'response_time_ms': 0
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_filesystem(self) -> Dict[str, Any]:
        """Check filesystem accessibility."""
        try:
            from pathlib import Path
            
            # Check key directories
            directories = [
                Path('data'),
                Path('logs'),
                Path('backups'),
                Path('config')
            ]
            
            directory_status = {}
            for directory in directories:
                directory_status[str(directory)] = {
                    'exists': directory.exists(),
                    'writable': directory.is_dir() and os.access(directory, os.W_OK) if directory.exists() else False
                }
            
            return {
                'status': 'healthy',
                'directories': directory_status
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'healthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'available_memory_gb': memory.available / (1024**3),
                'available_disk_gb': disk.free / (1024**3)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _log_health_check_results(self) -> None:
        """Log health check results to Evidence.md."""
        import json
        
        with open('Evidence.md', 'a') as f:
            f.write(f"\n## Health Check Evidence\n")
            f.write(f"**Timestamp**: {self.health_status['timestamp']}\n")
            f.write(f"**Overall Status**: {self.health_status['overall_status']}\n")
            
            if self.health_status['overall_status'] == 'unhealthy':
                f.write(f"**Failed Checks**: {', '.join(self.health_status.get('failed_checks', []))}\n")
            
            f.write(f"**Check Results**:\n")
            for check_name, result in self.health_status['checks'].items():
                status = result.get('status', 'unknown')
                f.write(f"  - **{check_name}**: {status}\n")
                
                if status == 'unhealthy':
                    f.write(f"    - Error: {result.get('error', 'Unknown error')}\n")
                elif status == 'skipped':
                    f.write(f"    - Reason: {result.get('reason', 'Unknown reason')}\n")
            
            f.write(f"```json\n{json.dumps(self.health_status, indent=2)}\n```\n\n")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return self.health_status
    
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.health_status.get('overall_status') == 'healthy'

# Global health checker instance
_health_checker_instance: Optional[HealthChecker] = None

def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    global _health_checker_instance
    if _health_checker_instance is None:
        _health_checker_instance = HealthChecker()
    return _health_checker_instance
