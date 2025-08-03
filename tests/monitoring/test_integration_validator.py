#!/usr/bin/env python3
"""
Integration Validator Test Suite

Comprehensive tests for the integration validation and monitoring system.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.monitoring.integration_validator import (
    IntegrationValidator,
    ValidationStatus,
    AlertSeverity,
    ValidationResult,
    Alert,
    AlertRule,
    HealthCheckConfig,
    create_production_validator,
    create_development_validator
)


class TestIntegrationValidator:
    """Test integration validator functionality"""
    
    @pytest.fixture
    async def validator(self):
        """Create test validator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "monitoring": {"enabled": True, "log_level": "INFO"},
                "validation": {"infrastructure_timeout": 10},
                "performance": {"cpu_threshold": 80.0, "memory_threshold": 85.0}
            }
            json.dump(config, f)
            f.flush()
            
            validator = IntegrationValidator(f.name)
            yield validator
            
            # Cleanup
            if validator._monitoring:
                await validator.stop_monitoring()
            await validator.cleanup()
            Path(f.name).unlink()
    
    @pytest.fixture
    def mock_infrastructure_integrator(self):
        """Mock infrastructure integrator"""
        mock = Mock()
        mock.initialize = AsyncMock(return_value=True)
        mock.get_integration_metrics = Mock(return_value={
            'component_status': {
                'database_optimizer': True,
                'memory_manager': True,
                'llm_cache_manager': True
            },
            'performance_metrics': {
                'cache_hit_rate': '65.2%',
                'average_speedup': '2.1x',
                'total_operations': 150
            }
        })
        mock.cleanup = AsyncMock()
        return mock
    
    @pytest.fixture
    def mock_service_manager(self):
        """Mock service manager"""
        mock = Mock()
        mock.health_check = Mock(return_value={
            'identity': True,
            'provenance': True,
            'quality': True,
            'workflow': True
        })
        return mock
    
    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator is not None
        assert validator.config is not None
        assert validator._monitoring is False
        assert len(validator.alert_rules) > 0
        assert len(validator.health_check_configs) > 0
    
    def test_config_loading(self):
        """Test configuration loading"""
        # Test with valid config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {"monitoring": {"enabled": True}}
            json.dump(config, f)
            f.flush()
            
            validator = IntegrationValidator(f.name)
            assert validator.config['monitoring']['enabled'] is True
            Path(f.name).unlink()
        
        # Test with invalid config path
        validator = IntegrationValidator("nonexistent.json")
        assert validator.config is not None  # Should use defaults
    
    @pytest.mark.asyncio
    async def test_component_initialization(self, validator, mock_infrastructure_integrator):
        """Test component initialization"""
        with patch.object(validator, 'service_manager', Mock()):
            with patch('src.monitoring.integration_validator.InfrastructureIntegrator', 
                      return_value=mock_infrastructure_integrator):
                
                success = await validator.initialize_components()
                assert success is True
                mock_infrastructure_integrator.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, validator, mock_infrastructure_integrator):
        """Test monitoring start/stop lifecycle"""
        with patch.object(validator, 'initialize_components', AsyncMock(return_value=True)):
            # Start monitoring
            success = await validator.start_monitoring()
            assert success is True
            assert validator._monitoring is True
            assert validator._monitoring_task is not None
            
            # Stop monitoring
            await validator.stop_monitoring()
            assert validator._monitoring is False
            assert validator._monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_infrastructure_health_check(self, validator, mock_infrastructure_integrator):
        """Test infrastructure health check"""
        validator.infrastructure_integrator = mock_infrastructure_integrator
        
        result = await validator._check_infrastructure_health()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "infrastructure"
        assert result.status in [ValidationStatus.HEALTHY, ValidationStatus.WARNING, ValidationStatus.CRITICAL]
        assert result.duration_ms >= 0
    
    @pytest.mark.asyncio
    async def test_services_health_check(self, validator, mock_service_manager):
        """Test services health check"""
        validator.service_manager = mock_service_manager
        
        result = await validator._check_services_health()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "services"
        assert result.status == ValidationStatus.HEALTHY
        mock_service_manager.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_services_health_check_with_failures(self, validator):
        """Test services health check with failures"""
        mock_service_manager = Mock()
        mock_service_manager.health_check = Mock(return_value={
            'identity': True,
            'provenance': False,  # Failed service
            'quality': True
        })
        validator.service_manager = mock_service_manager
        
        result = await validator._check_services_health()
        
        assert result.status == ValidationStatus.CRITICAL
        assert "provenance" in result.message
    
    @pytest.mark.asyncio
    async def test_performance_health_check(self, validator):
        """Test performance health check"""
        with patch('psutil.cpu_percent', return_value=75.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 80.0
                mock_memory.return_value.available = 4 * 1024**3  # 4GB
                
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.percent = 70.0
                    
                    result = await validator._check_performance_health()
                    
                    assert isinstance(result, ValidationResult)
                    assert result.component == "performance"
                    assert result.status == ValidationStatus.HEALTHY
    
    @pytest.mark.asyncio
    async def test_performance_health_check_high_usage(self, validator):
        """Test performance health check with high resource usage"""
        with patch('psutil.cpu_percent', return_value=95.0):  # High CPU
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 90.0  # High memory
                mock_memory.return_value.available = 1 * 1024**3  # 1GB
                
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.percent = 85.0
                    
                    result = await validator._check_performance_health()
                    
                    assert result.status == ValidationStatus.WARNING
                    assert "High CPU" in result.message or "High memory" in result.message
    
    def test_alert_rule_evaluation(self, validator):
        """Test alert rule evaluation"""
        metrics = {
            'cpu_percent': 85.0,
            'memory_percent': 90.0,
            'error_rate': 0.1,
            'failed_services': 0
        }
        
        # Test high CPU alert
        result = validator._evaluate_alert_condition("cpu_percent > 80", metrics)
        assert result is True
        
        # Test memory alert
        result = validator._evaluate_alert_condition("memory_percent > 85", metrics)
        assert result is True
        
        # Test service failure alert
        result = validator._evaluate_alert_condition("failed_services > 0", metrics)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_alert_generation(self, validator):
        """Test alert generation and processing"""
        # Setup mock metrics that will trigger alerts
        mock_metrics = {
            'cpu_percent': 95.0,  # Should trigger critical CPU alert
            'memory_percent': 90.0,  # Should trigger memory alert
            'error_rate': 0.0,
            'failed_services': 0,
            'infrastructure_status': 'HEALTHY'
        }
        
        with patch.object(validator, '_gather_alert_metrics', AsyncMock(return_value=mock_metrics)):
            with patch.object(validator, '_trigger_alert', AsyncMock()) as mock_trigger:
                
                await validator._process_alerts()
                
                # Should have triggered at least one alert
                assert mock_trigger.call_count > 0
                
                # Verify alert structure
                args, _ = mock_trigger.call_args
                alert = args[0]
                assert isinstance(alert, Alert)
                assert alert.severity in [AlertSeverity.WARNING, AlertSeverity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_alert_cooldown(self, validator):
        """Test alert cooldown functionality"""
        # Set up alert that should trigger
        rule = AlertRule(
            name="test_alert",
            condition="cpu_percent > 50",
            severity=AlertSeverity.WARNING,
            message_template="Test alert: {cpu_percent}%",
            cooldown_minutes=1  # 1 minute cooldown
        )
        
        validator.alert_rules = [rule]
        
        mock_metrics = {'cpu_percent': 75.0}
        
        with patch.object(validator, '_gather_alert_metrics', AsyncMock(return_value=mock_metrics)):
            with patch.object(validator, '_trigger_alert', AsyncMock()) as mock_trigger:
                
                # First alert should trigger
                await validator._process_alerts()
                assert mock_trigger.call_count == 1
                
                # Second alert should be blocked by cooldown
                await validator._process_alerts()
                assert mock_trigger.call_count == 1  # Still only 1
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, validator):
        """Test getting health status"""
        # Record some health check results
        validator._record_health_check_result(
            "infrastructure", 
            ValidationStatus.HEALTHY, 
            "All components operational"
        )
        validator._record_health_check_result(
            "services", 
            ValidationStatus.WARNING, 
            "One service degraded"
        )
        
        health_status = await validator.get_health_status()
        
        assert health_status['overall_status'] == ValidationStatus.WARNING.value
        assert 'infrastructure' in health_status['components']
        assert 'services' in health_status['components']
        assert health_status['components']['infrastructure']['status'] == 'healthy'
        assert health_status['components']['services']['status'] == 'warning'
    
    @pytest.mark.asyncio
    async def test_get_recent_alerts(self, validator):
        """Test getting recent alerts"""
        # Add some test alerts
        now = datetime.now()
        
        alert1 = Alert(
            rule_name="test_alert_1",
            severity=AlertSeverity.WARNING,
            message="Test warning alert",
            component="test",
            triggered_at=now - timedelta(hours=1)
        )
        
        alert2 = Alert(
            rule_name="test_alert_2",
            severity=AlertSeverity.CRITICAL,
            message="Test critical alert",
            component="test",
            triggered_at=now - timedelta(hours=25)  # Older than 24 hours
        )
        
        validator._alerts = [alert1, alert2]
        
        # Get alerts from last 24 hours
        recent_alerts = await validator.get_recent_alerts(hours=24)
        
        assert len(recent_alerts) == 1  # Only alert1 should be included
        assert recent_alerts[0]['rule_name'] == 'test_alert_1'
        assert recent_alerts[0]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    async def test_export_monitoring_data(self, validator):
        """Test exporting monitoring data"""
        # Add some test data
        validator._record_health_check_result(
            "test_component", 
            ValidationStatus.HEALTHY, 
            "Test message"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            success = await validator.export_monitoring_data(f.name)
            
            assert success is True
            
            # Verify exported data
            with open(f.name, 'r') as read_f:
                data = json.load(read_f)
                
                assert 'health_status' in data
                assert 'recent_alerts' in data
                assert 'validation_history' in data
                assert 'alert_rules' in data
                assert 'exported_at' in data
            
            Path(f.name).unlink()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, validator):
        """Test cleanup of old validation history and alerts"""
        # Add old data
        old_time = datetime.now() - timedelta(days=10)
        
        validator._validation_history = [
            {
                'component': 'test',
                'status': 'healthy',
                'message': 'Old entry',
                'timestamp': old_time.isoformat()
            }
        ]
        
        old_alert = Alert(
            rule_name="old_alert",
            severity=AlertSeverity.INFO,
            message="Old alert",
            component="test",
            triggered_at=old_time
        )
        validator._alerts = [old_alert]
        
        # Configure short retention period
        validator.config['monitoring']['history_retention_days'] = 1
        
        await validator._cleanup_old_data()
        
        # Old data should be cleaned up
        assert len(validator._validation_history) == 0
        assert len(validator._alerts) == 0


class TestValidatorFactories:
    """Test validator factory functions"""
    
    def test_create_production_validator(self):
        """Test production validator factory"""
        validator = create_production_validator()
        
        assert isinstance(validator, IntegrationValidator)
        assert validator.health_check_configs['infrastructure'].interval_seconds == 60
        assert validator.health_check_configs['services'].interval_seconds == 120
        assert validator.health_check_configs['performance'].interval_seconds == 30
    
    def test_create_development_validator(self):
        """Test development validator factory"""
        validator = create_development_validator()
        
        assert isinstance(validator, IntegrationValidator)
        assert validator.health_check_configs['workflows'].enabled is False
        assert validator.health_check_configs['performance'].interval_seconds == 300


class TestValidationResult:
    """Test ValidationResult data class"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation"""
        result = ValidationResult(
            component="test",
            check_name="test_check",
            status=ValidationStatus.HEALTHY,
            message="All good",
            details={"key": "value"},
            duration_ms=100.0
        )
        
        assert result.component == "test"
        assert result.check_name == "test_check"
        assert result.status == ValidationStatus.HEALTHY
        assert result.message == "All good"
        assert result.details == {"key": "value"}
        assert result.duration_ms == 100.0
        assert isinstance(result.timestamp, datetime)


class TestAlert:
    """Test Alert data class"""
    
    def test_alert_creation(self):
        """Test Alert creation"""
        now = datetime.now()
        
        alert = Alert(
            rule_name="test_rule",
            severity=AlertSeverity.WARNING,
            message="Test alert",
            component="test_component",
            triggered_at=now,
            details={"metric": "value"}
        )
        
        assert alert.rule_name == "test_rule"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.message == "Test alert"
        assert alert.component == "test_component"
        assert alert.triggered_at == now
        assert alert.details == {"metric": "value"}
        assert alert.resolved_at is None


@pytest.mark.asyncio
async def test_full_monitoring_cycle():
    """Integration test for full monitoring cycle"""
    validator = None
    
    try:
        # Create validator with minimal config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "monitoring": {"enabled": True},
                "health_checks": {
                    "infrastructure": {"interval_seconds": 1},
                    "services": {"interval_seconds": 1},
                    "performance": {"interval_seconds": 1}
                }
            }
            json.dump(config, f)
            f.flush()
            
            validator = IntegrationValidator(f.name)
            
            # Mock components to avoid actual initialization
            with patch.object(validator, 'initialize_components', AsyncMock(return_value=True)):
                # Start monitoring
                success = await validator.start_monitoring()
                assert success is True
                
                # Let it run briefly
                await asyncio.sleep(2)
                
                # Check that health checks were recorded
                assert len(validator._health_checks) > 0
                
                # Get health status
                health_status = await validator.get_health_status()
                assert 'overall_status' in health_status
                
            Path(f.name).unlink()
            
    finally:
        if validator:
            await validator.stop_monitoring()
            await validator.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])