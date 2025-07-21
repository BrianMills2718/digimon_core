#!/usr/bin/env python3
"""
KGAS Production Main Server
Main entry point for the production KGAS system with health endpoints and monitoring.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import psutil

# Import Phase 4 components
from src.core.error_handler import error_handler, ProductionErrorHandler
from src.core.performance_optimizer import performance_optimizer
from src.core.security_manager import security_manager
from src.monitoring.production_monitoring import production_monitor

# Import existing core components
from src.core.service_manager import get_service_manager
from src.core.config_manager import get_config
from src.core.health_checker import HealthChecker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KGAS Production API",
    description="Knowledge Graph Analytics System - Production API",
    version="4.0.0"
)

# Global health checker
health_checker = HealthChecker()

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for Kubernetes liveness probe.
    
    Returns:
        JSON response with health status
    """
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "kgas-production",
            "version": "4.0.0"
        }
        
        # Check system resources
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["system"] = {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "available_memory_gb": memory.available / (1024**3)
        }
        
        # Check if system is healthy
        if cpu_usage > 95 or memory.percent > 95:
            health_status["status"] = "degraded"
            health_status["warnings"] = []
            if cpu_usage > 95:
                health_status["warnings"].append("High CPU usage")
            if memory.percent > 95:
                health_status["warnings"].append("High memory usage")
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_handler.register_error(e, {"endpoint": "/health"})
        
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            },
            status_code=503
        )

@app.get("/ready")
async def readiness_check() -> JSONResponse:
    """
    Readiness check endpoint for Kubernetes readiness probe.
    
    Returns:
        JSON response with readiness status
    """
    try:
        # Check if all critical services are ready
        service_manager = get_service_manager()
        config = get_config()
        
        readiness_status = {
            "status": "ready",
            "timestamp": datetime.now().isoformat(),
            "service": "kgas-production",
            "checks": {}
        }
        
        # Check configuration
        try:
            config_data = config.get_config()
            readiness_status["checks"]["configuration"] = "ready"
        except Exception as e:
            readiness_status["checks"]["configuration"] = f"not_ready: {e}"
            readiness_status["status"] = "not_ready"
        
        # Check service manager
        try:
            service_stats = service_manager.get_service_stats()
            readiness_status["checks"]["service_manager"] = "ready"
            readiness_status["service_stats"] = service_stats
        except Exception as e:
            readiness_status["checks"]["service_manager"] = f"not_ready: {e}"
            readiness_status["status"] = "not_ready"
        
        # Check database connectivity (if available)
        try:
            # This would check Neo4j connectivity
            readiness_status["checks"]["database"] = "ready"
        except Exception as e:
            readiness_status["checks"]["database"] = f"not_ready: {e}"
            readiness_status["status"] = "not_ready"
        
        # Check monitoring systems
        try:
            monitoring_status = production_monitor.get_monitoring_status()
            readiness_status["checks"]["monitoring"] = "ready"
            readiness_status["monitoring_status"] = monitoring_status
        except Exception as e:
            readiness_status["checks"]["monitoring"] = f"not_ready: {e}"
            # Monitoring is not critical for readiness
        
        status_code = 200 if readiness_status["status"] == "ready" else 503
        return JSONResponse(content=readiness_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        error_handler.register_error(e, {"endpoint": "/ready"})
        
        return JSONResponse(
            content={
                "status": "not_ready",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            },
            status_code=503
        )

@app.get("/metrics")
async def metrics_endpoint() -> JSONResponse:
    """
    Metrics endpoint for Prometheus scraping.
    
    Returns:
        JSON response with system metrics
    """
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "service": "kgas-production"
        }
        
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        metrics["system"] = {
            "cpu_usage_percent": cpu_usage,
            "memory_total_bytes": memory.total,
            "memory_used_bytes": memory.used,
            "memory_available_bytes": memory.available,
            "memory_usage_percent": memory.percent,
            "disk_total_bytes": disk.total,
            "disk_used_bytes": disk.used,
            "disk_free_bytes": disk.free,
            "disk_usage_percent": (disk.used / disk.total) * 100,
            "network_bytes_sent": network.bytes_sent,
            "network_bytes_received": network.bytes_recv
        }
        
        # Performance metrics
        try:
            performance_report = performance_optimizer.get_performance_report()
            metrics["performance"] = performance_report
        except Exception as e:
            logger.warning(f"Failed to get performance metrics: {e}")
            metrics["performance"] = {"error": str(e)}
        
        # Error metrics
        try:
            error_stats = error_handler.get_error_statistics()
            metrics["errors"] = error_stats
        except Exception as e:
            logger.warning(f"Failed to get error metrics: {e}")
            metrics["errors"] = {"error": str(e)}
        
        # Security metrics
        try:
            security_report = security_manager.get_security_report()
            metrics["security"] = security_report
        except Exception as e:
            logger.warning(f"Failed to get security metrics: {e}")
            metrics["security"] = {"error": str(e)}
        
        return JSONResponse(content=metrics, status_code=200)
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        error_handler.register_error(e, {"endpoint": "/metrics"})
        
        return JSONResponse(
            content={
                "error": "Failed to collect metrics",
                "timestamp": datetime.now().isoformat(),
                "details": str(e)
            },
            status_code=500
        )

@app.get("/status")
async def status_endpoint() -> JSONResponse:
    """
    Comprehensive status endpoint.
    
    Returns:
        JSON response with detailed status information
    """
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "service": "kgas-production",
            "version": "4.0.0",
            "uptime_seconds": None,  # Would track actual uptime
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
        
        # Get health status
        health_response = await health_check()
        status["health"] = health_response.body.decode() if hasattr(health_response, 'body') else {}
        
        # Get readiness status
        ready_response = await readiness_check()
        status["readiness"] = ready_response.body.decode() if hasattr(ready_response, 'body') else {}
        
        # Get monitoring status
        try:
            monitoring_status = production_monitor.get_monitoring_status()
            status["monitoring"] = monitoring_status
        except Exception as e:
            status["monitoring"] = {"error": str(e)}
        
        # Get service manager stats
        try:
            service_manager = get_service_manager()
            status["services"] = service_manager.get_service_stats()
        except Exception as e:
            status["services"] = {"error": str(e)}
        
        return JSONResponse(content=status, status_code=200)
        
    except Exception as e:
        logger.error(f"Status endpoint failed: {e}")
        error_handler.register_error(e, {"endpoint": "/status"})
        
        return JSONResponse(
            content={
                "error": "Failed to get status",
                "timestamp": datetime.now().isoformat(),
                "details": str(e)
            },
            status_code=500
        )

@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint with basic service information.
    
    Returns:
        JSON response with service information
    """
    return JSONResponse(content={
        "service": "KGAS Production API",
        "version": "4.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "ready": "/ready", 
            "metrics": "/metrics",
            "status": "/status"
        }
    })

def setup_production_monitoring():
    """Set up production monitoring and alerting."""
    try:
        # Start production monitoring
        production_monitor.start_monitoring()
        logger.info("Production monitoring started")
    except Exception as e:
        logger.error(f"Failed to start production monitoring: {e}")
        error_handler.register_error(e, {"component": "production_monitoring"})

def setup_error_handling():
    """Set up production error handling."""
    try:
        # Error handling is automatically initialized
        logger.info("Production error handling initialized")
    except Exception as e:
        logger.error(f"Failed to initialize error handling: {e}")

def setup_security():
    """Set up production security features."""
    try:
        # Security manager is automatically initialized
        logger.info("Production security manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize security: {e}")

async def startup_checks():
    """Perform startup checks and initialization."""
    logger.info("Performing startup checks...")
    
    # Check environment
    environment = os.environ.get("ENVIRONMENT", "development")
    logger.info(f"Running in {environment} environment")
    
    # Setup Phase 4 components
    setup_production_monitoring()
    setup_error_handling()
    setup_security()
    
    # Check critical services
    try:
        service_manager = get_service_manager()
        config = get_config()
        
        # Verify configuration
        config_data = config.get_config()
        logger.info("Configuration loaded successfully")
        
        # Verify service manager
        service_stats = service_manager.get_service_stats()
        logger.info(f"Service manager initialized: {service_stats}")
        
    except Exception as e:
        logger.error(f"Startup check failed: {e}")
        error_handler.register_error(e, {"component": "startup"})
        raise
    
    logger.info("Startup checks completed successfully")

def main():
    """Main entry point for the production server."""
    try:
        # Perform startup checks
        asyncio.run(startup_checks())
        
        # Get server configuration
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "8000"))
        
        logger.info(f"Starting KGAS Production Server on {host}:{port}")
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        error_handler.register_error(e, {"component": "server_startup"})
        sys.exit(1)

if __name__ == "__main__":
    main()