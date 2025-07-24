"""
Tests for Grafana MCP Client

Tests the MCP client for Grafana monitoring and observability.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import json

from src.integrations.mcp.grafana_client import (
    GrafanaMCPClient,
    GrafanaDashboard,
    GrafanaPanel,
    GrafanaQuery,
    GrafanaAlert,
    TimeRange
)
from src.integrations.mcp.base_client import MCPRequest, MCPResponse
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreaker


class TestGrafanaMCPClient:
    """Test suite for Grafana MCP client"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter"""
        return APIRateLimiter()
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker"""
        return CircuitBreaker("grafana")
    
    @pytest.fixture
    def client(self, rate_limiter, circuit_breaker):
        """Create Grafana MCP client"""
        return GrafanaMCPClient(
            server_url="http://localhost:8012",
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    @pytest.mark.asyncio
    async def test_search_dashboards(self, client):
        """Test: Search for dashboards"""
        mock_response = {
            "result": {
                "dashboards": [
                    {
                        "uid": "abc123",
                        "title": "System Metrics",
                        "tags": ["monitoring", "system"],
                        "folder": "Infrastructure",
                        "url": "/d/abc123/system-metrics"
                    },
                    {
                        "uid": "def456",
                        "title": "Application Performance",
                        "tags": ["apm", "performance"],
                        "folder": "Applications",
                        "url": "/d/def456/app-performance"
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.search_dashboards(
                query="metrics",
                tags=["monitoring"]
            )
        
        # Verify request
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.method == "search_dashboards"
        assert request.params["query"] == "metrics"
        assert request.params["tags"] == ["monitoring"]
        
        # Verify response
        assert len(result.data) == 2
        assert result.data[0].uid == "abc123"
        assert result.data[0].title == "System Metrics"
    
    @pytest.mark.asyncio
    async def test_get_dashboard_details(self, client):
        """Test: Get dashboard with panels"""
        mock_response = {
            "result": {
                "dashboard": {
                    "uid": "abc123",
                    "title": "System Metrics",
                    "panels": [
                        {
                            "id": 1,
                            "title": "CPU Usage",
                            "type": "graph",
                            "datasource": "prometheus",
                            "targets": [
                                {"expr": "rate(cpu_usage[5m])"}
                            ]
                        },
                        {
                            "id": 2,
                            "title": "Memory Usage",
                            "type": "gauge",
                            "datasource": "prometheus",
                            "targets": [
                                {"expr": "memory_used / memory_total * 100"}
                            ]
                        }
                    ]
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_dashboard("abc123")
        
        assert isinstance(result.data, GrafanaDashboard)
        assert result.data.uid == "abc123"
        assert len(result.data.panels) == 2
        assert result.data.panels[0].title == "CPU Usage"
    
    @pytest.mark.asyncio
    async def test_query_datasource(self, client):
        """Test: Query Prometheus datasource"""
        mock_response = {
            "result": {
                "data": {
                    "resultType": "matrix",
                    "result": [
                        {
                            "metric": {"job": "node", "instance": "server1"},
                            "values": [[1642000000, "0.85"], [1642000060, "0.87"]]
                        }
                    ]
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            query = GrafanaQuery(
                expr="rate(cpu_usage[5m])",
                datasource="prometheus",
                refId="A"
            )
            
            result = await client.query_datasource(
                query=query,
                time_range=TimeRange(
                    from_time=datetime.now() - timedelta(hours=1),
                    to_time=datetime.now()
                )
            )
        
        assert result.data["resultType"] == "matrix"
        assert len(result.data["result"]) == 1
        assert result.data["result"][0]["metric"]["instance"] == "server1"
    
    @pytest.mark.asyncio
    async def test_get_alerts(self, client):
        """Test: Get active alerts"""
        mock_response = {
            "result": {
                "alerts": [
                    {
                        "id": 1,
                        "name": "High CPU Alert",
                        "state": "alerting",
                        "message": "CPU usage above 90%",
                        "dashboard_uid": "abc123",
                        "panel_id": 1,
                        "new_state_date": "2024-01-15T10:00:00Z"
                    },
                    {
                        "id": 2,
                        "name": "Disk Space Warning",
                        "state": "pending",
                        "message": "Disk usage above 80%",
                        "dashboard_uid": "def456",
                        "panel_id": 3,
                        "new_state_date": "2024-01-15T11:00:00Z"
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_alerts(states=["alerting", "pending"])
        
        assert len(result.data) == 2
        assert isinstance(result.data[0], GrafanaAlert)
        assert result.data[0].name == "High CPU Alert"
        assert result.data[0].state == "alerting"
    
    @pytest.mark.asyncio
    async def test_create_annotation(self, client):
        """Test: Create annotation for event"""
        mock_response = {
            "result": {
                "id": 123,
                "time": 1642000000000,
                "timeEnd": 1642003600000,
                "tags": ["deployment", "backend"],
                "text": "Backend deployment v2.0.1"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.create_annotation(
                text="Backend deployment v2.0.1",
                tags=["deployment", "backend"],
                time=datetime.now(),
                time_end=datetime.now() + timedelta(hours=1),
                dashboard_uid="abc123"
            )
        
        assert result.data["id"] == 123
        assert "deployment" in result.data["tags"]
    
    @pytest.mark.asyncio
    async def test_get_datasources(self, client):
        """Test: List available datasources"""
        mock_response = {
            "result": {
                "datasources": [
                    {
                        "id": 1,
                        "name": "prometheus",
                        "type": "prometheus",
                        "url": "http://prometheus:9090",
                        "access": "proxy",
                        "isDefault": True
                    },
                    {
                        "id": 2,
                        "name": "elasticsearch",
                        "type": "elasticsearch",
                        "url": "http://elastic:9200",
                        "access": "proxy",
                        "isDefault": False
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_datasources()
        
        assert len(result.data) == 2
        assert result.data[0]["name"] == "prometheus"
        assert result.data[0]["isDefault"] is True
    
    @pytest.mark.asyncio
    async def test_export_dashboard(self, client):
        """Test: Export dashboard JSON"""
        mock_response = {
            "result": {
                "dashboard": {
                    "uid": "abc123",
                    "title": "System Metrics",
                    "version": 5,
                    "panels": [],
                    "templating": {},
                    "time": {"from": "now-6h", "to": "now"}
                },
                "meta": {
                    "type": "db",
                    "canSave": True,
                    "canEdit": True,
                    "canAdmin": True
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.export_dashboard("abc123")
        
        assert result.data["dashboard"]["uid"] == "abc123"
        assert result.data["dashboard"]["version"] == 5
        assert result.data["meta"]["canEdit"] is True
    
    @pytest.mark.asyncio
    async def test_snapshot_dashboard(self, client):
        """Test: Create dashboard snapshot"""
        mock_response = {
            "result": {
                "key": "snapshot123",
                "url": "https://grafana.example.com/dashboard/snapshot/snapshot123",
                "deleteUrl": "https://grafana.example.com/api/snapshots/snapshot123",
                "expires": 3600
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.create_snapshot(
                dashboard_uid="abc123",
                name="Daily Report Snapshot",
                expires=3600
            )
        
        assert result.data["key"] == "snapshot123"
        assert result.data["expires"] == 3600
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, client):
        """Test: Get system metrics"""
        mock_response = {
            "result": {
                "metrics": {
                    "dashboards": {"total": 45, "starred": 12},
                    "datasources": {"total": 5},
                    "users": {"total": 25, "active": 18},
                    "alerts": {
                        "total": 30,
                        "alerting": 2,
                        "pending": 3,
                        "ok": 25
                    }
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_system_metrics()
        
        assert result.data["dashboards"]["total"] == 45
        assert result.data["alerts"]["alerting"] == 2
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, client):
        """Test: Advanced dashboard search with filters"""
        mock_response = {
            "result": {
                "dashboards": [
                    {
                        "uid": "xyz789",
                        "title": "Production Metrics",
                        "tags": ["prod", "critical"],
                        "folder": "Production"
                    }
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.search_dashboards(
                query="production",
                tags=["prod", "critical"],
                folder="Production",
                starred=True
            )
        
        request = mock_send.call_args[0][0]
        assert request.params["tags"] == ["prod", "critical"]
        assert request.params["folder"] == "Production"
        assert request.params["starred"] is True