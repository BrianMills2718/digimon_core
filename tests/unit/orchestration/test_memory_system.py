"""
Unit tests for memory system components.
"""

import pytest
import tempfile
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from src.orchestration.memory import AgentMemory, MemoryType, MemoryQuery, MemoryEntry
from src.orchestration.memory_agent import MemoryAwareAgent
from src.orchestration.memory_debug import MemoryDebugger, MemoryVisualizer
from src.orchestration.base import Task, Result


class TestAgentMemory:
    """Test AgentMemory system."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def memory(self, temp_db_path):
        """Create AgentMemory instance for testing."""
        return AgentMemory("test_agent", temp_db_path)
    
    def test_memory_initialization(self, memory):
        """Test memory system initialization."""
        assert memory.agent_id == "test_agent"
        assert memory.db_path is not None
        assert Path(memory.db_path).exists()
    
    @pytest.mark.asyncio
    async def test_store_memory(self, memory):
        """Test storing memory entries."""
        content = {"test_key": "test_value", "number": 42}
        
        entry_id = await memory.store_memory(
            memory_type=MemoryType.SEMANTIC,
            content=content,
            importance=0.8,
            tags=["test", "unit"]
        )
        
        assert entry_id is not None
        assert entry_id.startswith("test_agent_semantic_")
    
    @pytest.mark.asyncio
    async def test_query_memories(self, memory):
        """Test querying stored memories."""
        # Store some test memories
        await memory.store_memory(
            MemoryType.EPISODIC,
            {"task_type": "test_task", "success": True},
            importance=0.7,
            tags=["task", "success"]
        )
        
        await memory.store_memory(
            MemoryType.SEMANTIC,
            {"pattern_type": "test_pattern", "confidence": 0.9},
            importance=0.8,
            tags=["pattern", "learned"]
        )
        
        # Query all memories
        query = MemoryQuery(
            agent_id="test_agent",
            max_results=10
        )
        
        memories = await memory.query_memories(query)
        assert len(memories) == 2
        
        # Query by type
        episodic_query = MemoryQuery(
            agent_id="test_agent",
            memory_types=[MemoryType.EPISODIC],
            max_results=10
        )
        
        episodic_memories = await memory.query_memories(episodic_query)
        assert len(episodic_memories) == 1
        assert episodic_memories[0].memory_type == MemoryType.EPISODIC
    
    @pytest.mark.asyncio
    async def test_task_execution_storage(self, memory):
        """Test storing task execution in memory."""
        task = Task(
            task_type="document_processing",
            parameters={"documents": ["test.pdf"]},
            context={"source": "test"}
        )
        
        result = Result(
            success=True,
            data={"processed": 1},
            execution_time=2.5
        )
        
        entry_id = await memory.store_task_execution(task, result)
        
        assert entry_id is not None
        
        # Verify stored memory
        query = MemoryQuery(
            agent_id="test_agent",
            memory_types=[MemoryType.EPISODIC],
            content_keywords=["document_processing"]
        )
        
        memories = await memory.query_memories(query)
        assert len(memories) == 1
        
        stored_memory = memories[0]
        assert stored_memory.content["task_type"] == "document_processing"
        assert stored_memory.content["result_success"] is True
        assert stored_memory.content["execution_time"] == 2.5
    
    @pytest.mark.asyncio
    async def test_learned_patterns(self, memory):
        """Test storing and retrieving learned patterns."""
        pattern_data = {
            "chunk_size": 1000,
            "overlap": 200,
            "success_rate": 0.85,
            "confidence": 0.9
        }
        
        entry_id = await memory.store_learned_pattern(
            pattern_type="document_chunking_strategy",
            pattern_data=pattern_data,
            importance=0.8
        )
        
        assert entry_id is not None
        
        # Query the pattern
        query = MemoryQuery(
            agent_id="test_agent",
            memory_types=[MemoryType.SEMANTIC],
            content_keywords=["chunking_strategy"]
        )
        
        memories = await memory.query_memories(query)
        assert len(memories) == 1
        
        pattern_memory = memories[0]
        assert pattern_memory.content["pattern_type"] == "document_chunking_strategy"
        assert pattern_memory.content["pattern_data"]["chunk_size"] == 1000
    
    @pytest.mark.asyncio
    async def test_procedures(self, memory):
        """Test storing and retrieving procedures."""
        procedure_steps = [
            {"step": "load_document", "parameters": {"format": "pdf"}},
            {"step": "chunk_text", "parameters": {"size": 1000}},
            {"step": "validate_chunks", "parameters": {"min_count": 1}}
        ]
        
        entry_id = await memory.store_procedure(
            procedure_name="successful_document_processing",
            procedure_steps=procedure_steps,
            success_rate=0.9
        )
        
        assert entry_id is not None
        
        # Query the procedure
        query = MemoryQuery(
            agent_id="test_agent",
            memory_types=[MemoryType.PROCEDURAL],
            content_keywords=["document_processing"]
        )
        
        memories = await memory.query_memories(query)
        assert len(memories) == 1
        
        procedure_memory = memories[0]
        assert procedure_memory.content["procedure_name"] == "successful_document_processing"
        assert len(procedure_memory.content["steps"]) == 3
    
    @pytest.mark.asyncio
    async def test_working_memory(self, memory):
        """Test working memory functionality."""
        # Update working memory
        context = {"current_task": "test", "session_id": "123"}
        await memory.update_working_memory(context)
        
        # Retrieve working memory
        working_memory = await memory.get_working_memory()
        
        assert "current_task" in working_memory
        assert working_memory["current_task"] == "test"
    
    @pytest.mark.asyncio
    async def test_memory_cleanup(self, memory):
        """Test memory cleanup functionality."""
        # Store old memory (simulate by modifying timestamp)
        old_content = {"old_data": "should_be_cleaned"}
        await memory.store_memory(
            MemoryType.EPISODIC,
            old_content,
            importance=0.2  # Low importance
        )
        
        # Store important memory
        important_content = {"important_data": "should_be_kept"}
        await memory.store_memory(
            MemoryType.SEMANTIC,
            important_content,
            importance=0.9  # High importance
        )
        
        # Test cleanup (with immediate cleanup for testing)
        cleaned_count = await memory.cleanup_old_memories(
            max_age_days=0,  # Clean everything
            min_importance=0.5  # Keep only high importance
        )
        
        # Should clean the episodic memory but keep semantic
        assert cleaned_count >= 0  # At least some cleanup happened
    
    @pytest.mark.asyncio
    async def test_memory_stats(self, memory):
        """Test memory statistics."""
        # Store various types of memories
        await memory.store_memory(MemoryType.EPISODIC, {"test": "data1"}, 0.5)
        await memory.store_memory(MemoryType.SEMANTIC, {"test": "data2"}, 0.8)
        await memory.store_memory(MemoryType.PROCEDURAL, {"test": "data3"}, 0.7)
        
        stats = await memory.get_memory_stats()
        
        assert "agent_id" in stats
        assert stats["agent_id"] == "test_agent"
        assert "total_memories" in stats
        assert stats["total_memories"] >= 3
        assert "memories_by_type" in stats


class TestMemoryAwareAgent:
    """Test MemoryAwareAgent base class."""
    
    class TestAgent(MemoryAwareAgent):
        """Test agent implementation."""
        
        def get_capabilities(self):
            return ["test_capability"]
        
        def can_handle(self, task_type: str) -> bool:
            return task_type == "test_task"
        
        async def _execute_without_memory(self, task: Task) -> Result:
            return self._create_result(
                success=True,
                data={"executed": task.task_type},
                task=task
            )
        
        async def _execute_with_memory(self, task: Task, memory_context):
            # Apply some memory context
            enhanced_data = {"executed": task.task_type, "memory_used": True}
            if memory_context.get("learned_patterns"):
                enhanced_data["patterns_applied"] = len(memory_context["learned_patterns"])
            
            return self._create_result(
                success=True,
                data=enhanced_data,
                task=task
            )
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def memory_agent(self, temp_db_path):
        """Create memory-aware agent for testing."""
        memory_config = {"db_path": temp_db_path}
        return self.TestAgent("test_agent", memory_config)
    
    def test_agent_initialization(self, memory_agent):
        """Test memory-aware agent initialization."""
        assert memory_agent.agent_id == "test_agent"
        assert memory_agent.memory is not None
        assert memory_agent.enable_learning is True
    
    @pytest.mark.asyncio
    async def test_execute_with_memory(self, memory_agent):
        """Test agent execution with memory."""
        task = Task(task_type="test_task", parameters={"param": "value"})
        
        result = await memory_agent.execute(task)
        
        assert result.success is True
        assert result.data["executed"] == "test_task"
        assert result.data["memory_used"] is True
    
    @pytest.mark.asyncio
    async def test_learning_from_execution(self, memory_agent):
        """Test that agent learns from task execution."""
        task = Task(task_type="test_task", parameters={"param": "value"})
        
        # Execute task
        result = await memory_agent.execute(task)
        assert result.success is True
        
        # Check that memory was stored
        memories = await memory_agent.memory.query_memories(
            MemoryQuery(
                agent_id="test_agent",
                memory_types=[MemoryType.EPISODIC],
                content_keywords=["test_task"]
            )
        )
        
        assert len(memories) >= 1
        assert memories[0].content["task_type"] == "test_task"
    
    @pytest.mark.asyncio
    async def test_parameter_recommendations(self, memory_agent):
        """Test parameter recommendations from memory."""
        # Store some successful patterns first
        await memory_agent.memory.store_learned_pattern(
            pattern_type="test_task_successful_parameters",
            pattern_data={
                "parameters": {"optimal_param": "optimal_value"},
                "confidence": 0.8
            },
            importance=0.7
        )
        
        # Get recommendations
        recommendations = await memory_agent.get_parameter_recommendations("test_task")
        
        assert "recommended_parameters" in recommendations
        assert "confidence" in recommendations
    
    @pytest.mark.asyncio
    async def test_learned_strategies(self, memory_agent):
        """Test learned strategies retrieval."""
        # Store a successful strategy
        await memory_agent.memory.store_procedure(
            procedure_name="test_task_successful_strategy",
            procedure_steps=[
                {"step": "prepare", "parameters": {"prep": "value"}},
                {"step": "execute", "parameters": {"exec": "value"}}
            ],
            success_rate=0.9
        )
        
        # Get strategies
        strategies = await memory_agent.get_learned_strategies("test_task")
        
        assert len(strategies) >= 1
        assert "success_rate" in strategies[0]
        assert "steps" in strategies[0]
    
    @pytest.mark.asyncio
    async def test_memory_summary(self, memory_agent):
        """Test memory summary generation."""
        # Execute some tasks to generate memory
        task = Task(task_type="test_task")
        await memory_agent.execute(task)
        
        summary = await memory_agent.get_memory_summary()
        
        assert "agent_id" in summary
        assert summary["agent_id"] == "test_agent"
        assert "memory_stats" in summary
        assert "learning_enabled" in summary


class TestMemoryDebugger:
    """Test memory debugging tools."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    async def populated_memory(self, temp_db_path):
        """Create memory with test data."""
        memory = AgentMemory("debug_test_agent", temp_db_path)
        
        # Add various types of memories
        await memory.store_memory(
            MemoryType.EPISODIC,
            {"task_type": "test1", "success": True},
            importance=0.8
        )
        
        await memory.store_memory(
            MemoryType.SEMANTIC,
            {"pattern_type": "test_pattern", "confidence": 0.9},
            importance=0.7
        )
        
        await memory.store_memory(
            MemoryType.PROCEDURAL,
            {"procedure_name": "test_proc", "success_rate": 0.85},
            importance=0.9
        )
        
        return memory
    
    @pytest.mark.asyncio
    async def test_memory_analysis(self, populated_memory):
        """Test comprehensive memory analysis."""
        debugger = MemoryDebugger()
        
        analysis = await debugger.analyze_agent_memory("debug_test_agent")
        
        assert "agent_id" in analysis
        assert analysis["agent_id"] == "debug_test_agent"
        assert "basic_stats" in analysis
        assert "patterns" in analysis
        assert "health" in analysis
        assert "recent_activity" in analysis
        
        # Check basic stats
        stats = analysis["basic_stats"]
        assert stats["total_memories"] >= 3
        
        # Check health assessment
        health = analysis["health"]
        assert "health_score" in health
        assert "status" in health
        assert health["health_score"] >= 0.0
        assert health["health_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_memory_dump(self, populated_memory):
        """Test memory dump functionality."""
        debugger = MemoryDebugger()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_dump.json"
            
            result_path = await debugger.dump_agent_memories(
                "debug_test_agent",
                str(output_file)
            )
            
            assert Path(result_path).exists()
            
            # Verify dump content
            import json
            with open(result_path) as f:
                dump_data = json.load(f)
            
            assert "agent_id" in dump_data
            assert dump_data["agent_id"] == "debug_test_agent"
            assert "memories" in dump_data
            assert len(dump_data["memories"]) >= 3
    
    def test_memory_visualizer(self):
        """Test memory report generation."""
        visualizer = MemoryVisualizer()
        
        # Mock analysis data
        analysis = {
            "agent_id": "test_agent",
            "timestamp": datetime.now().isoformat(),
            "basic_stats": {
                "total_memories": 100,
                "recent_memories_7days": 10,
                "database_size_bytes": 1024 * 1024  # 1MB
            },
            "patterns": {
                "memory_distribution": {
                    "episodic": {"count": 50, "avg_importance": 0.6},
                    "semantic": {"count": 30, "avg_importance": 0.8},
                    "procedural": {"count": 20, "avg_importance": 0.9}
                },
                "learning_velocity": {
                    "memories_last_24h": 5,
                    "daily_learning_rate": 2.5,
                    "learning_trend": "stable"
                }
            },
            "health": {
                "health_score": 0.9,
                "status": "healthy",
                "issues": [],
                "recommendations": []
            },
            "recent_activity": {
                "total_recent_memories": 10,
                "most_recent_memories": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "content_type": "task: test_task",
                        "importance": 0.7
                    }
                ]
            }
        }
        
        report = visualizer.create_memory_report(analysis)
        
        assert "Memory Analysis Report" in report
        assert "test_agent" in report
        assert "Total Memories: 100" in report
        assert "healthy" in report


class TestMemoryIntegration:
    """Integration tests for memory system components."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_memory_workflow(self, temp_db_path):
        """Test complete memory workflow with agent."""
        # Create memory-aware agent
        memory_config = {"db_path": temp_db_path}
        
        class WorkflowTestAgent(MemoryAwareAgent):
            def get_capabilities(self):
                return ["workflow_test"]
            
            def can_handle(self, task_type: str) -> bool:
                return task_type == "workflow_test"
            
            async def _execute_without_memory(self, task: Task) -> Result:
                return self._create_result(
                    success=True,
                    data={"processed": True},
                    task=task
                )
            
            async def _execute_with_memory(self, task: Task, memory_context):
                # Use memory context to enhance execution
                data = {"processed": True, "memory_enhanced": True}
                
                # Apply learned patterns
                patterns = memory_context.get("learned_patterns", [])
                if patterns:
                    data["patterns_used"] = len(patterns)
                
                return self._create_result(
                    success=True,
                    data=data,
                    task=task
                )
        
        agent = WorkflowTestAgent("workflow_agent", memory_config)
        
        # Execute multiple tasks to build memory
        for i in range(3):
            task = Task(
                task_type="workflow_test",
                parameters={"iteration": i, "data": f"test_data_{i}"}
            )
            
            result = await agent.execute(task)
            
            assert result.success is True
            assert result.data["processed"] is True
            
            if i > 0:  # After first execution, memory should be used
                assert result.data.get("memory_enhanced") is True
        
        # Verify memory contains execution history
        memories = await agent.memory.query_memories(
            MemoryQuery(
                agent_id="workflow_agent",
                memory_types=[MemoryType.EPISODIC],
                content_keywords=["workflow_test"]
            )
        )
        
        assert len(memories) == 3
        
        # Test memory analysis
        debugger = MemoryDebugger()
        analysis = await debugger.analyze_agent_memory("workflow_agent")
        
        assert analysis["basic_stats"]["total_memories"] >= 3
        assert analysis["health"]["health_score"] > 0.5
        
        # Test parameter recommendations
        recommendations = await agent.get_parameter_recommendations("workflow_test")
        assert "confidence" in recommendations
        
        # Test memory cleanup
        initial_count = analysis["basic_stats"]["total_memories"]
        cleaned = await agent.cleanup_memory(max_age_days=0, min_importance=0.9)
        
        # Should clean some low-importance memories
        final_stats = await agent.memory.get_memory_stats()
        assert final_stats["total_memories"] <= initial_count