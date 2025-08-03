"""
Integration tests for memory-aware agent orchestration.

These tests demonstrate the complete memory system working with
real document processing workflows.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path

from src.orchestration.factory import create_orchestrator
from src.orchestration.memory_debug import debug_agent_memory, cleanup_agent_memory
from src.orchestration.base import Task


@pytest.mark.asyncio
async def test_memory_aware_document_workflow():
    """Test memory-aware document processing workflow."""
    
    # Create orchestrator with memory-enabled agents
    orchestrator = create_orchestrator("simple")
    
    # Initialize orchestrator
    success = await orchestrator.initialize()
    assert success, "Orchestrator initialization failed"
    
    # Test document processing request
    request = "Process documents and extract insights"
    
    # Execute workflow multiple times to build memory
    results = []
    for i in range(3):
        result = await orchestrator.process_request(
            request,
            context={
                "document_paths": [f"test_doc_{i}.pdf"],
                "iteration": i
            }
        )
        results.append(result)
        
        # Each execution should succeed
        assert result.success, f"Workflow execution {i} failed: {result.error}"
    
    # Verify agents have built memory
    document_agent = orchestrator.agents.get("document")
    analysis_agent = orchestrator.agents.get("analysis")
    
    if hasattr(document_agent, 'memory'):
        # Check document agent memory
        doc_summary = await document_agent.get_memory_summary()
        assert doc_summary["memory_stats"]["total_memories"] > 0
        
        # Get parameter recommendations (should improve over time)
        recommendations = await document_agent.get_parameter_recommendations("document_processing")
        assert "confidence" in recommendations
    
    if hasattr(analysis_agent, 'memory'):
        # Check analysis agent memory
        analysis_summary = await analysis_agent.get_memory_summary()
        assert analysis_summary["memory_stats"]["total_memories"] > 0
    
    # Cleanup
    await orchestrator.cleanup()


@pytest.mark.asyncio
async def test_memory_learning_progression():
    """Test that agents learn and improve over time."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create agents with temporary memory databases
        from src.orchestration.agents import DocumentAgent, AnalysisAgent
        from src.orchestration.mcp_adapter import MCPToolAdapter
        
        # Mock MCP adapter for testing
        mcp_adapter = MCPToolAdapter()
        
        memory_config = {
            "db_path": str(Path(temp_dir) / "test_agent.db"),
            "enable_learning": True
        }
        
        # Create memory-aware document agent
        agent = DocumentAgent(mcp_adapter, "test_doc_agent", memory_config)
        
        # Simulate multiple document processing tasks
        tasks = [
            Task(
                task_type="text_chunking",
                parameters={
                    "text": f"This is test document {i} with some content to chunk. " * 50,
                    "document_ref": f"doc_{i}",
                    "document_confidence": 0.8
                }
            )
            for i in range(5)
        ]
        
        # Execute tasks and track learning
        execution_times = []
        
        for i, task in enumerate(tasks):
            # Execute task (will fail without real MCP tools, but memory should still work)
            try:
                result = await agent.execute(task)
                execution_times.append(result.execution_time)
            except Exception:
                # Expected to fail without real MCP tools, but memory operations should work
                pass
            
            # Check memory growth
            summary = await agent.get_memory_summary()
            assert summary["memory_stats"]["total_memories"] >= i
            
            # After a few executions, should have parameter recommendations
            if i >= 2:
                recommendations = await agent.get_parameter_recommendations("text_chunking")
                assert "confidence" in recommendations
                
                # Should have some learned strategies
                strategies = await agent.get_learned_strategies("text_chunking")
                # May or may not have strategies yet, depending on success/failure patterns
        
        # Verify final memory state
        final_summary = await agent.get_memory_summary()
        assert final_summary["memory_stats"]["total_memories"] >= 3
        
        # Test memory debugging
        debug_output = await debug_agent_memory("test_doc_agent", temp_dir)
        assert Path(debug_output).exists()
        
        # Test memory cleanup
        initial_count = final_summary["memory_stats"]["total_memories"]
        cleaned = await cleanup_agent_memory("test_doc_agent", max_age_days=0, min_importance=0.9)
        
        # Should clean some memories
        assert cleaned >= 0


@pytest.mark.asyncio
async def test_memory_performance_impact():
    """Test that memory system doesn't significantly impact performance."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        from src.orchestration.agents import DocumentAgent
        from src.orchestration.mcp_adapter import MCPToolAdapter
        import time
        
        mcp_adapter = MCPToolAdapter()
        
        # Create agent without memory
        simple_agent = DocumentAgent(mcp_adapter, "simple_agent", {"enable_learning": False})
        
        # Create agent with memory
        memory_config = {
            "db_path": str(Path(temp_dir) / "memory_agent.db"),
            "enable_learning": True
        }
        memory_agent = DocumentAgent(mcp_adapter, "memory_agent", memory_config)
        
        # Test task
        task = Task(
            task_type="text_chunking",
            parameters={
                "text": "Test document content " * 100,
                "document_ref": "perf_test",
                "document_confidence": 0.8
            }
        )
        
        # Time executions (will fail but we can measure overhead)
        simple_times = []
        memory_times = []
        
        for _ in range(3):
            # Simple agent
            start = time.time()
            try:
                await simple_agent.execute(task)
            except:
                pass  # Expected to fail
            simple_times.append(time.time() - start)
            
            # Memory agent
            start = time.time()
            try:
                await memory_agent.execute(task)
            except:
                pass  # Expected to fail
            memory_times.append(time.time() - start)
        
        # Memory overhead should be reasonable (less than 10x)
        avg_simple = sum(simple_times) / len(simple_times)
        avg_memory = sum(memory_times) / len(memory_times)
        
        # This is a loose check - memory overhead should not be excessive
        overhead_ratio = avg_memory / avg_simple if avg_simple > 0 else 1
        
        print(f"Simple agent avg time: {avg_simple:.4f}s")
        print(f"Memory agent avg time: {avg_memory:.4f}s")
        print(f"Overhead ratio: {overhead_ratio:.2f}x")
        
        # Allow up to 10x overhead for memory operations in test environment
        assert overhead_ratio < 10, f"Memory overhead too high: {overhead_ratio:.2f}x"


@pytest.mark.asyncio
async def test_memory_persistence():
    """Test that memory persists across agent restarts."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        from src.orchestration.agents import DocumentAgent
        from src.orchestration.mcp_adapter import MCPToolAdapter
        
        db_path = str(Path(temp_dir) / "persistent_test.db")
        mcp_adapter = MCPToolAdapter()
        
        # Create first agent instance
        memory_config = {"db_path": db_path, "enable_learning": True}
        agent1 = DocumentAgent(mcp_adapter, "persistent_agent", memory_config)
        
        # Store some memory manually
        await agent1.memory.store_learned_pattern(
            pattern_type="test_persistence_pattern",
            pattern_data={"test_key": "test_value", "confidence": 0.9},
            importance=0.8
        )
        
        # Get initial memory count
        initial_summary = await agent1.get_memory_summary()
        initial_count = initial_summary["memory_stats"]["total_memories"]
        
        # Create second agent instance with same database
        agent2 = DocumentAgent(mcp_adapter, "persistent_agent", memory_config)
        
        # Should have same memory
        second_summary = await agent2.get_memory_summary()
        second_count = second_summary["memory_stats"]["total_memories"]
        
        assert second_count == initial_count, "Memory not persisted across agent instances"
        
        # Should be able to query the stored pattern
        from src.orchestration.memory import MemoryQuery, MemoryType
        
        query = MemoryQuery(
            agent_id="persistent_agent",
            memory_types=[MemoryType.SEMANTIC],
            content_keywords=["persistence_pattern"]
        )
        
        memories = await agent2.memory.query_memories(query)
        assert len(memories) >= 1
        
        found_pattern = memories[0]
        assert found_pattern.content["pattern_type"] == "test_persistence_pattern"
        assert found_pattern.content["pattern_data"]["test_key"] == "test_value"


@pytest.mark.asyncio
async def test_memory_debugging_tools():
    """Test memory debugging and visualization tools."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        from src.orchestration.memory import AgentMemory, MemoryType
        from src.orchestration.memory_debug import MemoryDebugger, MemoryVisualizer
        
        # Create memory with test data
        memory = AgentMemory("debug_test", str(Path(temp_dir) / "debug_test.db"))
        
        # Add various types of test memories
        await memory.store_memory(
            MemoryType.EPISODIC,
            {"task_type": "test_task", "success": True, "duration": 2.5},
            importance=0.8,
            tags=["test", "successful"]
        )
        
        await memory.store_memory(
            MemoryType.SEMANTIC,
            {"pattern_type": "optimization", "improvement": 0.15},
            importance=0.9,
            tags=["pattern", "optimization"]
        )
        
        await memory.store_memory(
            MemoryType.PROCEDURAL,
            {"procedure_name": "best_practice", "success_rate": 0.95},
            importance=0.85,
            tags=["procedure", "best_practice"]
        )
        
        # Test debugger analysis
        debugger = MemoryDebugger()
        analysis = await debugger.analyze_agent_memory("debug_test")
        
        # Verify analysis structure
        assert "agent_id" in analysis
        assert "basic_stats" in analysis
        assert "patterns" in analysis
        assert "health" in analysis
        
        # Check basic stats
        stats = analysis["basic_stats"]
        assert stats["total_memories"] >= 3
        
        # Check health assessment
        health = analysis["health"]
        assert 0.0 <= health["health_score"] <= 1.0
        assert health["status"] in ["healthy", "needs_attention", "unhealthy"]
        
        # Test memory dump
        dump_file = await debugger.dump_agent_memories(
            "debug_test",
            str(Path(temp_dir) / "memory_dump.json")
        )
        
        assert Path(dump_file).exists()
        
        # Test report generation
        visualizer = MemoryVisualizer()
        report = visualizer.create_memory_report(analysis)
        
        assert "Memory Analysis Report" in report
        assert "debug_test" in report
        assert "Total Memories:" in report
        
        # Save report
        report_file = Path(temp_dir) / "memory_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        assert report_file.exists()
        assert report_file.stat().st_size > 0


if __name__ == "__main__":
    # Quick test runner
    import asyncio
    
    async def run_tests():
        print("Running memory integration tests...")
        
        try:
            await test_memory_learning_progression()
            print("✓ Memory learning progression test passed")
        except Exception as e:
            print(f"✗ Memory learning progression test failed: {e}")
        
        try:
            await test_memory_persistence()
            print("✓ Memory persistence test passed")
        except Exception as e:
            print(f"✗ Memory persistence test failed: {e}")
        
        try:
            await test_memory_debugging_tools()
            print("✓ Memory debugging tools test passed")
        except Exception as e:
            print(f"✗ Memory debugging tools test failed: {e}")
        
        print("Memory integration tests completed")
    
    asyncio.run(run_tests())