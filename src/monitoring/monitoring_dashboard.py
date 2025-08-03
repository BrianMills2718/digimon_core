#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard for Structured Output Operations

Provides live monitoring capabilities for structured LLM operations with:
- Real-time metrics display
- Health status monitoring  
- Performance trend analysis
- Alert notifications
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading
from pathlib import Path

try:
    import streamlit as st
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .structured_output_monitor import get_monitor, StructuredOutputMetrics, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for monitoring dashboard."""
    refresh_interval: int = 5  # seconds
    max_display_metrics: int = 1000
    alert_sound: bool = False
    theme: str = "dark"
    auto_refresh: bool = True


class MonitoringDashboard:
    """
    Real-time dashboard for structured output monitoring.
    
    Provides live visualization of:
    - System health status
    - Performance metrics
    - Error patterns
    - Component-specific analytics
    """
    
    def __init__(self, config: DashboardConfig = None):
        """Initialize monitoring dashboard."""
        self.config = config or DashboardConfig()
        self.monitor = get_monitor()
        self.last_refresh = datetime.now()
        
        # Dashboard state
        self.alerts_acknowledged = set()
        self.dashboard_stats = {
            "page_loads": 0,
            "last_user_activity": datetime.now()
        }
        
        logger.info("Monitoring dashboard initialized")
    
    def render_dashboard(self):
        """Render the main monitoring dashboard."""
        if not STREAMLIT_AVAILABLE:
            st.error("Streamlit not available. Install with: pip install streamlit plotly")
            return
        
        st.set_page_config(
            page_title="KGAS Structured Output Monitor",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Dashboard header
        self._render_header()
        
        # Sidebar controls
        self._render_sidebar()
        
        # Main content
        self._render_main_content()
        
        # Auto-refresh logic
        if self.config.auto_refresh:
            time.sleep(self.config.refresh_interval)
            st.rerun()
    
    def _render_header(self):
        """Render dashboard header with system status."""
        st.title("🔍 KGAS Structured Output Monitor")
        
        # System status indicator
        health_results = self.monitor.validate_system_health()
        critical_alerts = [r for r in health_results if not r.success and r.severity == "critical"]
        error_alerts = [r for r in health_results if not r.success and r.severity == "error"]
        warning_alerts = [r for r in health_results if not r.success and r.severity == "warning"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if critical_alerts:
                st.error(f"🚨 {len(critical_alerts)} Critical Issues")
            elif error_alerts:
                st.warning(f"⚠️ {len(error_alerts)} Errors")
            elif warning_alerts:
                st.info(f"⚠️ {len(warning_alerts)} Warnings")
            else:
                st.success("✅ System Healthy")
        
        with col2:
            recent_metrics = self.monitor._get_recent_metrics(timedelta(minutes=5))
            st.metric("Operations (5m)", len(recent_metrics))
        
        with col3:
            if recent_metrics:
                success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
                st.metric("Success Rate", f"{success_rate:.1%}")
            else:
                st.metric("Success Rate", "No Data")
        
        with col4:
            st.metric("Last Update", self.last_refresh.strftime("%H:%M:%S"))
    
    def _render_sidebar(self):
        """Render sidebar controls."""
        with st.sidebar:
            st.header("📊 Dashboard Controls")
            
            # Auto-refresh toggle
            self.config.auto_refresh = st.checkbox(
                "Auto Refresh", 
                value=self.config.auto_refresh
            )
            
            if self.config.auto_refresh:
                self.config.refresh_interval = st.slider(
                    "Refresh Interval (s)", 
                    min_value=1, 
                    max_value=60, 
                    value=self.config.refresh_interval
                )
            
            # Time window selection
            st.subheader("Time Window")
            time_window_options = {
                "Last 5 minutes": timedelta(minutes=5),
                "Last 15 minutes": timedelta(minutes=15),
                "Last hour": timedelta(hours=1),
                "Last 6 hours": timedelta(hours=6),
                "Last 24 hours": timedelta(hours=24)
            }
            
            selected_window = st.selectbox(
                "Select Time Window",
                options=list(time_window_options.keys()),
                index=2  # Default to "Last hour"
            )
            
            self.time_window = time_window_options[selected_window]
            
            # Component filter
            st.subheader("Component Filter")
            all_components = set(m.component for m in self.monitor.metrics_history)
            if all_components:
                selected_components = st.multiselect(
                    "Select Components",
                    options=list(all_components),
                    default=list(all_components)
                )
            else:
                selected_components = []
            
            self.selected_components = selected_components
            
            # Manual refresh button
            if st.button("🔄 Refresh Now"):
                self.last_refresh = datetime.now()
                st.rerun()
            
            # Export options
            st.subheader("Export Data")
            if st.button("📥 Export JSON"):
                self._export_data("json")
            if st.button("📊 Export CSV"):
                self._export_data("csv")
    
    def _render_main_content(self):
        """Render main dashboard content."""
        # Get filtered metrics
        filtered_metrics = self._get_filtered_metrics()
        
        if not filtered_metrics:
            st.warning("No data available for selected filters")
            return
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏥 Health", "⚡ Performance", "🔧 Components"])
        
        with tab1:
            self._render_overview_tab(filtered_metrics)
        
        with tab2:
            self._render_health_tab()
        
        with tab3:
            self._render_performance_tab(filtered_metrics)
        
        with tab4:
            self._render_components_tab(filtered_metrics)
    
    def _render_overview_tab(self, metrics: List[StructuredOutputMetrics]):
        """Render overview tab with key metrics."""
        st.header("📈 System Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        total_ops = len(metrics)
        successful_ops = sum(1 for m in metrics if m.success)
        validation_errors = sum(1 for m in metrics if m.validation_error)
        llm_errors = sum(1 for m in metrics if m.llm_error)
        
        with col1:
            st.metric("Total Operations", total_ops)
        
        with col2:
            success_rate = successful_ops / total_ops if total_ops > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1%}")
        
        with col3:
            val_error_rate = validation_errors / total_ops if total_ops > 0 else 0
            st.metric("Validation Errors", f"{val_error_rate:.1%}")
        
        with col4:
            llm_error_rate = llm_errors / total_ops if total_ops > 0 else 0
            st.metric("LLM Errors", f"{llm_error_rate:.1%}")
        
        # Operations timeline
        st.subheader("Operations Timeline")
        if metrics:
            # Create timeline chart
            df = pd.DataFrame([
                {
                    "timestamp": m.timestamp,
                    "success": m.success,
                    "component": m.component,
                    "response_time": m.response_time_ms
                }
                for m in metrics
            ])
            
            fig = px.scatter(
                df,
                x="timestamp",
                y="response_time",
                color="success",
                hover_data=["component"],
                title="Response Time vs Success Rate Over Time",
                color_discrete_map={True: "green", False: "red"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent alerts
        st.subheader("Recent Alerts")
        health_results = self.monitor.validate_system_health()
        alerts = [r for r in health_results if not r.success]
        
        if alerts:
            for alert in alerts[-5:]:  # Show last 5 alerts
                if alert.severity == "critical":
                    st.error(f"🚨 {alert.check_name}: {alert.message}")
                elif alert.severity == "error":
                    st.error(f"❌ {alert.check_name}: {alert.message}")
                elif alert.severity == "warning":
                    st.warning(f"⚠️ {alert.check_name}: {alert.message}")
        else:
            st.success("✅ No active alerts")
    
    def _render_health_tab(self):
        """Render health monitoring tab."""
        st.header("🏥 System Health")
        
        # Run health validation
        health_results = self.monitor.validate_system_health()
        
        # Health summary
        total_checks = len(health_results)
        passed_checks = sum(1 for r in health_results if r.success)
        health_percentage = passed_checks / total_checks if total_checks > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Health Score", f"{health_percentage:.0%}")
        
        with col2:
            st.metric("Checks Passed", f"{passed_checks}/{total_checks}")
        
        with col3:
            failed_critical = sum(1 for r in health_results if not r.success and r.severity == "critical")
            st.metric("Critical Issues", failed_critical)
        
        # Detailed health checks
        st.subheader("Health Check Details")
        
        for result in health_results:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                if result.success:
                    st.success(f"✅ {result.check_name}")
                else:
                    if result.severity == "critical":
                        st.error(f"🚨 {result.check_name}")
                    elif result.severity == "error":
                        st.error(f"❌ {result.check_name}")
                    else:
                        st.warning(f"⚠️ {result.check_name}")
            
            with col2:
                st.text(result.message)
            
            with col3:
                st.text(f"Severity: {result.severity}")
        
        # Health trends
        st.subheader("Health Trends")
        
        # Get validation history for trends
        validation_history = list(self.monitor.validation_history)
        if validation_history:
            recent_validations = validation_history[-50:]  # Last 50 validations
            
            # Group by check name and calculate success rates
            check_trends = {}
            for validation in recent_validations:
                if validation.check_name not in check_trends:
                    check_trends[validation.check_name] = []
                check_trends[validation.check_name].append(validation.success)
            
            # Display trends
            for check_name, successes in check_trends.items():
                success_rate = sum(successes) / len(successes)
                trend_color = "green" if success_rate >= 0.95 else "orange" if success_rate >= 0.80 else "red"
                st.markdown(f"**{check_name}**: {success_rate:.1%} success rate")
    
    def _render_performance_tab(self, metrics: List[StructuredOutputMetrics]):
        """Render performance analysis tab."""
        st.header("⚡ Performance Analysis")
        
        if not metrics:
            st.warning("No performance data available")
            return
        
        # Performance metrics
        response_times = [m.response_time_ms for m in metrics]
        avg_response_time = sum(response_times) / len(response_times)
        median_response_time = sorted(response_times)[len(response_times) // 2]
        max_response_time = max(response_times)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
        
        with col2:
            st.metric("Median Response Time", f"{median_response_time:.0f}ms")
        
        with col3:
            st.metric("Max Response Time", f"{max_response_time:.0f}ms")
        
        # Response time distribution
        st.subheader("Response Time Distribution")
        fig = px.histogram(
            x=response_times,
            nbins=50,
            title="Response Time Distribution",
            labels={"x": "Response Time (ms)", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance by component
        st.subheader("Performance by Component")
        
        # Group metrics by component
        component_performance = {}
        for metric in metrics:
            if metric.component not in component_performance:
                component_performance[metric.component] = []
            component_performance[metric.component].append(metric.response_time_ms)
        
        # Create box plot
        component_data = []
        for component, times in component_performance.items():
            for time_val in times:
                component_data.append({"component": component, "response_time": time_val})
        
        if component_data:
            df = pd.DataFrame(component_data)
            fig = px.box(
                df,
                x="component",
                y="response_time",
                title="Response Time by Component"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance trends over time
        st.subheader("Performance Trends")
        
        # Create time series data
        df = pd.DataFrame([
            {
                "timestamp": m.timestamp,
                "response_time": m.response_time_ms,
                "component": m.component
            }
            for m in metrics
        ])
        
        fig = px.line(
            df,
            x="timestamp",
            y="response_time",
            color="component",
            title="Response Time Trends Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_components_tab(self, metrics: List[StructuredOutputMetrics]):
        """Render component-specific analysis tab."""
        st.header("🔧 Component Analysis")
        
        if not metrics:
            st.warning("No component data available")
            return
        
        # Component selector
        components = list(set(m.component for m in metrics))
        selected_component = st.selectbox("Select Component", components)
        
        # Filter metrics for selected component
        component_metrics = [m for m in metrics if m.component == selected_component]
        
        if not component_metrics:
            st.warning(f"No data for component: {selected_component}")
            return
        
        # Component statistics
        total_ops = len(component_metrics)
        successful_ops = sum(1 for m in component_metrics if m.success)
        success_rate = successful_ops / total_ops
        avg_response_time = sum(m.response_time_ms for m in component_metrics) / total_ops
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Operations", total_ops)
        
        with col2:
            st.metric("Success Rate", f"{success_rate:.1%}")
        
        with col3:
            st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
        
        # Schema usage for component
        st.subheader("Schema Usage")
        schema_usage = {}
        for metric in component_metrics:
            schema_usage[metric.schema_name] = schema_usage.get(metric.schema_name, 0) + 1
        
        if schema_usage:
            fig = px.pie(
                values=list(schema_usage.values()),
                names=list(schema_usage.keys()),
                title=f"Schema Usage for {selected_component}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Error analysis
        st.subheader("Error Analysis")
        
        validation_errors = [m for m in component_metrics if m.validation_error]
        llm_errors = [m for m in component_metrics if m.llm_error]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Validation Errors", len(validation_errors))
            if validation_errors:
                st.subheader("Recent Validation Errors")
                for error_metric in validation_errors[-5:]:
                    st.error(f"Schema: {error_metric.schema_name} - {error_metric.validation_error}")
        
        with col2:
            st.metric("LLM Errors", len(llm_errors))
            if llm_errors:
                st.subheader("Recent LLM Errors")
                for error_metric in llm_errors[-5:]:
                    st.error(f"Model: {error_metric.model_used} - {error_metric.llm_error}")
        
        # Recent operations table
        st.subheader("Recent Operations")
        
        recent_operations = component_metrics[-20:]  # Last 20 operations
        
        table_data = []
        for metric in recent_operations:
            table_data.append({
                "Timestamp": metric.timestamp.strftime("%H:%M:%S"),
                "Schema": metric.schema_name,
                "Success": "✅" if metric.success else "❌",
                "Response Time (ms)": f"{metric.response_time_ms:.0f}",
                "Model": metric.model_used,
                "Error": metric.validation_error or metric.llm_error or "-"
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
    
    def _get_filtered_metrics(self) -> List[StructuredOutputMetrics]:
        """Get metrics filtered by time window and components."""
        # Time filter
        recent_metrics = self.monitor._get_recent_metrics(self.time_window)
        
        # Component filter
        if self.selected_components:
            filtered_metrics = [
                m for m in recent_metrics 
                if m.component in self.selected_components
            ]
        else:
            filtered_metrics = recent_metrics
        
        return filtered_metrics
    
    def _export_data(self, format: str):
        """Export monitoring data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_data_{timestamp}.{format}"
        filepath = f"/tmp/{filename}"
        
        success = self.monitor.export_metrics(filepath, format=format)
        
        if success:
            st.success(f"✅ Data exported to {filepath}")
            
            # Provide download link
            with open(filepath, 'rb') as f:
                st.download_button(
                    label=f"📥 Download {format.upper()}",
                    data=f.read(),
                    file_name=filename,
                    mime='application/octet-stream'
                )
        else:
            st.error(f"❌ Failed to export data")


def launch_monitoring_dashboard():
    """Launch the monitoring dashboard."""
    if not STREAMLIT_AVAILABLE:
        print("❌ Streamlit not available. Install with: pip install streamlit plotly")
        return False
    
    dashboard = MonitoringDashboard()
    dashboard.render_dashboard()
    return True


if __name__ == "__main__":
    launch_monitoring_dashboard()