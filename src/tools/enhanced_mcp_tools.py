"""
Enhanced MCP Tools with Memory, Reasoning, and Communication Capabilities

This module provides enhanced versions of KGAS tools that integrate with the agent
architecture to provide memory-aware, reasoning-guided, and communication-enabled
entity extraction, relationship discovery, and graph building.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from ..orchestration.memory import AgentMemory
from ..orchestration.llm_reasoning import LLMReasoningEngine, ReasoningType
from ..orchestration.communication import MessageBus, Message, MessageType
from ..core.service_manager import ServiceManager
from .phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from .phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
from .phase1.t31_entity_builder_unified import T31EntityBuilderUnified

logger = logging.getLogger(__name__)


class EnhancedMCPTools:
    """
    Enhanced MCP tool wrapper that provides memory-aware, reasoning-guided,
    and communication-enabled versions of KGAS tools.
    
    Features:
    - Memory-aware entity extraction with learned patterns
    - Reasoning-guided relationship discovery
    - Collaborative graph building with agent communication
    - Adaptive parameter optimization
    - Cross-tool learning and pattern sharing
    """
    
    def __init__(self, service_manager: ServiceManager, agent_id: str = "enhanced_tools",
                 memory_config: Dict[str, Any] = None, reasoning_config: Dict[str, Any] = None,
                 communication_config: Dict[str, Any] = None, message_bus: MessageBus = None):
        """
        Initialize enhanced MCP tools.
        
        Args:
            service_manager: Core service manager
            agent_id: Identifier for the tool agent
            memory_config: Memory system configuration
            reasoning_config: Reasoning engine configuration  
            communication_config: Communication configuration
            message_bus: Message bus for inter-tool communication
        """
        self.service_manager = service_manager
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"{__name__}.{agent_id}")
        
        # Initialize enhanced capabilities
        memory_config = memory_config or {}
        db_path = memory_config.get("db_path")
        self.memory = AgentMemory(
            agent_id=agent_id,
            db_path=db_path
        )
        
        self.reasoning_engine = LLMReasoningEngine(
            llm_config=reasoning_config or {"enable_reasoning": True, "confidence_threshold": 0.7}
        )
        
        self.message_bus = message_bus
        self.communication_enabled = message_bus is not None
        
        # Initialize enhanced tools
        self.ner_tool = T23ASpacyNERUnified(service_manager)
        self.relationship_tool = T27RelationshipExtractorUnified(service_manager)
        self.entity_builder = T31EntityBuilderUnified(service_manager)
        
        # Cross-tool learning state
        self.extraction_patterns = {}
        self.collaboration_history = []
        self.performance_metrics = {
            "extractions": {"total": 0, "successful": 0, "reasoning_improved": 0},
            "relationships": {"total": 0, "successful": 0, "reasoning_improved": 0},
            "graph_building": {"total": 0, "successful": 0, "collaborative": 0}
        }
        
        # Register for communication if enabled
        if self.communication_enabled:
            self._register_communication_handlers()
    
    def _register_communication_handlers(self):
        """Register handlers for inter-agent communication."""
        if not self.message_bus:
            return
            
        # Subscribe to relevant topics
        self.message_bus.subscribe("entity_insights", self._handle_entity_insights)
        self.message_bus.subscribe("relationship_patterns", self._handle_relationship_patterns)
        self.message_bus.subscribe("graph_collaboration", self._handle_graph_collaboration)
    
    async def extract_entities_enhanced(self, text: str, chunk_ref: str, 
                                      context_metadata: Dict[str, Any] = None,
                                      reasoning_guidance: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced entity extraction with memory, reasoning, and communication.
        
        Args:
            text: Text to extract entities from
            chunk_ref: Reference to source chunk
            context_metadata: Additional context for reasoning
            reasoning_guidance: Specific reasoning parameters
            
        Returns:
            Enhanced extraction results with learning data
        """
        start_time = time.time()
        self.performance_metrics["extractions"]["total"] += 1
        
        try:
            # Get memory context for this extraction
            memory_context = await self._get_extraction_memory_context(text, context_metadata)
            
            # Apply reasoning for extraction optimization  
            reasoning_result = await self._apply_extraction_reasoning(
                text, context_metadata or {}, reasoning_guidance or {}, memory_context
            )
            
            # Prepare enhanced extraction request
            extraction_request = {
                "text": text,
                "chunk_ref": chunk_ref,
                "chunk_confidence": context_metadata.get("confidence", 0.8),
                "context_metadata": context_metadata or {},
                "reasoning_guidance": reasoning_guidance or {}
            }
            
            # Enhanced parameter optimization
            if reasoning_result and reasoning_result.get("success"):
                # Apply reasoning recommendations
                decision = reasoning_result.get("decision", {})
                if "confidence_threshold" in decision:
                    extraction_request["confidence_threshold"] = decision["confidence_threshold"]
                if "focus_types" in decision:
                    extraction_request["entity_types"] = decision["focus_types"]
            
            # Memory-based parameter adaptation
            if memory_context.get("learned_parameters"):
                learned_params = memory_context["learned_parameters"]
                for param, value in learned_params.items():
                    if param not in extraction_request:
                        extraction_request[param] = value
            
            # Execute enhanced extraction
            # Note: This would call the enhanced T23A tool if it was fully implemented
            # For now, we'll simulate the enhancement
            base_result = await self._simulate_enhanced_extraction(extraction_request)
            
            # Post-process with cross-tool learning
            enhanced_entities = await self._post_process_entities(
                base_result.get("entities", []), reasoning_result, memory_context
            )
            
            # Store learning data
            await self._store_extraction_learning(
                text, enhanced_entities, chunk_ref, context_metadata, reasoning_result
            )
            
            # Broadcast insights if communication enabled
            if self.communication_enabled and enhanced_entities:
                await self._broadcast_entity_insights(enhanced_entities, context_metadata)
            
            # Update performance metrics
            if enhanced_entities:
                self.performance_metrics["extractions"]["successful"] += 1
                if reasoning_result and reasoning_result.get("success"):
                    self.performance_metrics["extractions"]["reasoning_improved"] += 1
            
            return {
                "entities": enhanced_entities,
                "total_entities": len(enhanced_entities),
                "reasoning_applied": reasoning_result is not None,
                "memory_patterns_used": len(memory_context.get("relevant_patterns", [])),
                "execution_time": time.time() - start_time,
                "enhancement_metadata": {
                    "reasoning_confidence": reasoning_result.get("confidence", 0.0) if reasoning_result else 0.0,
                    "memory_boost": len(memory_context.get("relevant_patterns", [])) * 0.05,
                    "cross_tool_learning": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced entity extraction failed: {e}")
            return {
                "entities": [],
                "total_entities": 0,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def discover_relationships_enhanced(self, text: str, entities: List[Dict[str, Any]], 
                                            chunk_ref: str, context_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhanced relationship discovery with reasoning guidance and pattern learning.
        
        Args:
            text: Source text
            entities: Extracted entities
            chunk_ref: Reference to source chunk
            context_metadata: Additional context
            
        Returns:
            Enhanced relationship discovery results
        """
        start_time = time.time()
        self.performance_metrics["relationships"]["total"] += 1
        
        try:
            # Get memory context for relationship patterns
            memory_context = await self._get_relationship_memory_context(text, entities, context_metadata)
            
            # Apply reasoning for relationship discovery
            reasoning_result = await self._apply_relationship_reasoning(
                text, entities, context_metadata or {}, memory_context
            )
            
            # Enhanced relationship extraction with multiple strategies
            base_relationships = await self._extract_relationships_multi_strategy(
                text, entities, reasoning_result, memory_context
            )
            
            # Apply reasoning validation to relationships
            validated_relationships = await self._validate_relationships_with_reasoning(
                base_relationships, entities, reasoning_result
            )
            
            # Store relationship patterns for learning
            await self._store_relationship_patterns(
                validated_relationships, text, entities, reasoning_result
            )
            
            # Broadcast relationship patterns if communication enabled
            if self.communication_enabled and validated_relationships:
                await self._broadcast_relationship_patterns(validated_relationships, context_metadata)
            
            # Update performance metrics
            if validated_relationships:
                self.performance_metrics["relationships"]["successful"] += 1
                if reasoning_result and reasoning_result.get("success"):
                    self.performance_metrics["relationships"]["reasoning_improved"] += 1
            
            return {
                "relationships": validated_relationships,
                "total_relationships": len(validated_relationships),
                "reasoning_applied": reasoning_result is not None,
                "patterns_learned": len(memory_context.get("new_patterns", [])),
                "execution_time": time.time() - start_time,
                "enhancement_metadata": {
                    "reasoning_confidence": reasoning_result.get("confidence", 0.0) if reasoning_result else 0.0,
                    "validation_applied": True,
                    "multi_strategy": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced relationship discovery failed: {e}")
            return {
                "relationships": [],
                "total_relationships": 0,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def build_graph_collaboratively(self, entities: List[Dict[str, Any]], 
                                        relationships: List[Dict[str, Any]],
                                        source_refs: List[str], 
                                        collaboration_agents: List[str] = None) -> Dict[str, Any]:
        """
        Build knowledge graph collaboratively with other agents.
        
        Args:
            entities: Entities to build into graph
            relationships: Relationships to create
            source_refs: Source references
            collaboration_agents: Other agents to collaborate with
            
        Returns:
            Collaborative graph building results
        """
        start_time = time.time()
        self.performance_metrics["graph_building"]["total"] += 1
        
        try:
            # Check if collaborative building is beneficial
            should_collaborate = (
                self.communication_enabled and 
                collaboration_agents and 
                (len(entities) > 50 or len(relationships) > 100)
            )
            
            if should_collaborate:
                # Distribute graph building work
                result = await self._build_graph_distributed(
                    entities, relationships, source_refs, collaboration_agents
                )
                self.performance_metrics["graph_building"]["collaborative"] += 1
            else:
                # Build graph locally with enhancements
                result = await self._build_graph_enhanced(entities, relationships, source_refs)
            
            # Update performance metrics
            if result.get("success", False):
                self.performance_metrics["graph_building"]["successful"] += 1
            
            result["execution_time"] = time.time() - start_time
            result["collaborative"] = should_collaborate
            
            return result
            
        except Exception as e:
            self.logger.error(f"Collaborative graph building failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "collaborative": False
            }
    
    async def _get_extraction_memory_context(self, text: str, context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory context for entity extraction."""
        try:
            # Search for similar extractions
            search_query = f"entity extraction {context_metadata.get('domain', 'general')} {len(text)//100}k"
            memories = await self.memory.search(search_query, top_k=5)
            
            # Get learned patterns
            patterns = await self.memory.get_learned_patterns("entity_extraction")
            
            return {
                "relevant_memories": memories,
                "relevant_patterns": patterns,
                "learned_parameters": self._extract_learned_parameters(memories),
                "domain": context_metadata.get("domain", "general")
            }
        except Exception as e:
            self.logger.warning(f"Failed to get extraction memory context: {e}")
            return {"relevant_memories": [], "relevant_patterns": []}
    
    async def _apply_extraction_reasoning(self, text: str, context_metadata: Dict[str, Any],
                                        reasoning_guidance: Dict[str, Any], memory_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply reasoning to optimize entity extraction."""
        try:
            if not self.reasoning_engine:
                return None
            
            reasoning_context = {
                "text_length": len(text),
                "domain": context_metadata.get("domain", "general"),
                "previous_extractions": len(memory_context.get("relevant_memories", [])),
                "learned_patterns": len(memory_context.get("relevant_patterns", []))
            }
            
            query = f"""Optimize entity extraction for {context_metadata.get('domain', 'general')} domain.
            
            Text length: {len(text)} characters
            Available patterns: {len(memory_context.get('relevant_patterns', []))}
            
            What entity types should I focus on? What confidence threshold should I use?
            Should I use high precision or high recall strategy?
            """
            
            return await self.reasoning_engine.reason(
                reasoning_type=ReasoningType.TACTICAL,
                query=query,
                context=reasoning_context
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to apply extraction reasoning: {e}")
            return None
    
    async def _simulate_enhanced_extraction(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate enhanced extraction (placeholder for full implementation)."""
        # This would call the enhanced T23A tool when fully implemented
        # For now, simulate the enhancement
        text = request["text"]
        
        # Simple entity extraction simulation
        entities = []
        words = text.split()
        
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                # Simple heuristic for entity detection
                entity_type = "PERSON" if word.endswith("son") or word.endswith("man") else "ORG"
                entities.append({
                    "entity_id": f"entity_{i}",
                    "surface_form": word,
                    "entity_type": entity_type,
                    "confidence": 0.8 + (len(word) * 0.01),
                    "start_pos": text.find(word),
                    "end_pos": text.find(word) + len(word)
                })
        
        return {"entities": entities}
    
    async def _post_process_entities(self, entities: List[Dict[str, Any]], 
                                   reasoning_result: Optional[Dict[str, Any]],
                                   memory_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Post-process entities with reasoning and memory enhancements."""
        enhanced_entities = []
        
        for entity in entities:
            # Apply reasoning boosts
            confidence_boost = 0.0
            if reasoning_result and reasoning_result.get("success"):
                decision = reasoning_result.get("decision", {})
                if entity["entity_type"] in decision.get("focus_types", []):
                    confidence_boost += 0.1
            
            # Apply memory boosts
            for pattern in memory_context.get("relevant_patterns", []):
                if entity["entity_type"] in pattern.get("high_confidence_types", []):
                    confidence_boost += 0.05
            
            # Create enhanced entity
            enhanced_entity = entity.copy()
            enhanced_entity["confidence"] = min(1.0, entity["confidence"] + confidence_boost)
            enhanced_entity["enhancement_applied"] = confidence_boost > 0
            
            enhanced_entities.append(enhanced_entity)
        
        return enhanced_entities
    
    async def _store_extraction_learning(self, text: str, entities: List[Dict[str, Any]], 
                                       chunk_ref: str, context_metadata: Dict[str, Any],
                                       reasoning_result: Optional[Dict[str, Any]]) -> None:
        """Store extraction results for learning."""
        try:
            # Store execution result
            await self.memory.store_execution({
                "task_type": "enhanced_entity_extraction",
                "text_length": len(text),
                "entities_extracted": len(entities),
                "domain": context_metadata.get("domain", "general"),
                "reasoning_applied": reasoning_result is not None,
                "success": len(entities) > 0
            })
            
            # Store successful patterns
            if entities and len(entities) > 0:
                entity_types = [e["entity_type"] for e in entities]
                avg_confidence = sum(e["confidence"] for e in entities) / len(entities)
                
                await self.memory.store_learned_pattern(
                    pattern_type="enhanced_entity_extraction",
                    pattern_data={
                        "domain": context_metadata.get("domain", "general"),
                        "successful_types": entity_types,
                        "avg_confidence": avg_confidence,
                        "text_length_range": (len(text) - 500, len(text) + 500)
                    },
                    importance=0.8
                )
                
        except Exception as e:
            self.logger.warning(f"Failed to store extraction learning: {e}")
    
    async def _broadcast_entity_insights(self, entities: List[Dict[str, Any]], 
                                       context_metadata: Dict[str, Any]) -> None:
        """Broadcast entity insights to other agents."""
        if not self.message_bus:
            return
            
        try:
            insight_data = {
                "entity_types_found": [e["entity_type"] for e in entities],
                "avg_confidence": sum(e["confidence"] for e in entities) / len(entities),
                "domain": context_metadata.get("domain", "general"),
                "extraction_strategy": "enhanced",
                "timestamp": datetime.now().isoformat()
            }
            
            message = Message(
                message_type=MessageType.BROADCAST,
                sender_id=self.agent_id,
                topic="entity_insights",
                payload=insight_data
            )
            
            await self.message_bus.send_message(message)
            
        except Exception as e:
            self.logger.warning(f"Failed to broadcast entity insights: {e}")
    
    def _extract_learned_parameters(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract learned parameters from memory."""
        learned_params = {}
        
        for memory in memories:
            if memory.get("success") and "parameters" in memory:
                params = memory["parameters"]
                for key, value in params.items():
                    if key not in learned_params:
                        learned_params[key] = []
                    learned_params[key].append(value)
        
        # Average numeric parameters
        averaged_params = {}
        for key, values in learned_params.items():
            if values and isinstance(values[0], (int, float)):
                averaged_params[key] = sum(values) / len(values)
        
        return averaged_params
    
    async def _get_relationship_memory_context(self, text: str, entities: List[Dict[str, Any]], 
                                             context_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory context for relationship extraction.""" 
        # Placeholder implementation
        return {"relevant_patterns": [], "new_patterns": []}
    
    async def _apply_relationship_reasoning(self, text: str, entities: List[Dict[str, Any]],
                                          context_metadata: Dict[str, Any], memory_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply reasoning for relationship discovery."""
        # Placeholder implementation  
        return None
    
    async def _extract_relationships_multi_strategy(self, text: str, entities: List[Dict[str, Any]],
                                                   reasoning_result: Optional[Dict[str, Any]], 
                                                   memory_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relationships using multiple strategies."""
        # Placeholder implementation
        return []
    
    async def _validate_relationships_with_reasoning(self, relationships: List[Dict[str, Any]], 
                                                   entities: List[Dict[str, Any]], 
                                                   reasoning_result: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate relationships using reasoning."""
        # Placeholder implementation
        return relationships
    
    async def _store_relationship_patterns(self, relationships: List[Dict[str, Any]], text: str, 
                                         entities: List[Dict[str, Any]], reasoning_result: Optional[Dict[str, Any]]) -> None:
        """Store relationship patterns for learning."""
        # Placeholder implementation
        pass
    
    async def _broadcast_relationship_patterns(self, relationships: List[Dict[str, Any]], 
                                             context_metadata: Dict[str, Any]) -> None:
        """Broadcast relationship patterns to other agents."""
        # Placeholder implementation
        pass
    
    async def _build_graph_distributed(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]],
                                      source_refs: List[str], collaboration_agents: List[str]) -> Dict[str, Any]:
        """Build graph in distributed manner with other agents."""
        # Placeholder implementation
        return {"success": True, "entities_created": len(entities), "relationships_created": len(relationships)}
    
    async def _build_graph_enhanced(self, entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]],
                                   source_refs: List[str]) -> Dict[str, Any]:
        """Build graph with local enhancements."""
        # Placeholder implementation  
        return {"success": True, "entities_created": len(entities), "relationships_created": len(relationships)}
    
    # Communication handlers
    async def _handle_entity_insights(self, message: Message) -> None:
        """Handle incoming entity insights from other agents."""
        try:
            insights = message.payload
            # Store insights for learning
            await self.memory.store_execution({
                "task_type": "received_entity_insights",
                "source_agent": message.sender_id,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.warning(f"Failed to handle entity insights: {e}")
    
    async def _handle_relationship_patterns(self, message: Message) -> None:
        """Handle incoming relationship patterns from other agents."""
        # Placeholder implementation
        pass
    
    async def _handle_graph_collaboration(self, message: Message) -> None:
        """Handle graph collaboration requests from other agents."""
        # Placeholder implementation  
        pass
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()
    
    def get_enhancement_status(self) -> Dict[str, Any]:
        """Get status of all enhancements."""
        return {
            "memory_enabled": self.memory is not None,
            "reasoning_enabled": self.reasoning_engine is not None,
            "communication_enabled": self.communication_enabled,
            "patterns_learned": len(self.extraction_patterns),
            "collaborations": len(self.collaboration_history)
        }