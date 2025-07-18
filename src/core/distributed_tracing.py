"""
Distributed Tracing with OpenTelemetry

Implements comprehensive distributed tracing for KGAS using OpenTelemetry.
Provides request tracing, span creation, and observability across all components.

Features:
- Automatic span creation for all operations
- Distributed trace propagation
- Custom attributes and events
- Integration with Jaeger/Zipkin
- Performance monitoring
- Error tracking
"""

import time
import functools
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable
from contextlib import contextmanager, asynccontextmanager
from dataclasses import dataclass
import logging
import os

# OpenTelemetry imports with fallback
try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.zipkin.json import ZipkinExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.propagate import inject, extract
    from opentelemetry.baggage.propagation import W3CBaggagePropagator
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.util.http import get_excluded_urls
    
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Mock classes for when OpenTelemetry is not available
    class MockTracer:
        def start_span(self, name, **kwargs):
            return MockSpan()
        
        def start_as_current_span(self, name, **kwargs):
            return MockSpan()
    
    class MockSpan:
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            pass
        
        def set_attribute(self, key, value):
            pass
        
        def set_status(self, status, description=None):
            pass
        
        def record_exception(self, exception):
            pass
        
        def add_event(self, name, attributes=None):
            pass
    
    class MockTracerProvider:
        def get_tracer(self, *args, **kwargs):
            return MockTracer()
    
    # Mock functions
    def inject(carrier, context=None):
        pass
    
    def extract(carrier, context=None):
        return None

from .config import ConfigurationManager
from .logging_config import get_logger


@dataclass
class TracingConfig:
    """Configuration for distributed tracing"""
    enabled: bool = True
    service_name: str = "kgas"
    service_version: str = "1.0.0"
    jaeger_endpoint: Optional[str] = None
    zipkin_endpoint: Optional[str] = None
    sampling_rate: float = 1.0
    console_export: bool = False
    batch_export: bool = True
    max_export_batch_size: int = 512
    export_timeout: int = 30000
    custom_attributes: Dict[str, str] = None


class DistributedTracing:
    """Distributed tracing manager using OpenTelemetry"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.logger = get_logger("tracing.manager")
        
        # Load configuration
        tracing_config = self.config_manager.get_system_config().get("tracing", {})
        self.config = TracingConfig(
            enabled=tracing_config.get("enabled", True),
            service_name=tracing_config.get("service_name", "kgas"),
            service_version=tracing_config.get("service_version", "1.0.0"),
            jaeger_endpoint=tracing_config.get("jaeger_endpoint"),
            zipkin_endpoint=tracing_config.get("zipkin_endpoint"),
            sampling_rate=tracing_config.get("sampling_rate", 1.0),
            console_export=tracing_config.get("console_export", False),
            batch_export=tracing_config.get("batch_export", True),
            max_export_batch_size=tracing_config.get("max_export_batch_size", 512),
            export_timeout=tracing_config.get("export_timeout", 30000),
            custom_attributes=tracing_config.get("custom_attributes", {})
        )
        
        # Initialize tracing
        self.tracer_provider = None
        self.tracer = None
        self.span_processors = []
        
        if self.config.enabled:
            self._initialize_tracing()
        
        self.logger.info("Distributed tracing initialized - enabled: %s, service: %s", 
                        self.config.enabled, self.config.service_name)
    
    def _initialize_tracing(self):
        """Initialize OpenTelemetry tracing"""
        if not OTEL_AVAILABLE:
            self.logger.warning("OpenTelemetry not available, tracing disabled")
            self.config.enabled = False
            return
        
        # Create resource
        resource_attributes = {
            "service.name": self.config.service_name,
            "service.version": self.config.service_version,
        }
        
        if self.config.custom_attributes:
            resource_attributes.update(self.config.custom_attributes)
        
        resource = Resource.create(resource_attributes)
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add exporters
        self._add_exporters()
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(
            __name__,
            version=self.config.service_version
        )
        
        # Instrument libraries
        self._instrument_libraries()
        
        self.logger.info("OpenTelemetry tracing initialized")
    
    def _add_exporters(self):
        """Add configured exporters"""
        if not self.tracer_provider:
            return
        
        # Console exporter (for development)
        if self.config.console_export:
            console_exporter = ConsoleSpanExporter()
            if self.config.batch_export:
                console_processor = BatchSpanProcessor(console_exporter)
            else:
                from opentelemetry.sdk.trace.export import SimpleSpanProcessor
                console_processor = SimpleSpanProcessor(console_exporter)
            
            self.tracer_provider.add_span_processor(console_processor)
            self.span_processors.append(console_processor)
            self.logger.info("Console span exporter added")
        
        # Jaeger exporter
        if self.config.jaeger_endpoint:
            try:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=self.config.jaeger_endpoint.split(':')[0],
                    agent_port=int(self.config.jaeger_endpoint.split(':')[1]),
                )
                
                if self.config.batch_export:
                    jaeger_processor = BatchSpanProcessor(
                        jaeger_exporter,
                        max_export_batch_size=self.config.max_export_batch_size,
                        export_timeout_millis=self.config.export_timeout
                    )
                else:
                    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
                    jaeger_processor = SimpleSpanProcessor(jaeger_exporter)
                
                self.tracer_provider.add_span_processor(jaeger_processor)
                self.span_processors.append(jaeger_processor)
                self.logger.info("Jaeger span exporter added: %s", self.config.jaeger_endpoint)
            except Exception as e:
                self.logger.error("Failed to initialize Jaeger exporter: %s", str(e))
        
        # Zipkin exporter
        if self.config.zipkin_endpoint:
            try:
                zipkin_exporter = ZipkinExporter(
                    endpoint=self.config.zipkin_endpoint
                )
                
                if self.config.batch_export:
                    zipkin_processor = BatchSpanProcessor(
                        zipkin_exporter,
                        max_export_batch_size=self.config.max_export_batch_size,
                        export_timeout_millis=self.config.export_timeout
                    )
                else:
                    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
                    zipkin_processor = SimpleSpanProcessor(zipkin_exporter)
                
                self.tracer_provider.add_span_processor(zipkin_processor)
                self.span_processors.append(zipkin_processor)
                self.logger.info("Zipkin span exporter added: %s", self.config.zipkin_endpoint)
            except Exception as e:
                self.logger.error("Failed to initialize Zipkin exporter: %s", str(e))
    
    def _instrument_libraries(self):
        """Instrument common libraries"""
        try:
            # Instrument asyncio
            AsyncioInstrumentor().instrument()
            
            # Instrument requests
            RequestsInstrumentor().instrument()
            
            self.logger.info("Libraries instrumented successfully")
        except Exception as e:
            self.logger.error("Failed to instrument libraries: %s", str(e))
    
    def get_tracer(self) -> Union[trace.Tracer, MockTracer]:
        """Get the tracer instance"""
        return self.tracer or MockTracer()
    
    @contextmanager
    def trace_operation(self, operation_name: str, 
                       attributes: Optional[Dict[str, Any]] = None,
                       parent_span=None):
        """Context manager for tracing operations"""
        if not self.config.enabled:
            yield MockSpan()
            return
        
        tracer = self.get_tracer()
        
        span_attributes = attributes or {}
        
        with tracer.start_as_current_span(operation_name, attributes=span_attributes) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    @asynccontextmanager
    async def trace_async_operation(self, operation_name: str,
                                   attributes: Optional[Dict[str, Any]] = None):
        """Async context manager for tracing operations"""
        if not self.config.enabled:
            yield MockSpan()
            return
        
        tracer = self.get_tracer()
        
        span_attributes = attributes or {}
        
        with tracer.start_as_current_span(operation_name, attributes=span_attributes) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def trace_function(self, operation_name: Optional[str] = None,
                      attributes: Optional[Dict[str, Any]] = None):
        """Decorator for tracing functions"""
        def decorator(func):
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    async with self.trace_async_operation(span_name, attributes) as span:
                        # Add function arguments as attributes
                        if args:
                            span.set_attribute("args.count", len(args))
                        if kwargs:
                            span.set_attribute("kwargs.count", len(kwargs))
                            for key, value in kwargs.items():
                                if isinstance(value, (str, int, float, bool)):
                                    span.set_attribute(f"kwargs.{key}", value)
                        
                        result = await func(*args, **kwargs)
                        
                        # Add result information
                        if hasattr(result, '__len__'):
                            span.set_attribute("result.length", len(result))
                        
                        return result
                
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.trace_operation(span_name, attributes) as span:
                        # Add function arguments as attributes
                        if args:
                            span.set_attribute("args.count", len(args))
                        if kwargs:
                            span.set_attribute("kwargs.count", len(kwargs))
                            for key, value in kwargs.items():
                                if isinstance(value, (str, int, float, bool)):
                                    span.set_attribute(f"kwargs.{key}", value)
                        
                        result = func(*args, **kwargs)
                        
                        # Add result information
                        if hasattr(result, '__len__'):
                            span.set_attribute("result.length", len(result))
                        
                        return result
                
                return sync_wrapper
        
        return decorator
    
    def trace_document_processing(self, document_id: str, phase: str):
        """Specific tracing for document processing"""
        return self.trace_operation(
            f"document.{phase}.process",
            attributes={
                "document.id": document_id,
                "document.phase": phase,
                "component": "document_processor"
            }
        )
    
    def trace_api_call(self, api_provider: str, endpoint: str, method: str = "GET"):
        """Specific tracing for API calls"""
        return self.trace_operation(
            f"api.{api_provider}.{endpoint}",
            attributes={
                "api.provider": api_provider,
                "api.endpoint": endpoint,
                "api.method": method,
                "component": "api_client"
            }
        )
    
    def trace_database_operation(self, database_type: str, operation: str, collection: str = None):
        """Specific tracing for database operations"""
        attributes = {
            "database.type": database_type,
            "database.operation": operation,
            "component": "database_client"
        }
        
        if collection:
            attributes["database.collection"] = collection
        
        return self.trace_operation(
            f"database.{database_type}.{operation}",
            attributes=attributes
        )
    
    def trace_workflow_execution(self, workflow_type: str, workflow_id: str):
        """Specific tracing for workflow execution"""
        return self.trace_operation(
            f"workflow.{workflow_type}.execute",
            attributes={
                "workflow.type": workflow_type,
                "workflow.id": workflow_id,
                "component": "workflow_engine"
            }
        )
    
    def inject_trace_context(self, carrier: Dict[str, str]):
        """Inject trace context into carrier for distributed tracing"""
        if self.config.enabled and OTEL_AVAILABLE:
            inject(carrier)
    
    def extract_trace_context(self, carrier: Dict[str, str]):
        """Extract trace context from carrier for distributed tracing"""
        if self.config.enabled and OTEL_AVAILABLE:
            return extract(carrier)
        return None
    
    def get_current_trace_id(self) -> Optional[str]:
        """Get current trace ID"""
        if not self.config.enabled or not OTEL_AVAILABLE:
            return None
        
        try:
            current_span = trace.get_current_span()
            if current_span:
                return format(current_span.get_span_context().trace_id, '032x')
        except Exception:
            pass
        
        return None
    
    def get_current_span_id(self) -> Optional[str]:
        """Get current span ID"""
        if not self.config.enabled or not OTEL_AVAILABLE:
            return None
        
        try:
            current_span = trace.get_current_span()
            if current_span:
                return format(current_span.get_span_context().span_id, '016x')
        except Exception:
            pass
        
        return None
    
    def add_span_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the current span"""
        if not self.config.enabled or not OTEL_AVAILABLE:
            return
        
        try:
            current_span = trace.get_current_span()
            if current_span:
                current_span.add_event(name, attributes)
        except Exception as e:
            self.logger.error("Failed to add span event: %s", str(e))
    
    def set_span_attribute(self, key: str, value: Any):
        """Set an attribute on the current span"""
        if not self.config.enabled or not OTEL_AVAILABLE:
            return
        
        try:
            current_span = trace.get_current_span()
            if current_span:
                current_span.set_attribute(key, value)
        except Exception as e:
            self.logger.error("Failed to set span attribute: %s", str(e))
    
    def record_exception(self, exception: Exception):
        """Record an exception in the current span"""
        if not self.config.enabled or not OTEL_AVAILABLE:
            return
        
        try:
            current_span = trace.get_current_span()
            if current_span:
                current_span.record_exception(exception)
        except Exception as e:
            self.logger.error("Failed to record exception: %s", str(e))
    
    def get_tracing_stats(self) -> Dict[str, Any]:
        """Get tracing statistics"""
        return {
            "enabled": self.config.enabled,
            "opentelemetry_available": OTEL_AVAILABLE,
            "service_name": self.config.service_name,
            "service_version": self.config.service_version,
            "jaeger_endpoint": self.config.jaeger_endpoint,
            "zipkin_endpoint": self.config.zipkin_endpoint,
            "sampling_rate": self.config.sampling_rate,
            "console_export": self.config.console_export,
            "batch_export": self.config.batch_export,
            "span_processors": len(self.span_processors),
            "current_trace_id": self.get_current_trace_id(),
            "current_span_id": self.get_current_span_id()
        }
    
    def shutdown(self):
        """Shutdown tracing system"""
        if self.tracer_provider:
            try:
                # Shutdown span processors
                for processor in self.span_processors:
                    processor.shutdown()
                
                self.logger.info("Tracing system shutdown complete")
            except Exception as e:
                self.logger.error("Error during tracing shutdown: %s", str(e))


# Global tracing instance
_distributed_tracing = None


def get_distributed_tracing(config_manager: ConfigurationManager = None) -> DistributedTracing:
    """Get or create the global distributed tracing instance"""
    global _distributed_tracing
    
    if _distributed_tracing is None:
        _distributed_tracing = DistributedTracing(config_manager)
    
    return _distributed_tracing


def initialize_distributed_tracing(config_manager: ConfigurationManager = None) -> DistributedTracing:
    """Initialize the distributed tracing system"""
    return get_distributed_tracing(config_manager)


# Convenience functions for common tracing operations
def trace_operation(operation_name: str, attributes: Optional[Dict[str, Any]] = None):
    """Convenience function for tracing operations"""
    tracing = get_distributed_tracing()
    return tracing.trace_operation(operation_name, attributes)


def trace_function(operation_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Convenience decorator for tracing functions"""
    tracing = get_distributed_tracing()
    return tracing.trace_function(operation_name, attributes)


def get_current_trace_id() -> Optional[str]:
    """Get current trace ID"""
    tracing = get_distributed_tracing()
    return tracing.get_current_trace_id()


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add an event to the current span"""
    tracing = get_distributed_tracing()
    tracing.add_span_event(name, attributes)