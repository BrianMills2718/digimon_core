"""
Dynamic Execution Engine for Phase B
Implements actual dynamic tool execution based on question analysis
"""
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import logging
import time
from collections import defaultdict

from ..nlp.tool_chain_generator import ToolChain, ToolStep, ExecutionMode
from ..execution.mcp_executor import MCPExecutor, ExecutionResult
from ..nlp.question_parser import ExecutionPlan, ExecutionStep
from ..nlp.context_extractor import QuestionContext
from .programmatic_dependency_analyzer import ProgrammaticDependencyAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DynamicExecutionContext:
    """Context for dynamic execution decisions"""
    intermediate_results: Dict[str, Any]
    execution_times: Dict[str, float]
    skipped_tools: Set[str]
    adapted_parameters: Dict[str, Dict[str, Any]]
    parallel_groups_executed: List[List[str]]


class DynamicExecutor:
    """Execute tool chains dynamically based on Phase B analysis"""
    
    def __init__(self, mcp_executor: MCPExecutor):
        self.mcp_executor = mcp_executor
        self.execution_context = None
        self.dependency_analyzer = ProgrammaticDependencyAnalyzer()
        
    async def execute_dynamic_chain(self, 
                                  tool_chain: ToolChain,
                                  question: str,
                                  context: QuestionContext,
                                  current_document_path: Optional[str] = None) -> ExecutionResult:
        """Execute tool chain with dynamic adaptations"""
        
        logger.info(f"Starting dynamic execution for {len(tool_chain.steps)} steps")
        logger.info(f"Parallelization possible: {tool_chain.can_parallelize}")
        
        # Initialize execution context
        self.execution_context = DynamicExecutionContext(
            intermediate_results={},
            execution_times={},
            skipped_tools=set(),
            adapted_parameters={},
            parallel_groups_executed=[]
        )
        
        start_time = time.time()
        
        # Build execution groups (for parallelization)
        execution_groups = self._build_execution_groups(tool_chain)
        
        # Execute groups with dynamic parallel detection
        executed_tools = set()
        pending_tools = {step.tool_id: step for step in tool_chain.steps}
        
        while pending_tools:
            # Find tools that are ready to execute (dependencies satisfied)
            ready_tools = []
            for tool_id, step in pending_tools.items():
                if all(dep in executed_tools for dep in step.depends_on):
                    ready_tools.append(step)
            
            if not ready_tools:
                logger.error(f"No tools ready to execute. Pending: {list(pending_tools.keys())}")
                break
            
            # Check if any ready tools can run in parallel
            if len(ready_tools) > 1 and tool_chain.can_parallelize:
                logger.info(f"Multiple tools ready, checking for parallel opportunities: {[s.tool_id for s in ready_tools]}")
                
                # Find parallel opportunities among ready tools
                parallel_groups = self._find_parallel_groups(ready_tools)
                
                # Check if we actually found any parallel groups
                has_parallel = any(len(group) > 1 for group in parallel_groups)
                
                if has_parallel:
                    for group in parallel_groups:
                        if len(group) > 1:
                            # Execute parallel group
                            logger.info(f"🚀 EXECUTING TOOLS IN PARALLEL: {[s.tool_id for s in group]}")
                            await self._execute_parallel_group(group, question, context, current_document_path)
                            
                            # Mark as executed
                            for step in group:
                                executed_tools.add(step.tool_id)
                                del pending_tools[step.tool_id]
                        else:
                            # Execute single tool
                            step = group[0]
                            logger.info(f"Executing single tool: {step.tool_id}")
                            await self._execute_single_step(step, question, context, current_document_path)
                            executed_tools.add(step.tool_id)
                            del pending_tools[step.tool_id]
                else:
                    # No parallel opportunities found, execute sequentially
                    logger.debug("No parallel opportunities found, executing sequentially")
                    for step in ready_tools:
                        logger.info(f"Executing tool: {step.tool_id}")
                        await self._execute_single_step(step, question, context, current_document_path)
                        executed_tools.add(step.tool_id)
                        del pending_tools[step.tool_id]
            else:
                # Execute ready tools sequentially
                for step in ready_tools:
                    logger.info(f"Executing tool: {step.tool_id}")
                    await self._execute_single_step(step, question, context, current_document_path)
                    executed_tools.add(step.tool_id)
                    del pending_tools[step.tool_id]
        
        # Compile results
        total_time = time.time() - start_time
        
        return self._compile_dynamic_results(
            tool_chain=tool_chain,
            question=question,
            total_time=total_time
        )
    
    def _build_execution_groups(self, tool_chain: ToolChain) -> List[List[ToolStep]]:
        """Build execution groups for potential parallelization"""
        
        # Group tools by their dependency levels
        levels = self._compute_dependency_levels(tool_chain)
        
        # Create groups - tools at same level with no inter-dependencies can run in parallel
        max_level = max(levels.values()) if levels else 0
        groups = []
        
        for level in range(max_level + 1):
            level_steps = []
            for step in tool_chain.steps:
                if levels.get(step.tool_id, 0) == level:
                    level_steps.append(step)
            
            if level_steps:
                # Try to find parallel opportunities within this level
                if len(level_steps) > 1:
                    # Check if we can parallelize some tools at this level
                    parallel_groups = self._find_parallel_groups(level_steps)
                    groups.extend(parallel_groups)
                else:
                    # Single tool at this level
                    groups.append(level_steps)
        
        return groups
    
    def _find_parallel_groups(self, steps: List[ToolStep]) -> List[List[ToolStep]]:
        """Find groups of steps that can run in parallel using dynamic dependency analysis"""
        logger.info(f"Finding parallel groups for: {[s.tool_id for s in steps]}")
        
        # Use dependency analyzer to find parallel opportunities
        analysis = self.dependency_analyzer.analyze_dependencies(steps)
        
        logger.info(f"Dependency analysis found {len(analysis.parallel_groups)} groups")
        logger.info(f"Independent pairs: {analysis.independent_pairs}")
        
        # Convert tool IDs back to ToolStep objects
        step_map = {step.tool_id: step for step in steps}
        parallel_step_groups = []
        
        for group_ids in analysis.parallel_groups:
            step_group = [step_map[tool_id] for tool_id in group_ids if tool_id in step_map]
            parallel_step_groups.append(step_group)
            
            if len(step_group) > 1:
                logger.info(f"✅ Created dynamic parallel group: {[s.tool_id for s in step_group]}")
        
        return parallel_step_groups
    
    # Removed hardcoded _can_run_together - now using DependencyAnalyzer
    
    def _compute_dependency_levels(self, tool_chain: ToolChain) -> Dict[str, int]:
        """Compute dependency levels for each tool"""
        levels = {}
        
        # Build reverse dependency map
        dependents = defaultdict(list)
        for step in tool_chain.steps:
            for dep in step.depends_on:
                dependents[dep].append(step.tool_id)
        
        # BFS to compute levels
        queue = []
        for step in tool_chain.steps:
            if not step.depends_on:
                queue.append((step.tool_id, 0))
                levels[step.tool_id] = 0
        
        while queue:
            tool_id, level = queue.pop(0)
            
            for dependent in dependents[tool_id]:
                if dependent not in levels:
                    # Check if all dependencies are processed
                    dep_step = next(s for s in tool_chain.steps if s.tool_id == dependent)
                    if all(dep in levels for dep in dep_step.depends_on):
                        new_level = max(levels[dep] for dep in dep_step.depends_on) + 1
                        levels[dependent] = new_level
                        queue.append((dependent, new_level))
        
        # Log the levels for debugging
        logger.debug(f"Dependency levels: {levels}")
        
        return levels
    
    # Removed hardcoded _check_parallel_safety - now using DependencyAnalyzer
    
    async def _execute_parallel_group(self, group: List[ToolStep], 
                                    question: str,
                                    context: QuestionContext,
                                    current_document_path: Optional[str]):
        """Execute a group of tools in parallel"""
        
        logger.info(f"Executing {len(group)} tools in parallel: {[s.tool_id for s in group]}")
        
        # Start timing for parallel execution
        parallel_start = time.time()
        
        # Create coroutines for each tool in the group
        coroutines = []
        for step in group:
            # Create a coroutine for each tool execution
            coro = self._execute_single_step_async(step, question, context, current_document_path)
            coroutines.append(coro)
        
        # Execute all coroutines concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Calculate parallel execution time
        parallel_time = time.time() - parallel_start
        
        # Record parallel execution
        self.execution_context.parallel_groups_executed.append({
            'tools': [s.tool_id for s in group],
            'execution_time': parallel_time,
            'speedup': len(group) * 1.0  # Theoretical speedup factor
        })
        
        # Handle results and exceptions
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Parallel execution failed for {group[i].tool_id}: {result}")
                # Store error result
                self.execution_context.intermediate_results[group[i].tool_id] = {
                    'status': 'error',
                    'error': str(result),
                    'data': None
                }
            elif result is not None:
                success_count += 1
        
        logger.info(f"Parallel execution completed in {parallel_time:.2f}s. Success: {success_count}/{len(group)}")
    
    async def _execute_single_step(self, step: ToolStep,
                                 question: str,
                                 context: QuestionContext,
                                 current_document_path: Optional[str]):
        """Execute a single tool step with dynamic adaptations"""
        
        # Check if we should skip this tool based on intermediate results
        if self._should_skip_tool(step, context):
            logger.info(f"Skipping {step.tool_id} based on dynamic analysis")
            self.execution_context.skipped_tools.add(step.tool_id)
            return
        
        # Adapt parameters based on context and intermediate results
        adapted_params = self._adapt_parameters(step, context)
        
        # Convert ToolStep to ExecutionStep for MCP executor
        execution_step = self._convert_to_execution_step(step, adapted_params, current_document_path)
        
        # Resolve dependencies with intermediate results
        resolved_args = await self._resolve_dependencies(execution_step)
        
        # Execute via MCP
        start_time = time.time()
        
        try:
            result = await self.mcp_executor._execute_single_tool(
                execution_step.tool_id,
                resolved_args
            )
            
            # Store result and timing
            self.execution_context.intermediate_results[step.tool_id] = result
            self.execution_context.execution_times[step.tool_id] = time.time() - start_time
            
            # Adapt future steps based on this result
            self._adapt_future_steps(step.tool_id, result)
            
        except Exception as e:
            logger.error(f"Failed to execute {step.tool_id}: {e}")
            self.execution_context.intermediate_results[step.tool_id] = {
                'status': 'error',
                'error': str(e),
                'data': None
            }
    
    async def _execute_single_step_async(self, step: ToolStep,
                                       question: str,
                                       context: QuestionContext,
                                       current_document_path: Optional[str]):
        """Async wrapper for single step execution (for parallel execution)"""
        # This is just an alias for parallel execution
        await self._execute_single_step(step, question, context, current_document_path)
    
    def _should_skip_tool(self, step: ToolStep, context: QuestionContext) -> bool:
        """Determine if a tool should be skipped based on dynamic conditions"""
        
        # Skip relationship extractor if no entities found
        if step.tool_id == "T27_RELATIONSHIP_EXTRACTOR":
            ner_result = self.execution_context.intermediate_results.get("T23A_SPACY_NER", {})
            if ner_result.get('status') == 'success':
                entities = ner_result.get('data', {}).get('entities', [])
                if len(entities) < 2:
                    logger.info("Skipping relationship extraction - insufficient entities")
                    return True
        
        # Skip PageRank if graph is too small
        if step.tool_id == "T68_PAGE_RANK":
            entity_result = self.execution_context.intermediate_results.get("T31_ENTITY_BUILDER", {})
            if entity_result.get('status') == 'success':
                entity_count = entity_result.get('data', {}).get('entity_count', 0)
                if entity_count < 3:
                    logger.info("Skipping PageRank - graph too small")
                    return True
        
        # Skip multi-hop query if no complex relationships
        if step.tool_id == "T49_MULTI_HOP_QUERY":
            edge_result = self.execution_context.intermediate_results.get("T34_EDGE_BUILDER", {})
            if edge_result.get('status') == 'success':
                edge_count = edge_result.get('data', {}).get('edge_count', 0)
                if edge_count < 2:
                    logger.info("Skipping multi-hop query - insufficient edges")
                    return True
        
        return False
    
    def _adapt_parameters(self, step: ToolStep, context: QuestionContext) -> Dict[str, Any]:
        """Adapt tool parameters based on context"""
        
        adapted = step.parameters.copy()
        
        # Adapt based on temporal context
        if context and context.has_temporal_context and context.temporal_constraints:
            if step.tool_id in ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]:
                # Add temporal filtering to parameters
                adapted['time_filter'] = context.temporal_constraints[0]
                adapted['temporal_filtering_enabled'] = True
                logger.info(f"Adding temporal filter to {step.tool_id}: {context.temporal_constraints[0]}")
        
        # Adapt chunk size based on complexity
        if step.tool_id == "T15A_TEXT_CHUNKER":
            # Use aggregation requirements as a proxy for detailed analysis needs
            if context and (context.requires_aggregation or len(context.mentioned_entities) > 3):
                adapted['chunk_size'] = 500  # Smaller chunks for detailed analysis
            else:
                adapted['chunk_size'] = 1000  # Standard chunk size
        
        # Adapt NER confidence threshold based on ambiguity
        if step.tool_id == "T23A_SPACY_NER":
            if context and context.ambiguity_level > 0.5:
                adapted['confidence_threshold'] = 0.7  # Higher threshold for ambiguous questions
            else:
                adapted['confidence_threshold'] = 0.5  # Standard threshold
        
        # Adapt relationship extractor for comparison questions
        if step.tool_id == "T27_RELATIONSHIP_EXTRACTOR" and context and context.requires_comparison:
            adapted['extract_comparison_relationships'] = True
            adapted['comparison_entities'] = context.mentioned_entities
        
        # Adapt PageRank for importance ranking
        if step.tool_id == "T68_PAGE_RANK":
            # Increase iterations for complex questions (using aggregation as proxy)
            if context and (context.requires_aggregation or context.requires_comparison):
                adapted['max_iterations'] = 150
                adapted['tolerance'] = 1e-7
            # For entity-specific questions, boost those entities
            if context and context.mentioned_entities:
                adapted['boost_entities'] = context.mentioned_entities
                adapted['boost_factor'] = 2.0
        
        # Store adapted parameters
        if adapted != step.parameters:
            self.execution_context.adapted_parameters[step.tool_id] = adapted
        
        return adapted
    
    def _convert_to_execution_step(self, tool_step: ToolStep, 
                                 parameters: Dict[str, Any],
                                 current_document_path: Optional[str]) -> ExecutionStep:
        """Convert ToolStep to ExecutionStep format"""
        
        arguments = {
            "input_data": {},
            "parameters": parameters,
            "context": {}
        }
        
        # Special handling for T01_PDF_LOADER
        if tool_step.tool_id == "T01_PDF_LOADER" and current_document_path:
            arguments["input_data"]["file_path"] = current_document_path
        
        return ExecutionStep(
            tool_id=tool_step.tool_id,
            arguments=arguments,
            depends_on=tool_step.depends_on,
            optional=tool_step.optional
        )
    
    async def _resolve_dependencies(self, step: ExecutionStep) -> Dict[str, Any]:
        """Resolve dependencies using intermediate results"""
        
        resolved = step.arguments.copy()
        
        # Map intermediate results to input data
        for dep_tool in step.depends_on:
            if dep_tool in self.execution_context.intermediate_results:
                dep_result = self.execution_context.intermediate_results[dep_tool]
                
                if dep_result.get('status') == 'success':
                    # Use the existing resolution logic from MCPExecutor
                    resolved = await self.mcp_executor._resolve_step_dependencies(
                        step,
                        self.execution_context.intermediate_results
                    )
        
        return resolved
    
    def _adapt_future_steps(self, completed_tool: str, result: Dict[str, Any]):
        """Adapt future steps based on intermediate results"""
        
        # If NER found many entities, we might want to increase PageRank iterations
        if completed_tool == "T23A_SPACY_NER" and result.get('status') == 'success':
            entities = result.get('data', {}).get('entities', [])
            if len(entities) > 50:
                logger.info(f"Found {len(entities)} entities - adapting future steps")
                # This information can be used by PageRank when it executes
    
    def _compile_dynamic_results(self, tool_chain: ToolChain, 
                                question: str,
                                total_time: float) -> ExecutionResult:
        """Compile results from dynamic execution"""
        
        # Calculate success/failure counts
        success_count = sum(
            1 for r in self.execution_context.intermediate_results.values()
            if r.get('status') == 'success'
        )
        failure_count = len(self.execution_context.intermediate_results) - success_count
        
        # Collect errors
        errors = [
            f"{tool}: {r['error']}"
            for tool, r in self.execution_context.intermediate_results.items()
            if r.get('status') == 'error'
        ]
        
        # Build enhanced metadata
        execution_metadata = {
            'original_question': question,
            'tools_executed': list(self.execution_context.intermediate_results.keys()),
            'tools_skipped': list(self.execution_context.skipped_tools),
            'execution_time': total_time,
            'timestamp': time.time(),
            'parallelized': len(self.execution_context.parallel_groups_executed) > 0,
            'parallel_groups': self.execution_context.parallel_groups_executed,
            'execution_strategy': 'parallel_advanced' if tool_chain.can_parallelize else 'sequential',
            'adapted_parameters': self.execution_context.adapted_parameters,
            'execution_times_breakdown': self.execution_context.execution_times
        }
        
        return ExecutionResult(
            tool_outputs=self.execution_context.intermediate_results,
            execution_metadata=execution_metadata,
            total_execution_time=total_time,
            success_count=success_count,
            failure_count=failure_count,
            errors=errors
        )