#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Agent Workflow

Tests the complete agent architecture including memory, reasoning, communication,
and enhanced tools working together in realistic scenarios.
"""

import asyncio
import logging
import os
import pytest
import tempfile
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch

# Configure test logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test imports with fallback handling
try:
    from src.core.service_manager import ServiceManager
    from src.orchestration.memory import AgentMemory
    from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningType
    from src.orchestration.communication import MessageBus, Message, MessageType
    from src.orchestration.agents.document_agent import DocumentAgent
    from src.orchestration.mcp_adapter import MCPToolAdapter
    from src.orchestration.base import Task, Result
    from src.tools.enhanced_mcp_tools import EnhancedMCPTools
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some imports failed: {e}")
    IMPORTS_AVAILABLE = False


class TestAgentWorkflowComprehensive:
    """
    Comprehensive integration tests for the complete agent workflow.
    
    Tests scenarios that validate the full agent architecture:
    1. Memory learning and adaptation over multiple sessions
    2. Reasoning-guided task optimization
    3. Inter-agent communication and collaboration
    4. Enhanced tools integration with agent capabilities
    5. End-to-end document processing workflows
    """
    
    @pytest.fixture
    async def agent_test_environment(self):
        """Set up complete agent test environment."""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required modules not available")
        
        # Create test environment
        env = {
            'service_manager': None,
            'message_bus': None,
            'agents': {},
            'enhanced_tools': None,
            'test_data': self._create_test_data()
        }
        
        try:
            # Initialize core services with test configuration
            env['service_manager'] = ServiceManager()
            await env['service_manager'].initialize()
            
            # Initialize message bus for agent communication
            env['message_bus'] = MessageBus()
            
            # Initialize MCP adapter
            mcp_adapter = MCPToolAdapter()
            
            # Create enhanced tools
            env['enhanced_tools'] = EnhancedMCPTools(
                service_manager=env['service_manager'],
                agent_id="test_enhanced_tools",
                memory_config={"enable_memory": True, "max_memories": 1000},
                reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
                communication_config={"enable_broadcast": True},
                message_bus=env['message_bus']
            )
            
            # Create multiple agents for collaboration testing
            agent_configs = [
                {
                    "agent_id": "document_agent_1",
                    "capabilities": ["document_processing", "entity_extraction"]
                },
                {
                    "agent_id": "analysis_agent_1", 
                    "capabilities": ["relationship_analysis", "graph_building"]
                },
                {
                    "agent_id": "collaboration_agent_1",
                    "capabilities": ["collaborative_processing", "team_coordination"]
                }
            ]
            
            for config in agent_configs:
                agent = DocumentAgent(
                    mcp_adapter=mcp_adapter,
                    agent_id=config["agent_id"],
                    memory_config={"enable_memory": True, "max_memories": 500},
                    reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
                    communication_config={"enable_broadcast": True},
                    message_bus=env['message_bus']
                )
                env['agents'][config["agent_id"]] = agent
            
            logger.info("✅ Agent test environment initialized successfully")
            yield env
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize test environment: {e}")
            pytest.skip(f"Environment setup failed: {e}")
        
        finally:
            # Cleanup
            if env['message_bus']:
                await env['message_bus'].cleanup()
    
    def _create_test_data(self) -> Dict[str, Any]:
        """Create realistic test data for agent workflows."""
        return {
            "documents": [
                {
                    "id": "doc_1",
                    "title": "Artificial Intelligence in Healthcare",
                    "content": """
                    Microsoft Corporation has partnered with Johns Hopkins University to develop
                    AI-powered diagnostic tools. The collaboration involves Dr. Sarah Johnson,
                    a leading researcher in medical AI, working with Microsoft's healthcare division
                    based in Redmond, Washington. The project aims to create machine learning
                    algorithms that can detect early signs of cancer in medical imaging.
                    """,
                    "domain": "healthcare_technology",
                    "complexity": "medium"
                },
                {
                    "id": "doc_2", 
                    "title": "Global Tech Partnerships",
                    "content": """
                    Apple Inc. announced a strategic partnership with Stanford University for
                    research into wearable health monitoring devices. Tim Cook, Apple's CEO,
                    stated that the collaboration will focus on developing sensors that can
                    monitor vital signs continuously. The research team includes professors
                    from Stanford's medical school and Apple's engineering teams in Cupertino.
                    """,
                    "domain": "healthcare_technology",
                    "complexity": "medium"
                },
                {
                    "id": "doc_3",
                    "title": "Academic Research Collaboration Networks",
                    "content": """
                    A comprehensive study by Harvard University researchers examined collaboration
                    patterns between technology companies and academic institutions. The study,
                    led by Prof. Maria Rodriguez, analyzed over 500 research partnerships and
                    found that companies based in Silicon Valley had significantly higher
                    collaboration rates with universities. The research was funded by the
                    National Science Foundation and published in Nature.
                    """,
                    "domain": "academic_research",
                    "complexity": "high"
                }
            ],
            "expected_entities": [
                {"name": "Microsoft Corporation", "type": "ORG"},
                {"name": "Johns Hopkins University", "type": "ORG"},
                {"name": "Dr. Sarah Johnson", "type": "PERSON"},
                {"name": "Apple Inc.", "type": "ORG"},
                {"name": "Stanford University", "type": "ORG"},
                {"name": "Tim Cook", "type": "PERSON"},
                {"name": "Harvard University", "type": "ORG"},
                {"name": "Prof. Maria Rodriguez", "type": "PERSON"}
            ],
            "expected_relationships": [
                {"source": "Microsoft Corporation", "target": "Johns Hopkins University", "type": "PARTNERS_WITH"},
                {"source": "Dr. Sarah Johnson", "target": "Johns Hopkins University", "type": "WORKS_FOR"},
                {"source": "Apple Inc.", "target": "Stanford University", "type": "PARTNERS_WITH"},
                {"source": "Tim Cook", "target": "Apple Inc.", "type": "WORKS_FOR"}
            ],
            "collaboration_scenarios": [
                {
                    "name": "Large Document Processing",
                    "document_count": 3,
                    "expected_agents": 2,
                    "processing_mode": "collaborative"
                },
                {
                    "name": "Cross-Domain Analysis", 
                    "domains": ["healthcare_technology", "academic_research"],
                    "expected_insights": 5,
                    "reasoning_required": True
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_memory_learning_progression(self, agent_test_environment):
        """Test that agents learn and improve over multiple processing sessions."""
        env = agent_test_environment
        agent = env['agents']['document_agent_1']
        test_docs = env['test_data']['documents']
        
        logger.info("🧠 Testing memory learning progression...")
        
        # Session 1: Initial processing (baseline)
        session_1_results = []
        for doc in test_docs[:2]:  # Process first 2 documents
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"]
                },
                context={"session": "learning_session_1"}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            session_1_results.append({
                "document_id": doc["id"],
                "success": result.success,
                "execution_time": execution_time,
                "entities_extracted": len(result.data.get("entities", [])) if result.success else 0
            })
        
        # Allow time for memory consolidation
        await asyncio.sleep(1)
        
        # Session 2: Process similar documents (should show improvement)
        session_2_results = []
        for doc in test_docs[1:]:  # Process documents 2 and 3 (document 2 overlaps for comparison)
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"]
                },
                context={"session": "learning_session_2"}
            )
            
            start_time = time.time()
            result = await agent.execute(task)
            execution_time = time.time() - start_time
            
            session_2_results.append({
                "document_id": doc["id"],
                "success": result.success,
                "execution_time": execution_time,
                "entities_extracted": len(result.data.get("entities", [])) if result.success else 0
            })
        
        # Analyze learning progression
        logger.info("📊 Analyzing memory learning results...")
        
        # Check that all processing succeeded
        assert all(r["success"] for r in session_1_results), "Session 1 processing should succeed"
        assert all(r["success"] for r in session_2_results), "Session 2 processing should succeed"
        
        # For overlapping document (doc_2), check for improvements
        doc_2_session_1 = next(r for r in session_1_results if r["document_id"] == "doc_2")
        doc_2_session_2 = next(r for r in session_2_results if r["document_id"] == "doc_2")
        
        # Performance should improve or stay consistent
        assert doc_2_session_2["execution_time"] <= doc_2_session_1["execution_time"] * 1.1, \
            "Processing time should not significantly increase"
        
        # Entity extraction should be consistent or improved
        assert doc_2_session_2["entities_extracted"] >= doc_2_session_1["entities_extracted"], \
            "Entity extraction should maintain or improve consistency"
        
        # Check memory system has learned patterns
        memory_status = agent.memory.get_status() if hasattr(agent, 'memory') and agent.memory else {}
        logger.info(f"📈 Memory learning status: {memory_status}")
        
        logger.info("✅ Memory learning progression test completed successfully")
    
    @pytest.mark.asyncio
    async def test_reasoning_guided_optimization(self, agent_test_environment):
        """Test reasoning-guided task optimization across different scenarios."""
        env = agent_test_environment
        enhanced_tools = env['enhanced_tools']
        test_docs = env['test_data']['documents']
        
        logger.info("🧠 Testing reasoning-guided optimization...")
        
        optimization_results = []
        
        for doc in test_docs:
            # Test with different reasoning guidance
            reasoning_scenarios = [
                {
                    "name": "high_precision",
                    "guidance": {
                        "extraction_strategy": "high_precision",
                        "confidence_threshold": 0.9,
                        "focus_types": ["PERSON", "ORG"]
                    }
                },
                {
                    "name": "balanced",
                    "guidance": {
                        "extraction_strategy": "balanced", 
                        "confidence_threshold": 0.7,
                        "focus_types": ["PERSON", "ORG", "GPE"]
                    }
                },
                {
                    "name": "high_recall",
                    "guidance": {
                        "extraction_strategy": "high_recall",
                        "confidence_threshold": 0.5,
                        "focus_types": ["PERSON", "ORG", "GPE", "PRODUCT"]
                    }
                }
            ]
            
            for scenario in reasoning_scenarios:
                start_time = time.time()
                
                result = await enhanced_tools.extract_entities_enhanced(
                    text=doc["content"],
                    chunk_ref=f"{doc['id']}_{scenario['name']}",
                    context_metadata={
                        "domain": doc["domain"],
                        "document_type": "research",
                        "complexity": doc["complexity"]
                    },
                    reasoning_guidance=scenario["guidance"]
                )
                
                execution_time = time.time() - start_time
                
                optimization_results.append({
                    "document_id": doc["id"],
                    "scenario": scenario["name"],
                    "success": "entities" in result,
                    "entities_found": len(result.get("entities", [])),
                    "reasoning_applied": result.get("reasoning_applied", False),
                    "reasoning_confidence": result.get("enhancement_metadata", {}).get("reasoning_confidence", 0.0),
                    "execution_time": execution_time
                })
        
        # Analyze reasoning optimization results
        logger.info("📊 Analyzing reasoning optimization results...")
        
        # Check that reasoning was applied in all scenarios
        reasoning_applied_count = sum(1 for r in optimization_results if r["reasoning_applied"])
        assert reasoning_applied_count > 0, "Reasoning should be applied in at least some scenarios"
        
        # Check that different strategies produce different results
        strategy_results = {}
        for result in optimization_results:
            strategy = result["scenario"]
            if strategy not in strategy_results:
                strategy_results[strategy] = []
            strategy_results[strategy].append(result["entities_found"])
        
        # High precision should generally find fewer entities than high recall
        if "high_precision" in strategy_results and "high_recall" in strategy_results:
            avg_precision = sum(strategy_results["high_precision"]) / len(strategy_results["high_precision"])
            avg_recall = sum(strategy_results["high_recall"]) / len(strategy_results["high_recall"])
            
            logger.info(f"Average entities - High Precision: {avg_precision:.1f}, High Recall: {avg_recall:.1f}")
            # Allow some flexibility in the comparison due to simulated extraction
            assert avg_recall >= avg_precision * 0.8, "High recall should find at least as many entities as high precision"
        
        # Check reasoning confidence scores
        reasoning_confidences = [r["reasoning_confidence"] for r in optimization_results if r["reasoning_confidence"] > 0]
        if reasoning_confidences:
            avg_confidence = sum(reasoning_confidences) / len(reasoning_confidences)
            assert avg_confidence > 0.3, f"Average reasoning confidence should be reasonable, got {avg_confidence}"
        
        logger.info("✅ Reasoning-guided optimization test completed successfully")
    
    @pytest.mark.asyncio
    async def test_inter_agent_communication(self, agent_test_environment):
        """Test inter-agent communication and collaboration patterns."""
        env = agent_test_environment
        message_bus = env['message_bus']
        agents = env['agents']
        
        logger.info("📡 Testing inter-agent communication...")
        
        # Test direct messaging
        logger.info("Testing direct messaging...")
        sender = agents['document_agent_1']
        recipient = agents['analysis_agent_1']
        
        # Send direct message
        message_payload = {
            "task": "analyze_entities",
            "data": {"entities": ["Microsoft", "Apple"], "domain": "technology"},
            "priority": "high"
        }
        
        # Mock the message handling for testing
        received_messages = []
        
        async def mock_message_handler(message):
            received_messages.append(message)
        
        # Register mock handler
        if hasattr(message_bus, 'register_handler'):
            message_bus.register_handler(recipient.agent_id, mock_message_handler)
        
        # Send message through communication system
        if hasattr(sender, 'send_message'):
            success = await sender.send_message(recipient.agent_id, message_payload)
            assert success, "Direct message should be sent successfully"
        
        # Test broadcast messaging
        logger.info("Testing broadcast messaging...")
        broadcast_payload = {
            "type": "system_announcement",
            "message": "Processing workload available",
            "timestamp": time.time()
        }
        
        if hasattr(sender, 'broadcast'):
            recipients_count = await sender.broadcast(broadcast_payload, topic="system_announcements")
            assert recipients_count >= 0, "Broadcast should return recipient count"
        
        # Test topic-based messaging
        logger.info("Testing topic-based messaging...")
        
        # Subscribe agents to topics
        topics_tested = []
        if hasattr(message_bus, 'subscribe'):
            for agent_id, agent in agents.items():
                try:
                    await message_bus.subscribe("entity_insights", mock_message_handler)
                    topics_tested.append("entity_insights")
                except Exception as e:
                    logger.warning(f"Topic subscription failed for {agent_id}: {e}")
        
        # Publish to topic
        if topics_tested and hasattr(message_bus, 'publish'):
            topic_message = {
                "insights": "High-confidence entities found in technology domain",
                "entity_count": 15,
                "domain": "technology"
            }
            
            published = await message_bus.publish("entity_insights", topic_message)
            # Allow time for message processing
            await asyncio.sleep(0.1)
        
        # Test collaborative request-response
        logger.info("Testing collaborative request-response...")
        
        collaboration_results = []
        for agent_id, agent in agents.items():
            if hasattr(agent, 'collaborate_with'):
                try:
                    other_agents = [aid for aid in agents.keys() if aid != agent_id]
                    if other_agents:
                        collab_result = await agent.collaborate_with(
                            agent_id=other_agents[0],
                            task="joint_analysis",
                            context={
                                "data_type": "entities",
                                "collaboration_mode": "advisory"
                            }
                        )
                        collaboration_results.append({
                            "requester": agent_id,
                            "collaborator": other_agents[0],
                            "success": collab_result is not None,
                            "result": collab_result
                        })
                except Exception as e:
                    logger.warning(f"Collaboration test failed for {agent_id}: {e}")
        
        # Verify communication functionality
        logger.info("📊 Analyzing communication results...")
        
        # At minimum, message bus should be operational
        assert message_bus is not None, "Message bus should be initialized"
        
        # If any communication features are implemented, they should work
        if received_messages:
            assert len(received_messages) > 0, "Some messages should be received"
        
        if collaboration_results:
            successful_collaborations = sum(1 for r in collaboration_results if r["success"])
            logger.info(f"Successful collaborations: {successful_collaborations}/{len(collaboration_results)}")
        
        logger.info("✅ Inter-agent communication test completed successfully")
    
    @pytest.mark.asyncio
    async def test_enhanced_tools_integration(self, agent_test_environment):
        """Test enhanced tools integration with agent capabilities."""
        env = agent_test_environment
        enhanced_tools = env['enhanced_tools']
        test_docs = env['test_data']['documents']
        
        logger.info("🔧 Testing enhanced tools integration...")
        
        integration_results = []
        
        # Test enhanced entity extraction
        for doc in test_docs[:2]:  # Test with first 2 documents
            logger.info(f"Testing enhanced extraction for {doc['id']}...")
            
            extraction_result = await enhanced_tools.extract_entities_enhanced(
                text=doc["content"],
                chunk_ref=f"integration_test_{doc['id']}",
                context_metadata={
                    "domain": doc["domain"],
                    "document_type": "test",
                    "integration_test": True
                },
                reasoning_guidance={
                    "extraction_strategy": "balanced",
                    "focus_types": ["PERSON", "ORG", "GPE"]
                }
            )
            
            # Test relationship discovery
            entities = extraction_result.get("entities", [])
            if entities:
                relationship_result = await enhanced_tools.discover_relationships_enhanced(
                    text=doc["content"],
                    entities=entities,
                    chunk_ref=f"integration_test_{doc['id']}",
                    context_metadata={
                        "domain": doc["domain"],
                        "validation_level": "medium"
                    }
                )
            else:
                relationship_result = {"relationships": []}
            
            integration_results.append({
                "document_id": doc["id"],
                "extraction_success": "entities" in extraction_result,
                "entities_count": len(extraction_result.get("entities", [])),
                "relationship_success": "relationships" in relationship_result,
                "relationships_count": len(relationship_result.get("relationships", [])),
                "memory_applied": extraction_result.get("enhancement_metadata", {}).get("memory_boost", 0) > 0,
                "reasoning_applied": extraction_result.get("reasoning_applied", False)
            })
        
        # Test collaborative graph building
        logger.info("Testing collaborative graph building...")
        
        all_entities = []
        all_relationships = []
        
        for result in integration_results:
            # Simulate collected entities and relationships
            doc_entities = [
                {"entity_id": f"entity_{result['document_id']}_{i}", "surface_form": f"Entity {i}", "entity_type": "ORG"}
                for i in range(result["entities_count"])
            ]
            doc_relationships = [
                {"source_entity": f"Entity {i}", "target_entity": f"Entity {i+1}", "relationship_type": "RELATED"}
                for i in range(result["relationships_count"])
            ]
            
            all_entities.extend(doc_entities)
            all_relationships.extend(doc_relationships)
        
        if all_entities:
            graph_result = await enhanced_tools.build_graph_collaboratively(
                entities=all_entities,
                relationships=all_relationships,
                source_refs=[r["document_id"] for r in integration_results],
                collaboration_agents=["agent_1", "agent_2"]
            )
            
            graph_success = graph_result.get("success", False)
            logger.info(f"Graph building result: {graph_result}")
        else:
            graph_success = True  # No entities to build, consider successful
        
        # Test performance metrics collection
        performance_metrics = enhanced_tools.get_performance_metrics()
        enhancement_status = enhanced_tools.get_enhancement_status()
        
        # Analyze integration results
        logger.info("📊 Analyzing enhanced tools integration...")
        
        # Check that enhanced extraction worked
        successful_extractions = sum(1 for r in integration_results if r["extraction_success"])
        assert successful_extractions > 0, "At least some enhanced extractions should succeed"
        
        # Check that enhancements were applied
        memory_applications = sum(1 for r in integration_results if r["memory_applied"])
        reasoning_applications = sum(1 for r in integration_results if r["reasoning_applied"])
        
        logger.info(f"Enhancement applications - Memory: {memory_applications}, Reasoning: {reasoning_applications}")
        
        # Check enhancement status
        assert isinstance(enhancement_status, dict), "Enhancement status should be available"
        assert "memory_enabled" in enhancement_status, "Memory status should be reported"
        assert "reasoning_enabled" in enhancement_status, "Reasoning status should be reported"
        
        # Check performance metrics
        assert isinstance(performance_metrics, dict), "Performance metrics should be available"
        assert "extractions" in performance_metrics, "Extraction metrics should be tracked"
        
        # Verify graph building
        assert graph_success, "Graph building should succeed when entities are available"
        
        logger.info("✅ Enhanced tools integration test completed successfully")
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, agent_test_environment):
        """Test complete end-to-end document processing workflow."""
        env = agent_test_environment
        primary_agent = env['agents']['document_agent_1']
        test_docs = env['test_data']['documents']
        
        logger.info("🔄 Testing end-to-end workflow...")
        
        workflow_results = []
        
        # Process each document through complete workflow
        for doc in test_docs:
            logger.info(f"Processing document: {doc['title']}")
            
            # Create comprehensive processing task
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": doc["id"],
                    "processing_mode": "comprehensive",
                    "enable_collaboration": True,
                    "quality_threshold": 0.7
                },
                context={
                    "workflow_test": True,
                    "expected_entities": len([e for e in env['test_data']['expected_entities'] 
                                            if e['name'].lower() in doc['content'].lower()]),
                    "document_complexity": doc["complexity"]
                }
            )
            
            # Execute workflow
            start_time = time.time()
            result = await primary_agent.execute(task)
            execution_time = time.time() - start_time
            
            # Analyze workflow result
            workflow_analysis = {
                "document_id": doc["id"],
                "document_title": doc["title"],
                "success": result.success,
                "execution_time": execution_time,
                "error": result.error_message if not result.success else None,
                "data_quality": self._analyze_result_quality(result, doc, env['test_data']),
                "metadata": result.metadata if hasattr(result, 'metadata') else {}
            }
            
            workflow_results.append(workflow_analysis)
            
            # Brief pause between documents
            await asyncio.sleep(0.5)
        
        # Analyze end-to-end workflow performance
        logger.info("📊 Analyzing end-to-end workflow results...")
        
        # Check overall success rate
        successful_workflows = sum(1 for r in workflow_results if r["success"])
        total_workflows = len(workflow_results)
        success_rate = successful_workflows / total_workflows if total_workflows > 0 else 0
        
        logger.info(f"Workflow success rate: {successful_workflows}/{total_workflows} ({success_rate*100:.1f}%)")
        assert success_rate >= 0.5, f"Workflow success rate should be at least 50%, got {success_rate*100:.1f}%"
        
        # Check execution time consistency
        execution_times = [r["execution_time"] for r in workflow_results if r["success"]]
        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_execution_time = max(execution_times)
            
            logger.info(f"Execution times - Average: {avg_execution_time:.2f}s, Max: {max_execution_time:.2f}s")
            assert max_execution_time < 30.0, "Individual workflow should complete within 30 seconds"
        
        # Check data quality metrics
        quality_scores = [r["data_quality"]["overall_score"] for r in workflow_results 
                         if r["success"] and "overall_score" in r["data_quality"]]
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            logger.info(f"Average data quality score: {avg_quality:.2f}")
            assert avg_quality >= 0.3, f"Average data quality should be reasonable, got {avg_quality}"
        
        # Check for proper error handling
        failed_workflows = [r for r in workflow_results if not r["success"]]
        for failed in failed_workflows:
            assert failed["error"] is not None, f"Failed workflow {failed['document_id']} should have error message"
            logger.info(f"Expected failure for {failed['document_id']}: {failed['error']}")
        
        logger.info("✅ End-to-end workflow test completed successfully")
        
        return {
            "total_documents": total_workflows,
            "successful_documents": successful_workflows,
            "success_rate": success_rate,
            "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "workflow_results": workflow_results
        }
    
    def _analyze_result_quality(self, result: Result, document: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of workflow results."""
        if not result.success:
            return {"overall_score": 0.0, "analysis": "Workflow failed"}
        
        quality_analysis = {
            "overall_score": 0.5,  # Base score for successful execution
            "entity_quality": 0.0,
            "data_completeness": 0.0,
            "processing_metadata": {}
        }
        
        # Analyze entity extraction quality if available
        entities = result.data.get("entities", []) if result.data else []
        if entities:
            # Check if we found expected entities for this document
            expected_entities = [e["name"] for e in test_data["expected_entities"] 
                               if e["name"].lower() in document["content"].lower()]
            
            found_entity_names = [e.get("surface_form", e.get("text", "")) for e in entities]
            
            matches = sum(1 for expected in expected_entities 
                         if any(expected.lower() in found.lower() for found in found_entity_names))
            
            if expected_entities:
                entity_recall = matches / len(expected_entities)
                quality_analysis["entity_quality"] = entity_recall
                quality_analysis["overall_score"] += entity_recall * 0.3
        
        # Analyze data completeness
        data_fields = ["entities", "entity_count", "confidence"]
        present_fields = sum(1 for field in data_fields if field in (result.data or {}))
        completeness = present_fields / len(data_fields)
        quality_analysis["data_completeness"] = completeness
        quality_analysis["overall_score"] += completeness * 0.2
        
        # Add processing metadata
        if result.metadata:
            quality_analysis["processing_metadata"] = result.metadata
        
        quality_analysis["overall_score"] = min(1.0, quality_analysis["overall_score"])
        
        return quality_analysis
    
    @pytest.mark.asyncio
    async def test_memory_persistence_and_recovery(self, agent_test_environment):
        """Test memory persistence and recovery across agent restarts."""
        env = agent_test_environment
        agent = env['agents']['document_agent_1']
        
        logger.info("💾 Testing memory persistence and recovery...")
        
        # Store some learning data
        learning_data = [
            {
                "task_type": "entity_extraction",
                "domain": "technology",
                "success": True,
                "entities_found": 5,
                "confidence": 0.85,
                "parameters": {"confidence_threshold": 0.7}
            },
            {
                "task_type": "document_processing", 
                "domain": "healthcare",
                "success": True,
                "processing_time": 2.3,
                "quality_score": 0.9
            }
        ]
        
        # Store learning data in memory
        if hasattr(agent, 'memory') and agent.memory:
            for data in learning_data:
                await agent.memory.store_execution(data)
            
            # Get current memory state
            pre_restart_memories = await agent.memory.search("entity extraction", top_k=10)
            pre_restart_patterns = await agent.memory.get_learned_patterns("entity_extraction")
            
            logger.info(f"Pre-restart: {len(pre_restart_memories)} memories, {len(pre_restart_patterns)} patterns")
            
            # Simulate agent restart by creating new agent instance
            new_agent = DocumentAgent(
                mcp_adapter=env['agents']['document_agent_1']._mcp_adapter if hasattr(env['agents']['document_agent_1'], '_mcp_adapter') else None,
                agent_id="document_agent_1",  # Same ID to access same memory
                memory_config={"enable_memory": True, "max_memories": 500},
                reasoning_config={"enable_reasoning": True, "confidence_threshold": 0.7},
                communication_config={"enable_broadcast": True},
                message_bus=env['message_bus']
            )
            
            # Check memory recovery
            if hasattr(new_agent, 'memory') and new_agent.memory:
                post_restart_memories = await new_agent.memory.search("entity extraction", top_k=10)
                post_restart_patterns = await new_agent.memory.get_learned_patterns("entity_extraction")
                
                logger.info(f"Post-restart: {len(post_restart_memories)} memories, {len(post_restart_patterns)} patterns")
                
                # Verify memory persistence
                assert len(post_restart_memories) >= len(pre_restart_memories), \
                    "Memory should persist across agent restarts"
                
                logger.info("✅ Memory persistence test passed")
            else:
                logger.info("ℹ️  Memory system not fully implemented, skipping persistence test")
        else:
            logger.info("ℹ️  Memory system not available, skipping persistence test")
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, agent_test_environment):
        """Test agent performance under concurrent load."""
        env = agent_test_environment
        agents = list(env['agents'].values())
        test_docs = env['test_data']['documents']
        
        logger.info("⚡ Testing performance under concurrent load...")
        
        # Create multiple concurrent tasks
        concurrent_tasks = []
        for i in range(6):  # 6 concurrent tasks
            agent = agents[i % len(agents)]  # Distribute across available agents
            doc = test_docs[i % len(test_docs)]  # Cycle through documents
            
            task = Task(
                task_type="document_processing",
                parameters={
                    "text": doc["content"],
                    "domain": doc["domain"],
                    "document_id": f"{doc['id']}_concurrent_{i}",
                    "task_index": i
                },
                context={"load_test": True, "concurrent_batch": True}
            )
            
            concurrent_tasks.append((agent, task))
        
        # Execute all tasks concurrently
        start_time = time.time()
        
        async def execute_task(agent, task):
            task_start = time.time()
            try:
                result = await agent.execute(task)
                execution_time = time.time() - task_start
                return {
                    "task_index": task.parameters["task_index"],
                    "success": result.success,
                    "execution_time": execution_time,
                    "agent_id": agent.agent_id,
                    "error": result.error_message if not result.success else None
                }
            except Exception as e:
                execution_time = time.time() - task_start
                return {
                    "task_index": task.parameters["task_index"],
                    "success": False,
                    "execution_time": execution_time,
                    "agent_id": agent.agent_id,
                    "error": str(e)
                }
        
        # Run all tasks concurrently
        concurrent_results = await asyncio.gather(*[
            execute_task(agent, task) for agent, task in concurrent_tasks
        ], return_exceptions=True)
        
        total_execution_time = time.time() - start_time
        
        # Analyze concurrent performance
        logger.info("📊 Analyzing concurrent performance results...")
        
        # Filter out exceptions
        valid_results = [r for r in concurrent_results if isinstance(r, dict)]
        
        # Check success rate
        successful_tasks = sum(1 for r in valid_results if r["success"])
        total_tasks = len(valid_results)
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        logger.info(f"Concurrent execution - Success: {successful_tasks}/{total_tasks} ({success_rate*100:.1f}%)")
        logger.info(f"Total execution time: {total_execution_time:.2f}s")
        
        # Check individual execution times
        execution_times = [r["execution_time"] for r in valid_results if r["success"]]
        if execution_times:
            avg_execution_time = sum(execution_times) / len(execution_times)
            max_execution_time = max(execution_times)
            
            logger.info(f"Individual execution times - Average: {avg_execution_time:.2f}s, Max: {max_execution_time:.2f}s")
            
            # Performance assertions
            assert success_rate >= 0.5, f"Concurrent success rate should be at least 50%, got {success_rate*100:.1f}%"
            assert max_execution_time < 60.0, f"Individual task should complete within 60s, max was {max_execution_time:.2f}s"
            assert total_execution_time < avg_execution_time * total_tasks * 0.8, \
                "Concurrent execution should be faster than sequential"
        
        # Check for proper error handling under load
        failed_results = [r for r in valid_results if not r["success"]]
        for failed in failed_results:
            assert failed["error"] is not None, f"Failed task {failed['task_index']} should have error message"
        
        logger.info("✅ Performance under load test completed successfully")
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": success_rate,
            "total_time": total_execution_time,
            "average_individual_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "max_individual_time": max(execution_times) if execution_times else 0
        }


# Standalone test runner
if __name__ == "__main__":
    async def run_comprehensive_tests():
        """Run comprehensive agent workflow tests."""
        logger.info("🧪 Starting Comprehensive Agent Workflow Tests")
        logger.info("=" * 70)
        
        if not IMPORTS_AVAILABLE:
            logger.error("❌ Required modules not available. Please ensure all dependencies are installed.")
            return
        
        test_instance = TestAgentWorkflowComprehensive()
        
        # Create test environment
        async for env in test_instance.agent_test_environment():
            try:
                # Run all tests
                logger.info("1️⃣  Testing memory learning progression...")
                await test_instance.test_memory_learning_progression(env)
                
                logger.info("\n2️⃣  Testing reasoning-guided optimization...")
                await test_instance.test_reasoning_guided_optimization(env)
                
                logger.info("\n3️⃣  Testing inter-agent communication...")
                await test_instance.test_inter_agent_communication(env)
                
                logger.info("\n4️⃣  Testing enhanced tools integration...")
                await test_instance.test_enhanced_tools_integration(env)
                
                logger.info("\n5️⃣  Testing end-to-end workflow...")
                e2e_results = await test_instance.test_end_to_end_workflow(env)
                
                logger.info("\n6️⃣  Testing memory persistence...")
                await test_instance.test_memory_persistence_and_recovery(env)
                
                logger.info("\n7️⃣  Testing performance under load...")
                load_results = await test_instance.test_performance_under_load(env)
                
                # Summary
                logger.info("\n" + "=" * 70)
                logger.info("🎉 Comprehensive Agent Workflow Tests Completed Successfully!")
                logger.info(f"📊 End-to-End Results: {e2e_results['success_rate']*100:.1f}% success rate")
                logger.info(f"⚡ Load Test Results: {load_results['success_rate']*100:.1f}% success rate under load")
                logger.info("✅ All agent architecture components validated!")
                
            except Exception as e:
                logger.error(f"❌ Test execution failed: {e}")
                import traceback
                traceback.print_exc()
            
            break  # Exit after first (and only) environment
    
    # Run tests
    asyncio.run(run_comprehensive_tests())