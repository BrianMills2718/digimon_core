"""
Test Phase C Tool Wrappers

Verifies all Phase C modules are properly wrapped with BaseTool interface.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.phase_c import (
    MultiDocumentTool,
    CrossModalTool,
    ClusteringTool,
    TemporalTool,
    CollaborativeTool
)
from src.tools.base_tool_fixed import ToolRequest


def test_multi_document_tool_wrapper():
    """Test MultiDocumentTool wrapper."""
    print("\n🧪 Testing MultiDocumentTool wrapper...")
    
    tool = MultiDocumentTool()
    
    # Test document loading
    request = ToolRequest(
        tool_id="MULTI_DOCUMENT_PROCESSOR",
        operation="load_batch",
        input_data={
            "documents": ["doc1.txt", "doc2.txt"],
            "operation": "load_batch"
        }
    )
    
    result = tool.execute(request)
    assert result.status == "success", f"Expected success, got {result.status}"
    assert "processed_documents" in result.data
    print("  ✅ MultiDocumentTool wrapper working")
    
    # Test capabilities
    caps = tool.get_capabilities()
    assert caps["tool_id"] == "MULTI_DOCUMENT_PROCESSOR"
    assert "operations" in caps
    print("  ✅ Capabilities accessible")
    
    return True


def test_cross_modal_tool_wrapper():
    """Test CrossModalTool wrapper."""
    print("\n🧪 Testing CrossModalTool wrapper...")
    
    tool = CrossModalTool()
    
    request = ToolRequest(
        tool_id="CROSS_MODAL_ANALYZER",
        operation="analyze",
        input_data={
            "data": {"text": "sample text", "entities": ["entity1"]},
            "operation": "analyze",
            "modalities": ["text"]
        }
    )
    
    result = tool.execute(request)
    if result.status != "success":
        print(f"    Error: {result.error_code} - {result.error_message}")
    assert result.status == "success", f"Expected success, got {result.status}"
    assert "analysis" in result.data
    print("  ✅ CrossModalTool wrapper working")
    
    return True


def test_clustering_tool_wrapper():
    """Test ClusteringTool wrapper."""
    print("\n🧪 Testing ClusteringTool wrapper...")
    
    tool = ClusteringTool()
    
    request = ToolRequest(
        tool_id="INTELLIGENT_CLUSTERER",
        operation="adaptive",
        input_data={
            "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "operation": "adaptive",
            "parameters": {"min_clusters": 2, "max_clusters": 5}
        }
    )
    
    result = tool.execute(request)
    if result.status != "success":
        print(f"    Error: {result.error_code} - {result.error_message}")
    assert result.status == "success", f"Expected success, got {result.status}"
    assert "clusters" in result.data
    print("  ✅ ClusteringTool wrapper working")
    
    return True


def test_temporal_tool_wrapper():
    """Test TemporalTool wrapper."""
    print("\n🧪 Testing TemporalTool wrapper...")
    
    tool = TemporalTool()
    
    request = ToolRequest(
        tool_id="TEMPORAL_ANALYZER",
        operation="extract",
        input_data={
            "data": {"text": "Meeting on 2024-01-15 at 14:30"},
            "operation": "extract"
        }
    )
    
    result = tool.execute(request)
    if result.status != "success":
        print(f"    Error: {result.error_code} - {result.error_message}")
    assert result.status == "success", f"Expected success, got {result.status}"
    assert "temporal_entities" in result.data
    print("  ✅ TemporalTool wrapper working")
    
    return True


def test_collaborative_tool_wrapper():
    """Test CollaborativeTool wrapper."""
    print("\n🧪 Testing CollaborativeTool wrapper...")
    
    tool = CollaborativeTool()
    
    request = ToolRequest(
        tool_id="COLLABORATIVE_INTELLIGENCE",
        operation="coordinate",
        input_data={
            "task": {"type": "analysis", "data": "sample"},
            "agents": [],
            "operation": "coordinate"
        }
    )
    
    result = tool.execute(request)
    if result.status != "success":
        print(f"    Error: {result.error_code} - {result.error_message}")
    assert result.status == "success", f"Expected success, got {result.status}"
    assert "coordination_result" in result.data
    print("  ✅ CollaborativeTool wrapper working")
    
    # Test consensus operation
    request = ToolRequest(
        tool_id="COLLABORATIVE_INTELLIGENCE",
        operation="consensus",
        input_data={
            "operation": "consensus",
            "proposals": [
                {"agent": "a1", "value": "option_a"},
                {"agent": "a2", "value": "option_a"},
                {"agent": "a3", "value": "option_b"}
            ]
        }
    )
    
    result = tool.execute(request)
    assert result.status == "success"
    assert "consensus" in result.data
    print("  ✅ Consensus operation working")
    
    return True


def test_all_tools_implement_interface():
    """Verify all tools implement BaseTool interface correctly."""
    print("\n🧪 Testing BaseTool interface implementation...")
    
    tools = [
        MultiDocumentTool(),
        CrossModalTool(),
        ClusteringTool(),
        TemporalTool(),
        CollaborativeTool()
    ]
    
    for tool in tools:
        # Check required methods exist
        assert hasattr(tool, 'execute'), f"{tool.__class__.__name__} missing execute method"
        assert hasattr(tool, 'validate_input'), f"{tool.__class__.__name__} missing validate_input method"
        assert hasattr(tool, 'get_capabilities'), f"{tool.__class__.__name__} missing get_capabilities method"
        assert hasattr(tool, 'tool_id'), f"{tool.__class__.__name__} missing tool_id attribute"
        
        # Check tool_id is set
        assert tool.tool_id is not None, f"{tool.__class__.__name__} tool_id not set"
        
        print(f"  ✅ {tool.__class__.__name__} implements interface correctly")
    
    return True


def run_all_tests():
    """Run all Phase C tool wrapper tests."""
    print("=" * 60)
    print("PHASE C TOOL WRAPPER TESTS")
    print("=" * 60)
    
    tests = [
        test_multi_document_tool_wrapper,
        test_cross_modal_tool_wrapper,
        test_clustering_tool_wrapper,
        test_temporal_tool_wrapper,
        test_collaborative_tool_wrapper,
        test_all_tools_implement_interface
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n✅ Task 1 Complete: All Phase C modules wrapped with BaseTool interface!")
    else:
        print("\n❌ Task 1 Failed: Some tests did not pass")
    
    sys.exit(0 if success else 1)