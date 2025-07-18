#!/usr/bin/env python3
"""
Grafana Dashboards Demo

Demonstrates the creation of Grafana dashboards for KGAS visual monitoring.
Creates comprehensive dashboards and monitoring stack configuration.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitoring.grafana_dashboards import GrafanaDashboardManager, create_monitoring_stack


def display_dashboard_info(dashboard_name: str, dashboard_config: dict):
    """Display information about a dashboard"""
    dashboard_data = dashboard_config.get("dashboard", {})
    print(f"\n📊 {dashboard_name.replace('_', ' ').title()}")
    print("-" * 40)
    print(f"Title: {dashboard_data.get('title', 'N/A')}")
    print(f"Tags: {', '.join(dashboard_data.get('tags', []))}")
    print(f"Refresh: {dashboard_data.get('refresh', 'N/A')}")
    print(f"Panels: {len(dashboard_data.get('panels', []))}")
    
    # Show panel details
    for i, panel in enumerate(dashboard_data.get('panels', [])[:3]):  # Show first 3 panels
        print(f"  Panel {i+1}: {panel.get('title', 'N/A')} ({panel.get('type', 'N/A')})")
    
    if len(dashboard_data.get('panels', [])) > 3:
        print(f"  ... and {len(dashboard_data.get('panels', [])) - 3} more panels")


def main():
    """Main demo function"""
    print("🎯 Phase 2 Grafana Dashboards Demo")
    print("=" * 50)
    
    # Create dashboard manager
    dashboard_manager = GrafanaDashboardManager()
    
    print("📊 Creating Grafana dashboards for KGAS monitoring...")
    
    # Create individual dashboards
    dashboards = {
        "system_overview": dashboard_manager.create_system_overview_dashboard(),
        "document_processing": dashboard_manager.create_document_processing_dashboard(),
        "api_performance": dashboard_manager.create_api_performance_dashboard(),
        "database_monitoring": dashboard_manager.create_database_monitoring_dashboard(),
        "workflow_execution": dashboard_manager.create_workflow_execution_dashboard(),
        "error_tracking": dashboard_manager.create_error_tracking_dashboard()
    }
    
    # Display dashboard information
    for name, config in dashboards.items():
        display_dashboard_info(name, config)
    
    # Create all dashboard files
    print(f"\n💾 Creating dashboard files...")
    dashboard_files = dashboard_manager.create_all_dashboards()
    
    for name, file_path in dashboard_files.items():
        print(f"  ✅ {name}: {file_path}")
    
    # Get dashboard summary
    summary = dashboard_manager.get_dashboard_summary()
    print(f"\n📈 Dashboard Summary:")
    print(f"  Dashboards directory: {summary['dashboards_directory']}")
    print(f"  Available dashboards: {summary['available_dashboards']}")
    print(f"  Dashboard templates: {len(summary['dashboard_templates'])}")
    
    # Create complete monitoring stack
    print(f"\n🚀 Creating complete monitoring stack...")
    
    output_dir = "monitoring_stack"
    monitoring_stack = create_monitoring_stack(output_dir)
    
    print(f"✅ Monitoring stack created:")
    print(f"  Output directory: {monitoring_stack['output_directory']}")
    print(f"  Docker Compose file: {monitoring_stack['docker_compose_file']}")
    print(f"  Grafana datasource file: {monitoring_stack['grafana_datasource_file']}")
    print(f"  Prometheus config file: {monitoring_stack['prometheus_config_file']}")
    
    # Show sample dashboard JSON
    print(f"\n📋 Sample Dashboard Configuration (System Overview):")
    print("-" * 50)
    
    system_overview = dashboards["system_overview"]
    sample_panel = system_overview["dashboard"]["panels"][0]
    
    print(f"Panel: {sample_panel['title']}")
    print(f"Type: {sample_panel['type']}")
    print(f"Query: {sample_panel['targets'][0]['expr']}")
    print(f"Position: {sample_panel['gridPos']}")
    
    # Show deployment instructions
    print(f"\n🐳 Deployment Instructions:")
    print("=" * 40)
    print("1. Start the monitoring stack:")
    print(f"   cd {output_dir}")
    print("   docker-compose up -d")
    print()
    print("2. Access dashboards:")
    print(f"   Grafana: {monitoring_stack['grafana_url']} (admin/admin)")
    print(f"   Prometheus: {monitoring_stack['prometheus_url']}")
    print()
    print("3. Import dashboards:")
    print("   - Open Grafana web interface")
    print("   - Go to '+' -> Import")
    print("   - Upload the JSON files from the dashboards directory")
    print()
    print("4. Configure data source:")
    print("   - Data source should be auto-configured")
    print("   - Prometheus URL: http://prometheus:9090")
    
    # Show metrics requirements
    print(f"\n📊 Metrics Requirements:")
    print("=" * 30)
    print("These dashboards require the following metrics:")
    print("- kgas_documents_processed_total")
    print("- kgas_document_processing_duration_seconds")
    print("- kgas_entities_extracted_total")
    print("- kgas_relationships_extracted_total")
    print("- kgas_api_calls_total")
    print("- kgas_api_call_duration_seconds")
    print("- kgas_database_operations_total")
    print("- kgas_database_query_duration_seconds")
    print("- kgas_workflow_executions_total")
    print("- kgas_workflow_duration_seconds")
    print("- kgas_errors_total")
    print("- kgas_component_health")
    print("- kgas_cpu_usage_percent")
    print("- kgas_memory_usage_bytes")
    print("- kgas_disk_usage_bytes")
    
    print(f"\n🎉 Phase 2 Task 3: Grafana Dashboards - COMPLETE")
    print("✅ 6 comprehensive dashboards created")
    print("✅ Docker Compose monitoring stack ready")
    print("✅ Prometheus and Grafana configuration included")
    print("✅ Visual monitoring system fully configured")
    
    return 0


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)