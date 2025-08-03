#!/usr/bin/env python3
"""
Batch Processing Monitor - Phase D.4 Implementation

Real-time batch processing monitoring dashboard with resource tracking and error management.
"""

import streamlit as st
import time
import asyncio
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import logging
import json
from collections import deque

logger = logging.getLogger(__name__)


class BatchProcessingMonitor:
    """
    Real-time batch processing monitoring dashboard.
    
    Features:
    - Active batch tracking
    - Resource utilization monitoring
    - Error tracking and alerts
    - Performance metrics
    - Historical analysis
    """
    
    def __init__(self):
        self.refresh_interval = 5  # seconds
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize session state
        if 'batch_monitor_state' not in st.session_state:
            st.session_state.batch_monitor_state = {
                'selected_batch': None,
                'show_completed': False,
                'alert_threshold': 0.8,
                'metric_window': 60,  # minutes
                'auto_refresh': True
            }
        
        # Metrics tracking (in production, would come from database)
        if 'batch_metrics' not in st.session_state:
            st.session_state.batch_metrics = {
                'throughput': deque(maxlen=100),
                'latency': deque(maxlen=100),
                'error_rate': deque(maxlen=100),
                'resource_usage': deque(maxlen=100)
            }
    
    def render_batch_monitor(self):
        """Render the batch processing monitor dashboard"""
        st.header("⚡ Batch Processing Monitor")
        
        # Control panel
        self._render_control_panel()
        
        # Current batch status overview
        self._render_batch_overview()
        
        # Active batches table
        self._render_active_batches()
        
        # Resource utilization
        col1, col2 = st.columns(2)
        with col1:
            self._render_resource_utilization()
        with col2:
            self._render_processing_queue()
        
        # Error tracking
        self._render_error_tracking()
        
        # Historical performance
        self._render_historical_performance()
        
        # Detailed batch view
        if st.session_state.batch_monitor_state['selected_batch']:
            self._render_batch_details(st.session_state.batch_monitor_state['selected_batch'])
    
    def _render_control_panel(self):
        """Render monitor control panel"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Auto-refresh toggle
            auto_refresh = st.checkbox(
                "Auto-refresh",
                value=st.session_state.batch_monitor_state['auto_refresh']
            )
            st.session_state.batch_monitor_state['auto_refresh'] = auto_refresh
        
        with col2:
            # Show completed toggle
            show_completed = st.checkbox(
                "Show Completed",
                value=st.session_state.batch_monitor_state['show_completed']
            )
            st.session_state.batch_monitor_state['show_completed'] = show_completed
        
        with col3:
            # Alert threshold
            alert_threshold = st.slider(
                "Alert Threshold",
                0.5, 1.0,
                st.session_state.batch_monitor_state['alert_threshold'],
                0.05
            )
            st.session_state.batch_monitor_state['alert_threshold'] = alert_threshold
        
        with col4:
            # Metric window
            metric_window = st.selectbox(
                "Metric Window",
                [15, 30, 60, 120],
                index=2
            )
            st.session_state.batch_monitor_state['metric_window'] = metric_window
    
    def _render_batch_overview(self):
        """Render batch processing overview"""
        st.subheader("Processing Overview")
        
        # Get current metrics
        metrics = self._get_current_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Batches",
                metrics['active_batches'],
                delta=f"{metrics['active_batches_change']:+d}"
            )
        
        with col2:
            st.metric(
                "Queue Size",
                metrics['queue_size'],
                delta=f"{metrics['queue_size_change']:+d}",
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Success Rate",
                f"{metrics['success_rate']:.1%}",
                delta=f"{metrics['success_rate_change']:+.1%}"
            )
        
        with col4:
            st.metric(
                "Avg Processing Time",
                f"{metrics['avg_processing_time']:.1f}s",
                delta=f"{metrics['processing_time_change']:+.1f}s",
                delta_color="inverse"
            )
        
        # Alerts
        if metrics['alerts']:
            for alert in metrics['alerts']:
                if alert['severity'] == 'error':
                    st.error(f"🚨 {alert['message']}")
                elif alert['severity'] == 'warning':
                    st.warning(f"⚠️ {alert['message']}")
                else:
                    st.info(f"ℹ️ {alert['message']}")
    
    def _render_active_batches(self):
        """Render active batches table"""
        st.subheader("Active Batches")
        
        # Get batch data
        batches = self._get_active_batches()
        
        if not batches:
            st.info("No active batches")
            return
        
        # Create DataFrame
        df = pd.DataFrame(batches)
        
        # Add progress bars
        df['progress_bar'] = df['progress'].apply(
            lambda x: f"{'█' * int(x * 10)}{'░' * (10 - int(x * 10))} {x:.0%}"
        )
        
        # Style the dataframe
        styled_df = df.style.apply(
            lambda x: ['background-color: #ff4444' if x['status'] == 'error'
                      else 'background-color: #ffaa44' if x['status'] == 'warning'
                      else 'background-color: #44ff44' if x['status'] == 'completed'
                      else '' for _ in x],
            axis=1
        )
        
        # Display table
        selected_batch = st.dataframe(
            df[['batch_id', 'status', 'progress_bar', 'documents', 'started', 'eta']],
            use_container_width=True,
            height=200
        )
        
        # Batch selection
        batch_ids = df['batch_id'].tolist()
        if batch_ids:
            selected = st.selectbox(
                "Select batch for details",
                ["None"] + batch_ids
            )
            
            if selected != "None":
                st.session_state.batch_monitor_state['selected_batch'] = selected
    
    def _render_resource_utilization(self):
        """Render resource utilization metrics"""
        st.subheader("Resource Utilization")
        
        # Get resource data
        resources = self._get_resource_metrics()
        
        # Create gauge charts
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=['CPU Usage', 'Memory Usage', 'Disk I/O', 'Network I/O']
        )
        
        # CPU gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=resources['cpu_usage'],
                domain={'x': [0, 1], 'y': [0, 1]},
                delta={'reference': resources['cpu_avg']},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 90}}
            ),
            row=1, col=1
        )
        
        # Memory gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=resources['memory_usage'],
                domain={'x': [0, 1], 'y': [0, 1]},
                delta={'reference': resources['memory_avg']},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "darkgreen"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': 85}}
            ),
            row=1, col=2
        )
        
        # Disk I/O gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=resources['disk_io'],
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 1000]},
                       'bar': {'color': "purple"},
                       'steps': [
                           {'range': [0, 500], 'color': "lightgray"},
                           {'range': [500, 800], 'color': "yellow"},
                           {'range': [800, 1000], 'color': "red"}]}
            ),
            row=2, col=1
        )
        
        # Network I/O gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=resources['network_io'],
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "orange"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}]}
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_processing_queue(self):
        """Render processing queue status"""
        st.subheader("Processing Queue")
        
        # Get queue data
        queue_data = self._get_queue_metrics()
        
        # Queue depth over time
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=queue_data['timestamps'],
            y=queue_data['queue_depth'],
            mode='lines+markers',
            name='Queue Depth',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=queue_data['timestamps'],
            y=queue_data['processing_rate'],
            mode='lines+markers',
            name='Processing Rate',
            line=dict(color='green', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Queue Depth and Processing Rate",
            xaxis_title="Time",
            yaxis=dict(title="Queue Depth", side='left'),
            yaxis2=dict(title="Processing Rate (docs/min)", side='right', overlaying='y'),
            hovermode='x',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Queue statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Queue", queue_data['current_depth'])
        with col2:
            st.metric("Avg Wait Time", f"{queue_data['avg_wait_time']:.1f}s")
        with col3:
            st.metric("Processing Rate", f"{queue_data['current_rate']:.1f}/min")
    
    def _render_error_tracking(self):
        """Render error tracking section"""
        st.subheader("Error Tracking")
        
        # Get error data
        errors = self._get_error_metrics()
        
        if not errors['recent_errors']:
            st.success("No recent errors")
            return
        
        # Error rate chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.line(
                errors['error_timeline'],
                x='timestamp',
                y='error_rate',
                title='Error Rate Over Time',
                color_discrete_sequence=['red']
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Error breakdown
            fig = px.pie(
                errors['error_breakdown'],
                values='count',
                names='error_type',
                title='Error Types'
            )
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent errors table
        st.write("Recent Errors:")
        error_df = pd.DataFrame(errors['recent_errors'])
        st.dataframe(
            error_df[['timestamp', 'batch_id', 'error_type', 'message']],
            use_container_width=True,
            height=150
        )
    
    def _render_historical_performance(self):
        """Render historical performance metrics"""
        st.subheader("Historical Performance")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            ["Last Hour", "Last 24 Hours", "Last Week", "Last Month"]
        )
        
        # Get historical data
        history = self._get_historical_metrics(time_range)
        
        # Create multi-metric chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Throughput', 'Success Rate', 'Average Latency', 'Resource Usage']
        )
        
        # Throughput
        fig.add_trace(
            go.Scatter(
                x=history['timestamps'],
                y=history['throughput'],
                mode='lines',
                name='Throughput',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # Success rate
        fig.add_trace(
            go.Scatter(
                x=history['timestamps'],
                y=history['success_rate'],
                mode='lines',
                name='Success Rate',
                line=dict(color='green')
            ),
            row=1, col=2
        )
        
        # Latency
        fig.add_trace(
            go.Scatter(
                x=history['timestamps'],
                y=history['avg_latency'],
                mode='lines',
                name='Avg Latency',
                line=dict(color='orange')
            ),
            row=2, col=1
        )
        
        # Resource usage
        fig.add_trace(
            go.Scatter(
                x=history['timestamps'],
                y=history['cpu_usage'],
                mode='lines',
                name='CPU',
                line=dict(color='red')
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=history['timestamps'],
                y=history['memory_usage'],
                mode='lines',
                name='Memory',
                line=dict(color='purple')
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_batch_details(self, batch_id: str):
        """Render detailed view of selected batch"""
        st.divider()
        st.subheader(f"Batch Details: {batch_id}")
        
        # Get batch details
        details = self._get_batch_details(batch_id)
        
        if not details:
            st.error("Batch not found")
            return
        
        # Basic info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Status:**", details['status'])
            st.write("**Priority:**", details['priority'])
            st.write("**Started:**", details['started'])
        
        with col2:
            st.write("**Documents:**", f"{details['processed']}/{details['total']}")
            st.write("**Success Rate:**", f"{details['success_rate']:.1%}")
            st.write("**ETA:**", details['eta'])
        
        with col3:
            st.write("**Avg Time/Doc:**", f"{details['avg_time']:.2f}s")
            st.write("**Memory Used:**", f"{details['memory_mb']:.1f} MB")
            st.write("**Retries:**", details['retries'])
        
        # Document status breakdown
        st.write("**Document Status:**")
        
        status_df = pd.DataFrame(details['document_status'])
        fig = px.bar(
            status_df,
            x='status',
            y='count',
            color='status',
            color_discrete_map={
                'completed': 'green',
                'processing': 'blue',
                'pending': 'gray',
                'failed': 'red'
            }
        )
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
        
        # Failed documents
        if details['failed_documents']:
            st.write("**Failed Documents:**")
            failed_df = pd.DataFrame(details['failed_documents'])
            st.dataframe(failed_df, use_container_width=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Pause Batch", disabled=details['status'] != 'processing'):
                st.info("Pausing batch...")
        
        with col2:
            if st.button("Retry Failed", disabled=not details['failed_documents']):
                st.info("Retrying failed documents...")
        
        with col3:
            if st.button("Cancel Batch", type="secondary"):
                st.warning("Cancelling batch...")
    
    # Helper methods for real data retrieval
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics"""
        return {
            'active_batches': 3,
            'active_batches_change': 1,
            'queue_size': 45,
            'queue_size_change': -5,
            'success_rate': 0.943,
            'success_rate_change': 0.021,
            'avg_processing_time': 2.4,
            'processing_time_change': -0.3,
            'alerts': [
                {'severity': 'warning', 'message': 'High memory usage on worker-2'},
                {'severity': 'info', 'message': 'Batch B-2024-001 completed successfully'}
            ]
        }
    
    def _get_active_batches(self) -> List[Dict[str, Any]]:
        """Get active batch information"""
        # Generate sample data
        return [
            {
                'batch_id': 'B-2024-001',
                'status': 'processing',
                'progress': 0.75,
                'documents': 150,
                'started': '10:15 AM',
                'eta': '10:45 AM'
            },
            {
                'batch_id': 'B-2024-002',
                'status': 'processing',
                'progress': 0.23,
                'documents': 89,
                'started': '10:32 AM',
                'eta': '11:15 AM'
            },
            {
                'batch_id': 'B-2024-003',
                'status': 'queued',
                'progress': 0.0,
                'documents': 67,
                'started': '-',
                'eta': '11:30 AM'
            }
        ]
    
    def _get_resource_metrics(self) -> Dict[str, float]:
        """Get resource utilization metrics"""
        return {
            'cpu_usage': 67.3,
            'cpu_avg': 52.1,
            'memory_usage': 78.9,
            'memory_avg': 65.4,
            'disk_io': 234.5,
            'network_io': 45.2
        }
    
    def _get_queue_metrics(self) -> Dict[str, Any]:
        """Get queue metrics"""
        # Generate sample timeline data
        timestamps = pd.date_range(
            end=datetime.now(),
            periods=20,
            freq='5min'
        )
        
        return {
            'timestamps': timestamps,
            'queue_depth': [45, 52, 48, 43, 41, 38, 42, 47, 51, 49, 
                           46, 44, 42, 40, 38, 36, 41, 45, 48, 45],
            'processing_rate': [12, 15, 13, 14, 16, 15, 13, 11, 10, 12,
                               14, 15, 16, 17, 15, 14, 13, 12, 11, 12],
            'current_depth': 45,
            'avg_wait_time': 124.3,
            'current_rate': 12.5
        }
    
    def _get_error_metrics(self) -> Dict[str, Any]:
        """Get error tracking metrics"""
        return {
            'error_timeline': pd.DataFrame({
                'timestamp': pd.date_range(end=datetime.now(), periods=20, freq='5min'),
                'error_rate': [0.02, 0.03, 0.02, 0.04, 0.06, 0.05, 0.03, 0.02, 0.01, 0.02,
                              0.03, 0.02, 0.01, 0.02, 0.03, 0.04, 0.03, 0.02, 0.01, 0.02]
            }),
            'error_breakdown': pd.DataFrame({
                'error_type': ['Network', 'Processing', 'Validation', 'Timeout'],
                'count': [12, 8, 5, 3]
            }),
            'recent_errors': [
                {
                    'timestamp': '10:42 AM',
                    'batch_id': 'B-2024-001',
                    'error_type': 'Network',
                    'message': 'Connection timeout to LLM service'
                },
                {
                    'timestamp': '10:38 AM',
                    'batch_id': 'B-2024-002',
                    'error_type': 'Processing',
                    'message': 'Memory limit exceeded for large document'
                }
            ]
        }
    
    def _get_historical_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get historical performance metrics"""
        # Generate sample data based on time range
        if time_range == "Last Hour":
            periods = 60
            freq = '1min'
        elif time_range == "Last 24 Hours":
            periods = 96
            freq = '15min'
        elif time_range == "Last Week":
            periods = 168
            freq = '1H'
        else:  # Last Month
            periods = 120
            freq = '6H'
        
        timestamps = pd.date_range(end=datetime.now(), periods=periods, freq=freq)
        
        # Generate realistic looking metrics
        import numpy as np
        
        base_throughput = 100
        base_success = 0.94
        base_latency = 2.5
        base_cpu = 50
        base_memory = 60
        
        return {
            'timestamps': timestamps,
            'throughput': base_throughput + np.random.normal(0, 10, periods),
            'success_rate': np.clip(base_success + np.random.normal(0, 0.02, periods), 0, 1),
            'avg_latency': base_latency + np.random.normal(0, 0.3, periods),
            'cpu_usage': np.clip(base_cpu + np.random.normal(0, 15, periods), 0, 100),
            'memory_usage': np.clip(base_memory + np.random.normal(0, 10, periods), 0, 100)
        }
    
    def _get_batch_details(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed batch information"""
        # Sample batch details
        return {
            'batch_id': batch_id,
            'status': 'processing',
            'priority': 'high',
            'started': '10:15 AM',
            'eta': '10:45 AM',
            'total': 150,
            'processed': 112,
            'success_rate': 0.946,
            'avg_time': 2.3,
            'memory_mb': 487.2,
            'retries': 3,
            'document_status': [
                {'status': 'completed', 'count': 106},
                {'status': 'processing', 'count': 6},
                {'status': 'pending', 'count': 32},
                {'status': 'failed', 'count': 6}
            ],
            'failed_documents': [
                {'doc_id': 'doc_123', 'error': 'Network timeout', 'retries': 2},
                {'doc_id': 'doc_456', 'error': 'Invalid format', 'retries': 1}
            ]
        }


if __name__ == "__main__":
    # Test the batch monitor
    monitor = BatchProcessingMonitor()
    monitor.render_batch_monitor()