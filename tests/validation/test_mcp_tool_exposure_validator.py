#!/usr/bin/env python3
"""
Test MCP Tool Exposure Validator

Tests for the MCP tool exposure validation system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from validation.mcp_tool_exposure_validator import (
    MCPToolExposureValidator,
    MCPToolValidationConfig,
    ToolExposureStatus,
    ValidationSeverity
)


class TestMCPToolExposureValidator:
    """Test MCP tool exposure validator"""
    
    @pytest.fixture
    def validator_config(self):
        """Create test validator configuration"""
        return MCPToolValidationConfig(
            test_timeout_seconds=5.0,
            enable_deep_testing=False,
            enable_performance_testing=False,
            test_with_sample_data=True,
            validate_tool_contracts=False,
            check_error_handling=False
        )
    
    @pytest.fixture
    def validator(self, validator_config):
        """Create test validator"""
        return MCPToolExposureValidator(validator_config)
    
    @pytest.fixture
    def mock_mcp_server(self):
        """Create mock MCP server"""
        mock_server = Mock()
        mock_server._tools = {
            'test_connection': Mock(return_value="connection successful"),
            'echo': Mock(return_value="Echo: test"),
            'get_system_status': Mock(return_value={
                'status': 'operational',
                'total_tools': 10
            }),
            'load_documents': Mock(return_value={'documents': [], 'total_loaded': 0}),
            'get_pdf_loader_info': Mock(return_value={
                'tool_id': 'T01_PDF_LOADER',
                'status': 'ready',
                'description': 'PDF document loader'
            })
        }
        return mock_server
    
    def test_validator_initialization(self, validator_config):
        """Test validator initialization"""
        validator = MCPToolExposureValidator(validator_config)
        
        assert validator.config == validator_config
        assert validator.validation_results == {}
        assert validator.validation_issues == []
        assert validator.mcp_server is None
    
    def test_get_available_mcp_tools_empty_server(self, validator):
        """Test getting tools from empty server"""
        validator.mcp_server = None
        tools = validator._get_available_mcp_tools()
        assert tools == set()
    
    def test_get_available_mcp_tools_with_server(self, validator, mock_mcp_server):
        """Test getting tools from mock server"""
        validator.mcp_server = mock_mcp_server
        tools = validator._get_available_mcp_tools()
        
        expected_tools = {
            'test_connection', 'echo', 'get_system_status', 
            'load_documents', 'get_pdf_loader_info'
        }
        assert tools == expected_tools
    
    @pytest.mark.asyncio
    async def test_call_mcp_function_success(self, validator, mock_mcp_server):
        """Test successful MCP function call"""
        validator.mcp_server = mock_mcp_server
        
        result = await validator._call_mcp_function_with_test_data('test_connection')
        
        assert result['success'] is True
        assert result['result'] == "connection successful"
    
    @pytest.mark.asyncio
    async def test_call_mcp_function_not_found(self, validator, mock_mcp_server):
        """Test MCP function call for non-existent function"""
        validator.mcp_server = mock_mcp_server
        
        result = await validator._call_mcp_function_with_test_data('nonexistent_function')
        
        assert result['success'] is False
        assert result['error_type'] == 'function_not_found'
    
    @pytest.mark.asyncio
    async def test_call_mcp_function_with_parameters(self, validator, mock_mcp_server):
        """Test MCP function call with parameters"""
        validator.mcp_server = mock_mcp_server
        
        result = await validator._call_mcp_function_with_test_data('echo')
        
        assert result['success'] is True
        assert result['result'] == "Echo: test"
        assert result['test_data'] == {'message': 'test'}
    
    @pytest.mark.asyncio
    async def test_validate_tool_exposure_fully_exposed(self, validator, mock_mcp_server):
        """Test tool exposure validation for fully exposed tool"""
        validator.mcp_server = mock_mcp_server
        
        expected_functions = ['test_connection', 'echo']
        result = await validator._validate_tool_exposure(
            'TEST_TOOL', expected_functions, 'test'
        )
        
        assert result.tool_id == 'TEST_TOOL'
        assert result.exposure_status == ToolExposureStatus.EXPOSED
        assert set(result.mcp_functions_found) == set(expected_functions)
        assert len(result.validation_errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_tool_exposure_partially_exposed(self, validator, mock_mcp_server):
        """Test tool exposure validation for partially exposed tool"""
        validator.mcp_server = mock_mcp_server
        
        expected_functions = ['test_connection', 'nonexistent_function']
        result = await validator._validate_tool_exposure(
            'PARTIAL_TOOL', expected_functions, 'test'
        )
        
        assert result.exposure_status == ToolExposureStatus.PARTIALLY_EXPOSED
        assert 'test_connection' in result.mcp_functions_found
        assert 'nonexistent_function' not in result.mcp_functions_found
        assert len(result.validation_errors) > 0
    
    @pytest.mark.asyncio
    async def test_validate_tool_exposure_not_exposed(self, validator, mock_mcp_server):
        """Test tool exposure validation for non-exposed tool"""
        validator.mcp_server = mock_mcp_server
        
        expected_functions = ['nonexistent_function1', 'nonexistent_function2']
        result = await validator._validate_tool_exposure(
            'MISSING_TOOL', expected_functions, 'test'
        )
        
        assert result.exposure_status == ToolExposureStatus.NOT_EXPOSED
        assert len(result.mcp_functions_found) == 0
        assert len(result.validation_errors) > 0
    
    def test_add_validation_issue(self, validator):
        """Test adding validation issues"""
        validator._add_validation_issue(
            ValidationSeverity.ERROR,
            "TEST_COMPONENT",
            "TEST_ISSUE",
            "Test error description",
            "Test recommendation"
        )
        
        assert len(validator.validation_issues) == 1
        issue = validator.validation_issues[0]
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.component == "TEST_COMPONENT"
        assert issue.issue_type == "TEST_ISSUE"
        assert issue.description == "Test error description"
        assert issue.recommendation == "Test recommendation"
    
    def test_create_validation_summary_empty(self, validator):
        """Test creating validation summary with no results"""
        summary = validator._create_validation_summary(True, "Test completed")
        
        assert summary['validation_summary']['success'] is True
        assert summary['validation_summary']['message'] == "Test completed"
        assert summary['tool_exposure_statistics']['total_tools_validated'] == 0
        assert summary['tool_exposure_statistics']['exposure_rate_percent'] == 0
    
    def test_create_validation_summary_with_results(self, validator):
        """Test creating validation summary with results"""
        # Add mock validation results
        from validation.mcp_tool_exposure_validator import ToolExposureResult
        
        validator.validation_results = {
            'TOOL1': ToolExposureResult(
                tool_id='TOOL1',
                tool_name='Tool 1',
                exposure_status=ToolExposureStatus.EXPOSED,
                is_callable=True
            ),
            'TOOL2': ToolExposureResult(
                tool_id='TOOL2', 
                tool_name='Tool 2',
                exposure_status=ToolExposureStatus.PARTIALLY_EXPOSED,
                is_callable=False
            )
        }
        
        summary = validator._create_validation_summary(True, "Test completed")
        
        stats = summary['tool_exposure_statistics']
        assert stats['total_tools_validated'] == 2
        assert stats['fully_exposed'] == 1
        assert stats['partially_exposed'] == 1
        assert stats['exposure_rate_percent'] == 50.0
    
    def test_generate_recommendations_low_exposure(self, validator):
        """Test recommendation generation for low exposure rate"""
        from validation.mcp_tool_exposure_validator import ToolExposureResult
        
        # Create results with low exposure rate
        validator.validation_results = {
            f'TOOL{i}': ToolExposureResult(
                tool_id=f'TOOL{i}',
                tool_name=f'Tool {i}',
                exposure_status=ToolExposureStatus.NOT_EXPOSED if i > 2 else ToolExposureStatus.EXPOSED
            )
            for i in range(1, 11)  # 10 tools, only first 2 exposed (20%)
        }
        
        recommendations = validator._generate_recommendations()
        
        assert any("Less than 50%" in rec for rec in recommendations)
    
    def test_generate_recommendations_broken_tools(self, validator):
        """Test recommendation generation for broken tools"""
        from validation.mcp_tool_exposure_validator import ToolExposureResult
        
        validator.validation_results = {
            'BROKEN_TOOL': ToolExposureResult(
                tool_id='BROKEN_TOOL',
                tool_name='Broken Tool',
                exposure_status=ToolExposureStatus.EXPOSED_BUT_BROKEN
            )
        }
        
        recommendations = validator._generate_recommendations()
        
        assert any("tools are exposed but not functional" in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_server_failure(self, validator):
        """Test MCP server initialization failure"""
        with patch('validation.mcp_tool_exposure_validator.get_mcp_server_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("Server init failed")
            
            result = await validator.initialize_mcp_server()
            
            assert result is False
            assert len(validator.validation_issues) > 0
            assert any(issue.severity == ValidationSeverity.CRITICAL 
                      for issue in validator.validation_issues)


class TestMCPToolValidationConfig:
    """Test MCP tool validation configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = MCPToolValidationConfig()
        
        assert config.test_timeout_seconds == 30.0
        assert config.enable_deep_testing is True
        assert config.enable_performance_testing is False
        assert config.test_with_sample_data is True
        assert config.validate_tool_contracts is True
        assert config.check_error_handling is True
        assert config.validate_parameter_schemas is True
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = MCPToolValidationConfig(
            test_timeout_seconds=10.0,
            enable_deep_testing=False,
            validate_tool_contracts=False
        )
        
        assert config.test_timeout_seconds == 10.0
        assert config.enable_deep_testing is False
        assert config.validate_tool_contracts is False


@pytest.mark.asyncio
async def test_validator_integration():
    """Integration test for validator (requires actual MCP components)"""
    
    # This test would require actual MCP server components
    # For now, we'll test the basic validation flow with mocks
    
    config = MCPToolValidationConfig(
        enable_deep_testing=False,
        validate_tool_contracts=False
    )
    
    validator = MCPToolExposureValidator(config)
    
    # Mock the MCP server initialization
    with patch.object(validator, 'initialize_mcp_server', AsyncMock(return_value=True)):
        with patch.object(validator, '_validate_phase1_tool_exposure', AsyncMock()):
            with patch.object(validator, '_validate_service_tool_exposure', AsyncMock()):
                with patch.object(validator, '_validate_server_tool_exposure', AsyncMock()):
                    with patch.object(validator, '_validate_tool_discoverability', AsyncMock()):
                        
                        result = await validator.validate_all_tool_exposure()
                        
                        assert 'validation_summary' in result
                        assert 'tool_exposure_statistics' in result
                        assert 'validation_issues' in result
                        assert 'tool_results' in result
                        assert 'recommendations' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])