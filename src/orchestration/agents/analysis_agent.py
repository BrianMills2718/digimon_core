"""
Reasoning-enhanced analysis agent using KGAS MCP tools.

This agent handles entity and relationship extraction using existing
T23A (Entity Extractor) and T27 (Relationship Extractor) tools,
with memory capabilities and LLM reasoning for intelligent analysis decisions.
"""

import time
import logging
from typing import List, Dict, Any

from ..base import Task, Result
from ..reasoning_agent import ReasoningAgent
from ..llm_reasoning import ReasoningType
from ..mcp_adapter import MCPToolAdapter

logger = logging.getLogger(__name__)


class AnalysisAgent(ReasoningAgent):
    """
    Reasoning-enhanced analysis agent for entity and relationship extraction.
    
    Uses existing KGAS tools with memory and LLM reasoning capabilities:
    - T23A: SpaCy NER (extract_entities)
    - T27: Relationship Extractor (extract_relationships)
    
    Advanced features:
    - LLM reasoning for intelligent confidence threshold optimization
    - Memory-based learning of extraction patterns and domain terminology
    - Adaptive parameter adjustment based on content characteristics
    - Strategic decision-making for complex analysis workflows
    """
    
    def __init__(self, mcp_adapter: MCPToolAdapter, agent_id: str = None, 
                 memory_config: Dict[str, Any] = None, reasoning_config: Dict[str, Any] = None):
        """
        Initialize reasoning-enhanced analysis agent.
        
        Args:
            mcp_adapter: MCP tool adapter instance
            agent_id: Optional agent identifier
            memory_config: Memory system configuration
            reasoning_config: LLM reasoning configuration
        """
        super().__init__(agent_id or "analysis_agent", memory_config, reasoning_config)
        self.mcp = mcp_adapter
        self.capabilities = [
            "entity_extraction",
            "relationship_extraction",
            "analysis",
            "ner_processing"
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Analysis parameters (now dynamically optimized by reasoning)
        self.entity_confidence_threshold = 0.7
        self.relationship_confidence_threshold = 0.6
        self.max_entities_per_chunk = 50
        
        # Reasoning-specific configuration
        self.threshold_optimization = True
        self.entity_type_analysis = True
        self.relationship_strategy_reasoning = True
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type."""
        return task_type in self.capabilities
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return self.capabilities.copy()
    
    async def _execute_with_memory(self, task: Task, memory_context: Dict[str, Any]) -> Result:
        """
        Execute analysis task with memory context.
        
        Supported task types:
        - analysis: Extract both entities and relationships
        - entity_extraction: Just extract entities
        - relationship_extraction: Just extract relationships
        
        Args:
            task: Task to execute
            memory_context: Relevant memory context
            
        Returns:
            Result of execution
        """
        start_time = time.time()
        
        try:
            # Apply memory-based optimizations
            await self._apply_memory_optimizations(task, memory_context)
            
            self.logger.info(f"Executing task: {task.task_type} with memory context")
            
            if task.task_type in ["analysis", "entity_extraction", "relationship_extraction"]:
                return await self._analyze_content_with_memory(task, memory_context, start_time)
            else:
                return self._create_result(
                    success=False,
                    error=f"Unknown task type: {task.task_type}",
                    execution_time=time.time() - start_time,
                    task=task
                )
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return self._create_result(
                success=False,
                error=f"Task execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                task=task
            )
    
    async def _execute_without_memory(self, task: Task) -> Result:
        """Fallback execution without memory context."""
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing task: {task.task_type} (fallback mode)")
            
            if task.task_type in ["analysis", "entity_extraction", "relationship_extraction"]:
                return await self._analyze_content(task, start_time)
            else:
                return self._create_result(
                    success=False,
                    error=f"Unknown task type: {task.task_type}",
                    execution_time=time.time() - start_time,
                    task=task
                )
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return self._create_result(
                success=False,
                error=f"Task execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                task=task
            )
    
    async def _apply_memory_optimizations(self, task: Task, memory_context: Dict[str, Any]) -> None:
        """Apply memory-based optimizations to analysis parameters."""
        # Get parameter recommendations from memory
        recommendations = await self.get_parameter_recommendations(task.task_type)
        
        if recommendations["confidence"] > 0.5:
            # Apply recommended parameters
            for param, value in recommendations["recommended_parameters"].items():
                if param not in task.parameters:
                    task.parameters[param] = value
                    self.logger.debug(f"Applied memory recommendation: {param}={value}")
        
        # Adapt confidence thresholds based on learned patterns
        for pattern in memory_context.get("learned_patterns", []):
            if "confidence_threshold" in pattern.get("pattern_type", ""):
                pattern_data = pattern.get("pattern_data", {})
                if pattern_data.get("confidence", 0) > 0.7:
                    if "entity" in pattern.get("pattern_type", ""):
                        self.entity_confidence_threshold = pattern_data.get("threshold", self.entity_confidence_threshold)
                    elif "relationship" in pattern.get("pattern_type", ""):
                        self.relationship_confidence_threshold = pattern_data.get("threshold", self.relationship_confidence_threshold)
                    self.logger.debug(f"Applied learned confidence thresholds: entity={self.entity_confidence_threshold}, relationship={self.relationship_confidence_threshold}")
    
    async def _analyze_content_with_memory(self, task: Task, memory_context: Dict[str, Any], start_time: float) -> Result:
        """Analyze content with memory-enhanced strategies."""
        # Use learned strategies if available
        strategies = await self.get_learned_strategies(task.task_type)
        
        if strategies and await self.should_use_strategy(strategies[0]["name"]):
            self.logger.info(f"Using learned strategy: {strategies[0]['name']}")
            # Apply the learned strategy parameters
            for step in strategies[0]["steps"]:
                if step["step"] == "set_thresholds":
                    self.entity_confidence_threshold = step.get("entity_threshold", self.entity_confidence_threshold)
                    self.relationship_confidence_threshold = step.get("relationship_threshold", self.relationship_confidence_threshold)
        
        # Execute standard analysis with enhanced parameters
        result = await self._analyze_content(task, start_time)
        
        # Learn from the analysis results
        if result.success and result.data:
            await self._learn_from_analysis_results(task, result, memory_context)
        
        return result
    
    async def _learn_from_analysis_results(self, task: Task, result: Result, memory_context: Dict[str, Any]) -> None:
        """Learn patterns from analysis results."""
        data = result.data
        
        # Learn entity extraction patterns
        if "entities" in data and data["entities"]:
            entity_count = len(data["entities"])
            chunk_count = data.get("total_chunks_processed", 1)
            avg_entities_per_chunk = entity_count / chunk_count
            
            # Store entity extraction pattern
            await self.memory.store_learned_pattern(
                pattern_type=f"{task.task_type}_entity_extraction_pattern",
                pattern_data={
                    "avg_entities_per_chunk": avg_entities_per_chunk,
                    "total_entities": entity_count,
                    "entity_types": data.get("entity_types", {}),
                    "confidence_threshold": self.entity_confidence_threshold,
                    "confidence": 0.8 if avg_entities_per_chunk > 2 else 0.6
                },
                importance=0.7
            )
            
            # Learn optimal confidence thresholds if this was very successful
            if avg_entities_per_chunk > 5 and not result.warnings:
                await self.memory.store_learned_pattern(
                    pattern_type="entity_confidence_threshold_success",
                    pattern_data={
                        "threshold": self.entity_confidence_threshold,
                        "entities_per_chunk": avg_entities_per_chunk,
                        "task_type": task.task_type,
                        "confidence": 0.8
                    },
                    importance=0.6
                )
        
        # Learn relationship extraction patterns
        if "relationships" in data and data["relationships"]:
            relationship_count = len(data["relationships"])
            entity_count = len(data.get("entities", []))
            
            if entity_count > 0:
                relationship_ratio = relationship_count / entity_count
                
                # Store relationship extraction pattern
                await self.memory.store_learned_pattern(
                    pattern_type=f"{task.task_type}_relationship_extraction_pattern",
                    pattern_data={
                        "relationship_to_entity_ratio": relationship_ratio,
                        "total_relationships": relationship_count,
                        "relationship_types": data.get("relationship_types", {}),
                        "confidence_threshold": self.relationship_confidence_threshold,
                        "confidence": 0.8 if relationship_ratio > 0.3 else 0.6
                    },
                    importance=0.7
                )
                
                # Learn optimal relationship confidence thresholds
                if relationship_ratio > 0.5 and not result.warnings:
                    await self.memory.store_learned_pattern(
                        pattern_type="relationship_confidence_threshold_success",
                        pattern_data={
                            "threshold": self.relationship_confidence_threshold,
                            "relationship_ratio": relationship_ratio,
                            "task_type": task.task_type,
                            "confidence": 0.8
                        },
                        importance=0.6
                    )
    
    async def _customize_reasoning_type(self, suggested_type: ReasoningType, task: Task, memory_context: Dict[str, Any]) -> ReasoningType:
        """Customize reasoning type for analysis tasks."""
        
        # Use adaptive reasoning if we have confidence threshold learning patterns
        patterns = memory_context.get("learned_patterns", [])
        confidence_patterns = [p for p in patterns if "confidence_threshold" in p.get("pattern_type", "")]
        
        if confidence_patterns:
            return ReasoningType.ADAPTIVE
        
        # Use diagnostic reasoning for relationship extraction if entities are failing
        if task.task_type == "relationship_extraction":
            relevant_executions = memory_context.get("relevant_executions", [])
            entity_failures = [
                exec_info for exec_info in relevant_executions 
                if not exec_info.get("success", True) and "entity" in exec_info.get("task_type", "")
            ]
            if entity_failures:
                return ReasoningType.DIAGNOSTIC
        
        # Use strategic reasoning for complex analysis workflows
        chunks = self._get_chunks_from_task(task)
        if len(chunks) > 10:
            return ReasoningType.STRATEGIC
        
        # Default to suggested type
        return suggested_type
    
    async def _get_task_constraints(self, task: Task) -> Dict[str, Any]:
        """Get analysis-specific constraints."""
        base_constraints = await super()._get_task_constraints(task)
        
        # Add analysis-specific constraints
        analysis_constraints = {
            "max_entities_per_chunk": self.max_entities_per_chunk,
            "min_entity_confidence": 0.3,
            "max_entity_confidence": 1.0,
            "min_relationship_confidence": 0.2,
            "max_relationship_confidence": 1.0,
            "max_chunks_per_batch": 50,
            "entity_extraction_timeout": 30
        }
        
        return {**base_constraints, **analysis_constraints}
    
    async def _get_task_goals(self, task: Task) -> List[str]:
        """Get analysis-specific goals."""
        base_goals = await super()._get_task_goals(task)
        
        # Add analysis-specific goals
        analysis_goals = [
            "Optimize confidence thresholds for maximum accuracy",
            "Maximize entity extraction precision and recall",
            "Adapt to domain-specific terminology patterns",
            "Minimize false positives while capturing key entities",
            "Optimize relationship extraction based on entity quality"
        ]
        
        return base_goals + analysis_goals
    
    async def _analyze_content_characteristics(self, chunks: List[Dict], reasoning_result) -> Dict[str, Any]:
        """Analyze content characteristics for reasoning-based optimization."""
        
        if not chunks:
            return {"analysis": "no_content", "recommendations": {}}
        
        # Extract content characteristics
        total_text_length = sum(len(chunk.get("text", "")) for chunk in chunks)
        avg_chunk_length = total_text_length / len(chunks) if chunks else 0
        
        # Content complexity analysis
        complexity_indicators = []
        for chunk in chunks:
            text = chunk.get("text", "")
            # Simple heuristics for complexity
            if len(text.split()) > 200:  # Long chunks
                complexity_indicators.append("verbose")
            if len([w for w in text.split() if len(w) > 10]) > 10:  # Technical terms
                complexity_indicators.append("technical")
            if text.count(",") > 20:  # Many entities likely
                complexity_indicators.append("entity_rich")
        
        # Apply reasoning decisions if available
        entity_threshold = self.entity_confidence_threshold
        relationship_threshold = self.relationship_confidence_threshold
        extraction_strategy = "balanced"
        
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            entity_threshold = decision.get("entity_threshold", entity_threshold)
            relationship_threshold = decision.get("relationship_threshold", relationship_threshold)
            extraction_strategy = decision.get("extraction_strategy", extraction_strategy)
        
        return {
            "analysis": {
                "chunk_count": len(chunks),
                "total_text_length": total_text_length,
                "avg_chunk_length": avg_chunk_length,
                "complexity_indicators": complexity_indicators,
                "complexity": "high" if len(complexity_indicators) > 2 else "medium" if complexity_indicators else "low"
            },
            "recommendations": {
                "entity_threshold": entity_threshold,
                "relationship_threshold": relationship_threshold,
                "extraction_strategy": extraction_strategy,
                "max_entities_per_chunk": self._calculate_optimal_entity_limit(complexity_indicators, reasoning_result)
            }
        }
    
    def _calculate_optimal_entity_limit(self, complexity_indicators: List[str], reasoning_result) -> int:
        """Calculate optimal entity limit based on content complexity and reasoning."""
        
        # Base calculation
        if "entity_rich" in complexity_indicators:
            base_limit = 100
        elif "technical" in complexity_indicators:
            base_limit = 75
        else:
            base_limit = 50
        
        # Apply reasoning adjustments
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            if "max_entities" in decision.get("parameter_adjustments", {}):
                adjustment = decision["parameter_adjustments"]["max_entities"]
                if isinstance(adjustment, (int, float)):
                    base_limit = int(adjustment)
        
        return max(10, min(200, base_limit))
    
    async def _optimize_thresholds_with_reasoning(self, reasoning_result, content_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Optimize confidence thresholds based on reasoning and content analysis."""
        
        # Default thresholds
        thresholds = {
            "entity_confidence": self.entity_confidence_threshold,
            "relationship_confidence": self.relationship_confidence_threshold
        }
        
        # Apply reasoning optimizations
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            
            # Direct threshold adjustments
            if "entity_threshold" in decision:
                thresholds["entity_confidence"] = decision["entity_threshold"]
            if "relationship_threshold" in decision:
                thresholds["relationship_confidence"] = decision["relationship_threshold"]
            
            # Strategy-based adjustments
            strategy = decision.get("extraction_strategy", "balanced")
            if strategy == "precision_focused":
                thresholds["entity_confidence"] += 0.1
                thresholds["relationship_confidence"] += 0.15
            elif strategy == "recall_focused":
                thresholds["entity_confidence"] = max(0.4, thresholds["entity_confidence"] - 0.1)
                thresholds["relationship_confidence"] = max(0.3, thresholds["relationship_confidence"] - 0.1)
        
        # Content-based adjustments
        complexity = content_analysis.get("analysis", {}).get("complexity", "medium")
        if complexity == "high":
            # Higher thresholds for complex content to reduce noise
            thresholds["entity_confidence"] = min(0.9, thresholds["entity_confidence"] + 0.05)
            thresholds["relationship_confidence"] = min(0.9, thresholds["relationship_confidence"] + 0.1)
        elif complexity == "low":
            # Lower thresholds for simple content to capture more
            thresholds["entity_confidence"] = max(0.4, thresholds["entity_confidence"] - 0.05)
            thresholds["relationship_confidence"] = max(0.3, thresholds["relationship_confidence"] - 0.05)
        
        # Ensure valid ranges
        thresholds["entity_confidence"] = max(0.1, min(1.0, thresholds["entity_confidence"]))
        thresholds["relationship_confidence"] = max(0.1, min(1.0, thresholds["relationship_confidence"]))
        
        return thresholds
    
    async def _analyze_content(self, task: Task, start_time: float) -> Result:
        """Analyze content - extract entities and/or relationships."""
        # Get chunks from context or parameters
        chunks = self._get_chunks_from_task(task)
        
        if not chunks:
            return self._create_result(
                success=False,
                error="No chunks provided for analysis",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Determine what to extract
        extract_entities = task.task_type in ["analysis", "entity_extraction"]
        extract_relationships = task.task_type in ["analysis", "relationship_extraction"]
        
        all_entities = []
        all_relationships = []
        entity_errors = []
        relationship_errors = []
        
        # Process each chunk
        for chunk in chunks:
            chunk_ref = chunk.get("chunk_ref", "unknown")
            chunk_text = chunk.get("text", "")
            chunk_confidence = chunk.get("chunk_confidence", 0.8)
            
            if not chunk_text:
                self.logger.warning(f"Chunk {chunk_ref} has no text")
                continue
            
            # Extract entities if requested
            if extract_entities:
                entity_result = await self._extract_entities_from_chunk(
                    chunk_ref, chunk_text, chunk_confidence
                )
                
                if entity_result["success"]:
                    all_entities.extend(entity_result["entities"])
                else:
                    entity_errors.append(entity_result["error"])
            
            # Extract relationships if requested
            if extract_relationships:
                # Get entities for this chunk (either just extracted or from context)
                chunk_entities = []
                if extract_entities:
                    # Use entities we just extracted
                    chunk_entities = [e for e in all_entities if e.get("chunk_ref") == chunk_ref]
                else:
                    # Try to get from context
                    if task.context and "entities" in task.context:
                        chunk_entities = [e for e in task.context["entities"] 
                                        if e.get("chunk_ref") == chunk_ref]
                
                if chunk_entities:
                    rel_result = await self._extract_relationships_from_chunk(
                        chunk_ref, chunk_text, chunk_entities
                    )
                    
                    if rel_result["success"]:
                        all_relationships.extend(rel_result["relationships"])
                    else:
                        relationship_errors.append(rel_result["error"])
        
        # Compile results
        result_data = {
            "total_chunks_processed": len(chunks)
        }
        
        if extract_entities:
            result_data["entities"] = all_entities
            result_data["total_entities"] = len(all_entities)
            result_data["entity_types"] = self._count_entity_types(all_entities)
        
        if extract_relationships:
            result_data["relationships"] = all_relationships
            result_data["total_relationships"] = len(all_relationships)
            result_data["relationship_types"] = self._count_relationship_types(all_relationships)
        
        # Add warnings for any errors
        warnings = []
        if entity_errors:
            warnings.extend(entity_errors)
        if relationship_errors:
            warnings.extend(relationship_errors)
        
        self.logger.info(f"Analysis complete: {len(all_entities)} entities, "
                        f"{len(all_relationships)} relationships")
        
        return Result(
            success=True,
            data=result_data,
            warnings=warnings,
            execution_time=time.time() - start_time,
            agent_id=self.agent_id,
            task_id=task.task_id,
            metadata={
                "agent_type": self.agent_type,
                "task_type": task.task_type,
                "chunks_processed": len(chunks)
            }
        )
    
    async def _extract_entities_from_chunk(self, chunk_ref: str, text: str, 
                                         confidence: float) -> Dict[str, Any]:
        """Extract entities from a single chunk."""
        try:
            result = await self.mcp.call_tool("extract_entities", {
                "chunk_ref": chunk_ref,
                "text": text,
                "chunk_confidence": confidence
            })
            
            if result.success:
                entities = result.data.get("entities", [])
                self.logger.debug(f"Extracted {len(entities)} entities from chunk {chunk_ref}")
                return {"success": True, "entities": entities}
            else:
                error_msg = f"Entity extraction failed for chunk {chunk_ref}: {result.error}"
                self.logger.warning(error_msg)
                return {"success": False, "error": error_msg, "entities": []}
                
        except Exception as e:
            error_msg = f"Entity extraction error for chunk {chunk_ref}: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "entities": []}
    
    async def _extract_relationships_from_chunk(self, chunk_ref: str, text: str,
                                              entities: List[Dict]) -> Dict[str, Any]:
        """Extract relationships from a single chunk."""
        try:
            result = await self.mcp.call_tool("extract_relationships", {
                "chunk_ref": chunk_ref,
                "text": text,
                "entities": entities
            })
            
            if result.success:
                relationships = result.data.get("relationships", [])
                self.logger.debug(f"Extracted {len(relationships)} relationships from chunk {chunk_ref}")
                return {"success": True, "relationships": relationships}
            else:
                error_msg = f"Relationship extraction failed for chunk {chunk_ref}: {result.error}"
                self.logger.warning(error_msg)
                return {"success": False, "error": error_msg, "relationships": []}
                
        except Exception as e:
            error_msg = f"Relationship extraction error for chunk {chunk_ref}: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg, "relationships": []}
    
    def _get_chunks_from_task(self, task: Task) -> List[Dict]:
        """Get chunks from task parameters or context."""
        # Check parameters first
        chunks = task.parameters.get("chunks", [])
        
        if not chunks and task.context:
            # Check context for chunks
            if "chunks" in task.context:
                chunks = task.context["chunks"]
            elif "document_result" in task.context:
                # Try to get from document processing result
                doc_result = task.context["document_result"]
                if isinstance(doc_result, dict) and "chunks" in doc_result:
                    chunks = doc_result["chunks"]
        
        return chunks
    
    def _count_entity_types(self, entities: List[Dict]) -> Dict[str, int]:
        """Count entities by type."""
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    def _count_relationship_types(self, relationships: List[Dict]) -> Dict[str, int]:
        """Count relationships by type."""
        type_counts = {}
        for rel in relationships:
            rel_type = rel.get("relationship_type", "UNKNOWN")
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts