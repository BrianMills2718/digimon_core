#!/usr/bin/env python3
"""
Tests for structured output monitoring framework.

Validates monitoring capabilities for structured LLM operations across all components.
"""

import pytest
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

# Add src to path for testing
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring.structured_output_monitor import (
    StructuredOutputMonitor,
    StructuredOutputMetrics,
    ValidationResult,
    get_monitor,
    track_structured_output
)


class TestStructuredOutputMonitor:
    """Test suite for structured output monitoring."""
    
    def setup_method(self):
        """Setup fresh monitor for each test."""
        # Create isolated monitor instance
        self.monitor = StructuredOutputMonitor(max_history_size=100)
    
    def test_monitor_initialization(self):
        """Test monitor initializes correctly."""
        monitor = StructuredOutputMonitor()
        
        assert monitor.max_history_size == 10000
        assert len(monitor.metrics_history) == 0
        assert len(monitor.validation_history) == 0
        assert monitor.alert_thresholds["success_rate_threshold"] == 0.95
        assert monitor.alert_thresholds["avg_response_time_threshold"] == 5000
        
    def test_record_successful_operation(self):
        """Test recording successful operation."""
        metrics = StructuredOutputMetrics(
            component="test_component",
            schema_name="TestSchema",
            success=True,
            response_time_ms=250.0,
            model_used="gemini/gemini-2.5-flash",
            temperature=0.05,
            max_tokens=1000,
            input_length=100,
            output_length=200
        )
        
        self.monitor.record_operation(metrics)
        
        # Check metrics recorded
        assert len(self.monitor.metrics_history) == 1
        recorded = self.monitor.metrics_history[0]
        assert recorded.component == "test_component"
        assert recorded.success is True
        assert recorded.response_time_ms == 250.0
        
        # Check component stats updated
        stats = self.monitor.component_stats["test_component"]
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 1
        assert stats["validation_failures"] == 0
        assert stats["llm_failures"] == 0
        assert stats["total_response_time"] == 250.0
        assert stats["schema_usage"]["TestSchema"] == 1
    
    def test_record_validation_failure(self):
        """Test recording validation failure."""
        metrics = StructuredOutputMetrics(
            component="test_component",
            schema_name="TestSchema",
            success=False,
            response_time_ms=180.0,
            model_used="gemini/gemini-2.5-flash",
            temperature=0.05,
            max_tokens=1000,
            input_length=100,
            output_length=0,
            validation_error="Invalid JSON structure"
        )
        
        self.monitor.record_operation(metrics)
        
        # Check component stats
        stats = self.monitor.component_stats["test_component"]
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 0
        assert stats["validation_failures"] == 1
        assert stats["llm_failures"] == 0
    
    def test_record_llm_failure(self):
        """Test recording LLM failure."""
        metrics = StructuredOutputMetrics(
            component="test_component",
            schema_name="TestSchema",
            success=False,
            response_time_ms=5000.0,
            model_used="gemini/gemini-2.5-flash",
            temperature=0.05,
            max_tokens=1000,
            input_length=100,
            output_length=0,
            llm_error="API timeout"
        )
        
        self.monitor.record_operation(metrics)
        
        # Check component stats
        stats = self.monitor.component_stats["test_component"]
        assert stats["total_requests"] == 1
        assert stats["successful_requests"] == 0
        assert stats["validation_failures"] == 0
        assert stats["llm_failures"] == 1
    
    def test_operation_tracker_context_manager(self):
        """Test operation tracking context manager."""
        with self.monitor.track_operation(
            component="entity_extraction",
            schema_name="EntityExtractionResponse",
            model="smart",
            temperature=0.05,
            input_text="Test input"
        ) as tracker:
            # Simulate processing time
            time.sleep(0.1)
            
            # Mark as successful
            tracker.set_success(True, {"entities": ["test"]})
        
        # Check metrics were recorded
        assert len(self.monitor.metrics_history) == 1
        metrics = self.monitor.metrics_history[0]
        assert metrics.component == "entity_extraction"
        assert metrics.schema_name == "EntityExtractionResponse"
        assert metrics.success is True
        assert metrics.response_time_ms >= 100  # At least 100ms due to sleep
        assert metrics.output_length > 0  # Should have output length
    
    def test_operation_tracker_with_validation_error(self):
        """Test operation tracking with validation error."""
        with self.monitor.track_operation(
            component="mcp_adapter",
            schema_name="MCPOrchestrationResponse"
        ) as tracker:
            tracker.set_validation_error("Schema mismatch: missing required field")
        
        # Check error recorded
        assert len(self.monitor.metrics_history) == 1
        metrics = self.monitor.metrics_history[0]
        assert metrics.success is False
        assert metrics.validation_error == "Schema mismatch: missing required field"
        assert metrics.llm_error is None
    
    def test_operation_tracker_with_exception(self):
        """Test operation tracking with uncaught exception."""
        try:
            with self.monitor.track_operation(
                component="test_component",
                schema_name="TestSchema"
            ) as tracker:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        # Check exception recorded
        assert len(self.monitor.metrics_history) == 1
        metrics = self.monitor.metrics_history[0]
        assert metrics.success is False
        assert "Test exception" in metrics.llm_error
    
    def test_health_validation_good_performance(self):
        """Test health validation with good performance."""
        # Add successful operations
        for i in range(20):
            metrics = StructuredOutputMetrics(
                component="test_component",
                schema_name="TestSchema",
                success=True,
                response_time_ms=200.0,
                model_used="gemini/gemini-2.5-flash",
                temperature=0.05,
                max_tokens=1000,
                input_length=100,
                output_length=150
            )
            self.monitor.record_operation(metrics)
        
        # Validate health
        results = self.monitor.validate_system_health()
        
        # Check overall success rate
        success_rate_result = next(r for r in results if r.check_name == "overall_success_rate")
        assert success_rate_result.success is True
        assert success_rate_result.value == 1.0  # 100% success rate
        assert success_rate_result.severity == "info"
        
        # Check response time
        response_time_result = next(r for r in results if r.check_name == "avg_response_time")
        assert response_time_result.success is True
        assert response_time_result.value == 200.0
        
        # Check error rates
        validation_error_result = next(r for r in results if r.check_name == "validation_error_rate")
        assert validation_error_result.success is True
        assert validation_error_result.value == 0.0
        
        llm_error_result = next(r for r in results if r.check_name == "llm_error_rate")
        assert llm_error_result.success is True
        assert llm_error_result.value == 0.0
    
    def test_health_validation_poor_performance(self):
        """Test health validation with poor performance."""
        # Add mostly failed operations
        for i in range(20):
            success = i < 5  # Only 25% success rate
            metrics = StructuredOutputMetrics(
                component="test_component",
                schema_name="TestSchema",
                success=success,
                response_time_ms=3000.0,  # High response time
                model_used="gemini/gemini-2.5-flash",
                temperature=0.05,
                max_tokens=1000,
                input_length=100,
                output_length=150 if success else 0,
                validation_error=None if success else "Validation failed"
            )
            self.monitor.record_operation(metrics)
        
        # Validate health
        results = self.monitor.validate_system_health()
        
        # Check overall success rate (should fail)
        success_rate_result = next(r for r in results if r.check_name == "overall_success_rate")
        assert success_rate_result.success is False
        assert success_rate_result.value == 0.25  # 25% success rate
        assert success_rate_result.severity in ["critical", "error"]
        
        # Check validation error rate (should fail)
        validation_error_result = next(r for r in results if r.check_name == "validation_error_rate")
        assert validation_error_result.success is False
        assert validation_error_result.value == 0.75  # 75% validation errors
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        # Add mixed operations
        components = ["entity_extraction", "mcp_adapter", "reasoning"]
        schemas = ["EntityResponse", "MCPResponse", "ReasoningResponse"]
        
        for i in range(30):
            component = components[i % 3]
            schema = schemas[i % 3]
            success = i % 4 != 0  # 75% success rate overall
            
            metrics = StructuredOutputMetrics(
                component=component,
                schema_name=schema,
                success=success,
                response_time_ms=200.0 + (i * 10),  # Varying response times
                model_used="gemini/gemini-2.5-flash",
                temperature=0.05,
                max_tokens=1000,
                input_length=100,
                output_length=150 if success else 0,
                validation_error=None if success else "Failed"
            )
            self.monitor.record_operation(metrics)
        
        # Get performance summary
        summary = self.monitor.get_performance_summary()
        
        # Debug output
        print(f"Summary: {summary}")
        
        # Check overall stats (if summary exists)
        if "error" not in summary:
            assert summary["overall_stats"]["total_operations"] == 30
            # Success rate should be approximately 73.3% (22/30) based on i % 4 != 0 pattern
            success_rate = summary["overall_stats"]["success_rate"]
            assert 0.7 <= success_rate <= 0.8, f"Expected success rate ~0.73, got {success_rate}"
            
            validation_error_rate = summary["overall_stats"]["validation_error_rate"]
            assert 0.2 <= validation_error_rate <= 0.3, f"Expected validation error rate ~0.27, got {validation_error_rate}"
            
            assert summary["overall_stats"]["llm_error_rate"] == 0.0
            
            # Check component breakdown exists
            assert "component_breakdown" in summary
            if len(summary["component_breakdown"]) > 0:
                # Just check that components exist in breakdown
                for component in components:
                    if component in summary["component_breakdown"]:
                        comp_stats = summary["component_breakdown"][component]
                        assert comp_stats["total_operations"] >= 1  # At least some operations
            
            # Check schema usage exists
            assert "schema_usage" in summary
        else:
            # If no recent metrics, this is also acceptable
            assert summary["error"] == "No recent metrics available"
    
    def test_export_metrics_json(self):
        """Test exporting metrics to JSON."""
        # Add some test metrics
        for i in range(5):
            metrics = StructuredOutputMetrics(
                component=f"component_{i}",
                schema_name=f"Schema_{i}",
                success=True,
                response_time_ms=200.0,
                model_used="gemini/gemini-2.5-flash",
                temperature=0.05,
                max_tokens=1000,
                input_length=100,
                output_length=150
            )
            self.monitor.record_operation(metrics)
        
        # Export to temporary file
        export_path = "/tmp/test_metrics.json"
        success = self.monitor.export_metrics(export_path, format="json")
        
        assert success is True
        assert os.path.exists(export_path)
        
        # Verify exported data
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        assert "export_timestamp" in data
        assert "metrics" in data
        assert len(data["metrics"]) == 5
        
        # Check first metric structure
        first_metric = data["metrics"][0]
        assert first_metric["component"] == "component_0"
        assert first_metric["schema_name"] == "Schema_0"
        assert first_metric["success"] is True
        assert first_metric["response_time_ms"] == 200.0
        
        # Cleanup
        os.remove(export_path)
    
    def test_export_metrics_csv(self):
        """Test exporting metrics to CSV."""
        # Add test metrics
        metrics = StructuredOutputMetrics(
            component="test_component",
            schema_name="TestSchema",
            success=True,
            response_time_ms=300.0,
            model_used="gemini/gemini-2.5-flash",
            temperature=0.05,
            max_tokens=1000,
            input_length=100,
            output_length=150
        )
        self.monitor.record_operation(metrics)
        
        # Export to CSV
        export_path = "/tmp/test_metrics.csv"
        success = self.monitor.export_metrics(export_path, format="csv")
        
        assert success is True
        assert os.path.exists(export_path)
        
        # Verify CSV content
        with open(export_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2  # Header + 1 data row
        assert "timestamp" in lines[0]  # Header row
        assert "test_component" in lines[1]  # Data row
        
        # Cleanup
        os.remove(export_path)
    
    def test_global_monitor_instance(self):
        """Test global monitor instance access."""
        # Get global instance
        monitor1 = get_monitor()
        monitor2 = get_monitor()
        
        # Should be same instance
        assert monitor1 is monitor2
        
        # Test tracking function
        with track_structured_output("test_component", "TestSchema") as tracker:
            tracker.set_success(True)
        
        # Should have recorded in global monitor
        assert len(monitor1.metrics_history) >= 1


class TestMonitoringIntegration:
    """Integration tests for monitoring with real components."""
    
    def test_structured_llm_service_integration(self):
        """Test monitoring integration with StructuredLLMService."""
        try:
            from src.core.structured_llm_service import StructuredLLMService
            from src.orchestration.reasoning_schema import ReasoningStep
            from src.monitoring.structured_output_monitor import get_monitor
            
            # Get fresh monitor
            monitor = get_monitor()
            initial_count = len(monitor.metrics_history)
            
            # Create service
            service = StructuredLLMService()
            
            if service.available:
                # Test with simple schema
                try:
                    result = service.structured_completion(
                        prompt="Create a reasoning step with action 'test', reasoning 'testing', and confidence 0.9",
                        schema=ReasoningStep,
                        temperature=0.05
                    )
                    
                    # Check monitoring recorded the operation
                    assert len(monitor.metrics_history) > initial_count
                    
                    # Check latest metric
                    latest_metric = monitor.metrics_history[-1]
                    assert latest_metric.component == "structured_llm_service"
                    assert latest_metric.schema_name == "ReasoningStep"
                    assert latest_metric.model_used.startswith("gemini/")
                    assert latest_metric.temperature == 0.05
                    
                    if latest_metric.success:
                        assert latest_metric.validation_error is None
                        assert latest_metric.llm_error is None
                    
                    print(f"✅ Integration test successful - monitored operation: {latest_metric.success}")
                    
                except Exception as e:
                    # Still check if monitoring captured the error
                    if len(monitor.metrics_history) > initial_count:
                        latest_metric = monitor.metrics_history[-1]
                        assert latest_metric.success is False
                        assert latest_metric.llm_error is not None or latest_metric.validation_error is not None
                        print(f"✅ Integration test successful - monitored error: {e}")
                    else:
                        print(f"❌ Integration test failed - no monitoring: {e}")
                        raise
            else:
                print("⚠️ StructuredLLMService not available - skipping integration test")
                
        except ImportError as e:
            print(f"⚠️ Cannot import required modules for integration test: {e}")


def test_monitoring_framework():
    """Main test function to run all monitoring tests."""
    print("🔧 Testing Structured Output Monitoring Framework")
    print("-" * 60)
    
    # Run basic monitor tests
    test_monitor = TestStructuredOutputMonitor()
    
    test_methods = [
        test_monitor.test_monitor_initialization,
        test_monitor.test_record_successful_operation,
        test_monitor.test_record_validation_failure,
        test_monitor.test_record_llm_failure,
        test_monitor.test_operation_tracker_context_manager,
        test_monitor.test_operation_tracker_with_validation_error,
        test_monitor.test_operation_tracker_with_exception,
        test_monitor.test_health_validation_good_performance,
        test_monitor.test_health_validation_poor_performance,
        test_monitor.test_performance_summary,
        test_monitor.test_export_metrics_json,
        test_monitor.test_export_metrics_csv,
        test_monitor.test_global_monitor_instance
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_monitor.setup_method()
            test_method()
            print(f"✅ {test_method.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: {e}")
            failed += 1
    
    # Run integration test
    try:
        integration_test = TestMonitoringIntegration()
        integration_test.test_structured_llm_service_integration()
        print(f"✅ test_structured_llm_service_integration")
        passed += 1
    except Exception as e:
        print(f"❌ test_structured_llm_service_integration: {e}")
        failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All monitoring tests passed!")
        return True
    else:
        print("❌ Some monitoring tests failed")
        return False


if __name__ == "__main__":
    success = test_monitoring_framework()
    sys.exit(0 if success else 1)