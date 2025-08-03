#!/usr/bin/env python3
"""
Test script for KGAS Agent Orchestration System.

This demonstrates how to use the flexible orchestration system
with existing KGAS MCP tools.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestration import create_orchestrator, initialize_orchestration_system


async def test_basic_orchestration():
    """Test basic orchestration functionality."""
    print("\n" + "="*60)
    print("🚀 KGAS Agent Orchestration Test")
    print("="*60)
    
    try:
        # Initialize orchestration system
        print("\n📋 Initializing orchestration system...")
        orchestrator = await initialize_orchestration_system(
            strategy="simple",
            config_path="config/orchestration/default_config.json"
        )
        
        # Check status
        status = orchestrator.get_status()
        print(f"✅ Orchestrator initialized: {status['orchestrator_type']}")
        print(f"   Agents available: {', '.join(status['agents_available'])}")
        print(f"   MCP tools: {status.get('mcp_adapter', {}).get('total_tools', 0)} tools available")
        
        # Test with a simple request
        print("\n📝 Testing with sample request...")
        test_request = "Analyze the key concepts and relationships in the provided documents"
        
        # For this test, we'll simulate document paths
        # In real usage, these would come from user input
        context = {
            "document_paths": ["test_data/sample.pdf"]  # Adjust to your test files
        }
        
        print(f"   Request: '{test_request}'")
        print(f"   Context: {context}")
        
        # Process request
        print("\n🔄 Processing request through orchestration pipeline...")
        result = await orchestrator.process_request(test_request, context)
        
        # Display results
        print("\n📊 Orchestration Results:")
        print(f"   Success: {result.success}")
        print(f"   Execution time: {result.execution_time:.2f} seconds")
        
        if result.success:
            data = result.data
            completed_steps = data.get("completed_steps", [])
            
            print(f"\n   Completed Steps ({len(completed_steps)}):")
            for step in completed_steps:
                status_emoji = "✅" if step["success"] else "❌"
                print(f"     {status_emoji} Step {step['step']}: {step['agent']}.{step['task_type']}")
            
            # Show final insights
            final_insights = data.get("final_insights", {})
            if final_insights:
                print("\n   Final Insights:")
                
                # Statistics
                stats = final_insights.get("statistics", {})
                if stats:
                    print("     Statistics:")
                    for key, value in stats.items():
                        print(f"       - {key}: {value}")
                
                # Key findings
                findings = final_insights.get("key_findings", [])
                if findings:
                    print(f"     Key Findings ({len(findings)}):")
                    for i, finding in enumerate(findings[:5]):  # Show top 5
                        print(f"       {i+1}. {finding}")
                    if len(findings) > 5:
                        print(f"       ... and {len(findings) - 5} more")
        else:
            print(f"   Error: {result.error}")
            if result.data:
                print(f"   Partial results available: {result.data.get('completed_steps', [])}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        await orchestrator.cleanup()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_different_workflows():
    """Test different workflow configurations."""
    print("\n" + "="*60)
    print("🔄 Testing Different Workflows")
    print("="*60)
    
    try:
        orchestrator = await initialize_orchestration_system()
        
        # Get available workflows
        workflows = orchestrator.get_supported_workflows()
        print(f"\n📋 Available workflows: {', '.join(workflows)}")
        
        # Test quick analysis workflow
        print("\n🚀 Testing 'quick_analysis' workflow...")
        result = await orchestrator.process_request(
            "quick_analysis: Extract key information",
            {"document_paths": ["test_data/sample.txt"]}
        )
        print(f"   Result: {'✅ Success' if result.success else '❌ Failed'}")
        
        await orchestrator.cleanup()
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        return False
    
    return True


async def test_pivot_flexibility():
    """Demonstrate how easy it is to pivot to different strategies."""
    print("\n" + "="*60)
    print("🔀 Testing Pivot Flexibility")
    print("="*60)
    
    strategies = ["simple", "simple_sequential", "sequential"]
    
    for strategy in strategies:
        try:
            print(f"\n📋 Creating orchestrator with strategy: '{strategy}'")
            orchestrator = create_orchestrator(strategy)
            print(f"✅ Created: {orchestrator.__class__.__name__}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Show how to add new strategies
    print("\n💡 To add new orchestration strategies:")
    print("   1. Create new orchestrator class inheriting from Orchestrator")
    print("   2. Register it: register_orchestrator('name', YourOrchestrator)")
    print("   3. Use it: orchestrator = create_orchestrator('name')")
    print("\n   No other code changes needed! 🎉")


async def main():
    """Main test function."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Reduce noise from specific loggers
    logging.getLogger("src.mcp_tools").setLevel(logging.WARNING)
    logging.getLogger("src.core").setLevel(logging.WARNING)
    
    print("\n🎯 KGAS Agent Orchestration System Test Suite")
    print("="*70)
    print("Testing flexible, pivot-ready agent orchestration...")
    print("="*70)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic orchestration
    if await test_basic_orchestration():
        tests_passed += 1
    
    # Test 2: Different workflows
    if await test_different_workflows():
        tests_passed += 1
    
    # Test 3: Pivot flexibility
    if await test_pivot_flexibility():
        tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 Test Summary: {tests_passed}/{total_tests} tests passed")
    print("="*60)
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The orchestration system is working correctly.")
        print("\n✅ Key achievements:")
        print("   - Flexible agent orchestration implemented")
        print("   - MCP tool integration working")
        print("   - Configuration-driven workflows")
        print("   - Easy pivoting to new strategies")
        print("\n🚀 Ready for production use and future enhancements!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 Common issues:")
        print("   - Missing test documents in test_data/")
        print("   - MCP tools not properly initialized")
        print("   - Neo4j or spaCy dependencies not installed")


if __name__ == "__main__":
    asyncio.run(main())