"""
Grafana Dashboard Manager - Phase 2 Implementation

Creates and manages comprehensive monitoring dashboards.
"""

import json
import requests
from typing import Dict, Any, List
from datetime import datetime
from src.core.config_manager import get_config

class GrafanaDashboardManager:
    """Grafana dashboard creation and management."""
    
    def __init__(self, grafana_url: str = "http://localhost:3000", api_key: str = None):
        self.config = get_config()
        self.grafana_url = grafana_url
        self.api_key = api_key or self.config.get('grafana.api_key')
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_system_overview_dashboard(self) -> Dict[str, Any]:
        """Create system overview dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS System Overview",
                "tags": ["kgas", "system", "overview"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "System CPU Usage",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_system_cpu_usage_percent",
                            "legendFormat": "CPU %"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 70},
                                        {"color": "red", "value": 90}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 2,
                        "title": "System Memory Usage",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_system_memory_usage_percent",
                            "legendFormat": "Memory %"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "fieldConfig": {
                            "defaults": {
                                "unit": "percent",
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 70},
                                        {"color": "red", "value": 90}
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "id": 3,
                        "title": "Documents Processed",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_documents_processed_total[5m])",
                            "legendFormat": "{{status}}"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Health Check Status",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_health_check_status",
                            "legendFormat": "{{service}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
                    },
                    {
                        "id": 5,
                        "title": "System Load",
                        "type": "gauge",
                        "targets": [{
                            "expr": "kgas_system_cpu_usage_percent",
                            "legendFormat": "System Load %"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_performance_dashboard(self) -> Dict[str, Any]:
        """Create performance monitoring dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Performance Monitoring",
                "tags": ["kgas", "performance"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Document Processing Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, kgas_document_processing_duration_seconds)",
                            "legendFormat": "95th percentile"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "API Response Time",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, kgas_api_response_duration_seconds)",
                            "legendFormat": "{{provider}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Throughput",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_documents_processed_total[5m])",
                            "legendFormat": "Documents/sec"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_documents_processed_total{status=\"error\"}[5m])",
                            "legendFormat": "Errors/sec"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_database_dashboard(self) -> Dict[str, Any]:
        """Create database monitoring dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Database Monitoring",
                "tags": ["kgas", "database"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Graph Nodes",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_graph_nodes_total",
                            "legendFormat": "Nodes"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Graph Edges",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_graph_edges_total",
                            "legendFormat": "Edges"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Database Operations",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_database_operations_total[5m])",
                            "legendFormat": "{{operation_type}}"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Connection Pool",
                        "type": "graph",
                        "targets": [{
                            "expr": "kgas_database_connections_active",
                            "legendFormat": "Active Connections"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_api_monitoring_dashboard(self) -> Dict[str, Any]:
        """Create API monitoring dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS API Monitoring",
                "tags": ["kgas", "api"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "API Calls by Provider",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_api_calls_total[5m])",
                            "legendFormat": "{{provider}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "API Success Rate",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(kgas_api_calls_total{status=\"success\"}[5m]) / rate(kgas_api_calls_total[5m])",
                            "legendFormat": "Success Rate"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Response Time by Provider",
                        "type": "graph",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, kgas_api_response_duration_seconds)",
                            "legendFormat": "{{provider}}"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "API Errors",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_api_calls_total{status=\"error\"}[5m])",
                            "legendFormat": "{{provider}}"
                        }],
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_entity_processing_dashboard(self) -> Dict[str, Any]:
        """Create entity processing dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Entity Processing",
                "tags": ["kgas", "entities"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Entities Extracted",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_entities_extracted_total[5m])",
                            "legendFormat": "{{entity_type}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Relationships Created",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_relationships_created_total[5m])",
                            "legendFormat": "{{relationship_type}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Entity Types Distribution",
                        "type": "piechart",
                        "targets": [{
                            "expr": "kgas_entities_extracted_total",
                            "legendFormat": "{{entity_type}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Processing Quality",
                        "type": "stat",
                        "targets": [{
                            "expr": "rate(kgas_entities_extracted_total[5m]) / rate(kgas_documents_processed_total[5m])",
                            "legendFormat": "Entities per Document"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_error_tracking_dashboard(self) -> Dict[str, Any]:
        """Create error tracking dashboard."""
        
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Error Tracking",
                "tags": ["kgas", "errors"],
                "timezone": "browser",
                "refresh": "30s",
                "panels": [
                    {
                        "id": 1,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_documents_processed_total{status=\"error\"}[5m])",
                            "legendFormat": "Document Errors"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "API Errors",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_api_calls_total{status=\"error\"}[5m])",
                            "legendFormat": "{{provider}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Database Errors",
                        "type": "graph",
                        "targets": [{
                            "expr": "rate(kgas_database_operations_total{status=\"error\"}[5m])",
                            "legendFormat": "{{operation_type}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Health Check Failures",
                        "type": "stat",
                        "targets": [{
                            "expr": "kgas_health_check_status == 0",
                            "legendFormat": "{{service}}"
                        }],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def provision_all_dashboards(self) -> Dict[str, Any]:
        """Provision all dashboards to Grafana."""
        
        dashboards = [
            ("system_overview", self.create_system_overview_dashboard()),
            ("performance", self.create_performance_dashboard()),
            ("database", self.create_database_dashboard()),
            ("api_monitoring", self.create_api_monitoring_dashboard()),
            ("entity_processing", self.create_entity_processing_dashboard()),
            ("error_tracking", self.create_error_tracking_dashboard())
        ]
        
        results = {}
        
        for dashboard_name, dashboard_config in dashboards:
            try:
                response = requests.post(
                    f"{self.grafana_url}/api/dashboards/db",
                    headers=self.headers,
                    json=dashboard_config
                )
                
                if response.status_code == 200:
                    results[dashboard_name] = {
                        "status": "success",
                        "dashboard_id": response.json().get("id"),
                        "url": response.json().get("url")
                    }
                else:
                    results[dashboard_name] = {
                        "status": "error",
                        "error": response.text
                    }
                    
            except Exception as e:
                results[dashboard_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Log evidence
        with open('Evidence.md', 'a') as f:
            f.write(f"\n## Grafana Dashboard Provisioning Evidence\n")
            f.write(f"**Timestamp**: {datetime.now().isoformat()}\n")
            f.write(f"**Total Dashboards**: {len(dashboards)}\n")
            f.write(f"**Successful**: {sum(1 for r in results.values() if r['status'] == 'success')}\n")
            f.write(f"**Failed**: {sum(1 for r in results.values() if r['status'] == 'error')}\n")
            f.write(f"**Dashboard Results**:\n")
            for name, result in results.items():
                f.write(f"  - {name}: {result['status']}\n")
            f.write(f"\n")
        
        return results