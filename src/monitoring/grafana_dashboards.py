"""
Grafana Dashboard Configuration for KGAS

Creates and manages Grafana dashboards for visual monitoring of the KGAS system.
Provides comprehensive dashboards for system performance, processing metrics, and health monitoring.
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path

from src.core.config import ConfigurationManager
from src.core.logging_config import get_logger


class GrafanaDashboardManager:
    """Manages Grafana dashboards for KGAS monitoring"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("monitoring.grafana")
        
        # Configuration
        self.dashboards_dir = Path(__file__).parent / "dashboards"
        self.dashboards_dir.mkdir(exist_ok=True)
        
        # Dashboard metadata
        self.dashboard_templates = {
            "system_overview": "KGAS System Overview",
            "document_processing": "Document Processing Metrics",
            "api_performance": "API Performance Dashboard",
            "database_monitoring": "Database Operations Dashboard",
            "workflow_execution": "Workflow Execution Dashboard",
            "error_tracking": "Error Tracking Dashboard"
        }
    
    def create_system_overview_dashboard(self) -> Dict[str, Any]:
        """Create system overview dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS System Overview",
                "tags": ["kgas", "system", "overview"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "System Health",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "kgas_component_health",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "thresholds"
                                },
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "green", "value": 1}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "CPU Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "kgas_cpu_usage_percent",
                                "legendFormat": "CPU Usage %",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Memory Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "kgas_memory_usage_bytes{type=\"used\"} / kgas_memory_usage_bytes{type=\"total\"} * 100",
                                "legendFormat": "Memory Usage %",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
                    },
                    {
                        "id": 4,
                        "title": "Disk Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "kgas_disk_usage_bytes{type=\"used\"} / kgas_disk_usage_bytes{type=\"total\"} * 100",
                                "legendFormat": "Disk Usage %",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
                    },
                    {
                        "id": 5,
                        "title": "Documents Processed",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_documents_processed_total[5m]))",
                                "legendFormat": "Documents/sec",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 4}
                    },
                    {
                        "id": 6,
                        "title": "API Calls Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_api_calls_total[5m])) by (api_provider)",
                                "legendFormat": "{{api_provider}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 7,
                        "title": "Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_errors_total[5m])) by (component)",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_document_processing_dashboard(self) -> Dict[str, Any]:
        """Create document processing dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Document Processing",
                "tags": ["kgas", "documents", "processing"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Document Processing Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_documents_processed_total[5m])) by (phase)",
                                "legendFormat": "{{phase}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Processing Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(kgas_document_processing_duration_seconds_bucket[5m])) by (le, phase))",
                                "legendFormat": "{{phase}} 95th percentile",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.50, sum(rate(kgas_document_processing_duration_seconds_bucket[5m])) by (le, phase))",
                                "legendFormat": "{{phase}} 50th percentile",
                                "refId": "B"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Entities Extracted",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_entities_extracted_total[5m])) by (entity_type)",
                                "legendFormat": "{{entity_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Relationships Extracted",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_relationships_extracted_total[5m])) by (relationship_type)",
                                "legendFormat": "{{relationship_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "Processing by Document Type",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum(kgas_documents_processed_total) by (document_type)",
                                "legendFormat": "{{document_type}}",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 16}
                    },
                    {
                        "id": 6,
                        "title": "Processing by Component",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum(kgas_documents_processed_total) by (component)",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 16}
                    },
                    {
                        "id": 7,
                        "title": "Processing by Phase",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum(kgas_documents_processed_total) by (phase)",
                                "legendFormat": "{{phase}}",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 8, "x": 16, "y": 16}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_api_performance_dashboard(self) -> Dict[str, Any]:
        """Create API performance dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS API Performance",
                "tags": ["kgas", "api", "performance"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "API Call Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_api_calls_total[5m])) by (api_provider)",
                                "legendFormat": "{{api_provider}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "API Call Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(kgas_api_call_duration_seconds_bucket[5m])) by (le, api_provider))",
                                "legendFormat": "{{api_provider}} 95th percentile",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.50, sum(rate(kgas_api_call_duration_seconds_bucket[5m])) by (le, api_provider))",
                                "legendFormat": "{{api_provider}} 50th percentile",
                                "refId": "B"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "API Success Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_api_calls_total{status=\"success\"}[5m])) by (api_provider) / sum(rate(kgas_api_calls_total[5m])) by (api_provider) * 100",
                                "legendFormat": "{{api_provider}} Success Rate",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "API Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_api_calls_total{status!=\"success\"}[5m])) by (api_provider, status)",
                                "legendFormat": "{{api_provider}} {{status}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_database_monitoring_dashboard(self) -> Dict[str, Any]:
        """Create database monitoring dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Database Operations",
                "tags": ["kgas", "database", "monitoring"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Database Operations Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_database_operations_total[5m])) by (database_type)",
                                "legendFormat": "{{database_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Database Query Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(kgas_database_query_duration_seconds_bucket[5m])) by (le, database_type))",
                                "legendFormat": "{{database_type}} 95th percentile",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.50, sum(rate(kgas_database_query_duration_seconds_bucket[5m])) by (le, database_type))",
                                "legendFormat": "{{database_type}} 50th percentile",
                                "refId": "B"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Database Success Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_database_operations_total{status=\"success\"}[5m])) by (database_type) / sum(rate(kgas_database_operations_total[5m])) by (database_type) * 100",
                                "legendFormat": "{{database_type}} Success Rate",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Operations by Type",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_database_operations_total[5m])) by (operation)",
                                "legendFormat": "{{operation}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_workflow_execution_dashboard(self) -> Dict[str, Any]:
        """Create workflow execution dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Workflow Execution",
                "tags": ["kgas", "workflow", "execution"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Workflow Execution Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_workflow_executions_total[5m])) by (workflow_type)",
                                "legendFormat": "{{workflow_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Workflow Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, sum(rate(kgas_workflow_duration_seconds_bucket[5m])) by (le, workflow_type))",
                                "legendFormat": "{{workflow_type}} 95th percentile",
                                "refId": "A"
                            },
                            {
                                "expr": "histogram_quantile(0.50, sum(rate(kgas_workflow_duration_seconds_bucket[5m])) by (le, workflow_type))",
                                "legendFormat": "{{workflow_type}} 50th percentile",
                                "refId": "B"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Workflow Success Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_workflow_executions_total{status=\"success\"}[5m])) by (workflow_type) / sum(rate(kgas_workflow_executions_total[5m])) by (workflow_type) * 100",
                                "legendFormat": "{{workflow_type}} Success Rate",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "percent",
                                "min": 0,
                                "max": 100
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Concurrent Operations",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "kgas_concurrent_operations",
                                "legendFormat": "{{operation_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "short"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_error_tracking_dashboard(self) -> Dict[str, Any]:
        """Create error tracking dashboard"""
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "KGAS Error Tracking",
                "tags": ["kgas", "errors", "tracking"],
                "timezone": "browser",
                "refresh": "5s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Error Rate by Component",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_errors_total[5m])) by (component)",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Error Rate by Type",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(kgas_errors_total[5m])) by (error_type)",
                                "legendFormat": "{{error_type}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Total Errors",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(kgas_errors_total)",
                                "legendFormat": "Total Errors",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "thresholds"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 10},
                                        {"color": "red", "value": 50}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Error Distribution",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "sum(kgas_errors_total) by (error_type)",
                                "legendFormat": "{{error_type}}",
                                "refId": "A"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 9, "x": 6, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "Component Health",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "kgas_component_health",
                                "legendFormat": "{{component}}",
                                "refId": "A"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "unit": "short",
                                "min": 0,
                                "max": 1
                            }
                        },
                        "gridPos": {"h": 8, "w": 9, "x": 15, "y": 8}
                    }
                ]
            }
        }
        
        return dashboard
    
    def create_all_dashboards(self) -> Dict[str, str]:
        """Create all dashboard configurations and save them to files"""
        dashboards = {
            "system_overview": self.create_system_overview_dashboard(),
            "document_processing": self.create_document_processing_dashboard(),
            "api_performance": self.create_api_performance_dashboard(),
            "database_monitoring": self.create_database_monitoring_dashboard(),
            "workflow_execution": self.create_workflow_execution_dashboard(),
            "error_tracking": self.create_error_tracking_dashboard()
        }
        
        saved_files = {}
        
        for name, dashboard in dashboards.items():
            file_path = self.dashboards_dir / f"{name}_dashboard.json"
            
            with open(file_path, 'w') as f:
                json.dump(dashboard, f, indent=2)
            
            saved_files[name] = str(file_path)
            self.logger.info("Created dashboard: %s -> %s", name, file_path)
        
        return saved_files
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary of available dashboards"""
        dashboard_files = list(self.dashboards_dir.glob("*_dashboard.json"))
        
        return {
            "dashboards_directory": str(self.dashboards_dir),
            "available_dashboards": len(dashboard_files),
            "dashboard_files": [str(f) for f in dashboard_files],
            "dashboard_templates": self.dashboard_templates
        }
    
    def generate_docker_compose_config(self) -> str:
        """Generate Docker Compose configuration for Grafana with dashboards"""
        config = f"""
version: '3.8'

services:
  grafana:
    image: grafana/grafana:latest
    container_name: kgas-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - {self.dashboards_dir}:/etc/grafana/provisioning/dashboards/kgas:ro
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro
    networks:
      - kgas-monitoring

  prometheus:
    image: prom/prometheus:latest
    container_name: kgas-prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus-data:/prometheus
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - kgas-monitoring

volumes:
  grafana-data:
  prometheus-data:

networks:
  kgas-monitoring:
    driver: bridge
"""
        
        return config.strip()
    
    def generate_grafana_datasource_config(self) -> str:
        """Generate Grafana datasource configuration"""
        config = """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    basicAuth: false
    isDefault: true
    editable: true
"""
        
        return config.strip()
    
    def generate_prometheus_config(self) -> str:
        """Generate Prometheus configuration"""
        config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kgas'
    static_configs:
      - targets: ['host.docker.internal:8000']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
        
        return config.strip()


def create_monitoring_stack(output_dir: str = "monitoring") -> Dict[str, Any]:
    """Create complete monitoring stack with Grafana dashboards"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create dashboard manager
    dashboard_manager = GrafanaDashboardManager()
    
    # Create all dashboards
    dashboard_files = dashboard_manager.create_all_dashboards()
    
    # Create Docker Compose configuration
    docker_compose_config = dashboard_manager.generate_docker_compose_config()
    with open(output_path / "docker-compose.yml", 'w') as f:
        f.write(docker_compose_config)
    
    # Create Grafana datasource configuration
    datasource_config = dashboard_manager.generate_grafana_datasource_config()
    with open(output_path / "grafana-datasources.yml", 'w') as f:
        f.write(datasource_config)
    
    # Create Prometheus configuration
    prometheus_config = dashboard_manager.generate_prometheus_config()
    with open(output_path / "prometheus.yml", 'w') as f:
        f.write(prometheus_config)
    
    return {
        "output_directory": str(output_path),
        "dashboard_files": dashboard_files,
        "docker_compose_file": str(output_path / "docker-compose.yml"),
        "grafana_datasource_file": str(output_path / "grafana-datasources.yml"),
        "prometheus_config_file": str(output_path / "prometheus.yml"),
        "grafana_url": "http://localhost:3000",
        "prometheus_url": "http://localhost:9090"
    }