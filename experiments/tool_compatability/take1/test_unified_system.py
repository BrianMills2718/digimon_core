#!/usr/bin/env python3
"""
Quick test to verify the unified tool system works correctly.
Run this to confirm all components are functioning.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from unified_data_contract import UnifiedData, Entity, Relationship, ToolCategory
        from base_tool import UnifiedTool, ToolResult, ToolStatus
        from real_tools import (
            PDFLoaderTool, EntityExtractorTool, RelationshipExtractorTool,
            GraphBuilderTool, PageRankAnalyzerTool, GraphToTableConverterTool
        )
        from tool_registry import ToolRegistry
        from dag_executor import DAGExecutor, DAG, DAGStep
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_unified_data():
    """Test UnifiedData creation and manipulation"""
    print("\nTesting UnifiedData...")
    try:
        from unified_data_contract import UnifiedData, Entity, Relationship
        
        # Create data
        data = UnifiedData(text="Test text")
        
        # Add entity
        entity = Entity(
            id="e1",
            text="Test Entity",
            type="PERSON",
            confidence=0.9,
            source_ref="test"
        )
        data.add_entity(entity)
        
        # Add relationship
        rel = Relationship(
            id="r1",
            source_id="e1",
            target_id="e2",
            type="KNOWS",
            confidence=0.8,
            source_ref="test"
        )
        data.add_relationship(rel)
        
        # Test serialization
        data_dict = data.to_dict()
        data_restored = UnifiedData.from_dict(data_dict)
        
        assert data_restored.text == "Test text"
        assert len(data_restored.entities) == 1
        assert len(data_restored.relationships) == 1
        
        print("✅ UnifiedData working correctly")
        return True
    except Exception as e:
        print(f"❌ UnifiedData test failed: {e}")
        return False


def test_tool_registry():
    """Test tool registration and discovery"""
    print("\nTesting Tool Registry...")
    try:
        from tool_registry import ToolRegistry
        from real_tools import PDFLoaderTool, EntityExtractorTool, GraphBuilderTool
        
        registry = ToolRegistry()
        
        # Register tools
        tools = [
            PDFLoaderTool(),
            EntityExtractorTool(),
            GraphBuilderTool()
        ]
        
        for tool in tools:
            registry.register_tool(tool)
        
        # Test retrieval
        loader = registry.get_tool("T01_PDF_LOADER")
        assert loader is not None
        
        # Test compatibility
        compatible = registry.find_compatible_tools("T01_PDF_LOADER")
        assert "T23A_ENTITY_EXTRACTOR" in compatible
        
        # Test statistics
        stats = registry.get_statistics()
        assert stats["total_tools"] == 3
        
        print(f"✅ Registry working with {stats['total_tools']} tools")
        return True
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        return False


def test_tool_execution():
    """Test actual tool execution"""
    print("\nTesting Tool Execution...")
    try:
        from unified_data_contract import UnifiedData
        from real_tools import EntityExtractorTool
        
        # Create test data
        data = UnifiedData(text="Dr. Jane Smith works at TechCorp.")
        
        # Create and execute tool
        extractor = EntityExtractorTool()
        result = extractor.execute(data)
        
        assert result.status.value == "success"
        assert len(result.data.entities) > 0
        
        print(f"✅ Tool execution successful, extracted {len(result.data.entities)} entities")
        return True
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        return False


def test_dag_execution():
    """Test DAG creation and validation"""
    print("\nTesting DAG Execution...")
    try:
        from tool_registry import ToolRegistry
        from dag_executor import DAGExecutor, DAG, DAGStep
        from real_tools import PDFLoaderTool, EntityExtractorTool
        from unified_data_contract import UnifiedData
        
        # Setup registry
        registry = ToolRegistry()
        registry.register_tool(PDFLoaderTool())
        registry.register_tool(EntityExtractorTool())
        
        # Create DAG
        dag = DAG(
            dag_id="test_dag",
            description="Test DAG",
            steps=[
                DAGStep(step_id="load", tool_id="T01_PDF_LOADER"),
                DAGStep(step_id="extract", tool_id="T23A_ENTITY_EXTRACTOR", depends_on=["load"])
            ]
        )
        
        # Create executor
        executor = DAGExecutor(registry)
        
        # Validate DAG
        validation = executor.validate_dag(dag)
        assert validation["valid"] == True
        
        print("✅ DAG validation successful")
        return True
    except Exception as e:
        print(f"❌ DAG test failed: {e}")
        return False


def test_category_compatibility():
    """Test category-based compatibility rules"""
    print("\nTesting Category Compatibility...")
    try:
        from unified_data_contract import ToolCategory, can_chain_categories
        
        # Test valid chains
        assert can_chain_categories(ToolCategory.LOADER, ToolCategory.EXTRACTOR) == True
        assert can_chain_categories(ToolCategory.EXTRACTOR, ToolCategory.BUILDER) == True
        assert can_chain_categories(ToolCategory.BUILDER, ToolCategory.ANALYZER) == True
        
        # Test invalid chain
        assert can_chain_categories(ToolCategory.ANALYZER, ToolCategory.LOADER) == False
        
        print("✅ Category compatibility rules working")
        return True
    except Exception as e:
        print(f"❌ Category compatibility test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("UNIFIED TOOL SYSTEM TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("UnifiedData", test_unified_data),
        ("Tool Registry", test_tool_registry),
        ("Tool Execution", test_tool_execution),
        ("DAG Execution", test_dag_execution),
        ("Category Compatibility", test_category_compatibility)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed - Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())