"""Tool Contract Compliance Tests

Tests that all MVRT tools implement the KGASTool interface correctly
and comply with the standardized contracts per ADR-001.
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, ToolValidationResult,
    get_tool_registry, register_tool
)
from src.core.confidence_score import ConfidenceScore
from src.core.tool_adapter import create_mvrt_tool_adapters, register_all_mvrt_tools


class TestToolContractCompliance:
    """Test suite for tool contract compliance."""
    
    @pytest.fixture(autouse=True)
    def setup_tools(self):
        """Register all MVRT tools before tests."""
        register_all_mvrt_tools()
        self.tool_registry = get_tool_registry()
    
    def test_all_tools_registered(self):
        """Test that all expected MVRT tools are registered."""
        expected_tools = [
            'T01_PDF_LOADER',
            'T15A_TEXT_CHUNKER', 
            'T15B_VECTOR_EMBEDDER',
            'T23A_SPACY_NER',
            'T23C_ONTOLOGY_AWARE_EXTRACTOR',
            'T27_RELATIONSHIP_EXTRACTOR',
            'T31_ENTITY_BUILDER',
            'T34_EDGE_BUILDER',
            'T49_MULTIHOP_QUERY',
            'T68_PAGERANK',
            'T301_MULTI_DOCUMENT_FUSION',
            'GRAPH_TABLE_EXPORTER',
            'MULTI_FORMAT_EXPORTER'
        ]
        
        registered_tools = self.tool_registry.list_tools()
        
        missing_tools = []
        for tool_id in expected_tools:
            if tool_id not in registered_tools:
                missing_tools.append(tool_id)
        
        assert not missing_tools, f"Missing tools: {missing_tools}"
    
    def test_tool_interface_compliance(self):
        """Test that all tools implement the KGASTool interface."""
        validation_results = self.tool_registry.validate_all_tools()
        
        failed_tools = []
        for tool_id, result in validation_results.items():
            if not result.is_valid:
                failed_tools.append({
                    'tool_id': tool_id,
                    'errors': result.errors
                })
        
        assert not failed_tools, f"Tools failed interface compliance: {failed_tools}"
    
    @pytest.mark.parametrize("tool_id", [
        'T01_PDF_LOADER',
        'T15A_TEXT_CHUNKER',
        'T23A_SPACY_NER',
        'T49_MULTIHOP_QUERY',
        'GRAPH_TABLE_EXPORTER',
        'MULTI_FORMAT_EXPORTER'
    ])
    def test_individual_tool_compliance(self, tool_id: str):
        """Test individual tool compliance with KGASTool interface."""
        tool = self.tool_registry.get_tool(tool_id)
        assert tool is not None, f"Tool {tool_id} not found in registry"
        
        # Test required methods exist
        required_methods = ['execute', 'get_theory_compatibility', 'get_input_schema', 
                           'get_output_schema', 'validate_input', 'get_tool_info']
        
        for method_name in required_methods:
            assert hasattr(tool, method_name), f"Tool {tool_id} missing method {method_name}"
            assert callable(getattr(tool, method_name)), f"Tool {tool_id} method {method_name} not callable"
    
    def test_tool_info_completeness(self):
        """Test that all tools provide complete tool information."""
        for tool_id in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_id)
            tool_info = tool.get_tool_info()
            
            # Check required fields
            required_fields = ['tool_id', 'tool_name', 'version', 'description']
            for field in required_fields:
                assert field in tool_info, f"Tool {tool_id} missing {field} in tool_info"
                assert tool_info[field], f"Tool {tool_id} has empty {field}"
    
    def test_input_schema_validity(self):
        """Test that all tools provide valid input schemas."""
        for tool_id in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_id)
            schema = tool.get_input_schema()
            
            # Basic schema validation
            assert isinstance(schema, dict), f"Tool {tool_id} input schema must be dict"
            assert 'type' in schema, f"Tool {tool_id} input schema missing 'type'"
            
            if 'properties' in schema:
                assert isinstance(schema['properties'], dict), f"Tool {tool_id} schema properties must be dict"
    
    def test_output_schema_validity(self):
        """Test that all tools provide valid output schemas."""
        for tool_id in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_id)
            schema = tool.get_output_schema()
            
            # Basic schema validation
            assert isinstance(schema, dict), f"Tool {tool_id} output schema must be dict"
            assert 'type' in schema, f"Tool {tool_id} output schema missing 'type'"
    
    def test_input_validation_functionality(self):
        """Test that input validation works correctly."""
        test_cases = [
            ('T01_PDF_LOADER', None, False),  # None input should fail
            ('T01_PDF_LOADER', {'file_path': 'test.pdf'}, True),  # Valid input
            ('T49_MULTIHOP_QUERY', {'query': 'test query'}, True),  # Valid query
            ('T49_MULTIHOP_QUERY', {}, False),  # Missing query should fail
        ]
        
        for tool_id, test_input, should_be_valid in test_cases:
            tool = self.tool_registry.get_tool(tool_id)
            if tool is None:
                continue  # Skip if tool not available
            
            result = tool.validate_input(test_input)
            assert isinstance(result, ToolValidationResult)
            
            if should_be_valid:
                assert result.is_valid, f"Tool {tool_id} validation failed for valid input: {test_input}"
            else:
                assert not result.is_valid, f"Tool {tool_id} validation passed for invalid input: {test_input}"
    
    def test_theory_compatibility_format(self):
        """Test that theory compatibility is returned in correct format."""
        for tool_id in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_id)
            compatibility = tool.get_theory_compatibility()
            
            assert isinstance(compatibility, list), f"Tool {tool_id} theory compatibility must be list"
            
            for theory_id in compatibility:
                assert isinstance(theory_id, str), f"Tool {tool_id} theory IDs must be strings"
    
    def test_confidence_score_integration(self):
        """Test that tools properly integrate with ConfidenceScore system."""
        # Test ConfidenceScore creation and combination
        score1 = ConfidenceScore.create_high_confidence(0.9, 5)
        score2 = ConfidenceScore.create_medium_confidence(0.7, 3)
        
        combined = score1.combine_with(score2)
        
        assert isinstance(combined, ConfidenceScore)
        assert 0.0 <= combined.value <= 1.0
        assert combined.evidence_weight > 0
    
    @pytest.mark.integration
    def test_tool_execution_basic(self):
        """Basic integration test for tool execution."""
        # Test PDF Loader with mock input
        pdf_loader = self.tool_registry.get_tool('T01_PDF_LOADER')
        if pdf_loader is None:
            pytest.skip("PDF Loader not available")
        
        # Create mock request
        request = ToolRequest(
            input_data={'file_path': 'tests/test_data/sample.pdf'},
            workflow_id='test_workflow'
        )
        
        # Note: This will fail if test file doesn't exist, but tests the interface
        try:
            result = pdf_loader.execute(request)
            assert isinstance(result, ToolResult)
            assert hasattr(result, 'status')
            assert hasattr(result, 'confidence')
            assert isinstance(result.confidence, ConfidenceScore)
        except Exception as e:
            # Expected to fail without actual test file
            assert "validation failed" in str(e).lower() or "not found" in str(e).lower()
    
    def test_error_handling_compliance(self):
        """Test that tools handle errors correctly."""
        for tool_id in ['T01_PDF_LOADER', 'T49_MULTIHOP_QUERY']:
            tool = self.tool_registry.get_tool(tool_id)
            if tool is None:
                continue
            
            # Test with invalid input
            request = ToolRequest(
                input_data=None,  # Invalid input
                workflow_id='test_workflow'
            )
            
            result = tool.execute(request)
            assert isinstance(result, ToolResult)
            assert result.status == 'error'
            assert result.error_details is not None
    
    def test_provenance_integration(self):
        """Test that tools integrate with provenance tracking."""
        tool = self.tool_registry.get_tool('T49_MULTIHOP_QUERY')
        if tool is None:
            pytest.skip("Multi-hop query tool not available")
        
        request = ToolRequest(
            input_data={'query': 'test query'},
            workflow_id='test_workflow'
        )
        
        result = tool.execute(request)
        assert isinstance(result, ToolResult)
        assert result.provenance is not None
        assert hasattr(result.provenance, '__dict__')  # Has provenance data


class TestToolRegistryFunctionality:
    """Test tool registry functionality."""
    
    def test_tool_registry_singleton(self):
        """Test that tool registry behaves as singleton."""
        registry1 = get_tool_registry()
        registry2 = get_tool_registry()
        assert registry1 is registry2
    
    def test_tool_registration(self):
        """Test tool registration and retrieval."""
        from src.core.tool_contract import BaseKGASTool
        
        # Create test tool
        class TestTool(BaseKGASTool):
            def execute(self, request):
                return ToolResult(
                    status='success',
                    data={'test': True},
                    confidence=ConfidenceScore.create_medium_confidence(),
                    metadata={},
                    provenance={},
                    request_id=request.request_id
                )
            
            def validate_input(self, input_data):
                return ToolValidationResult(True)
        
        test_tool = TestTool('TEST_TOOL', 'Test Tool')
        register_tool(test_tool)
        
        registry = get_tool_registry()
        retrieved_tool = registry.get_tool('TEST_TOOL')
        assert retrieved_tool is test_tool
    
    def test_tools_by_category(self):
        """Test retrieving tools by category."""
        register_all_mvrt_tools()
        registry = get_tool_registry()
        
        cross_modal_tools = registry.get_tools_by_category('cross_modal')
        assert len(cross_modal_tools) >= 2  # Should have graph exporter and format exporter
    
    def test_theory_compatible_tools(self):
        """Test retrieving theory-compatible tools."""
        register_all_mvrt_tools()
        registry = get_tool_registry()
        
        # Get tools that support general theory
        general_theory_tools = registry.get_theory_compatible_tools('general')
        # Should include T23C and other theory-aware tools
        
        tool_ids = [tool.tool_id for tool in general_theory_tools]
        assert any('T23C' in tool_id for tool_id in tool_ids)


class TestConfidenceScoreCompliance:
    """Test ConfidenceScore ADR-004 compliance."""
    
    def test_confidence_score_creation(self):
        """Test confidence score creation methods."""
        # Test factory methods
        high_conf = ConfidenceScore.create_high_confidence()
        assert high_conf.value >= 0.8
        assert high_conf.evidence_weight >= 3
        
        medium_conf = ConfidenceScore.create_medium_confidence()
        assert 0.6 <= medium_conf.value < 0.8
        assert medium_conf.evidence_weight >= 2
        
        low_conf = ConfidenceScore.create_low_confidence()
        assert medium_conf.value < 0.6
        assert low_conf.evidence_weight >= 1
    
    def test_confidence_combination(self):
        """Test confidence score combination methods."""
        score1 = ConfidenceScore.create_high_confidence(0.9, 5)
        score2 = ConfidenceScore.create_medium_confidence(0.7, 3)
        
        # Test Bayesian combination
        combined = score1.combine_with(score2)
        assert isinstance(combined, ConfidenceScore)
        assert combined.evidence_weight == 8  # 5 + 3
        assert 0.7 < combined.value < 0.9  # Should be between inputs
    
    def test_confidence_decay(self):
        """Test confidence decay functionality."""
        original = ConfidenceScore.create_high_confidence(0.9, 5)
        decayed = original.decay(0.95)
        
        assert decayed.value < original.value
        assert decayed.evidence_weight <= original.evidence_weight
    
    def test_quality_tier_conversion(self):
        """Test quality tier conversion."""
        high_conf = ConfidenceScore.create_high_confidence(0.9, 5)
        assert high_conf.to_quality_tier() == "HIGH"
        
        medium_conf = ConfidenceScore.create_medium_confidence(0.7, 3)
        assert medium_conf.to_quality_tier() == "MEDIUM"
        
        low_conf = ConfidenceScore.create_low_confidence(0.4, 1)
        assert low_conf.to_quality_tier() == "LOW"


if __name__ == "__main__":
    # Run basic compliance checks
    register_all_mvrt_tools()
    registry = get_tool_registry()
    
    print("Tool Contract Compliance Report")
    print("=" * 40)
    
    # Check tool registration
    tools = registry.list_tools()
    print(f"Registered tools: {len(tools)}")
    for tool_id in sorted(tools):
        print(f"  - {tool_id}")
    
    print("\nInterface Compliance:")
    validation_results = registry.validate_all_tools()
    
    passed = 0
    failed = 0
    
    for tool_id, result in validation_results.items():
        if result.is_valid:
            print(f"  ✓ {tool_id}")
            passed += 1
        else:
            print(f"  ✗ {tool_id}: {'; '.join(result.errors)}")
            failed += 1
    
    print(f"\nSummary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tools are contract compliant!")
    else:
        print("⚠️  Some tools need contract compliance fixes.")