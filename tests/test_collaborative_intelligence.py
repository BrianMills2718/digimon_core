"""
Test suite for Task C.6: Collaborative Intelligence Framework

Tests multi-agent reasoning, conflict resolution, and consensus building
capabilities for collaborative document analysis.
"""

import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import AsyncMock

from src.collaboration.multi_agent_coordinator import MultiAgentCoordinator
from src.collaboration.agent_specializer import AgentSpecializer
from src.collaboration.conflict_resolver import ConflictResolver
from src.collaboration.consensus_builder import ConsensusBuilder


class TestCollaborativeIntelligence:
    """Test suite for collaborative intelligence framework (Task C.6)"""
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for collaborative analysis"""
        return [
            {
                "id": "doc1",
                "content": "The new quantum computing breakthrough promises to revolutionize cryptography.",
                "metadata": {"source": "Science Journal", "year": 2024}
            },
            {
                "id": "doc2",
                "content": "Critics argue quantum computing threats to encryption are overstated.",
                "metadata": {"source": "Tech Review", "year": 2024}
            },
            {
                "id": "doc3",
                "content": "Quantum-resistant algorithms are being developed to counter potential threats.",
                "metadata": {"source": "Security Forum", "year": 2024}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_multi_agent_task_decomposition(self, sample_documents):
        """Test breaking complex tasks across multiple agents"""
        coordinator = MultiAgentCoordinator()
        
        # Complex task: Analyze contradictory viewpoints on quantum computing
        task = {
            "type": "analyze_controversy",
            "topic": "quantum computing impact on cryptography",
            "documents": sample_documents
        }
        
        # Decompose into subtasks
        subtasks = await coordinator.decompose_task(task)
        
        assert len(subtasks) >= 3, "Should create multiple subtasks"
        assert any(st["type"] == "extract_claims" for st in subtasks)
        assert any(st["type"] == "identify_contradictions" for st in subtasks)
        assert any(st["type"] == "synthesize_viewpoints" for st in subtasks)
    
    @pytest.mark.asyncio
    async def test_agent_specialization_routing(self, sample_documents):
        """Test routing subtasks to specialized agents"""
        specializer = AgentSpecializer()
        
        # Initialize specialized agents
        await specializer.initialize_agents(
            agent_types=["entity_extractor", "sentiment_analyzer", "fact_checker"]
        )
        
        # Route tasks to appropriate agents
        entity_task = {"type": "extract_entities", "content": sample_documents[0]["content"]}
        sentiment_task = {"type": "analyze_sentiment", "content": sample_documents[1]["content"]}
        
        entity_agent = await specializer.route_task(entity_task)
        sentiment_agent = await specializer.route_task(sentiment_task)
        
        assert entity_agent.specialization == "entity_extractor"
        assert sentiment_agent.specialization == "sentiment_analyzer"
    
    @pytest.mark.asyncio
    async def test_parallel_agent_coordination(self, sample_documents):
        """Test coordinating multiple agents working in parallel"""
        coordinator = MultiAgentCoordinator()
        
        # Create parallel analysis tasks
        parallel_tasks = [
            {"type": "extract_entities", "doc_id": doc["id"], "content": doc["content"]}
            for doc in sample_documents
        ]
        
        # Execute in parallel
        results = await coordinator.execute_parallel(parallel_tasks, max_workers=3)
        
        assert len(results) == len(sample_documents)
        assert all(r["status"] == "completed" for r in results)
        
        # Verify parallel execution (should be faster than sequential)
        execution_times = [r["execution_time"] for r in results]
        assert max(execution_times) < sum(execution_times) * 0.6  # Parallel speedup
    
    @pytest.mark.asyncio
    async def test_conflict_detection_resolution(self, sample_documents):
        """Test detecting and resolving conflicts between agents"""
        resolver = ConflictResolver()
        
        # Simulate conflicting agent results
        agent_results = [
            {
                "agent_id": "agent1",
                "claim": "Quantum computing will break all encryption",
                "confidence": 0.8,
                "source": "doc1"
            },
            {
                "agent_id": "agent2",
                "claim": "Quantum computing threats are exaggerated",
                "confidence": 0.7,
                "source": "doc2"
            },
            {
                "agent_id": "agent3",
                "claim": "Quantum-resistant algorithms provide protection",
                "confidence": 0.9,
                "source": "doc3"
            }
        ]
        
        # Detect conflicts
        conflicts = await resolver.detect_conflicts(agent_results)
        
        assert len(conflicts) > 0, "Should detect conflicts between agents"
        
        # Resolve conflicts
        resolution = await resolver.resolve_conflicts(conflicts)
        
        assert resolution["strategy"] in ["consensus", "weighted_average", "expert_override"]
        assert "final_claim" in resolution
        assert resolution["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_consensus_building_algorithms(self, sample_documents):
        """Test building consensus from multiple agent opinions"""
        consensus_builder = ConsensusBuilder()
        
        # Multiple agent opinions on same topic
        opinions = [
            {"agent": "agent1", "assessment": "high_risk", "confidence": 0.8},
            {"agent": "agent2", "assessment": "moderate_risk", "confidence": 0.9},
            {"agent": "agent3", "assessment": "high_risk", "confidence": 0.7},
            {"agent": "agent4", "assessment": "low_risk", "confidence": 0.6},
            {"agent": "agent5", "assessment": "moderate_risk", "confidence": 0.85}
        ]
        
        # Build consensus
        consensus = await consensus_builder.build_consensus(
            opinions,
            method="weighted_voting"
        )
        
        assert consensus["final_assessment"] in ["high_risk", "moderate_risk", "low_risk"]
        assert consensus["agreement_score"] > 0.4  # Reasonable agreement given split opinions
        assert "dissenting_opinions" in consensus
    
    @pytest.mark.asyncio
    async def test_agent_confidence_aggregation(self, sample_documents):
        """Test aggregating confidence scores across agents"""
        coordinator = MultiAgentCoordinator()
        
        # Agent results with confidence scores
        agent_scores = [
            {"agent": "entity_agent", "result": "5 entities", "confidence": 0.9},
            {"agent": "sentiment_agent", "result": "negative", "confidence": 0.7},
            {"agent": "fact_agent", "result": "2 facts verified", "confidence": 0.85}
        ]
        
        # Aggregate confidence
        aggregated = await coordinator.aggregate_confidence(agent_scores)
        
        assert aggregated["overall_confidence"] > 0
        assert aggregated["overall_confidence"] <= 1.0
        assert aggregated["method"] in ["average", "weighted", "min", "bayesian"]
        assert "per_agent_contribution" in aggregated
    
    @pytest.mark.asyncio
    async def test_agent_performance_monitoring(self):
        """Test monitoring and optimizing agent performance"""
        coordinator = MultiAgentCoordinator()
        
        # Initialize monitoring
        await coordinator.start_monitoring()
        
        # Simulate agent executions
        for i in range(10):
            await coordinator.record_agent_execution(
                agent_id=f"agent_{i % 3}",
                task_type="analysis",
                execution_time=0.1 * (i % 3 + 1),
                success=i % 4 != 0  # Some failures
            )
        
        # Get performance metrics
        metrics = await coordinator.get_performance_metrics()
        
        assert "agent_stats" in metrics
        assert len(metrics["agent_stats"]) == 3
        
        for agent_id, stats in metrics["agent_stats"].items():
            assert "success_rate" in stats
            assert "avg_execution_time" in stats
            assert "task_count" in stats
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self):
        """Test handling agent failures gracefully"""
        coordinator = MultiAgentCoordinator()
        
        # Configure failure handling
        await coordinator.configure_failure_handling(
            max_retries=3,
            fallback_strategy="reassign"
        )
        
        # Simulate task with failing agent
        task = {"id": "task1", "type": "complex_analysis"}
        
        # First attempt fails
        result = await coordinator.execute_with_recovery(
            task,
            agent_id="unreliable_agent",
            failure_probability=0.8
        )
        
        assert result["status"] in ["completed", "completed_with_fallback"]
        assert result["attempts"] <= 4  # Original + 3 retries
        
        if result["status"] == "completed_with_fallback":
            assert result["fallback_agent"] != "unreliable_agent"
    
    @pytest.mark.asyncio
    async def test_hierarchical_agent_organization(self):
        """Test organizing agents in hierarchies"""
        coordinator = MultiAgentCoordinator()
        
        # Create agent hierarchy
        hierarchy = await coordinator.create_hierarchy({
            "supervisor": {
                "id": "supervisor_1",
                "subordinates": [
                    {"id": "analyst_1", "type": "data_analyst"},
                    {"id": "analyst_2", "type": "data_analyst"},
                    {"id": "reviewer_1", "type": "quality_reviewer"}
                ]
            }
        })
        
        # Delegate task through hierarchy
        task = {"type": "comprehensive_analysis", "complexity": "high"}
        
        result = await coordinator.delegate_hierarchically(task, hierarchy)
        
        assert result["delegated_to"] == "supervisor_1"
        assert len(result["subtask_assignments"]) >= 2
        assert "quality_review" in [a["task_type"] for a in result["subtask_assignments"]]
    
    @pytest.mark.asyncio
    async def test_agent_communication_protocols(self):
        """Test efficient agent communication"""
        coordinator = MultiAgentCoordinator()
        
        # Set up communication channels
        await coordinator.setup_communication(
            protocol="async_message_passing",
            max_message_size=1024
        )
        
        # Test agent-to-agent communication
        message = {
            "from": "agent1",
            "to": "agent2",
            "type": "information_request",
            "content": "Need entity list from doc1"
        }
        
        response = await coordinator.send_message(message)
        
        assert response["status"] == "delivered"
        assert response["latency_ms"] < 100
        
        # Test broadcast
        broadcast = {
            "from": "coordinator",
            "type": "task_update",
            "content": "Priority change"
        }
        
        broadcast_result = await coordinator.broadcast(broadcast)
        
        assert broadcast_result["delivered_to_count"] >= 2
    
    @pytest.mark.asyncio
    async def test_collaborative_learning(self):
        """Test agents learning from each other's successes"""
        coordinator = MultiAgentCoordinator()
        
        # Initialize learning system
        await coordinator.enable_collaborative_learning()
        
        # Agent 1 discovers effective strategy
        await coordinator.record_success(
            agent_id="agent1",
            task_type="entity_extraction",
            strategy="context_window_expansion",
            performance_gain=0.3
        )
        
        # Agent 2 attempts similar task
        recommendation = await coordinator.get_strategy_recommendation(
            agent_id="agent2",
            task_type="entity_extraction"
        )
        
        assert recommendation["suggested_strategy"] == "context_window_expansion"
        assert recommendation["expected_gain"] > 0.2
        assert recommendation["learned_from"] == "agent1"
    
    @pytest.mark.asyncio
    async def test_workload_distribution(self):
        """Test distributing work optimally across agents"""
        coordinator = MultiAgentCoordinator()
        
        # Define agent capacities
        agents = [
            {"id": "fast_agent", "capacity": 10, "speed_multiplier": 2.0},
            {"id": "accurate_agent", "capacity": 5, "accuracy_bonus": 0.2},
            {"id": "balanced_agent", "capacity": 7, "speed_multiplier": 1.5}
        ]
        
        # Tasks to distribute
        tasks = [
            {"id": f"task_{i}", "priority": i % 3, "estimated_effort": 1 + i % 4}
            for i in range(15)
        ]
        
        # Distribute workload
        distribution = await coordinator.distribute_workload(
            tasks=tasks,
            agents=agents,
            optimization_goal="balanced"  # or "speed" or "accuracy"
        )
        
        assert len(distribution) == len(agents)
        
        # Check workload balance
        for agent_work in distribution:
            assigned_effort = sum(t["estimated_effort"] for t in agent_work["tasks"])
            agent = next(a for a in agents if a["id"] == agent_work["agent_id"])
            assert assigned_effort <= agent["capacity"]
    
    @pytest.mark.asyncio
    async def test_collaborative_result_synthesis(self, sample_documents):
        """Test synthesizing results from multiple agents"""
        coordinator = MultiAgentCoordinator()
        
        # Multiple agent results
        agent_results = [
            {
                "agent": "entity_agent",
                "entities": ["quantum computing", "cryptography", "encryption"],
                "confidence": 0.9
            },
            {
                "agent": "sentiment_agent",
                "sentiments": {"doc1": "positive", "doc2": "negative", "doc3": "neutral"},
                "confidence": 0.8
            },
            {
                "agent": "summary_agent",
                "summary": "Documents discuss quantum computing's impact on cryptography with mixed opinions",
                "confidence": 0.85
            }
        ]
        
        # Synthesize comprehensive result
        synthesis = await coordinator.synthesize_results(
            agent_results,
            synthesis_strategy="comprehensive"
        )
        
        assert "unified_summary" in synthesis
        assert "key_entities" in synthesis
        assert "sentiment_overview" in synthesis
        assert synthesis["overall_confidence"] > 0.7
        assert len(synthesis["contributing_agents"]) == 3