"""
Grafana MCP Client

MCP client for Grafana monitoring and observability platform.
Provides access to dashboards, metrics, alerts, and annotations.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

from .base_client import BaseMCPClient, MCPRequest, MCPResponse
from .http_client import HTTPMCPClient
from ..exceptions import MCPError


logger = logging.getLogger(__name__)


class AlertState(str, Enum):
    """Grafana alert states"""
    OK = "ok"
    ALERTING = "alerting"
    PENDING = "pending"
    NO_DATA = "no_data"
    PAUSED = "paused"


@dataclass
class TimeRange:
    """Time range for queries"""
    from_time: datetime
    to_time: datetime
    
    def to_params(self) -> Dict[str, str]:
        """Convert to API parameters"""
        return {
            "from": self.from_time.isoformat(),
            "to": self.to_time.isoformat()
        }


@dataclass
class GrafanaDashboard:
    """Grafana dashboard with panels"""
    uid: str
    title: str
    tags: List[str]
    folder: str
    url: str
    panels: Optional[List['GrafanaPanel']] = None
    version: Optional[int] = None


@dataclass
class GrafanaPanel:
    """Dashboard panel with visualization"""
    id: int
    title: str
    type: str  # graph, gauge, table, stat, etc.
    datasource: str
    targets: List[Dict[str, Any]]
    grid_pos: Optional[Dict[str, int]] = None


@dataclass
class GrafanaQuery:
    """Query for datasource"""
    expr: str  # Query expression (e.g., Prometheus query)
    datasource: str
    refId: str
    interval: Optional[str] = None
    format: Optional[str] = None


@dataclass
class GrafanaAlert:
    """Alert with state and metadata"""
    id: int
    name: str
    state: str
    message: str
    dashboard_uid: str
    panel_id: int
    new_state_date: str
    eval_data: Optional[Dict[str, Any]] = None


class GrafanaError(MCPError):
    """Grafana-specific errors"""
    pass


class GrafanaMCPClient(HTTPMCPClient):
    """
    MCP client for Grafana monitoring platform.
    
    Provides access to:
    - Dashboard search and management
    - Datasource queries (Prometheus, Elasticsearch, etc.)
    - Alert management and state
    - Annotations for events
    - System metrics and health
    """
    
    def __init__(self, server_url: str, rate_limiter, circuit_breaker):
        """Initialize Grafana MCP client"""
        super().__init__(
            server_name="grafana",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    async def search_dashboards(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder: Optional[str] = None,
        starred: Optional[bool] = None
    ) -> MCPResponse[List[GrafanaDashboard]]:
        """
        Search for dashboards with filters.
        
        Args:
            query: Search query
            tags: Filter by tags
            folder: Filter by folder
            starred: Only starred dashboards
            
        Returns:
            List of matching dashboards
        """
        params = {}
        if query:
            params["query"] = query
        if tags:
            params["tags"] = tags
        if folder:
            params["folder"] = folder
        if starred is not None:
            params["starred"] = starred
        
        request = MCPRequest(
            method="search_dashboards",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        dashboards = []
        for item in response["result"]["dashboards"]:
            dashboard = GrafanaDashboard(
                uid=item["uid"],
                title=item["title"],
                tags=item.get("tags", []),
                folder=item.get("folder", "General"),
                url=item.get("url", "")
            )
            dashboards.append(dashboard)
        
        return MCPResponse(success=True, data=dashboards)
    
    async def get_dashboard(
        self,
        dashboard_uid: str
    ) -> MCPResponse[GrafanaDashboard]:
        """
        Get dashboard details with panels.
        
        Args:
            dashboard_uid: Dashboard UID
            
        Returns:
            Dashboard with full details
        """
        request = MCPRequest(
            method="get_dashboard",
            params={"uid": dashboard_uid}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        data = response["result"]["dashboard"]
        
        # Parse panels
        panels = []
        for panel_data in data.get("panels", []):
            panel = GrafanaPanel(
                id=panel_data["id"],
                title=panel_data["title"],
                type=panel_data["type"],
                datasource=panel_data.get("datasource", ""),
                targets=panel_data.get("targets", []),
                grid_pos=panel_data.get("gridPos")
            )
            panels.append(panel)
        
        dashboard = GrafanaDashboard(
            uid=data["uid"],
            title=data["title"],
            tags=data.get("tags", []),
            folder=data.get("folder", "General"),
            url=data.get("url", ""),
            panels=panels,
            version=data.get("version")
        )
        
        return MCPResponse(success=True, data=dashboard)
    
    async def query_datasource(
        self,
        query: GrafanaQuery,
        time_range: TimeRange
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Execute query against datasource.
        
        Args:
            query: Query configuration
            time_range: Time range for query
            
        Returns:
            Query results
        """
        request = MCPRequest(
            method="query_datasource",
            params={
                "query": {
                    "expr": query.expr,
                    "datasource": query.datasource,
                    "refId": query.refId,
                    "interval": query.interval,
                    "format": query.format
                },
                "time_range": time_range.to_params()
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]["data"]
        )
    
    async def get_alerts(
        self,
        states: Optional[List[Union[str, AlertState]]] = None,
        dashboard_uid: Optional[str] = None
    ) -> MCPResponse[List[GrafanaAlert]]:
        """
        Get alerts with optional filters.
        
        Args:
            states: Filter by alert states
            dashboard_uid: Filter by dashboard
            
        Returns:
            List of alerts
        """
        params = {}
        if states:
            params["states"] = [s.value if isinstance(s, AlertState) else s for s in states]
        if dashboard_uid:
            params["dashboard_uid"] = dashboard_uid
        
        request = MCPRequest(
            method="get_alerts",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        alerts = []
        for alert_data in response["result"]["alerts"]:
            alert = GrafanaAlert(
                id=alert_data["id"],
                name=alert_data["name"],
                state=alert_data["state"],
                message=alert_data["message"],
                dashboard_uid=alert_data["dashboard_uid"],
                panel_id=alert_data["panel_id"],
                new_state_date=alert_data["new_state_date"],
                eval_data=alert_data.get("eval_data")
            )
            alerts.append(alert)
        
        return MCPResponse(success=True, data=alerts)
    
    async def create_annotation(
        self,
        text: str,
        tags: List[str],
        time: datetime,
        time_end: Optional[datetime] = None,
        dashboard_uid: Optional[str] = None,
        panel_id: Optional[int] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Create annotation for event.
        
        Args:
            text: Annotation text
            tags: Tags for categorization
            time: Start time
            time_end: End time (for ranges)
            dashboard_uid: Associated dashboard
            panel_id: Associated panel
            
        Returns:
            Created annotation details
        """
        params = {
            "text": text,
            "tags": tags,
            "time": int(time.timestamp() * 1000),  # Milliseconds
        }
        
        if time_end:
            params["timeEnd"] = int(time_end.timestamp() * 1000)
        if dashboard_uid:
            params["dashboardUID"] = dashboard_uid
        if panel_id:
            params["panelId"] = panel_id
        
        request = MCPRequest(
            method="create_annotation",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_datasources(self) -> MCPResponse[List[Dict[str, Any]]]:
        """
        Get available datasources.
        
        Returns:
            List of configured datasources
        """
        request = MCPRequest(method="get_datasources", params={})
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]["datasources"]
        )
    
    async def export_dashboard(
        self,
        dashboard_uid: str
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Export dashboard JSON.
        
        Args:
            dashboard_uid: Dashboard to export
            
        Returns:
            Dashboard JSON configuration
        """
        request = MCPRequest(
            method="export_dashboard",
            params={"uid": dashboard_uid}
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def create_snapshot(
        self,
        dashboard_uid: str,
        name: Optional[str] = None,
        expires: Optional[int] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Create dashboard snapshot.
        
        Args:
            dashboard_uid: Dashboard to snapshot
            name: Snapshot name
            expires: Expiration in seconds
            
        Returns:
            Snapshot details with URL
        """
        params = {"dashboard_uid": dashboard_uid}
        if name:
            params["name"] = name
        if expires:
            params["expires"] = expires
        
        request = MCPRequest(
            method="create_snapshot",
            params=params
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_system_metrics(self) -> MCPResponse[Dict[str, Any]]:
        """
        Get Grafana system metrics.
        
        Returns:
            System-level metrics and statistics
        """
        request = MCPRequest(method="get_system_metrics", params={})
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]["metrics"]
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get Grafana service health status"""
        response = await self._send_request(MCPRequest(method="health", params={}))
        
        if "error" in response:
            return {
                "service_status": "unhealthy",
                "error": response["error"],
                "circuit_breaker_state": self.circuit_breaker.state.name
            }
        
        result = response.get("result", {})
        return {
            "service_status": result.get("status", "unknown"),
            "version": result.get("grafana_version"),
            "database": result.get("database", {}).get("status"),
            "features": result.get("features", []),
            "circuit_breaker_state": self.circuit_breaker.state.name,
            "rate_limit_remaining": self.rate_limiter.get_remaining_requests(self.server_name)
        }