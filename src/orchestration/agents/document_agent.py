"""
Reasoning-enhanced document processing agent using KGAS MCP tools.

This agent handles document loading and text chunking using existing
T01 (PDF Loader) and T15A (Text Chunker) tools, with memory capabilities
and LLM reasoning for intelligent document processing decisions.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
from pathlib import Path

from ..base import Task, Result
from ..communicating_agent import CommunicatingAgent
from ..communication import MessageBus
from ..llm_reasoning import ReasoningType
from ..mcp_adapter import MCPToolAdapter

logger = logging.getLogger(__name__)


class DocumentAgent(CommunicatingAgent):
    """
    Reasoning-enhanced document processing agent.
    
    Uses existing KGAS tools with memory and LLM reasoning capabilities:
    - T01: PDF Loader (load_documents)
    - T15A: Text Chunker (chunk_text)
    
    Advanced features:
    - LLM reasoning for intelligent chunking strategy selection
    - Memory-based learning of optimal document processing patterns
    - Adaptive parameter optimization based on document characteristics
    - Strategic decision-making for complex document workflows
    """
    
    def __init__(self, mcp_adapter: MCPToolAdapter, agent_id: str = None, 
                 memory_config: Dict[str, Any] = None, reasoning_config: Dict[str, Any] = None,
                 communication_config: Dict[str, Any] = None, message_bus: MessageBus = None):
        """
        Initialize reasoning-enhanced document agent.
        
        Args:
            mcp_adapter: MCP tool adapter instance
            agent_id: Optional agent identifier
            memory_config: Memory system configuration
            reasoning_config: LLM reasoning configuration
            communication_config: Communication configuration
            message_bus: Message bus for inter-agent communication
        """
        super().__init__(
            agent_id or "document_agent",
            "document",
            memory_config,
            reasoning_config,
            communication_config,
            message_bus
        )
        self.mcp = mcp_adapter
        self.capabilities = [
            "document_processing",
            "load_documents", 
            "text_chunking",
            "pdf_processing",
            "collaborative_processing"
        ]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Document processing parameters (now dynamically optimized by reasoning)
        self.default_chunk_size = 1000
        self.default_overlap = 200
        self.confidence_threshold = 0.7
        
        # Reasoning-specific configuration
        self.chunk_strategy_reasoning = True
        self.document_type_analysis = True
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle task type."""
        return task_type in self.capabilities
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return self.capabilities.copy()
    
    async def _execute_with_memory(self, task: Task, memory_context: Dict[str, Any]) -> Result:
        """
        Execute document processing task with memory context.
        
        Supported task types:
        - document_processing: Load and chunk documents
        - load_documents: Just load documents
        - text_chunking: Just chunk text
        
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
            
            if task.task_type == "document_processing":
                return await self._process_documents_with_memory(task, memory_context, start_time)
            elif task.task_type == "load_documents":
                return await self._load_documents(task, start_time)
            elif task.task_type == "text_chunking":
                return await self._chunk_text_with_memory(task, memory_context, start_time)
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
            
            if task.task_type == "document_processing":
                return await self._process_documents(task, start_time)
            elif task.task_type == "load_documents":
                return await self._load_documents(task, start_time)
            elif task.task_type == "text_chunking":
                return await self._chunk_text(task, start_time)
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
        """Apply memory-based optimizations to task parameters."""
        # Get parameter recommendations from memory
        recommendations = await self.get_parameter_recommendations(task.task_type)
        
        if recommendations["confidence"] > 0.5:
            # Apply recommended parameters
            for param, value in recommendations["recommended_parameters"].items():
                if param not in task.parameters:
                    task.parameters[param] = value
                    self.logger.debug(f"Applied memory recommendation: {param}={value}")
        
        # Adapt chunking parameters based on learned patterns
        for pattern in memory_context.get("learned_patterns", []):
            if pattern.get("pattern_type") == f"{task.task_type}_chunking_strategy":
                pattern_data = pattern.get("pattern_data", {})
                if pattern_data.get("confidence", 0) > 0.7:
                    self.default_chunk_size = pattern_data.get("chunk_size", self.default_chunk_size)
                    self.default_overlap = pattern_data.get("overlap", self.default_overlap)
                    self.logger.debug(f"Applied learned chunking strategy: size={self.default_chunk_size}, overlap={self.default_overlap}")
    
    async def _process_documents_with_memory(self, task: Task, memory_context: Dict[str, Any], start_time: float) -> Result:
        """Process documents with memory-enhanced strategies."""
        # Use learned strategies if available
        strategies = await self.get_learned_strategies("document_processing")
        
        if strategies and await self.should_use_strategy(strategies[0]["name"]):
            self.logger.info(f"Using learned strategy: {strategies[0]['name']}")
            # Apply the learned strategy steps
            for step in strategies[0]["steps"]:
                if step["step"] == "prepare_parameters":
                    # Merge learned parameters with current ones
                    learned_params = step.get("parameters", {})
                    for key, value in learned_params.items():
                        if key not in task.parameters:
                            task.parameters[key] = value
        
        # Execute standard document processing with enhanced parameters
        result = await self._process_documents(task, start_time)
        
        # If successful, store the chunking strategy used
        if result.success and result.data:
            total_chunks = result.data.get("total_chunks", 0)
            total_docs = result.data.get("total_documents", 0)
            
            if total_chunks > 0 and total_docs > 0:
                avg_chunks_per_doc = total_chunks / total_docs
                
                await self.memory.store_learned_pattern(
                    pattern_type="document_processing_chunking_strategy",
                    pattern_data={
                        "chunk_size": self.default_chunk_size,
                        "overlap": self.default_overlap,
                        "avg_chunks_per_doc": avg_chunks_per_doc,
                        "total_documents": total_docs,
                        "confidence": 0.8 if avg_chunks_per_doc > 5 else 0.6
                    },
                    importance=0.7
                )
        
        return result
    
    async def _chunk_text_with_memory(self, task: Task, memory_context: Dict[str, Any], start_time: float) -> Result:
        """Chunk text with memory-based parameter optimization."""
        # Look for similar text chunking patterns in memory
        text_length = len(task.parameters.get("text", ""))
        
        # Find similar text lengths from memory
        for execution in memory_context.get("relevant_executions", []):
            if execution.get("task_type") == "text_chunking" and execution.get("success"):
                # This could help us estimate optimal chunk parameters
                # For now, just log the pattern
                self.logger.debug(f"Found similar successful chunking execution")
        
        # Apply learned chunking parameters if we don't have specific ones
        if "chunk_size" not in task.parameters:
            task.parameters["chunk_size"] = self.default_chunk_size
        if "overlap" not in task.parameters:
            task.parameters["overlap"] = self.default_overlap
        
        # Execute chunking
        result = await self._chunk_text(task, start_time)
        
        # Learn from the chunking result
        if result.success and result.data:
            chunks = result.data.get("chunks", [])
            if chunks:
                await self.memory.store_learned_pattern(
                    pattern_type="text_chunking_result",
                    pattern_data={
                        "text_length": text_length,
                        "chunk_count": len(chunks),
                        "chunk_size": task.parameters.get("chunk_size", self.default_chunk_size),
                        "overlap": task.parameters.get("overlap", self.default_overlap),
                        "chunks_per_kb": len(chunks) / max(1, text_length / 1000),
                        "confidence": 0.7
                    },
                    importance=0.6
                )
        
        return result
    
    async def _customize_reasoning_type(self, suggested_type: ReasoningType, task: Task, memory_context: Dict[str, Any]) -> ReasoningType:
        """Customize reasoning type for document processing tasks."""
        
        # Use strategic reasoning for complex document workflows
        if task.task_type == "document_processing":
            document_paths = task.parameters.get("document_paths", [])
            if len(document_paths) > 5:
                return ReasoningType.STRATEGIC
            elif len(document_paths) > 2:
                return ReasoningType.TACTICAL
        
        # Use adaptive reasoning if we have good memory context
        relevant_executions = memory_context.get("relevant_executions", [])
        if len(relevant_executions) >= 3:
            return ReasoningType.ADAPTIVE
        
        # Use diagnostic reasoning if there were recent failures
        recent_failures = [
            exec_info for exec_info in relevant_executions 
            if not exec_info.get("success", True)
        ]
        if recent_failures:
            return ReasoningType.DIAGNOSTIC
        
        # Default to suggested type
        return suggested_type
    
    async def _get_task_constraints(self, task: Task) -> Dict[str, Any]:
        """Get document processing specific constraints."""
        base_constraints = await super()._get_task_constraints(task)
        
        # Add document-specific constraints
        document_constraints = {
            "max_chunk_size": 10000,
            "min_chunk_size": 100,
            "max_overlap_ratio": 0.5,
            "min_confidence": 0.5,
            "max_documents_per_batch": 20,
            "memory_budget": "2GB"
        }
        
        return {**base_constraints, **document_constraints}
    
    async def _get_task_goals(self, task: Task) -> List[str]:
        """Get document processing specific goals."""
        base_goals = await super()._get_task_goals(task)
        
        # Add document-specific goals
        document_goals = [
            "Optimize chunking strategy for document characteristics",
            "Maximize information preservation during chunking",
            "Minimize processing time while maintaining quality",
            "Adapt chunk size based on document complexity",
            "Ensure consistent chunk quality across documents"
        ]
        
        return base_goals + document_goals
    
    async def _analyze_document_characteristics(self, documents: List[Dict], reasoning_result) -> Dict[str, Any]:
        """Analyze document characteristics for reasoning-based optimization."""
        
        if not documents:
            return {"analysis": "no_documents", "recommendations": {}}
        
        # Extract document characteristics
        total_length = sum(len(doc.get("content", "")) for doc in documents)
        avg_length = total_length / len(documents) if documents else 0
        
        # Document type analysis (basic heuristics)
        doc_types = []
        for doc in documents:
            content = doc.get("content", "")
            if len(content) < 1000:
                doc_types.append("short")
            elif len(content) > 10000:
                doc_types.append("long")
            else:
                doc_types.append("medium")
        
        # Apply reasoning decisions if available
        chunk_strategy = "adaptive_sizing"  # Default
        confidence_adjustment = 0.0
        
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            chunk_strategy = decision.get("chunk_strategy", chunk_strategy)
            confidence_adjustment = decision.get("confidence_threshold", 0.7) - 0.7
        
        return {
            "analysis": {
                "document_count": len(documents),
                "total_length": total_length,
                "avg_length": avg_length,
                "document_types": doc_types,
                "complexity": "high" if avg_length > 5000 else "medium" if avg_length > 1000 else "low"
            },
            "recommendations": {
                "chunk_strategy": chunk_strategy,
                "optimal_chunk_size": self._calculate_optimal_chunk_size(avg_length, reasoning_result),
                "optimal_overlap": self._calculate_optimal_overlap(doc_types, reasoning_result),
                "confidence_adjustment": confidence_adjustment
            }
        }
    
    def _calculate_optimal_chunk_size(self, avg_doc_length: float, reasoning_result) -> int:
        """Calculate optimal chunk size based on document characteristics and reasoning."""
        
        # Base calculation
        if avg_doc_length < 1000:
            base_size = 500
        elif avg_doc_length > 10000:
            base_size = 1500
        else:
            base_size = 1000
        
        # Apply reasoning adjustments
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            if "chunk_size" in decision.get("parameter_adjustments", {}):
                adjustment = decision["parameter_adjustments"]["chunk_size"]
                if isinstance(adjustment, (int, float)):
                    base_size = int(adjustment)
        
        return max(100, min(5000, base_size))
    
    def _calculate_optimal_overlap(self, doc_types: List[str], reasoning_result) -> int:
        """Calculate optimal overlap based on document types and reasoning."""
        
        # Base calculation
        if "long" in doc_types:
            base_overlap = 300
        elif "short" in doc_types:
            base_overlap = 100
        else:
            base_overlap = 200
        
        # Apply reasoning adjustments
        if reasoning_result and reasoning_result.success:
            decision = reasoning_result.decision
            if "overlap" in decision.get("parameter_adjustments", {}):
                adjustment = decision["parameter_adjustments"]["overlap"]
                if isinstance(adjustment, (int, float)):
                    base_overlap = int(adjustment)
        
        return max(50, min(1000, base_overlap))
    
    async def _process_documents(self, task: Task, start_time: float) -> Result:
        """Process documents - load and chunk."""
        # Get document paths from parameters
        document_paths = task.parameters.get("document_paths", [])
        
        if not document_paths:
            # Check context for document paths
            if task.context and "document_paths" in task.context:
                document_paths = task.context["document_paths"]
            else:
                return self._create_result(
                    success=False,
                    error="No document paths provided",
                    execution_time=time.time() - start_time,
                    task=task
                )
        
        # Ensure paths are strings
        if isinstance(document_paths, str):
            document_paths = [document_paths]
        
        # Load documents using T01 tool
        self.logger.debug(f"Loading {len(document_paths)} documents")
        doc_result = await self.mcp.call_tool("load_documents", {
            "document_paths": document_paths
        })
        
        if not doc_result.success:
            return self._create_result(
                success=False,
                error=f"Document loading failed: {doc_result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        documents = doc_result.data.get("documents", [])
        self.logger.info(f"Loaded {len(documents)} documents")
        
        # Chunk text from each document using T15A tool
        all_chunks = []
        chunk_errors = []
        
        for doc in documents:
            if "content" not in doc:
                self.logger.warning(f"Document {doc.get('document_id', 'unknown')} has no content")
                continue
            
            # Chunk the document
            chunk_result = await self.mcp.call_tool("chunk_text", {
                "document_ref": doc.get("document_id", "unknown"),
                "text": doc["content"],
                "document_confidence": doc.get("confidence", 0.8)
            })
            
            if chunk_result.success:
                chunks = chunk_result.data.get("chunks", [])
                all_chunks.extend(chunks)
                self.logger.debug(f"Created {len(chunks)} chunks from document {doc.get('document_id')}")
            else:
                error_msg = f"Chunking failed for document {doc.get('document_id')}: {chunk_result.error}"
                chunk_errors.append(error_msg)
                self.logger.warning(error_msg)
        
        # Create result
        result_data = {
            "documents": documents,
            "chunks": all_chunks,
            "total_documents": len(documents),
            "total_chunks": len(all_chunks),
            "document_paths": document_paths
        }
        
        # Add warnings if any chunking errors occurred
        warnings = chunk_errors if chunk_errors else []
        
        return self._create_result(
            success=True,
            data=result_data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def _load_documents(self, task: Task, start_time: float) -> Result:
        """Just load documents without chunking."""
        document_paths = task.parameters.get("document_paths", [])
        
        if not document_paths:
            return self._create_result(
                success=False,
                error="No document paths provided",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Load documents
        doc_result = await self.mcp.call_tool("load_documents", {
            "document_paths": document_paths
        })
        
        if not doc_result.success:
            return self._create_result(
                success=False,
                error=f"Document loading failed: {doc_result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        return self._create_result(
            success=True,
            data=doc_result.data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def _chunk_text(self, task: Task, start_time: float) -> Result:
        """Just chunk provided text."""
        text = task.parameters.get("text", "")
        document_ref = task.parameters.get("document_ref", "direct_text")
        document_confidence = task.parameters.get("document_confidence", 0.8)
        
        if not text:
            return self._create_result(
                success=False,
                error="No text provided for chunking",
                execution_time=time.time() - start_time,
                task=task
            )
        
        # Chunk text
        chunk_result = await self.mcp.call_tool("chunk_text", {
            "document_ref": document_ref,
            "text": text,
            "document_confidence": document_confidence
        })
        
        if not chunk_result.success:
            return self._create_result(
                success=False,
                error=f"Text chunking failed: {chunk_result.error}",
                execution_time=time.time() - start_time,
                task=task
            )
        
        return self._create_result(
            success=True,
            data=chunk_result.data,
            execution_time=time.time() - start_time,
            task=task
        )
    
    async def process_large_document_collaboratively(self, document_path: str, 
                                                   team_agents: List[str] = None) -> Result:
        """
        Process a large document collaboratively with other agents.
        
        Uses communication to distribute work and aggregate results.
        """
        start_time = time.time()
        
        # Load the document
        doc_result = await self.mcp.call_tool("load_documents", {
            "document_paths": [document_path]
        })
        
        if not doc_result.success or not doc_result.data.get("documents"):
            return self._create_result(
                success=False,
                error=f"Failed to load document: {doc_result.error}",
                execution_time=time.time() - start_time,
                task=None
            )
        
        document = doc_result.data["documents"][0]
        content = document.get("content", "")
        
        # If small document, process normally
        if len(content) < 10000:
            return await self._process_documents(
                Task(task_type="document_processing", parameters={"document_paths": [document_path]}),
                start_time
            )
        
        # For large documents, use collaborative processing
        self.logger.info(f"Large document detected ({len(content)} chars), using collaborative processing")
        
        # Find available document agents
        if not team_agents and self.communicator:
            available_agents = self.communicator.discover_agents(
                agent_type="document",
                capability="text_chunking"
            )
            team_agents = [
                agent.agent_id for agent in available_agents 
                if agent.agent_id != self.agent_id
            ][:3]  # Use up to 3 other agents
        
        if not team_agents:
            # No other agents available, process normally
            self.logger.info("No other agents available, processing document alone")
            return await self._process_documents(
                Task(task_type="document_processing", parameters={"document_paths": [document_path]}),
                start_time
            )
        
        # Split document into sections
        section_size = len(content) // (len(team_agents) + 1)
        sections = []
        
        for i in range(len(team_agents) + 1):
            start_idx = i * section_size
            end_idx = (i + 1) * section_size if i < len(team_agents) else len(content)
            sections.append({
                "section_id": i,
                "content": content[start_idx:end_idx],
                "start": start_idx,
                "end": end_idx
            })
        
        # Process first section locally
        local_result = await self._chunk_text(
            Task(task_type="text_chunking", parameters={
                "text": sections[0]["content"],
                "document_ref": f"{document.get('document_id', 'doc')}_section_0"
            }),
            start_time
        )
        
        all_chunks = local_result.data.get("chunks", []) if local_result.success else []
        
        # Distribute other sections to team agents
        collaboration_tasks = []
        for i, agent_id in enumerate(team_agents, 1):
            if i < len(sections):
                task_data = {
                    "task": "chunk_text_section",
                    "context": {
                        "text": sections[i]["content"],
                        "document_ref": f"{document.get('document_id', 'doc')}_section_{i}",
                        "section_info": {
                            "section_id": sections[i]["section_id"],
                            "start": sections[i]["start"],
                            "end": sections[i]["end"]
                        }
                    }
                }
                
                collaboration_tasks.append(
                    self.collaborate_with(agent_id, "chunk_text_section", task_data["context"])
                )
        
        # Wait for all collaborations to complete
        collaboration_results = await asyncio.gather(*collaboration_tasks, return_exceptions=True)
        
        # Aggregate results
        for i, result in enumerate(collaboration_results):
            if isinstance(result, dict) and result.get("result", {}).get("chunks"):
                chunks = result["result"]["chunks"]
                # Adjust chunk offsets based on section position
                section_start = sections[i + 1]["start"]
                for chunk in chunks:
                    if "start" in chunk:
                        chunk["start"] += section_start
                    if "end" in chunk:
                        chunk["end"] += section_start
                all_chunks.extend(chunks)
        
        # Sort chunks by position
        all_chunks.sort(key=lambda c: c.get("start", 0))
        
        # Broadcast completion
        if self.communicator:
            await self.broadcast_insight({
                "type": "collaborative_document_processed",
                "document_id": document.get("document_id", "unknown"),
                "total_chunks": len(all_chunks),
                "team_size": len(team_agents) + 1,
                "processing_time": time.time() - start_time
            })
        
        return self._create_result(
            success=True,
            data={
                "documents": [document],
                "chunks": all_chunks,
                "total_documents": 1,
                "total_chunks": len(all_chunks),
                "collaborative": True,
                "team_size": len(team_agents) + 1
            },
            execution_time=time.time() - start_time,
            task=None
        )
    
    async def handle_collaboration_request(self, message) -> Dict[str, Any]:
        """Handle incoming collaboration requests."""
        task_type = message.payload.get("task")
        
        if task_type == "chunk_text_section":
            # Extract section data
            context = message.payload.get("context", {})
            text = context.get("text", "")
            document_ref = context.get("document_ref", "section")
            
            # Process the section
            result = await self._chunk_text(
                Task(task_type="text_chunking", parameters={
                    "text": text,
                    "document_ref": document_ref
                }),
                time.time()
            )
            
            if result.success:
                return {
                    "accepted": True,
                    "result": result.data,
                    "agent_id": self.agent_id
                }
            else:
                return {
                    "accepted": False,
                    "error": result.error,
                    "agent_id": self.agent_id
                }
        
        # Default to parent handler
        return await super()._handle_collaboration_request(message)