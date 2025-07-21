# Task 1.5: Health Monitoring Implementation

**Duration**: Days 9-10 (Week 3)  
**Owner**: DevOps Lead  
**Priority**: HIGH - Essential for production readiness

## Objective

Design and implement comprehensive health check architecture with service health endpoints, monitoring dashboard, and alerting rules for all KGAS components.

## Current State Analysis

### Missing Health Checks
- No standardized health endpoints
- Manual service status checking
- No centralized monitoring
- Limited observability into system state

## Implementation Plan

### Day 9 Morning: Health Check Framework

#### Step 1: Base Health Check Interface
```python
# File: src/core/health_checker.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    component: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = None
    timestamp: datetime = None
    response_time: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.details is None:
            self.details = {}

class HealthCheck(ABC):
    """Base health check interface"""
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform health check"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Component name"""
        pass

class SystemHealthChecker:
    """Orchestrates health checks across all components"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.cache_ttl = 30  # seconds
        self._cache: Dict[str, HealthCheckResult] = {}
        self._last_check: Dict[str, datetime] = {}
    
    def register_check(self, health_check: HealthCheck):
        """Register a health check"""
        self.checks.append(health_check)
    
    async def check_all(self, use_cache: bool = True) -> Dict[str, HealthCheckResult]:
        """Check health of all registered components"""
        tasks = []
        
        for check in self.checks:
            if use_cache and self._is_cached(check.name):
                continue
            tasks.append(self._run_check(check))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, HealthCheckResult):
                    self._cache[result.component] = result
                    self._last_check[result.component] = datetime.now()
        
        return self._cache.copy()
    
    async def _run_check(self, check: HealthCheck) -> HealthCheckResult:
        """Run individual health check with timeout"""
        try:
            return await asyncio.wait_for(check.check(), timeout=10.0)
        except asyncio.TimeoutError:
            return HealthCheckResult(
                component=check.name,
                status=HealthStatus.UNHEALTHY,
                message="Health check timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                component=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
    
    def _is_cached(self, component_name: str) -> bool:
        """Check if result is cached and still valid"""
        if component_name not in self._last_check:
            return False
        
        elapsed = (datetime.now() - self._last_check[component_name]).total_seconds()
        return elapsed < self.cache_ttl
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status"""
        if not self._cache:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in self._cache.values()]
        
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
```

#### Step 2: Service-Specific Health Checks
```python
# File: src/core/service_health_checks.py

import aiohttp
import asyncio
from neo4j import AsyncGraphDatabase
from src.core.health_checker import HealthCheck, HealthCheckResult, HealthStatus

class Neo4jHealthCheck(HealthCheck):
    """Neo4j database health check"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    @property
    def name(self) -> str:
        return "neo4j"
    
    async def check(self) -> HealthCheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.driver:
                self.driver = AsyncGraphDatabase.driver(
                    self.uri, 
                    auth=(self.user, self.password)
                )
            
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as health")
                record = await result.single()
                
                if record and record["health"] == 1:
                    # Get additional metrics
                    metrics_query = """
                    CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Store file sizes')
                    YIELD attributes
                    RETURN attributes.TotalStoreSize.value as storeSize
                    """
                    
                    metrics_result = await session.run(metrics_query)
                    metrics_record = await metrics_result.single()
                    
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    return HealthCheckResult(
                        component=self.name,
                        status=HealthStatus.HEALTHY,
                        message="Neo4j is accessible",
                        response_time=response_time,
                        details={
                            "store_size": metrics_record["storeSize"] if metrics_record else None,
                            "uri": self.uri,
                            "response_time_ms": round(response_time * 1000, 2)
                        }
                    )
        
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Neo4j connection failed: {str(e)}",
                response_time=response_time
            )

class QdrantHealthCheck(HealthCheck):
    """Qdrant vector database health check"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    @property
    def name(self) -> str:
        return "qdrant"
    
    async def check(self) -> HealthCheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            timeout = aiohttp.ClientTimeout(total=5.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Check basic health
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        # Get collections info
                        async with session.get(f"{self.base_url}/collections") as coll_response:
                            collections_data = await coll_response.json()
                            
                            response_time = asyncio.get_event_loop().time() - start_time
                            
                            return HealthCheckResult(
                                component=self.name,
                                status=HealthStatus.HEALTHY,
                                message="Qdrant is accessible",
                                response_time=response_time,
                                details={
                                    "collections": len(collections_data.get("result", {}).get("collections", [])),
                                    "host": self.host,
                                    "port": self.port,
                                    "response_time_ms": round(response_time * 1000, 2)
                                }
                            )
                    else:
                        return HealthCheckResult(
                            component=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"Qdrant returned status {response.status}"
                        )
        
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Qdrant connection failed: {str(e)}",
                response_time=response_time
            )

class OpenAIHealthCheck(HealthCheck):
    """OpenAI API health check"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @property
    def name(self) -> str:
        return "openai"
    
    async def check(self) -> HealthCheckResult:
        start_time = asyncio.get_event_loop().time()
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    'https://api.openai.com/v1/models', 
                    headers=headers
                ) as response:
                    
                    response_time = asyncio.get_event_loop().time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('data', [])
                        
                        return HealthCheckResult(
                            component=self.name,
                            status=HealthStatus.HEALTHY,
                            message="OpenAI API is accessible",
                            response_time=response_time,
                            details={
                                "available_models": len(models),
                                "gpt4_available": any('gpt-4' in m.get('id', '') for m in models),
                                "response_time_ms": round(response_time * 1000, 2)
                            }
                        )
                    elif response.status == 401:
                        return HealthCheckResult(
                            component=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message="OpenAI API authentication failed"
                        )
                    else:
                        return HealthCheckResult(
                            component=self.name,
                            status=HealthStatus.DEGRADED,
                            message=f"OpenAI API returned status {response.status}"
                        )
        
        except Exception as e:
            response_time = asyncio.get_event_loop().time() - start_time
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"OpenAI API check failed: {str(e)}",
                response_time=response_time
            )
```

### Day 9 Afternoon: API Endpoints

#### Step 3: Health API Endpoints
```python
# File: src/api/health_endpoints.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from src.core.health_checker import SystemHealthChecker, HealthStatus
from src.core.service_health_checks import Neo4jHealthCheck, QdrantHealthCheck, OpenAIHealthCheck
import os

def setup_health_endpoints(app: FastAPI, health_checker: SystemHealthChecker):
    """Setup health check endpoints"""
    
    @app.get("/health")
    async def health_summary():
        """Basic health check endpoint"""
        results = await health_checker.check_all()
        overall_status = health_checker.get_overall_status()
        
        status_code = 200
        if overall_status == HealthStatus.UNHEALTHY:
            status_code = 503
        elif overall_status == HealthStatus.DEGRADED:
            status_code = 200  # Degraded but still functional
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": overall_status.value,
                "timestamp": results[list(results.keys())[0]].timestamp.isoformat() if results else None,
                "components": {
                    name: {
                        "status": result.status.value,
                        "message": result.message
                    }
                    for name, result in results.items()
                }
            }
        )
    
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health check with metrics"""
        results = await health_checker.check_all()
        overall_status = health_checker.get_overall_status()
        
        return {
            "status": overall_status.value,
            "timestamp": results[list(results.keys())[0]].timestamp.isoformat() if results else None,
            "components": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "response_time": result.response_time,
                    "details": result.details,
                    "timestamp": result.timestamp.isoformat()
                }
                for name, result in results.items()
            },
            "summary": {
                "total_components": len(results),
                "healthy": sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY),
                "degraded": sum(1 for r in results.values() if r.status == HealthStatus.DEGRADED),
                "unhealthy": sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
            }
        }
    
    @app.get("/health/{component}")
    async def health_component(component: str):
        """Health check for specific component"""
        results = await health_checker.check_all()
        
        if component not in results:
            raise HTTPException(status_code=404, detail=f"Component '{component}' not found")
        
        result = results[component]
        status_code = 200 if result.status == HealthStatus.HEALTHY else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "component": component,
                "status": result.status.value,
                "message": result.message,
                "response_time": result.response_time,
                "details": result.details,
                "timestamp": result.timestamp.isoformat()
            }
        )

def create_health_checker() -> SystemHealthChecker:
    """Initialize health checker with all components"""
    checker = SystemHealthChecker()
    
    # Register Neo4j health check
    if all(os.getenv(var) for var in ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']):
        checker.register_check(Neo4jHealthCheck(
            uri=os.getenv('NEO4J_URI'),
            user=os.getenv('NEO4J_USER'),
            password=os.getenv('NEO4J_PASSWORD')
        ))
    
    # Register Qdrant health check
    if os.getenv('QDRANT_HOST'):
        checker.register_check(QdrantHealthCheck(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', '6333'))
        ))
    
    # Register OpenAI health check
    if os.getenv('OPENAI_API_KEY'):
        checker.register_check(OpenAIHealthCheck(
            api_key=os.getenv('OPENAI_API_KEY')
        ))
    
    return checker
```

### Day 10: Monitoring Dashboard

#### Step 4: Monitoring Dashboard
```python
# File: src/monitoring/health_dashboard.py

import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from src.core.health_checker import SystemHealthChecker, HealthStatus
from src.api.health_endpoints import create_health_checker

class HealthDashboard:
    """Streamlit-based health monitoring dashboard"""
    
    def __init__(self):
        self.health_checker = create_health_checker()
        self.history = []
        
    def run(self):
        """Run the dashboard"""
        st.set_page_config(
            page_title="KGAS Health Monitor",
            page_icon="🏥",
            layout="wide"
        )
        
        st.title("🏥 KGAS Health Monitor")
        
        # Auto-refresh
        if st.button("🔄 Refresh"):
            st.rerun()
        
        # Main dashboard
        self.render_dashboard()
        
        # Auto-refresh every 30 seconds
        time.sleep(30)
        st.rerun()
    
    def render_dashboard(self):
        """Render the main dashboard"""
        # Get current health status
        results = asyncio.run(self.health_checker.check_all())
        overall_status = self.health_checker.get_overall_status()
        
        # Store in history
        self.history.append({
            'timestamp': datetime.now(),
            'overall_status': overall_status,
            'results': results
        })
        
        # Keep only last 100 entries
        self.history = self.history[-100:]
        
        # Overall status
        self.render_overall_status(overall_status)
        
        # Component status grid
        self.render_component_grid(results)
        
        # Performance metrics
        self.render_performance_metrics(results)
        
        # Historical trends
        if len(self.history) > 1:
            self.render_historical_trends()
    
    def render_overall_status(self, status: HealthStatus):
        """Render overall system status"""
        status_colors = {
            HealthStatus.HEALTHY: "🟢",
            HealthStatus.DEGRADED: "🟡", 
            HealthStatus.UNHEALTHY: "🔴",
            HealthStatus.UNKNOWN: "⚪"
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Overall Status",
                value=f"{status_colors[status]} {status.value.upper()}"
            )
        
        with col2:
            st.metric(
                label="Last Check",
                value=datetime.now().strftime("%H:%M:%S")
            )
        
        with col3:
            uptime_hours = len(self.history) * 0.5  # Assuming 30s intervals
            st.metric(
                label="Monitor Uptime",
                value=f"{uptime_hours:.1f}h"
            )
    
    def render_component_grid(self, results):
        """Render component status grid"""
        st.subheader("Component Status")
        
        cols = st.columns(len(results))
        
        for i, (component, result) in enumerate(results.items()):
            with cols[i]:
                status_color = {
                    HealthStatus.HEALTHY: "🟢",
                    HealthStatus.DEGRADED: "🟡",
                    HealthStatus.UNHEALTHY: "🔴",
                    HealthStatus.UNKNOWN: "⚪"
                }[result.status]
                
                st.metric(
                    label=f"{status_color} {component.upper()}",
                    value=f"{result.response_time:.2f}s",
                    delta=result.message
                )
                
                # Component details in expander
                with st.expander(f"Details - {component}"):
                    st.json(result.details)
    
    def render_performance_metrics(self, results):
        """Render performance metrics"""
        st.subheader("Performance Metrics")
        
        # Response times chart
        response_times = {
            component: result.response_time 
            for component, result in results.items()
        }
        
        fig = px.bar(
            x=list(response_times.keys()),
            y=list(response_times.values()),
            title="Component Response Times",
            labels={'x': 'Component', 'y': 'Response Time (seconds)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_historical_trends(self):
        """Render historical health trends"""
        st.subheader("Historical Trends")
        
        # Prepare data
        trend_data = []
        for entry in self.history[-50:]:  # Last 50 entries
            for component, result in entry['results'].items():
                trend_data.append({
                    'timestamp': entry['timestamp'],
                    'component': component,
                    'status': result.status.value,
                    'response_time': result.response_time,
                    'healthy': 1 if result.status == HealthStatus.HEALTHY else 0
                })
        
        if trend_data:
            df = pd.DataFrame(trend_data)
            
            # Health status over time
            fig = px.line(
                df,
                x='timestamp',
                y='healthy',
                color='component',
                title="Component Health Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    dashboard = HealthDashboard()
    dashboard.run()
```

## Success Criteria

- [ ] Health endpoints return meaningful status for all services
- [ ] Dashboard shows real-time system health
- [ ] Alert system notifies of health issues
- [ ] Performance metrics tracked over time
- [ ] Zero false positives in health checks

## Deliverables

1. **Health check framework** with base classes
2. **Service-specific health checks** (Neo4j, Qdrant, OpenAI)
3. **Health API endpoints** (/health, /health/detailed)
4. **Monitoring dashboard** with real-time updates
5. **Alert configuration** for critical issues