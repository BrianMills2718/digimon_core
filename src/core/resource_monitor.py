#!/usr/bin/env python3
"""
Resource Monitor and Automatic Scaling System

Provides comprehensive system resource monitoring, bottleneck prediction, 
automatic scaling decisions, and resource optimization for large-scale 
document processing and analysis workflows.
"""

import logging
import asyncio
import threading
import time
import psutil
import gc
import os
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Union, NamedTuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque, defaultdict
from contextlib import contextmanager
from abc import ABC, abstractmethod
from enum import Enum
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import pickle

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of system resources to monitor"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"
    PROCESS = "process"


class AlertLevel(Enum):
    """Resource alert levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ScalingAction(Enum):
    """Automatic scaling actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    OPTIMIZE = "optimize"
    EMERGENCY_CLEANUP = "emergency_cleanup"


@dataclass
class ResourceMetrics:
    """Resource usage metrics at a point in time"""
    timestamp: datetime
    cpu_percent: float
    cpu_count: int
    memory_total_gb: float
    memory_used_gb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    thread_count: int
    handle_count: int = 0
    gpu_percent: float = 0.0
    gpu_memory_percent: float = 0.0
    
    def __post_init__(self):
        # Ensure GPU metrics are floats
        if self.gpu_percent is None:
            self.gpu_percent = 0.0
        if self.gpu_memory_percent is None:
            self.gpu_memory_percent = 0.0


@dataclass
class ResourceAlert:
    """Resource alert information"""
    alert_id: str
    resource_type: ResourceType
    alert_level: AlertLevel
    message: str
    current_value: float
    threshold: float
    timestamp: datetime
    suggested_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScalingDecision:
    """Automatic scaling decision"""
    decision_id: str
    action: ScalingAction
    target_resource: ResourceType
    current_value: float
    target_value: float
    confidence: float
    reasoning: str
    estimated_impact: Dict[str, Any]
    timestamp: datetime
    implemented: bool = False


@dataclass
class ResourceThresholds:
    """Resource monitoring thresholds"""
    cpu_warning: float = 70.0
    cpu_critical: float = 85.0
    cpu_emergency: float = 95.0
    memory_warning: float = 75.0
    memory_critical: float = 85.0
    memory_emergency: float = 95.0
    disk_warning: float = 80.0
    disk_critical: float = 90.0
    disk_emergency: float = 95.0
    network_warning_mbps: float = 100.0
    network_critical_mbps: float = 500.0
    process_warning: int = 1000
    process_critical: int = 2000
    gpu_warning: float = 80.0
    gpu_critical: float = 90.0


class ResourceCollector(ABC):
    """Abstract base for resource data collection"""
    
    @abstractmethod
    def collect_metrics(self) -> ResourceMetrics:
        """Collect current resource metrics"""
        pass
    
    @abstractmethod
    def get_collector_info(self) -> Dict[str, Any]:
        """Get information about this collector"""
        pass


class SystemResourceCollector(ResourceCollector):
    """System-wide resource metrics collector"""
    
    def __init__(self):
        self.boot_time = psutil.boot_time()
        self.network_stats_baseline = None
        self._initialize_network_baseline()
        
        # Try to detect GPU
        self.gpu_available = self._detect_gpu()
        
    def _initialize_network_baseline(self):
        """Initialize network statistics baseline"""
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                self.network_stats_baseline = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'timestamp': time.time()
                }
        except Exception as e:
            logger.warning(f"Failed to initialize network baseline: {e}")
    
    def _detect_gpu(self) -> bool:
        """Detect if GPU monitoring is available"""
        try:
            # Try different GPU libraries
            try:
                import GPUtil
                return len(GPUtil.getGPUs()) > 0
            except ImportError:
                pass
            
            try:
                import pynvml
                pynvml.nvmlInit()
                return pynvml.nvmlDeviceGetCount() > 0
            except (ImportError, Exception):
                pass
            
            return False
        except Exception:
            return False
    
    def collect_metrics(self) -> ResourceMetrics:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_used_gb = disk.used / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            
            # Network metrics
            network_sent_mb, network_recv_mb = self._get_network_metrics()
            
            # Process metrics
            process_count = len(psutil.pids())
            thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
            
            # Handle count (Windows specific)
            handle_count = 0
            try:
                if os.name == 'nt':  # Windows
                    handle_count = sum(p.num_handles() for p in psutil.process_iter(['num_handles']) if p.info['num_handles'])
            except Exception:
                pass
            
            # GPU metrics
            gpu_percent, gpu_memory_percent = self._get_gpu_metrics()
            
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total_gb=memory_total_gb,
                memory_used_gb=memory_used_gb,
                memory_percent=memory_percent,
                disk_total_gb=disk_total_gb,
                disk_used_gb=disk_used_gb,
                disk_percent=disk_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                thread_count=thread_count,
                handle_count=handle_count,
                gpu_percent=gpu_percent,
                gpu_memory_percent=gpu_memory_percent
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            # Return minimal metrics
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                cpu_count=1,
                memory_total_gb=1.0,
                memory_used_gb=0.0,
                memory_percent=0.0,
                disk_total_gb=1.0,
                disk_used_gb=0.0,
                disk_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                process_count=0,
                thread_count=0,
                handle_count=0,
                gpu_percent=0.0,
                gpu_memory_percent=0.0
            )
    
    def _get_network_metrics(self) -> Tuple[float, float]:
        """Get network transfer rates in MB/s"""
        try:
            net_io = psutil.net_io_counters()
            if not net_io or not self.network_stats_baseline:
                return 0.0, 0.0
            
            current_time = time.time()
            time_diff = current_time - self.network_stats_baseline['timestamp']
            
            if time_diff <= 0:
                return 0.0, 0.0
            
            sent_diff = net_io.bytes_sent - self.network_stats_baseline['bytes_sent']
            recv_diff = net_io.bytes_recv - self.network_stats_baseline['bytes_recv']
            
            sent_mb_per_sec = (sent_diff / time_diff) / (1024**2)
            recv_mb_per_sec = (recv_diff / time_diff) / (1024**2)
            
            # Update baseline
            self.network_stats_baseline = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'timestamp': current_time
            }
            
            return sent_mb_per_sec, recv_mb_per_sec
            
        except Exception as e:
            logger.warning(f"Failed to collect network metrics: {e}")
            return 0.0, 0.0
    
    def _get_gpu_metrics(self) -> Tuple[float, float]:
        """Get GPU utilization metrics"""
        if not self.gpu_available:
            return 0.0, 0.0
        
        try:
            # Try GPUtil first
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    return gpu.load * 100, gpu.memoryUtil * 100
            except ImportError:
                pass
            
            # Try pynvml
            try:
                import pynvml
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # Get utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_percent = util.gpu
                
                # Get memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_percent = (mem_info.used / mem_info.total) * 100
                
                return float(gpu_percent), float(gpu_memory_percent)
            except (ImportError, Exception):
                pass
            
            return 0.0, 0.0
            
        except Exception as e:
            logger.warning(f"Failed to collect GPU metrics: {e}")
            return 0.0, 0.0
    
    def get_collector_info(self) -> Dict[str, Any]:
        """Get collector information"""
        return {
            "collector_type": "SystemResourceCollector",
            "gpu_available": self.gpu_available,
            "boot_time": datetime.fromtimestamp(self.boot_time).isoformat(),
            "network_monitoring": self.network_stats_baseline is not None
        }


class ProcessResourceCollector(ResourceCollector):
    """Process-specific resource metrics collector"""
    
    def __init__(self, pid: Optional[int] = None):
        self.pid = pid or os.getpid()
        try:
            self.process = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            logger.error(f"Process {self.pid} not found")
            self.process = None
    
    def collect_metrics(self) -> ResourceMetrics:
        """Collect process-specific metrics"""
        if not self.process:
            return self._empty_metrics()
        
        try:
            # CPU metrics
            cpu_percent = self.process.cpu_percent()
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory_info = self.process.memory_info()
            system_memory = psutil.virtual_memory()
            
            memory_used_gb = memory_info.rss / (1024**3)
            memory_total_gb = system_memory.total / (1024**3)
            memory_percent = (memory_info.rss / system_memory.total) * 100
            
            # Process-specific metrics
            process_count = 1  # This process
            thread_count = self.process.num_threads()
            handle_count = 0
            
            try:
                if hasattr(self.process, 'num_handles'):
                    handle_count = self.process.num_handles()
            except Exception:
                pass
            
            # Network and disk are system-wide, not process-specific
            return ResourceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_count=cpu_count,
                memory_total_gb=memory_total_gb,
                memory_used_gb=memory_used_gb,
                memory_percent=memory_percent,
                disk_total_gb=0.0,  # Not applicable for process
                disk_used_gb=0.0,
                disk_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0,
                process_count=process_count,
                thread_count=thread_count,
                handle_count=handle_count,
                gpu_percent=0.0,
                gpu_memory_percent=0.0
            )
            
        except Exception as e:
            logger.error(f"Failed to collect process metrics: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> ResourceMetrics:
        """Return empty metrics when collection fails"""
        return ResourceMetrics(
            timestamp=datetime.now(),
            cpu_percent=0.0,
            cpu_count=1,
            memory_total_gb=1.0,
            memory_used_gb=0.0,
            memory_percent=0.0,
            disk_total_gb=0.0,
            disk_used_gb=0.0,
            disk_percent=0.0,
            network_sent_mb=0.0,
            network_recv_mb=0.0,
            process_count=0,
            thread_count=0,
            handle_count=0,
            gpu_percent=0.0,
            gpu_memory_percent=0.0
        )
    
    def get_collector_info(self) -> Dict[str, Any]:
        """Get collector information"""
        info = {
            "collector_type": "ProcessResourceCollector", 
            "pid": self.pid,
            "process_exists": self.process is not None
        }
        
        if self.process:
            try:
                info.update({
                    "process_name": self.process.name(),
                    "process_status": self.process.status(),
                    "process_create_time": datetime.fromtimestamp(self.process.create_time()).isoformat()
                })
            except Exception as e:
                info["process_info_error"] = str(e)
        
        return info


class ResourceAnalyzer:
    """Analyzes resource metrics and predicts bottlenecks"""
    
    def __init__(self, 
                 history_size: int = 1000,
                 prediction_window: int = 60):
        self.history_size = history_size
        self.prediction_window = prediction_window
        self.metrics_history = deque(maxlen=history_size)
        self.trend_analysis_cache = {}
        self.last_analysis_time = 0.0
        
    def add_metrics(self, metrics: ResourceMetrics) -> None:
        """Add metrics to history for analysis"""
        self.metrics_history.append(metrics)
        
        # Clear cache periodically
        current_time = time.time()
        if current_time - self.last_analysis_time > 300:  # 5 minutes
            self.trend_analysis_cache.clear()
            self.last_analysis_time = current_time
    
    def analyze_trends(self, resource_type: ResourceType, 
                      window_minutes: int = 10) -> Dict[str, Any]:
        """Analyze trends for specific resource type"""
        
        cache_key = f"{resource_type.value}_{window_minutes}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.trend_analysis_cache:
            cached_result, cache_time = self.trend_analysis_cache[cache_key]
            if current_time - cache_time < 60:  # Cache for 1 minute
                return cached_result
        
        if len(self.metrics_history) < 2:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        try:
            # Filter metrics within time window
            cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            if len(recent_metrics) < 2:
                return {"trend": "insufficient_data", "confidence": 0.0}
            
            # Extract values based on resource type
            values = []
            timestamps = []
            
            for metrics in recent_metrics:
                timestamps.append(metrics.timestamp.timestamp())
                
                if resource_type == ResourceType.CPU:
                    values.append(metrics.cpu_percent)
                elif resource_type == ResourceType.MEMORY:
                    values.append(metrics.memory_percent)
                elif resource_type == ResourceType.DISK:
                    values.append(metrics.disk_percent)
                elif resource_type == ResourceType.NETWORK:
                    values.append(metrics.network_sent_mb + metrics.network_recv_mb)
                elif resource_type == ResourceType.GPU:
                    values.append(metrics.gpu_percent)
                else:
                    values.append(0.0)
            
            # Calculate trend
            if len(values) < 2:
                return {"trend": "insufficient_data", "confidence": 0.0}
            
            # Linear regression for trend
            x = np.array(timestamps)
            y = np.array(values)
            
            # Normalize x to avoid numerical issues
            x_norm = (x - x[0]) / (x[-1] - x[0] + 1e-10)
            
            slope, intercept = np.polyfit(x_norm, y, 1)
            
            # Calculate R-squared for confidence
            y_pred = slope * x_norm + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / (ss_tot + 1e-10))
            
            # Classify trend
            if abs(slope) < 0.1:
                trend = "stable"
            elif slope > 0.1:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Predict future value
            future_time_norm = 1 + (self.prediction_window / (x[-1] - x[0] + 1e-10))
            predicted_value = slope * future_time_norm + intercept
            
            result = {
                "trend": trend,
                "slope": float(slope),
                "confidence": float(max(0.0, min(1.0, r_squared))),
                "current_value": float(values[-1]),
                "predicted_value": float(predicted_value),
                "prediction_window_seconds": self.prediction_window,
                "sample_count": len(values),
                "time_range_minutes": window_minutes,
                "variance": float(np.var(values)),
                "mean": float(np.mean(values)),
                "std_dev": float(np.std(values))
            }
            
            # Cache result
            self.trend_analysis_cache[cache_key] = (result, current_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze trends for {resource_type.value}: {e}")
            return {
                "trend": "analysis_error",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def predict_bottlenecks(self, thresholds: ResourceThresholds) -> List[Dict[str, Any]]:
        """Predict potential resource bottlenecks"""
        bottlenecks = []
        
        resource_types = [
            ResourceType.CPU,
            ResourceType.MEMORY, 
            ResourceType.DISK,
            ResourceType.NETWORK,
            ResourceType.GPU
        ]
        
        for resource_type in resource_types:
            try:
                trend_analysis = self.analyze_trends(resource_type, window_minutes=15)
                
                if trend_analysis["confidence"] < 0.3:
                    continue  # Skip low-confidence predictions
                
                predicted_value = trend_analysis.get("predicted_value", 0.0)
                current_value = trend_analysis.get("current_value", 0.0)
                
                # Determine threshold based on resource type
                warning_threshold = 70.0
                critical_threshold = 85.0
                
                if resource_type == ResourceType.CPU:
                    warning_threshold = thresholds.cpu_warning
                    critical_threshold = thresholds.cpu_critical
                elif resource_type == ResourceType.MEMORY:
                    warning_threshold = thresholds.memory_warning
                    critical_threshold = thresholds.memory_critical
                elif resource_type == ResourceType.DISK:
                    warning_threshold = thresholds.disk_warning
                    critical_threshold = thresholds.disk_critical
                elif resource_type == ResourceType.GPU:
                    warning_threshold = thresholds.gpu_warning
                    critical_threshold = thresholds.gpu_critical
                
                # Check for potential bottleneck
                severity = "none"
                time_to_threshold = None
                
                if predicted_value > critical_threshold:
                    severity = "critical"
                elif predicted_value > warning_threshold:
                    severity = "warning"
                
                # Calculate time to threshold if trending upward
                if (trend_analysis["trend"] == "increasing" and 
                    trend_analysis["slope"] > 0 and
                    current_value < warning_threshold):
                    
                    time_to_warning = (warning_threshold - current_value) / trend_analysis["slope"]
                    time_to_threshold = max(0, time_to_warning)
                
                if severity != "none" or time_to_threshold is not None:
                    bottleneck = {
                        "resource_type": resource_type.value,
                        "severity": severity,
                        "current_value": current_value,
                        "predicted_value": predicted_value,
                        "confidence": trend_analysis["confidence"],
                        "trend": trend_analysis["trend"],
                        "time_to_threshold_seconds": time_to_threshold,
                        "prediction_window_seconds": self.prediction_window,
                        "warning_threshold": warning_threshold,
                        "critical_threshold": critical_threshold
                    }
                    
                    bottlenecks.append(bottleneck)
                    
            except Exception as e:
                logger.error(f"Failed to predict bottleneck for {resource_type.value}: {e}")
        
        # Sort by severity and confidence
        bottlenecks.sort(key=lambda x: (
            {"critical": 3, "warning": 2, "none": 1}.get(x["severity"], 0),
            x["confidence"]
        ), reverse=True)
        
        return bottlenecks
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get comprehensive resource analysis summary"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate averages over different time windows
        windows = [5, 15, 60]  # minutes
        summaries = {}
        
        for window_min in windows:
            cutoff_time = datetime.now() - timedelta(minutes=window_min)
            window_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            if window_metrics:
                summaries[f"{window_min}min"] = {
                    "avg_cpu": statistics.mean(m.cpu_percent for m in window_metrics),
                    "avg_memory": statistics.mean(m.memory_percent for m in window_metrics),
                    "avg_disk": statistics.mean(m.disk_percent for m in window_metrics),
                    "max_cpu": max(m.cpu_percent for m in window_metrics),
                    "max_memory": max(m.memory_percent for m in window_metrics),
                    "sample_count": len(window_metrics)
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": asdict(latest_metrics),
            "window_summaries": summaries,
            "total_samples": len(self.metrics_history),
            "history_span_hours": (
                (self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds() / 3600
                if len(self.metrics_history) > 1 else 0
            )
        }


class AutoScaler:
    """Automatic scaling decisions based on resource analysis"""
    
    def __init__(self, 
                 thresholds: Optional[ResourceThresholds] = None,
                 scaling_cooldown: float = 300.0):  # 5 minutes
        
        self.thresholds = thresholds or ResourceThresholds()
        self.scaling_cooldown = scaling_cooldown
        self.last_scaling_decisions = {}
        self.scaling_history = deque(maxlen=100)
        
    def make_scaling_decision(self, 
                            current_metrics: ResourceMetrics,
                            trend_analysis: Dict[str, Dict[str, Any]],
                            bottleneck_predictions: List[Dict[str, Any]]) -> List[ScalingDecision]:
        """Make automatic scaling decisions"""
        
        decisions = []
        current_time = datetime.now()
        
        # Check cooldown for each resource type
        for resource_type in ResourceType:
            last_decision_time = self.last_scaling_decisions.get(resource_type.value, datetime.min)
            if (current_time - last_decision_time).total_seconds() < self.scaling_cooldown:
                continue  # Still in cooldown
            
            decision = self._evaluate_resource_scaling(
                resource_type, current_metrics, trend_analysis, bottleneck_predictions
            )
            
            if decision and decision.action != ScalingAction.MAINTAIN:
                decisions.append(decision)
                self.last_scaling_decisions[resource_type.value] = current_time
                self.scaling_history.append(decision)
        
        return decisions
    
    def _evaluate_resource_scaling(self, 
                                 resource_type: ResourceType,
                                 metrics: ResourceMetrics,
                                 trends: Dict[str, Dict[str, Any]],
                                 bottlenecks: List[Dict[str, Any]]) -> Optional[ScalingDecision]:
        """Evaluate scaling needs for specific resource"""
        
        try:
            # Get current value and thresholds
            current_value, warning_threshold, critical_threshold, emergency_threshold = self._get_resource_values(
                resource_type, metrics
            )
            
            # Get trend analysis
            trend_data = trends.get(resource_type.value, {})
            trend = trend_data.get("trend", "stable")
            predicted_value = trend_data.get("predicted_value", current_value)
            confidence = trend_data.get("confidence", 0.0)
            
            # Find relevant bottleneck predictions
            resource_bottlenecks = [
                b for b in bottlenecks 
                if b["resource_type"] == resource_type.value
            ]
            
            # Determine scaling action
            action = ScalingAction.MAINTAIN
            reasoning = "Resource usage within normal range"
            target_value = current_value
            
            # Emergency scaling
            if current_value >= emergency_threshold:
                action = ScalingAction.EMERGENCY_CLEANUP
                reasoning = f"Emergency: {resource_type.value} usage at {current_value:.1f}% (threshold: {emergency_threshold:.1f}%)"
                target_value = warning_threshold
            
            # Critical scaling up
            elif current_value >= critical_threshold or predicted_value >= critical_threshold:
                action = ScalingAction.SCALE_UP
                reasoning = f"Critical: {resource_type.value} usage at {current_value:.1f}% (predicted: {predicted_value:.1f}%)"
                target_value = warning_threshold
            
            # Warning level scaling
            elif current_value >= warning_threshold and trend == "increasing":
                action = ScalingAction.SCALE_UP
                reasoning = f"Warning: {resource_type.value} trending up, current: {current_value:.1f}%"
                target_value = warning_threshold * 0.8  # Target 80% of warning threshold
            
            # Predictive scaling based on bottleneck analysis
            elif resource_bottlenecks and confidence > 0.5:
                bottleneck = resource_bottlenecks[0]  # Highest priority
                time_to_threshold = bottleneck.get("time_to_threshold_seconds")
                
                if time_to_threshold and time_to_threshold < 300:  # Less than 5 minutes
                    action = ScalingAction.SCALE_UP
                    reasoning = f"Predictive: {resource_type.value} will reach threshold in {time_to_threshold:.0f}s"
                    target_value = warning_threshold * 0.8
            
            # Scale down opportunity
            elif (current_value < warning_threshold * 0.6 and 
                  trend in ["stable", "decreasing"] and
                  confidence > 0.3):
                action = ScalingAction.SCALE_DOWN
                reasoning = f"Optimization: {resource_type.value} consistently low at {current_value:.1f}%"
                target_value = warning_threshold * 0.7
            
            # Optimization opportunities
            elif trend == "stable" and current_value < warning_threshold * 0.8:
                action = ScalingAction.OPTIMIZE
                reasoning = f"Stable usage, optimization opportunity for {resource_type.value}"
                target_value = current_value
            
            # Create decision if action needed
            if action != ScalingAction.MAINTAIN:
                decision_id = f"{resource_type.value}_{int(time.time())}"
                
                # Estimate impact
                impact = self._estimate_scaling_impact(action, resource_type, current_value, target_value)
                
                return ScalingDecision(
                    decision_id=decision_id,
                    action=action,
                    target_resource=resource_type,
                    current_value=current_value,
                    target_value=target_value,
                    confidence=confidence,
                    reasoning=reasoning,
                    estimated_impact=impact,
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to evaluate scaling for {resource_type.value}: {e}")
            return None
    
    def _get_resource_values(self, resource_type: ResourceType, 
                           metrics: ResourceMetrics) -> Tuple[float, float, float, float]:
        """Get current value and thresholds for resource type"""
        
        if resource_type == ResourceType.CPU:
            return (metrics.cpu_percent, 
                   self.thresholds.cpu_warning,
                   self.thresholds.cpu_critical,
                   self.thresholds.cpu_emergency)
        
        elif resource_type == ResourceType.MEMORY:
            return (metrics.memory_percent,
                   self.thresholds.memory_warning,
                   self.thresholds.memory_critical,
                   self.thresholds.memory_emergency)
        
        elif resource_type == ResourceType.DISK:
            return (metrics.disk_percent,
                   self.thresholds.disk_warning,
                   self.thresholds.disk_critical,
                   self.thresholds.disk_emergency)
        
        elif resource_type == ResourceType.NETWORK:
            network_usage = metrics.network_sent_mb + metrics.network_recv_mb
            return (network_usage,
                   self.thresholds.network_warning_mbps,
                   self.thresholds.network_critical_mbps,
                   self.thresholds.network_critical_mbps)
        
        elif resource_type == ResourceType.GPU:
            return (metrics.gpu_percent,
                   self.thresholds.gpu_warning,
                   self.thresholds.gpu_critical,
                   100.0)
        
        else:
            return (0.0, 100.0, 100.0, 100.0)
    
    def _estimate_scaling_impact(self, action: ScalingAction, 
                               resource_type: ResourceType,
                               current_value: float, 
                               target_value: float) -> Dict[str, Any]:
        """Estimate impact of scaling decision"""
        
        impact = {
            "resource_reduction_percent": 0.0,
            "estimated_time_to_effect": 0.0,
            "confidence": 0.5,
            "side_effects": [],
            "cost_impact": "neutral"
        }
        
        try:
            if action == ScalingAction.SCALE_UP:
                # Scaling up reduces resource pressure
                impact["resource_reduction_percent"] = max(0, current_value - target_value)
                impact["estimated_time_to_effect"] = 30.0  # 30 seconds
                impact["confidence"] = 0.8
                impact["cost_impact"] = "increase"
                
                if resource_type == ResourceType.CPU:
                    impact["side_effects"].append("Increased power consumption")
                elif resource_type == ResourceType.MEMORY:
                    impact["side_effects"].append("Increased memory allocation")
            
            elif action == ScalingAction.SCALE_DOWN:
                # Scaling down saves resources
                impact["resource_reduction_percent"] = max(0, target_value - current_value)
                impact["estimated_time_to_effect"] = 60.0  # 1 minute
                impact["confidence"] = 0.6
                impact["cost_impact"] = "decrease"
                impact["side_effects"].append("Potential performance reduction")
            
            elif action == ScalingAction.EMERGENCY_CLEANUP:
                # Emergency cleanup has immediate but uncertain impact
                impact["resource_reduction_percent"] = max(0, current_value - target_value)
                impact["estimated_time_to_effect"] = 5.0  # 5 seconds
                impact["confidence"] = 0.9
                impact["cost_impact"] = "neutral"
                impact["side_effects"].extend([
                    "Potential data loss",
                    "Service interruption",
                    "Cache clearing"
                ])
            
            elif action == ScalingAction.OPTIMIZE:
                # Optimization has gradual improvement
                impact["resource_reduction_percent"] = 5.0  # Conservative estimate
                impact["estimated_time_to_effect"] = 120.0  # 2 minutes
                impact["confidence"] = 0.4
                impact["cost_impact"] = "neutral"
                impact["side_effects"].append("Temporary performance variation")
            
        except Exception as e:
            logger.error(f"Failed to estimate scaling impact: {e}")
            impact["error"] = str(e)
        
        return impact
    
    def get_scaling_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent scaling decisions"""
        history = list(self.scaling_history)[-limit:]
        return [asdict(decision) for decision in history]


class ResourceMonitor:
    """Main resource monitoring and scaling coordinator"""
    
    def __init__(self,
                 collectors: Optional[List[ResourceCollector]] = None,
                 thresholds: Optional[ResourceThresholds] = None,
                 monitoring_interval: float = 30.0,
                 enable_auto_scaling: bool = False,
                 data_retention_hours: int = 24):
        
        # Initialize collectors
        self.collectors = collectors or [SystemResourceCollector()]
        self.thresholds = thresholds or ResourceThresholds()
        self.monitoring_interval = monitoring_interval
        self.enable_auto_scaling = enable_auto_scaling
        self.data_retention_hours = data_retention_hours
        
        # Initialize components
        self.analyzer = ResourceAnalyzer(
            history_size=int((data_retention_hours * 3600) / monitoring_interval),
            prediction_window=int(monitoring_interval * 2)
        )
        
        self.auto_scaler = AutoScaler(thresholds=self.thresholds) if enable_auto_scaling else None
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.alert_handlers = []
        self.scaling_handlers = []
        
        # Statistics
        self.monitoring_stats = {
            'total_collections': 0,
            'alerts_generated': 0,
            'scaling_decisions': 0,
            'start_time': datetime.now(),
            'errors': 0
        }
        
        logger.info(f"ResourceMonitor initialized with {len(self.collectors)} collectors")
    
    def add_alert_handler(self, handler: Callable[[ResourceAlert], None]):
        """Add handler for resource alerts"""
        self.alert_handlers.append(handler)
    
    def add_scaling_handler(self, handler: Callable[[List[ScalingDecision]], None]):
        """Add handler for scaling decisions"""
        self.scaling_handlers.append(handler)
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="ResourceMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10.0)
        
        logger.info("Resource monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                cycle_start = time.time()
                
                # Collect metrics from all collectors
                all_metrics = []
                for collector in self.collectors:
                    try:
                        metrics = collector.collect_metrics()
                        all_metrics.append(metrics)
                        self.analyzer.add_metrics(metrics)
                    except Exception as e:
                        logger.error(f"Failed to collect metrics from {type(collector).__name__}: {e}")
                        self.monitoring_stats['errors'] += 1
                
                if all_metrics:
                    # Use the first (primary) metrics for analysis
                    primary_metrics = all_metrics[0]
                    
                    # Generate alerts
                    alerts = self._check_for_alerts(primary_metrics)
                    for alert in alerts:
                        self._handle_alert(alert)
                    
                    # Make scaling decisions if enabled
                    if self.enable_auto_scaling and self.auto_scaler:
                        scaling_decisions = self._make_scaling_decisions(primary_metrics)
                        if scaling_decisions:
                            self._handle_scaling_decisions(scaling_decisions)
                
                self.monitoring_stats['total_collections'] += 1
                
                # Sleep for remaining interval time
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.monitoring_interval - cycle_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.monitoring_stats['errors'] += 1
                time.sleep(min(self.monitoring_interval, 60.0))  # Wait at least 1 minute on error
    
    def _check_for_alerts(self, metrics: ResourceMetrics) -> List[ResourceAlert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        try:
            # CPU alerts
            if metrics.cpu_percent >= self.thresholds.cpu_emergency:
                alerts.append(self._create_alert(
                    ResourceType.CPU, AlertLevel.EMERGENCY,
                    f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                    metrics.cpu_percent, self.thresholds.cpu_emergency,
                    ["Immediate CPU scaling required", "Check for runaway processes"]
                ))
            elif metrics.cpu_percent >= self.thresholds.cpu_critical:
                alerts.append(self._create_alert(
                    ResourceType.CPU, AlertLevel.CRITICAL,
                    f"CPU usage high: {metrics.cpu_percent:.1f}%",
                    metrics.cpu_percent, self.thresholds.cpu_critical,
                    ["Scale up CPU resources", "Investigate high CPU processes"]
                ))
            elif metrics.cpu_percent >= self.thresholds.cpu_warning:
                alerts.append(self._create_alert(
                    ResourceType.CPU, AlertLevel.WARNING,
                    f"CPU usage elevated: {metrics.cpu_percent:.1f}%",
                    metrics.cpu_percent, self.thresholds.cpu_warning,
                    ["Monitor CPU trends", "Consider scaling if trend continues"]
                ))
            
            # Memory alerts
            if metrics.memory_percent >= self.thresholds.memory_emergency:
                alerts.append(self._create_alert(
                    ResourceType.MEMORY, AlertLevel.EMERGENCY,
                    f"Memory usage critical: {metrics.memory_percent:.1f}%",
                    metrics.memory_percent, self.thresholds.memory_emergency,
                    ["Emergency memory cleanup", "Force garbage collection", "Kill non-essential processes"]
                ))
            elif metrics.memory_percent >= self.thresholds.memory_critical:
                alerts.append(self._create_alert(
                    ResourceType.MEMORY, AlertLevel.CRITICAL,
                    f"Memory usage high: {metrics.memory_percent:.1f}%",
                    metrics.memory_percent, self.thresholds.memory_critical,
                    ["Scale up memory", "Clear caches", "Optimize memory usage"]
                ))
            elif metrics.memory_percent >= self.thresholds.memory_warning:
                alerts.append(self._create_alert(
                    ResourceType.MEMORY, AlertLevel.WARNING,
                    f"Memory usage elevated: {metrics.memory_percent:.1f}%",
                    metrics.memory_percent, self.thresholds.memory_warning,
                    ["Monitor memory trends", "Review memory allocation"]
                ))
            
            # Disk alerts
            if metrics.disk_percent >= self.thresholds.disk_emergency:
                alerts.append(self._create_alert(
                    ResourceType.DISK, AlertLevel.EMERGENCY,
                    f"Disk usage critical: {metrics.disk_percent:.1f}%",
                    metrics.disk_percent, self.thresholds.disk_emergency,
                    ["Emergency disk cleanup", "Delete temporary files", "Archive old data"]
                ))
            elif metrics.disk_percent >= self.thresholds.disk_critical:
                alerts.append(self._create_alert(
                    ResourceType.DISK, AlertLevel.CRITICAL,
                    f"Disk usage high: {metrics.disk_percent:.1f}%", 
                    metrics.disk_percent, self.thresholds.disk_critical,
                    ["Add more disk space", "Clean up unnecessary files"]
                ))
            elif metrics.disk_percent >= self.thresholds.disk_warning:
                alerts.append(self._create_alert(
                    ResourceType.DISK, AlertLevel.WARNING,
                    f"Disk usage elevated: {metrics.disk_percent:.1f}%",
                    metrics.disk_percent, self.thresholds.disk_warning,
                    ["Monitor disk usage", "Plan disk expansion"]
                ))
            
            # GPU alerts (if available)
            if metrics.gpu_percent > 0:
                if metrics.gpu_percent >= self.thresholds.gpu_critical:
                    alerts.append(self._create_alert(
                        ResourceType.GPU, AlertLevel.CRITICAL,
                        f"GPU usage high: {metrics.gpu_percent:.1f}%",
                        metrics.gpu_percent, self.thresholds.gpu_critical,
                        ["Check GPU workload", "Consider GPU scaling"]
                    ))
                elif metrics.gpu_percent >= self.thresholds.gpu_warning:
                    alerts.append(self._create_alert(
                        ResourceType.GPU, AlertLevel.WARNING,
                        f"GPU usage elevated: {metrics.gpu_percent:.1f}%",
                        metrics.gpu_percent, self.thresholds.gpu_warning,
                        ["Monitor GPU usage", "Review GPU intensive tasks"]
                    ))
        
        except Exception as e:
            logger.error(f"Error checking for alerts: {e}")
        
        return alerts
    
    def _create_alert(self, resource_type: ResourceType, level: AlertLevel,
                     message: str, current_value: float, threshold: float,
                     actions: List[str]) -> ResourceAlert:
        """Create resource alert"""
        alert_id = f"{resource_type.value}_{level.value}_{int(time.time())}"
        
        return ResourceAlert(
            alert_id=alert_id,
            resource_type=resource_type,
            alert_level=level,
            message=message,
            current_value=current_value,
            threshold=threshold,
            timestamp=datetime.now(),
            suggested_actions=actions
        )
    
    def _handle_alert(self, alert: ResourceAlert):
        """Handle generated alert"""
        self.monitoring_stats['alerts_generated'] += 1
        
        # Log alert
        log_level = {
            AlertLevel.NORMAL: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.CRITICAL: logging.ERROR,
            AlertLevel.EMERGENCY: logging.CRITICAL
        }.get(alert.alert_level, logging.INFO)
        
        logger.log(log_level, f"Resource Alert: {alert.message}")
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def _make_scaling_decisions(self, metrics: ResourceMetrics) -> List[ScalingDecision]:
        """Make scaling decisions based on current metrics"""
        try:
            # Get trend analysis for all resource types
            trend_analysis = {}
            for resource_type in ResourceType:
                trend_analysis[resource_type.value] = self.analyzer.analyze_trends(resource_type)
            
            # Get bottleneck predictions
            bottleneck_predictions = self.analyzer.predict_bottlenecks(self.thresholds)
            
            # Make scaling decisions
            decisions = self.auto_scaler.make_scaling_decision(
                metrics, trend_analysis, bottleneck_predictions
            )
            
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to make scaling decisions: {e}")
            return []
    
    def _handle_scaling_decisions(self, decisions: List[ScalingDecision]):
        """Handle scaling decisions"""
        self.monitoring_stats['scaling_decisions'] += len(decisions)
        
        for decision in decisions:
            logger.info(f"Scaling Decision: {decision.action.value} for {decision.target_resource.value} - {decision.reasoning}")
        
        # Call scaling handlers
        for handler in self.scaling_handlers:
            try:
                handler(decisions)
            except Exception as e:
                logger.error(f"Scaling handler failed: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        try:
            # Get latest metrics from primary collector
            current_metrics = None
            if self.collectors:
                current_metrics = self.collectors[0].collect_metrics()
            
            # Get analysis summary
            analysis_summary = self.analyzer.get_resource_summary()
            
            # Get recent scaling decisions
            scaling_history = []
            if self.auto_scaler:
                scaling_history = self.auto_scaler.get_scaling_history(limit=10)
            
            return {
                "monitoring_active": self.monitoring_active,
                "current_metrics": asdict(current_metrics) if current_metrics else None,
                "analysis_summary": analysis_summary,
                "scaling_history": scaling_history,
                "monitoring_stats": self.monitoring_stats,
                "configuration": {
                    "monitoring_interval": self.monitoring_interval,
                    "auto_scaling_enabled": self.enable_auto_scaling,
                    "data_retention_hours": self.data_retention_hours,
                    "collector_count": len(self.collectors),
                    "thresholds": asdict(self.thresholds)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get monitoring status: {e}")
            return {"error": str(e)}
    
    def export_monitoring_data(self, export_path: str, 
                             include_raw_metrics: bool = False) -> bool:
        """Export monitoring data for analysis"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "monitoring_stats": self.monitoring_stats,
                "configuration": {
                    "monitoring_interval": self.monitoring_interval,
                    "auto_scaling_enabled": self.enable_auto_scaling,
                    "data_retention_hours": self.data_retention_hours,
                    "thresholds": asdict(self.thresholds)
                },
                "collector_info": [collector.get_collector_info() for collector in self.collectors]
            }
            
            # Include analysis summary
            export_data["analysis_summary"] = self.analyzer.get_resource_summary()
            
            # Include scaling history if available
            if self.auto_scaler:
                export_data["scaling_history"] = self.auto_scaler.get_scaling_history()
            
            # Include raw metrics if requested
            if include_raw_metrics:
                export_data["raw_metrics"] = [
                    asdict(metrics) for metrics in list(self.analyzer.metrics_history)
                ]
            
            # Write to file
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported monitoring data to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export monitoring data: {e}")
            return False


# Factory functions for common configurations
def create_system_monitor(enable_auto_scaling: bool = False,
                         monitoring_interval: float = 30.0) -> ResourceMonitor:
    """Create system-wide resource monitor"""
    
    return ResourceMonitor(
        collectors=[SystemResourceCollector()],
        thresholds=ResourceThresholds(),
        monitoring_interval=monitoring_interval,
        enable_auto_scaling=enable_auto_scaling,
        data_retention_hours=24
    )


def create_process_monitor(pid: Optional[int] = None,
                         enable_auto_scaling: bool = False) -> ResourceMonitor:
    """Create process-specific resource monitor"""
    
    return ResourceMonitor(
        collectors=[ProcessResourceCollector(pid)],
        thresholds=ResourceThresholds(),
        monitoring_interval=10.0,  # More frequent for process monitoring
        enable_auto_scaling=enable_auto_scaling,
        data_retention_hours=12
    )


def create_hybrid_monitor(enable_auto_scaling: bool = True) -> ResourceMonitor:
    """Create hybrid system and process monitor"""
    
    return ResourceMonitor(
        collectors=[
            SystemResourceCollector(),
            ProcessResourceCollector()  # Current process
        ],
        thresholds=ResourceThresholds(),
        monitoring_interval=30.0,
        enable_auto_scaling=enable_auto_scaling,
        data_retention_hours=24
    )


# Example usage and testing
if __name__ == "__main__":
    def example_alert_handler(alert: ResourceAlert):
        """Example alert handler"""
        print(f"ALERT: {alert.alert_level.value.upper()} - {alert.message}")
        if alert.suggested_actions:
            print(f"  Suggested actions: {', '.join(alert.suggested_actions)}")
    
    def example_scaling_handler(decisions: List[ScalingDecision]):
        """Example scaling decision handler"""
        for decision in decisions:
            print(f"SCALING: {decision.action.value} for {decision.target_resource.value}")
            print(f"  Reasoning: {decision.reasoning}")
            print(f"  Confidence: {decision.confidence:.2f}")
    
    def test_resource_monitoring():
        # Create resource monitor
        monitor = create_hybrid_monitor(enable_auto_scaling=True)
        
        # Add handlers
        monitor.add_alert_handler(example_alert_handler)
        monitor.add_scaling_handler(example_scaling_handler)
        
        # Start monitoring
        print("Starting resource monitoring...")
        monitor.start_monitoring()
        
        # Let it run for a bit
        import time
        time.sleep(120)  # Monitor for 2 minutes
        
        # Get status
        status = monitor.get_current_status()
        print("\nMonitoring Status:")
        print(f"  Active: {status['monitoring_active']}")
        print(f"  Collections: {status['monitoring_stats']['total_collections']}")
        print(f"  Alerts: {status['monitoring_stats']['alerts_generated']}")
        print(f"  Scaling Decisions: {status['monitoring_stats']['scaling_decisions']}")
        
        if status['current_metrics']:
            metrics = status['current_metrics']
            print(f"\nCurrent Metrics:")
            print(f"  CPU: {metrics['cpu_percent']:.1f}%")
            print(f"  Memory: {metrics['memory_percent']:.1f}%")
            print(f"  Disk: {metrics['disk_percent']:.1f}%")
        
        # Export data
        monitor.export_monitoring_data("monitoring_export.json", include_raw_metrics=True)
        print("\nMonitoring data exported to monitoring_export.json")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("Monitoring stopped.")
    
    test_resource_monitoring()