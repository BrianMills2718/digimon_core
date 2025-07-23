# CLAUDE.md Implementation Validation Bundle

## Validation Request
Validate the CLAUDE.md implementation claims by examining the specific files included. For each claim:

**VALIDATION CRITERIA:**
1. **Implementation Present**: Does the claimed feature/documentation exist in the specified file?
2. **Functionality Complete**: Is it fully implemented (not a stub, template, or placeholder)?
3. **Requirements Met**: Does it satisfy the specific requirements mentioned in the claim?
4. **Evidence Quality**: Are status claims backed by actual evidence rather than assumptions?

**FOR EACH CLAIM, PROVIDE:**
- **Status**: ✅ FULLY RESOLVED / ⚠️ PARTIALLY RESOLVED / ❌ NOT RESOLVED
- **Evidence**: Specific file paths and line numbers where implementation is found
- **Assessment**: What was implemented vs what was claimed
- **Issues**: Any gaps between claims and actual implementation

**FOCUS ON:**
- Architecture documentation completeness and implementation guidance quality
- Tool validation methodology (real testing vs mocks/stubs)
- Tool registry accuracy and conflict resolution implementation
- Roadmap honesty (evidence-based vs inflated claims)
- Overall adherence to fail-fast principles

**BE ESPECIALLY CRITICAL OF:**
- Any documentation that lacks implementation detail
- Tool validation that uses mocks instead of real testing
- Status claims not backed by concrete evidence
- Roadmap percentages that don't match validation results
- Any evidence of deceptive practices or inflated capabilities

Provide a line-by-line analysis where possible, referencing specific implementations found in the included files.


## Claims to Validate
CLAIM 1: Architecture documentation is comprehensive and separated from implementation status
- LOCATION: docs/architecture/architecture_overview.md
- EXPECTED: Document describes target architecture without claiming current implementation
- VALIDATION: Check for clear "*Status: Target Architecture*" indicators and separation of design from status

CLAIM 2: AnyIO concurrency strategy is fully documented with implementation patterns  
- LOCATION: docs/architecture/concurrency-strategy.md
- EXPECTED: Complete AnyIO patterns with code examples for structured concurrency
- VALIDATION: Verify async/await patterns, task groups, resource management examples

CLAIM 3: Multi-layer agent interface architecture is documented (3 layers)
- LOCATION: docs/architecture/agent-interface.md  
- EXPECTED: Layer 1 (Agent-Controlled), Layer 2 (Agent-Assisted), Layer 3 (Manual Control) fully described
- VALIDATION: Check for complete architectural descriptions of all 3 layers with implementation details

CLAIM 4: LLM-ontology integration architecture is documented with theory-driven validation
- LOCATION: docs/architecture/llm-ontology-integration.md
- EXPECTED: Theory-aware extraction, ontological validation, confidence scoring architecture
- VALIDATION: Verify comprehensive integration patterns with domain ontology generation

CLAIM 5: Cross-modal analysis architecture is documented with format conversion capabilities  
- LOCATION: docs/architecture/cross-modal-analysis.md
- EXPECTED: Graph/Table/Vector representation modes with conversion architecture
- VALIDATION: Check for detailed cross-modal conversion patterns and provenance tracking

CLAIM 6: Tool inventory validation is comprehensive with real functional testing
- LOCATION: validate_tool_inventory.py
- EXPECTED: Real import attempts, class instantiation, execution testing with error capture
- VALIDATION: Verify functional testing methods, not mocks or stubs

CLAIM 7: Tool registry accurately reflects validation results with conflict tracking
- LOCATION: src/core/tool_registry.py  
- EXPECTED: Registry contains actual validation status, version conflicts, missing tools
- VALIDATION: Check ToolRegistry class with comprehensive conflict and status tracking

CLAIM 8: Tool conflict resolution strategy is implemented with archival approach
- LOCATION: resolve_tool_conflicts.py
- EXPECTED: Version conflict resolution with safe archival (no deletion)
- VALIDATION: Verify ToolConflictResolver class with archival strategy implementation

CLAIM 9: Roadmap reflects evidence-based status assessment (0.0% MVRT completion)
- LOCATION: docs/planning/roadmap_overview.md
- EXPECTED: Honest assessment showing 0% completion with evidence backing
- VALIDATION: Check for realistic completion percentages and evidence-based claims

CLAIM 10: All documentation follows fail-fast principles and evidence-based claims
- LOCATION: All architecture and roadmap files
- EXPECTED: No inflated claims, problems exposed immediately, evidence backing
- VALIDATION: Verify realistic assessments and evidence-based documentation throughout


## Implementation Files


### File: docs/architecture/concurrency-strategy.md

```
# AnyIO Structured Concurrency Architecture

*Status: Target Architecture*

## Overview

KGAS implements structured concurrency using AnyIO to provide reliable, predictable asynchronous operations with automatic resource management and cancellation.

## Design Principles

### Structured Concurrency Benefits
- **Automatic cancellation**: Task groups ensure all child tasks are cancelled if parent fails
- **Resource management**: Async context managers guarantee proper cleanup
- **Error propagation**: Exceptions bubble up predictably through task hierarchy
- **Deadlock prevention**: Structured approach prevents common async pitfalls

### Performance Characteristics
- **Rate limiting**: Built-in backpressure control prevents resource exhaustion
- **Monitoring**: Real-time performance tracking with evidence logging
- **Scalability**: Efficient handling of concurrent operations within single-node constraints

## Implementation Patterns

### Core Task Group Pattern
```python
async def execute_parallel_tasks(tasks: List[Task]) -> Dict[str, Any]:
    """Execute multiple tasks concurrently with structured cancellation."""
    results = {}
    
    async with anyio.create_task_group() as task_group:
        for task in tasks:
            task_group.start_soon(
                self._execute_single_task, 
                task, 
                results
            )
    
    return results

async def _execute_single_task(self, task: Task, results: Dict[str, Any]) -> None:
    """Execute single task with error handling and result storage."""
    try:
        result = await task.execute_async()
        results[task.id] = {
            "status": "success",
            "data": result,
            "execution_time": task.execution_time
        }
    except Exception as e:
        results[task.id] = {
            "status": "error", 
            "error": str(e),
            "execution_time": task.execution_time
        }
        # Error propagates to task group for structured handling
        raise
```

### Resource Management Pattern
```python
class AsyncResourceManager:
    """Manages async resources with automatic cleanup."""
    
    async def __aenter__(self):
        # Initialize async resources
        self.neo4j_session = await self.neo4j_driver.session()
        self.api_client = await self.create_api_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Guaranteed cleanup regardless of success/failure
        await self.neo4j_session.close()
        await self.api_client.close()

# Usage pattern
async def process_with_resources(data):
    async with AsyncResourceManager() as resources:
        return await resources.process(data)
    # Resources automatically cleaned up
```

### Rate Limiting and Backpressure
```python
class RateLimitedProcessor:
    """Implements rate limiting with AnyIO semaphores."""
    
    def __init__(self, max_concurrent: int = 10, rate_per_second: float = 5.0):
        self.semaphore = anyio.Semaphore(max_concurrent)
        self.rate_limiter = anyio.to_thread.current_default_thread_limiter()
        self.rate_per_second = rate_per_second
    
    async def process_batch(self, items: List[Any]) -> List[Any]:
        """Process items with rate limiting."""
        results = []
        
        async with anyio.create_task_group() as task_group:
            for item in items:
                task_group.start_soon(self._rate_limited_process, item, results)
        
        return results
    
    async def _rate_limited_process(self, item: Any, results: List[Any]) -> None:
        """Process single item with rate limiting."""
        async with self.semaphore:  # Limit concurrent operations
            await anyio.sleep(1.0 / self.rate_per_second)  # Rate limiting
            result = await self._process_item(item)
            results.append(result)
```

## Tool Contract Integration

### Async Tool Interface
```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class KGASTool(ABC):
    """Base tool contract with async support."""
    
    @abstractmethod
    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """Async execution method - primary interface."""
        pass
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Sync wrapper for backward compatibility."""
        return anyio.run(self.execute_async, **kwargs)
    
    async def validate_inputs(self, **kwargs) -> None:
        """Async input validation."""
        pass
    
    async def cleanup_resources(self) -> None:
        """Async resource cleanup."""
        pass

# Implementation example
class TextEmbedder(KGASTool):
    async def execute_async(self, texts: List[str]) -> Dict[str, Any]:
        """Embed texts using async API calls."""
        async with self.rate_limited_client() as client:
            embeddings = []
            
            async with anyio.create_task_group() as task_group:
                for text in texts:
                    task_group.start_soon(
                        self._embed_single_text, 
                        text, 
                        embeddings, 
                        client
                    )
            
            return {"embeddings": embeddings}
```

### Error Handling Strategy
```python
class StructuredErrorHandler:
    """Centralized error handling for async operations."""
    
    async def execute_with_recovery(self, operation, *args, **kwargs):
        """Execute operation with structured error handling."""
        try:
            return await operation(*args, **kwargs)
        except anyio.get_cancelled_exc_class():
            # Handle cancellation gracefully
            await self._cleanup_cancelled_operation(operation)
            raise
        except Exception as e:
            # Log error with context
            await self._log_error(operation, e, args, kwargs)
            
            # Attempt recovery if configured
            if hasattr(operation, 'recovery_strategy'):
                return await operation.recovery_strategy(e)
            
            # Fail fast - propagate error
            raise

    async def _cleanup_cancelled_operation(self, operation):
        """Clean up resources from cancelled operation."""
        if hasattr(operation, 'cleanup_resources'):
            await operation.cleanup_resources()
```

## Performance Monitoring

### Execution Tracking
```python
class PerformanceMonitor:
    """Monitor async operation performance."""
    
    async def track_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Track operation performance with evidence logging."""
        start_time = anyio.current_time()
        memory_start = self._get_memory_usage()
        
        try:
            result = await operation_func(*args, **kwargs)
            
            execution_time = anyio.current_time() - start_time
            memory_delta = self._get_memory_usage() - memory_start
            
            # Log performance evidence
            self.logger.info(f"{operation_name} completed", extra={
                "execution_time": execution_time,
                "memory_delta": memory_delta,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            execution_time = anyio.current_time() - start_time
            
            self.logger.error(f"{operation_name} failed", extra={
                "execution_time": execution_time,
                "error": str(e),
                "status": "error",
                "timestamp": datetime.now().isoformat()
            })
            
            raise
```

## Integration with Core Services

### Service Manager Pattern
```python
class AsyncServiceManager:
    """Manages core services with async lifecycle."""
    
    async def __aenter__(self):
        """Initialize all core services."""
        async with anyio.create_task_group() as task_group:
            # Initialize services concurrently
            task_group.start_soon(self._init_neo4j_service)
            task_group.start_soon(self._init_api_clients)
            task_group.start_soon(self._init_provenance_service)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Shutdown all services gracefully."""
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(self._shutdown_neo4j_service)
            task_group.start_soon(self._shutdown_api_clients)
            task_group.start_soon(self._shutdown_provenance_service)

# Usage in application
async def run_kgas_pipeline(workflow_config):
    """Run KGAS pipeline with structured concurrency."""
    async with AsyncServiceManager() as services:
        async with anyio.create_task_group() as task_group:
            # Execute workflow phases concurrently where possible
            for phase in workflow_config.phases:
                if phase.can_run_parallel:
                    task_group.start_soon(services.execute_phase, phase)
                else:
                    await services.execute_phase(phase)
```

## Migration Strategy

### Gradual Async Adoption
```python
class ToolAdapter:
    """Adapter for gradual migration to async tools."""
    
    def __init__(self, tool):
        self.tool = tool
        self.is_async = hasattr(tool, 'execute_async')
    
    async def execute(self, **kwargs):
        """Execute tool with async/sync compatibility."""
        if self.is_async:
            return await self.tool.execute_async(**kwargs)
        else:
            # Run sync tool in thread pool
            return await anyio.to_thread.run_sync(
                self.tool.execute, **kwargs
            )

# Enables gradual migration while maintaining compatibility
async def execute_mixed_tools(tools: List[KGASTool], inputs):
    """Execute mix of async and sync tools."""
    results = {}
    
    async with anyio.create_task_group() as task_group:
        for tool in tools:
            adapter = ToolAdapter(tool)
            task_group.start_soon(
                adapter.execute,
                **inputs[tool.id]
            )
    
    return results
```

## Benefits and Trade-offs

### Benefits
- **Predictable cancellation**: No orphaned tasks or resource leaks
- **Automatic cleanup**: Context managers ensure resource management
- **Clear error handling**: Structured exception propagation
- **Performance monitoring**: Built-in tracking and evidence generation
- **Scalability**: Efficient concurrent processing within node constraints

### Trade-offs
- **Learning curve**: Requires understanding of structured concurrency concepts
- **Migration effort**: Existing sync code needs adaptation
- **Complexity**: More complex than simple threading for simple cases

### Performance Expectations
- **40-50% pipeline performance improvement** through parallelization
- **Reduced resource usage** through structured cleanup
- **Better error recovery** through predictable cancellation
- **Enhanced monitoring** through async performance tracking

## Implementation Priority

### Phase 1: Core Infrastructure
1. **AsyncServiceManager**: Core service lifecycle management
2. **ToolAdapter**: Backward compatibility layer
3. **PerformanceMonitor**: Evidence-based performance tracking

### Phase 2: Tool Migration
1. **High-impact tools**: Text processing, API calls, embedding generation
2. **Workflow integration**: Pipeline orchestration with structured concurrency
3. **Error handling**: Robust error recovery and cleanup

### Phase 3: Optimization
1. **Rate limiting**: Advanced backpressure control
2. **Resource monitoring**: Real-time resource usage tracking
3. **Performance tuning**: Fine-tune concurrency parameters

This structured concurrency architecture provides the foundation for reliable, high-performance async operations while maintaining the fail-fast philosophy and evidence-based validation required by KGAS.
```


### File: docs/architecture/agent-interface.md

```
# Multi-Layer Agent Interface Architecture

## Overview

KGAS implements a three-layer agent interface that provides different levels of automation and user control, from complete automation to expert-level manual control. This architecture balances ease of use with the precision required for academic research.

## Design Principles

### Progressive Control Model
- **Layer 1**: Full automation for simple research tasks
- **Layer 2**: Assisted automation with user review and approval
- **Layer 3**: Complete manual control for expert users

### Research-Oriented Design
- **Academic workflow support**: Designed for research methodologies
- **Reproducibility**: All workflows generate reproducible YAML configurations
- **Transparency**: Clear visibility into all processing steps
- **Flexibility**: Support for diverse research questions and methodologies

## Three-Layer Architecture

### Layer 1: Agent-Controlled Interface

```
┌─────────────────────────────────────────────────────────┐
│                  Layer 1: Agent-Controlled              │
│                                                         │
│  Natural Language → LLM Analysis → YAML → Execution    │
│                                                         │
│  "Analyze sentiment in these                            │
│   customer reviews"                                     │
│              ↓                                          │
│  [Automated workflow generation and execution]          │
│              ↓                                          │
│  Complete results with source links                     │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class AgentControlledInterface:
    """Layer 1: Complete automation for simple research tasks."""
    
    def __init__(self, llm_client, workflow_engine, service_manager):
        self.llm_client = llm_client
        self.workflow_engine = workflow_engine
        self.service_manager = service_manager
    
    async def process_natural_language_request(self, request: str, documents: List[str]) -> Dict[str, Any]:
        """Process request from natural language to results."""
        
        # Step 1: Analyze request and generate workflow
        workflow_yaml = await self._generate_workflow(request, documents)
        
        # Step 2: Execute workflow automatically
        execution_result = await self.workflow_engine.execute(workflow_yaml)
        
        # Step 3: Format results for user
        formatted_results = await self._format_results(execution_result)
        
        return {
            "request": request,
            "generated_workflow": workflow_yaml,
            "execution_result": execution_result,
            "formatted_results": formatted_results,
            "source_provenance": execution_result.get("provenance", [])
        }
    
    async def _generate_workflow(self, request: str, documents: List[str]) -> str:
        """Generate YAML workflow from natural language request."""
        
        prompt = f"""
        Generate a KGAS workflow YAML for this research request:
        "{request}"
        
        Documents available: {len(documents)} files
        
        Generate a complete workflow that:
        1. Processes the documents appropriately
        2. Extracts relevant entities and relationships
        3. Performs the analysis needed to answer the request
        4. Provides results with source traceability
        
        Use KGAS workflow format with proper tool selection.
        """
        
        response = await self.llm_client.generate(prompt)
        return self._extract_yaml_from_response(response)

# Usage example
agent = AgentControlledInterface(llm_client, workflow_engine, services)
results = await agent.process_natural_language_request(
    "What are the main themes in these research papers?", 
    ["paper1.pdf", "paper2.pdf"]
)
```

#### Supported Use Cases
- **Simple content analysis**: Theme extraction, sentiment analysis
- **Basic entity extraction**: People, organizations, concepts from documents
- **Straightforward queries**: "What are the main findings?", "Who are the key authors?"
- **Standard workflows**: Common research patterns with established methodologies

### Layer 2: Agent-Assisted Interface

```
┌─────────────────────────────────────────────────────────┐
│                  Layer 2: Agent-Assisted                │
│                                                         │
│  Natural Language → YAML Generation → User Review →     │
│  User Approval/Editing → Execution                      │
│                                                         │
│  "Perform network analysis on                           │
│   co-authorship patterns"                               │
│              ↓                                          │
│  [Generated YAML workflow]                              │
│              ↓                                          │
│  User reviews and modifies workflow                     │
│              ↓                                          │
│  Approved workflow executed                             │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class AgentAssistedInterface:
    """Layer 2: Agent-generated workflows with user review."""
    
    async def generate_workflow_for_review(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow and present for user review."""
        
        # Generate initial workflow
        generated_workflow = await self._generate_detailed_workflow(request, context)
        
        # Validate workflow structure
        validation_result = await self.workflow_engine.validate(generated_workflow)
        
        # Prepare for user review
        review_package = {
            "original_request": request,
            "generated_workflow": generated_workflow,
            "validation": validation_result,
            "explanation": await self._explain_workflow(generated_workflow),
            "suggested_modifications": await self._suggest_improvements(generated_workflow),
            "estimated_execution_time": await self._estimate_execution_time(generated_workflow)
        }
        
        return review_package
    
    async def execute_reviewed_workflow(self, workflow_yaml: str, user_modifications: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow after user review and approval."""
        
        # Apply user modifications
        final_workflow = await self._apply_user_modifications(workflow_yaml, user_modifications)
        
        # Final validation
        validation = await self.workflow_engine.validate(final_workflow)
        if not validation.is_valid:
            raise WorkflowValidationError(validation.errors)
        
        # Execute with user approval
        return await self.workflow_engine.execute(final_workflow)
    
    async def _explain_workflow(self, workflow_yaml: str) -> str:
        """Generate human-readable explanation of workflow."""
        
        prompt = f"""
        Explain this KGAS workflow in plain language:
        
        {workflow_yaml}
        
        Focus on:
        1. What data processing steps will occur
        2. What analysis methods will be used
        3. What outputs will be generated
        4. Any potential limitations or considerations
        """
        
        return await self.llm_client.generate(prompt)

# User interface for workflow review
class WorkflowReviewInterface:
    """Interface for reviewing and modifying generated workflows."""
    
    def display_workflow_review(self, review_package: Dict[str, Any]) -> None:
        """Display workflow for user review."""
        
        print("Generated Workflow Review")
        print("=" * 50)
        print(f"Original Request: {review_package['original_request']}")
        print(f"Estimated Execution Time: {review_package['estimated_execution_time']}")
        print()
        
        print("Workflow Explanation:")
        print(review_package['explanation'])
        print()
        
        print("Generated YAML:")
        print(review_package['generated_workflow'])
        print()
        
        if review_package['suggested_modifications']:
            print("Suggested Improvements:")
            for suggestion in review_package['suggested_modifications']:
                print(f"- {suggestion}")
    
    def get_user_modifications(self) -> Dict[str, Any]:
        """Get user modifications to the workflow."""
        # Interactive interface for workflow editing
        pass
```

#### Supported Use Cases
- **Complex analysis tasks**: Multi-step analysis requiring parameter tuning
- **Research methodology verification**: Ensuring workflow matches research standards
- **Parameter optimization**: Adjusting confidence thresholds, analysis parameters
- **Novel research questions**: Questions requiring custom workflow adaptation

### Layer 3: Manual Control Interface

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 3: Manual Control               │
│                                                         │
│  Direct YAML Authoring → Validation → Execution        │
│                                                         │
│  User writes complete YAML workflow specification       │
│              ↓                                          │
│  System validates workflow structure and dependencies   │
│              ↓                                          │
│  Workflow executed with full user control              │
└─────────────────────────────────────────────────────────┘
```

#### Component Design
```python
class ManualControlInterface:
    """Layer 3: Direct YAML workflow authoring and execution."""
    
    def __init__(self, workflow_engine, schema_validator, service_manager):
        self.workflow_engine = workflow_engine
        self.schema_validator = schema_validator
        self.service_manager = service_manager
    
    async def validate_workflow(self, workflow_yaml: str) -> ValidationResult:
        """Comprehensive workflow validation."""
        
        # Parse YAML
        try:
            workflow_dict = yaml.safe_load(workflow_yaml)
        except yaml.YAMLError as e:
            return ValidationResult(False, [f"YAML parsing error: {e}"])
        
        # Schema validation
        schema_validation = await self.schema_validator.validate(workflow_dict)
        
        # Dependency validation
        dependency_validation = await self._validate_dependencies(workflow_dict)
        
        # Resource validation
        resource_validation = await self._validate_resources(workflow_dict)
        
        return ValidationResult.combine([
            schema_validation,
            dependency_validation, 
            resource_validation
        ])
    
    async def execute_workflow(self, workflow_yaml: str) -> ExecutionResult:
        """Execute manually authored workflow."""
        
        # Validate before execution
        validation = await self.validate_workflow(workflow_yaml)
        if not validation.is_valid:
            raise WorkflowValidationError(validation.errors)
        
        # Execute with full logging
        return await self.workflow_engine.execute(workflow_yaml, verbose=True)
    
    def get_workflow_schema(self) -> Dict[str, Any]:
        """Get complete workflow schema for manual authoring."""
        return {
            "workflow_schema": self.schema_validator.get_schema(),
            "available_tools": self.service_manager.get_available_tools(),
            "parameter_documentation": self._get_parameter_docs(),
            "examples": self._get_workflow_examples()
        }

# Workflow authoring support
class WorkflowAuthoringSupport:
    """Support tools for manual workflow authoring."""
    
    def generate_workflow_template(self, task_type: str) -> str:
        """Generate template for specific task types."""
        
        templates = {
            "entity_extraction": """
name: "Entity Extraction Workflow"
description: "Extract entities from documents"

phases:
  - name: "document_processing"
    tools:
      - tool: "t01_pdf_loader"
        inputs:
          file_paths: ["{{input_documents}}"]
      - tool: "t15a_text_chunker"
        inputs:
          chunk_size: 1000
          overlap: 200
  
  - name: "entity_extraction"
    tools:
      - tool: "t23c_ontology_aware_extractor"
        inputs:
          ontology_domain: "{{domain}}"
          confidence_threshold: 0.8
          
outputs:
  - name: "extracted_entities"
    format: "json"
    include_provenance: true
""",
            "graph_analysis": """
name: "Graph Analysis Workflow"
description: "Analyze knowledge graph structure"

phases:
  - name: "graph_construction"
    tools:
      - tool: "t31_entity_builder"
      - tool: "t34_edge_builder"
  
  - name: "graph_analysis"
    tools:
      - tool: "t68_pagerank"
        inputs:
          damping_factor: 0.85
          iterations: 100
      - tool: "community_detection"
        inputs:
          algorithm: "louvain"
          
outputs:
  - name: "graph_metrics"
    format: "csv"
  - name: "community_structure"
    format: "json"
"""
        }
        
        return templates.get(task_type, self._generate_generic_template())
```

#### Supported Use Cases
- **Advanced research methodologies**: Custom analysis requiring precise control
- **Experimental workflows**: Testing new combinations of tools and parameters
- **Performance optimization**: Fine-tuning workflows for specific performance requirements
- **Integration with external tools**: Custom tool integration and data flow

## Implementation Components

### WorkflowAgent: LLM-Driven Generation
```python
class WorkflowAgent:
    """LLM-powered workflow generation for Layers 1 and 2."""
    
    def __init__(self, llm_client, tool_registry, domain_knowledge):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.domain_knowledge = domain_knowledge
    
    async def generate_workflow(self, request: str, context: Dict[str, Any]) -> str:
        """Generate workflow YAML from natural language request."""
        
        # Analyze request intent
        intent_analysis = await self._analyze_request_intent(request)
        
        # Select appropriate tools
        tool_selection = await self._select_tools(intent_analysis, context)
        
        # Generate workflow structure
        workflow_structure = await self._generate_workflow_structure(
            intent_analysis, tool_selection, context
        )
        
        # Convert to YAML
        return self._structure_to_yaml(workflow_structure)
    
    async def _analyze_request_intent(self, request: str) -> IntentAnalysis:
        """Analyze user request to understand research intent."""
        
        prompt = f"""
        Analyze this research request and identify:
        1. Primary research question type (descriptive, explanatory, exploratory)
        2. Required data processing steps
        3. Analysis methods needed
        4. Expected output format
        5. Complexity level (simple, moderate, complex)
        
        Request: "{request}"
        
        Return structured analysis.
        """
        
        response = await self.llm_client.generate(prompt)
        return IntentAnalysis.from_llm_response(response)
```

### WorkflowEngine: YAML/JSON Execution
```python
class WorkflowEngine:
    """Execute workflows defined in YAML/JSON format."""
    
    def __init__(self, service_manager, tool_registry):
        self.service_manager = service_manager
        self.tool_registry = tool_registry
        self.execution_history = []
    
    async def execute(self, workflow_yaml: str, **execution_options) -> ExecutionResult:
        """Execute workflow with full provenance tracking."""
        
        workflow = yaml.safe_load(workflow_yaml)
        execution_id = self._generate_execution_id()
        
        execution_context = ExecutionContext(
            execution_id=execution_id,
            workflow=workflow,
            start_time=datetime.now(),
            options=execution_options
        )
        
        try:
            # Execute phases sequentially
            results = {}
            for phase in workflow.get('phases', []):
                phase_result = await self._execute_phase(phase, execution_context)
                results[phase['name']] = phase_result
                
                # Update context with phase results
                execution_context.add_phase_result(phase['name'], phase_result)
            
            # Generate final outputs
            outputs = await self._generate_outputs(workflow.get('outputs', []), results)
            
            return ExecutionResult(
                execution_id=execution_id,
                status="success",
                results=results,
                outputs=outputs,
                execution_time=(datetime.now() - execution_context.start_time).total_seconds(),
                provenance=execution_context.get_provenance()
            )
            
        except Exception as e:
            return ExecutionResult(
                execution_id=execution_id,
                status="error",
                error=str(e),
                execution_time=(datetime.now() - execution_context.start_time).total_seconds(),
                provenance=execution_context.get_provenance()
            )
```

### WorkflowSchema: Validation and Structure
```python
class WorkflowSchema:
    """Schema validation and structure definition for workflows."""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get complete workflow schema definition."""
        return {
            "type": "object",
            "required": ["name", "phases"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string", "default": "1.0"},
                "phases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "tools"],
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "parallel": {"type": "boolean", "default": False},
                            "tools": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["tool"],
                                    "properties": {
                                        "tool": {"type": "string"},
                                        "inputs": {"type": "object"},
                                        "outputs": {"type": "object"},
                                        "conditions": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "outputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "format"],
                        "properties": {
                            "name": {"type": "string"},
                            "format": {"type": "string", "enum": ["json", "csv", "yaml", "txt"]},
                            "include_provenance": {"type": "boolean", "default": True}
                        }
                    }
                }
            }
        }
```

## Integration Benefits

### Research Workflow Support
- **Methodology alignment**: Workflows map to established research methodologies
- **Reproducibility**: All workflows generate reusable YAML configurations
- **Transparency**: Clear visibility into all processing decisions
- **Flexibility**: Support for diverse research questions and approaches

### Progressive Complexity Handling
- **Simple tasks**: Layer 1 provides immediate results
- **Complex analysis**: Layer 2 enables review and refinement
- **Expert control**: Layer 3 provides complete customization

### Quality Assurance
- **Validation at every layer**: Schema, dependency, and resource validation
- **Error handling**: Structured error reporting and recovery guidance
- **Performance monitoring**: Execution time and resource usage tracking
- **Provenance tracking**: Complete audit trail for all operations

This multi-layer agent interface architecture provides the flexibility needed for academic research while maintaining the rigor and reproducibility required for scientific work.
```


### File: docs/architecture/llm-ontology-integration.md

```
# LLM-Ontology Integration Architecture

*Status: Target Architecture*

## Overview

KGAS implements deep integration between Large Language Models (LLMs) and domain ontologies to enable theory-aware entity extraction, relationship detection, and validation. This architecture combines the flexibility of LLMs with the rigor of formal ontologies.

## Design Principles

### Theory-Driven Processing
- **Domain ontology generation**: LLMs create domain-specific ontologies from user conversations
- **Theory-aware extraction**: Entity extraction guided by theoretical frameworks
- **Ontological validation**: Extracted entities validated against domain concepts
- **Confidence alignment**: Confidence scoring incorporates ontological fit

### Academic Rigor
- **Theoretical grounding**: All extractions validated against academic theories
- **Methodological transparency**: Clear documentation of ontological decisions
- **Reproducible results**: Consistent extraction using stable ontological frameworks
- **Source traceability**: All theory applications linked to original sources

## Core Components

### Domain Ontology Generation

```python
class DomainOntologyGenerator:
    """Generate domain ontologies from user conversations using LLMs."""
    
    def __init__(self, llm_client, theory_repository):
        self.llm_client = llm_client
        self.theory_repository = theory_repository
    
    async def generate_ontology_from_conversation(self, conversation_history: List[str], domain_context: str) -> DomainOntology:
        """Generate domain ontology from user conversation and context."""
        
        # Analyze conversation for domain concepts
        concept_analysis = await self._analyze_domain_concepts(conversation_history, domain_context)
        
        # Generate concept hierarchy
        concept_hierarchy = await self._generate_concept_hierarchy(concept_analysis)
        
        # Define relationships between concepts
        concept_relationships = await self._define_concept_relationships(concept_hierarchy)
        
        # Validate against existing theories
        validation_result = await self._validate_against_theories(concept_hierarchy, concept_relationships)
        
        # Create formal ontology
        ontology = DomainOntology(
            domain=domain_context,
            concepts=concept_hierarchy,
            relationships=concept_relationships,
            validation=validation_result,
            generation_metadata={
                "conversation_hash": self._hash_conversation(conversation_history),
                "generation_time": datetime.now().isoformat(),
                "llm_model": self.llm_client.model_name,
                "confidence_score": validation_result.confidence
            }
        )
        
        # Store in theory repository
        await self.theory_repository.store_ontology(ontology)
        
        return ontology
    
    async def _analyze_domain_concepts(self, conversation: List[str], domain: str) -> ConceptAnalysis:
        """Extract domain concepts from conversation."""
        
        conversation_text = "\n".join(conversation)
        
        prompt = f"""
        Analyze this conversation about {domain} research and identify:
        
        1. Core domain concepts and their definitions
        2. Hierarchical relationships between concepts
        3. Key attributes for each concept
        4. Domain-specific terminology and synonyms
        5. Theoretical frameworks mentioned or implied
        
        Conversation:
        {conversation_text}
        
        Generate a structured analysis of domain concepts that could guide entity extraction.
        Focus on concepts that would be important for knowledge graph construction.
        """
        
        response = await self.llm_client.generate(prompt)
        return ConceptAnalysis.from_llm_response(response)
    
    async def _generate_concept_hierarchy(self, analysis: ConceptAnalysis) -> ConceptHierarchy:
        """Generate hierarchical concept structure."""
        
        prompt = f"""
        Create a hierarchical concept structure for this domain analysis:
        
        {analysis.to_structured_text()}
        
        Generate a concept hierarchy with:
        1. Top-level domain concepts
        2. Sub-concepts and specializations
        3. Abstract vs concrete concept classification
        4. Concept attributes and properties
        5. Cross-references and related concepts
        
        Use formal ontology structure with clear parent-child relationships.
        """
        
        response = await self.llm_client.generate(prompt)
        return ConceptHierarchy.from_llm_response(response)
```

### Theory-Aware Entity Extraction

```python
class OntologyAwareExtractor:
    """Extract entities using domain ontology guidance."""
    
    def __init__(self, llm_client, ontology_manager, confidence_scorer):
        self.llm_client = llm_client
        self.ontology_manager = ontology_manager
        self.confidence_scorer = confidence_scorer
    
    async def extract_with_theory(self, text: str, ontology: DomainOntology) -> List[TheoryAwareEntity]:
        """Extract entities guided by domain ontology."""
        
        # Prepare ontology context for extraction
        ontology_context = await self._prepare_ontology_context(ontology)
        
        # Extract entities with ontological guidance
        raw_entities = await self._extract_ontology_guided_entities(text, ontology_context)
        
        # Validate entities against ontology
        validated_entities = []
        for entity in raw_entities:
            validation = await self._validate_entity_against_ontology(entity, ontology)
            
            theory_aware_entity = TheoryAwareEntity(
                text=entity.text,
                entity_type=entity.entity_type,
                start_pos=entity.start_pos,
                end_pos=entity.end_pos,
                ontological_validation=validation,
                theory_alignment=await self._assess_theory_alignment(entity, ontology),
                confidence_score=await self._calculate_ontological_confidence(entity, validation)
            )
            
            validated_entities.append(theory_aware_entity)
        
        return validated_entities
    
    async def _extract_ontology_guided_entities(self, text: str, ontology_context: str) -> List[Entity]:
        """Extract entities with ontological guidance."""
        
        prompt = f"""
        Extract entities from this text using the provided domain ontology as guidance.
        
        Domain Ontology Context:
        {ontology_context}
        
        Text to analyze:
        {text}
        
        Instructions:
        1. Identify entities that match concepts in the ontology
        2. Use ontology definitions to guide entity boundaries
        3. Apply concept hierarchies to classify entity types
        4. Note entities that don't fit the ontology (potential new concepts)
        5. Provide confidence based on ontological alignment
        
        Return structured entity list with ontological justification.
        """
        
        response = await self.llm_client.generate(prompt)
        return self._parse_entity_response(response)
    
    async def _validate_entity_against_ontology(self, entity: Entity, ontology: DomainOntology) -> OntologicalValidation:
        """Validate extracted entity against domain ontology."""
        
        # Check concept existence
        concept_match = ontology.find_concept(entity.entity_type)
        
        # Validate against concept definition
        definition_alignment = await self._check_definition_alignment(entity, concept_match)
        
        # Check hierarchical consistency
        hierarchy_consistency = await self._check_hierarchy_consistency(entity, concept_match, ontology)
        
        # Assess relationship compatibility
        relationship_compatibility = await self._assess_relationship_compatibility(entity, ontology)
        
        return OntologicalValidation(
            concept_exists=concept_match is not None,
            definition_aligned=definition_alignment.is_aligned,
            hierarchy_consistent=hierarchy_consistency.is_consistent,
            relationship_compatible=relationship_compatibility.is_compatible,
            confidence_score=self._calculate_validation_confidence([
                definition_alignment, hierarchy_consistency, relationship_compatibility
            ]),
            validation_details={
                "concept_match": concept_match,
                "definition_alignment": definition_alignment,
                "hierarchy_consistency": hierarchy_consistency,
                "relationship_compatibility": relationship_compatibility
            }
        )
```

### Theory-Driven Validation Framework

```python
class TheoryDrivenValidator:
    """Validate extractions against theoretical frameworks."""
    
    def __init__(self, theory_repository, validation_engine):
        self.theory_repository = theory_repository
        self.validation_engine = validation_engine
    
    async def validate_extraction_against_theories(self, entities: List[TheoryAwareEntity], ontology: DomainOntology) -> TheoryValidationResult:
        """Validate entity extraction against theoretical frameworks."""
        
        # Load relevant theories
        relevant_theories = await self.theory_repository.get_theories_for_domain(ontology.domain)
        
        # Validate entities against each theory
        theory_validations = []
        for theory in relevant_theories:
            validation = await self._validate_against_single_theory(entities, theory)
            theory_validations.append(validation)
        
        # Cross-theory consistency check
        consistency_check = await self._check_cross_theory_consistency(theory_validations)
        
        # Generate overall validation result
        return TheoryValidationResult(
            ontology_domain=ontology.domain,
            theory_validations=theory_validations,
            consistency_check=consistency_check,
            overall_confidence=self._calculate_overall_confidence(theory_validations, consistency_check),
            recommendations=await self._generate_validation_recommendations(theory_validations, consistency_check)
        )
    
    async def _validate_against_single_theory(self, entities: List[TheoryAwareEntity], theory: Theory) -> SingleTheoryValidation:
        """Validate entities against a single theoretical framework."""
        
        # Check entity types against theory concepts
        concept_validation = await self._validate_concepts_against_theory(entities, theory)
        
        # Check relationships against theory constraints
        relationship_validation = await self._validate_relationships_against_theory(entities, theory)
        
        # Check theoretical assumptions
        assumption_validation = await self._validate_theoretical_assumptions(entities, theory)
        
        return SingleTheoryValidation(
            theory_name=theory.name,
            theory_version=theory.version,
            concept_validation=concept_validation,
            relationship_validation=relationship_validation,
            assumption_validation=assumption_validation,
            overall_alignment=self._calculate_theory_alignment([
                concept_validation, relationship_validation, assumption_validation
            ])
        )
```

### Ontological Confidence Scoring

```python
class OntologicalConfidenceScorer:
    """Calculate confidence scores incorporating ontological alignment."""
    
    def __init__(self, base_confidence_scorer):
        self.base_confidence_scorer = base_confidence_scorer
    
    async def calculate_ontological_confidence(self, entity: TheoryAwareEntity, validation: OntologicalValidation) -> ConfidenceScore:
        """Calculate confidence score incorporating ontological factors."""
        
        # Get base confidence from standard methods
        base_confidence = await self.base_confidence_scorer.calculate_base_confidence(entity)
        
        # Calculate ontological alignment score
        ontological_score = self._calculate_ontological_alignment_score(validation)
        
        # Calculate theory coherence score
        theory_coherence = self._calculate_theory_coherence_score(entity.theory_alignment)
        
        # Combine scores using weighted approach
        combined_score = self._combine_confidence_scores(
            base_confidence=base_confidence,
            ontological_alignment=ontological_score,
            theory_coherence=theory_coherence,
            weights={
                "base": 0.4,
                "ontological": 0.35,
                "theory": 0.25
            }
        )
        
        return ConfidenceScore(
            overall_score=combined_score,
            components={
                "base_confidence": base_confidence,
                "ontological_alignment": ontological_score,
                "theory_coherence": theory_coherence
            },
            methodology="ontological_weighted_combination",
            metadata={
                "ontology_validation": validation,
                "theory_alignment": entity.theory_alignment,
                "calculation_time": datetime.now().isoformat()
            }
        )
    
    def _calculate_ontological_alignment_score(self, validation: OntologicalValidation) -> float:
        """Calculate alignment score based on ontological validation."""
        
        factors = []
        
        # Concept existence (strong factor)
        if validation.concept_exists:
            factors.append(0.9)
        else:
            factors.append(0.1)
        
        # Definition alignment (medium factor)
        factors.append(validation.definition_aligned * 0.8)
        
        # Hierarchy consistency (medium factor)
        factors.append(validation.hierarchy_consistent * 0.7)
        
        # Relationship compatibility (weak factor)
        factors.append(validation.relationship_compatible * 0.6)
        
        # Weighted average
        weights = [0.4, 0.25, 0.25, 0.1]
        return sum(f * w for f, w in zip(factors, weights))
```

## Integration Patterns

### Ontology-Driven Workflow Integration

```python
class OntologyDrivenWorkflow:
    """Integrate ontological processing into standard workflows."""
    
    async def execute_theory_aware_extraction(self, documents: List[str], domain: str, conversation_history: List[str]) -> TheoryAwareExtractionResult:
        """Execute extraction workflow with theory awareness."""
        
        # Step 1: Generate domain ontology
        ontology = await self.ontology_generator.generate_ontology_from_conversation(
            conversation_history, domain
        )
        
        # Step 2: Process documents with ontology guidance
        extraction_results = []
        for document in documents:
            # Load and chunk document
            chunks = await self.document_processor.process_document(document)
            
            # Extract entities with ontological guidance
            for chunk in chunks:
                entities = await self.ontology_extractor.extract_with_theory(chunk.text, ontology)
                extraction_results.extend(entities)
        
        # Step 3: Validate against theoretical frameworks
        validation_result = await self.theory_validator.validate_extraction_against_theories(
            extraction_results, ontology
        )
        
        # Step 4: Build knowledge graph with theory awareness
        knowledge_graph = await self.graph_builder.build_theory_aware_graph(
            extraction_results, ontology, validation_result
        )
        
        return TheoryAwareExtractionResult(
            ontology=ontology,
            extracted_entities=extraction_results,
            theory_validation=validation_result,
            knowledge_graph=knowledge_graph,
            provenance=self._generate_theory_provenance(ontology, extraction_results, validation_result)
        )
```

### Cross-Modal Theory Integration

```python
class CrossModalTheoryIntegration:
    """Integrate theoretical frameworks across analysis modes."""
    
    async def apply_theory_across_modalities(self, knowledge_graph: KnowledgeGraph, ontology: DomainOntology) -> CrossModalTheoryResult:
        """Apply theoretical frameworks across graph, table, and vector modalities."""
        
        # Graph-mode theory application
        graph_theory_analysis = await self._apply_theory_to_graph(knowledge_graph, ontology)
        
        # Convert to table mode with theory preservation
        table_representation = await self.graph_to_table_converter.convert_with_theory(
            knowledge_graph, ontology
        )
        
        # Table-mode theory analysis
        table_theory_analysis = await self._apply_theory_to_table(table_representation, ontology)
        
        # Convert to vector mode with theory context
        vector_representation = await self.graph_to_vector_converter.convert_with_theory(
            knowledge_graph, ontology
        )
        
        # Vector-mode theory analysis
        vector_theory_analysis = await self._apply_theory_to_vectors(vector_representation, ontology)
        
        # Cross-modal theory consistency check
        consistency_analysis = await self._check_cross_modal_theory_consistency([
            graph_theory_analysis,
            table_theory_analysis,
            vector_theory_analysis
        ])
        
        return CrossModalTheoryResult(
            ontology=ontology,
            graph_analysis=graph_theory_analysis,
            table_analysis=table_theory_analysis,
            vector_analysis=vector_theory_analysis,
            consistency_analysis=consistency_analysis
        )
```

## Implementation Architecture

### Theory Repository Integration

```python
class TheoryRepository:
    """Central repository for theories and ontologies."""
    
    def __init__(self, storage_backend, versioning_system):
        self.storage = storage_backend
        self.versioning = versioning_system
    
    async def store_ontology(self, ontology: DomainOntology) -> str:
        """Store domain ontology with versioning."""
        
        # Generate ontology ID
        ontology_id = self._generate_ontology_id(ontology)
        
        # Version control
        version = await self.versioning.create_version(ontology_id, ontology)
        
        # Store with metadata
        await self.storage.store_with_metadata(
            key=f"ontology/{ontology_id}/{version}",
            data=ontology,
            metadata={
                "domain": ontology.domain,
                "creation_time": datetime.now().isoformat(),
                "version": version,
                "concepts_count": len(ontology.concepts),
                "relationships_count": len(ontology.relationships)
            }
        )
        
        return ontology_id
    
    async def get_theories_for_domain(self, domain: str) -> List[Theory]:
        """Retrieve theories relevant to domain."""
        
        # Search for domain-specific theories
        domain_theories = await self.storage.query_by_metadata({"domain": domain})
        
        # Search for general theories applicable to domain
        general_theories = await self._find_applicable_general_theories(domain)
        
        # Combine and rank by relevance
        all_theories = domain_theories + general_theories
        ranked_theories = await self._rank_theories_by_relevance(all_theories, domain)
        
        return ranked_theories
```

### LLM Integration Patterns

```python
class LLMOntologyBridge:
    """Bridge between LLM capabilities and ontological reasoning."""
    
    def __init__(self, llm_client, ontology_reasoner):
        self.llm_client = llm_client
        self.ontology_reasoner = ontology_reasoner
    
    async def enhance_llm_with_ontology(self, prompt: str, ontology: DomainOntology) -> str:
        """Enhance LLM prompts with ontological context."""
        
        # Generate ontology context summary
        ontology_summary = await self.ontology_reasoner.generate_summary(ontology)
        
        # Create enhanced prompt
        enhanced_prompt = f"""
        Use the following domain ontology to guide your analysis:
        
        Domain: {ontology.domain}
        Key Concepts: {ontology_summary.key_concepts}
        Concept Relationships: {ontology_summary.relationships}
        Theoretical Framework: {ontology_summary.theoretical_basis}
        
        Original Task:
        {prompt}
        
        Apply the ontological framework to ensure theoretical consistency and domain appropriateness.
        """
        
        return enhanced_prompt
    
    async def validate_llm_output_with_ontology(self, llm_output: str, ontology: DomainOntology) -> ValidationResult:
        """Validate LLM output against ontological constraints."""
        
        # Parse LLM output for ontological elements
        ontological_elements = await self._extract_ontological_elements(llm_output)
        
        # Validate each element against ontology
        validations = []
        for element in ontological_elements:
            validation = await self.ontology_reasoner.validate_element(element, ontology)
            validations.append(validation)
        
        # Generate overall validation
        return ValidationResult.combine(validations)
```

## Benefits and Applications

### Research Quality Enhancement
- **Theoretical grounding**: All extractions validated against established theories
- **Consistency assurance**: Cross-modal consistency through shared ontological framework
- **Reproducibility**: Stable ontological frameworks ensure consistent results
- **Transparency**: Clear documentation of theoretical assumptions and applications

### Adaptive Analysis
- **Domain-specific processing**: Ontologies tailored to specific research domains
- **Theory-aware extraction**: Extraction guided by theoretical frameworks
- **Intelligent validation**: Automatic validation against domain knowledge
- **Cross-modal coherence**: Consistent theoretical application across analysis modes

### Academic Integration
- **Methodology alignment**: Processing aligns with established research methodologies
- **Citation support**: Theoretical frameworks linked to academic sources
- **Peer review readiness**: Results include theoretical justification and validation
- **Research reproducibility**: Complete ontological and theoretical documentation

This LLM-ontology integration architecture provides the theoretical rigor and domain awareness required for high-quality academic research while leveraging the flexibility and power of modern LLMs.
```


### File: docs/architecture/cross-modal-analysis.md

```
# Cross-Modal Analysis Architecture

*Status: Target Architecture with Production Theory Integration*

## Overview

KGAS implements a comprehensive cross-modal analysis architecture that enables fluid movement between Graph, Table, and Vector data representations. The system integrates **production-ready automated theory extraction** with **LLM-driven intelligent orchestration** to provide theory-aware, multi-modal analysis capabilities. This design allows researchers to leverage optimal analysis modes for each research question while maintaining complete theoretical grounding and source traceability.

## Integrated Theory-Modal Architecture

KGAS combines two sophisticated systems for unprecedented analytical capability:

### **Theory-Adaptive Modal Selection** (Production-Ready Integration)
The automated theory extraction system provides **theory-specific modal guidance**:

- **Property Graph Theories**: Social Identity Theory, Cognitive Mapping → Graph mode prioritization  
- **Hypergraph Theories**: Semantic Hypergraphs, N-ary Relations → Custom hypergraph processing
- **Table/Matrix Theories**: Game Theory, Classification Systems → Table mode optimization
- **Sequence Theories**: Stage Models, Process Theories → Temporal analysis workflows
- **Tree Theories**: Taxonomies, Hierarchies → Structural decomposition
- **Timeline Theories**: Historical Development → Temporal progression analysis

### **Intelligent Modal Orchestration** (LLM-Enhanced)
Advanced reasoning layer determines optimal analysis approach by considering both:
- **Research Question Intent**: What the user wants to discover
- **Theoretical Framework**: What the underlying theory suggests
- **Data Characteristics**: What the data structure supports

## Architectural Principles

### Format-Agnostic Research
- **Research question drives format selection**: LLM analyzes research goals and automatically selects optimal analysis mode
- **Seamless transformation**: Intelligent conversion between all representation modes
- **Unified querying**: Single interface for cross-modal queries and analysis
- **Preservation of meaning**: All transformations maintain semantic integrity

### Theory-Enhanced LLM Mode Selection
KGAS combines automated theory extraction insights with advanced LLM reasoning to determine optimal analysis approaches:

#### **Enhanced Mode Selection Algorithm**
```python
async def select_analysis_mode(self, research_question: str, theory_schema: Dict, data_characteristics: Dict) -> AnalysisStrategy:
    """Theory-aware analysis mode selection with production integration."""
    
    # Get theory-specific modal preferences from extraction system
    theory_modal_preferences = self.get_theory_modal_preferences(theory_schema)
    extracted_model_type = theory_schema.get('model_type')  # From lit_review extraction
    analytical_purposes = theory_schema.get('analytical_purposes', [])
    
    mode_selection_prompt = f"""
    Research Question: "{research_question}"
    Theory Framework: {theory_schema.get('theory_name')}
    Extracted Model Type: {extracted_model_type}
    Analytical Purposes: {analytical_purposes}
    Theory Modal Preferences: {theory_modal_preferences}
    Data Characteristics: {data_characteristics}
    
    PRIORITY 1: Honor theory-specific modal preferences from automated extraction
    PRIORITY 2: Consider research question requirements  
    PRIORITY 3: Account for data characteristics and constraints
    """
```

#### **Integrated LLM-Driven Mode Selection**
The enhanced system provides both theory-grounded and question-driven analysis recommendations:

```python
class CrossModalOrchestrator:
    """LLM-driven intelligent mode selection for research questions."""
    
    async def select_analysis_mode(self, research_question: str, data_characteristics: Dict) -> AnalysisStrategy:
        """Analyze research question and recommend optimal analysis approach."""
        
        mode_selection_prompt = f"""
        Research Question: "{research_question}"
        Data Characteristics: {data_characteristics}
        
        Analyze this research question and recommend the optimal analysis approach:
        
        GRAPH MODE best for:
        - Network analysis (influence, centrality, communities)
        - Relationship exploration (who connects to whom)
        - Path analysis (how information/influence flows)
        - Structural analysis (network topology, clustering)
        
        TABLE MODE best for:
        - Statistical analysis (correlations, significance tests)
        - Aggregation and summarization (counts, averages, trends)
        - Comparative analysis (between groups, over time)
        - Quantitative hypothesis testing
        
        VECTOR MODE best for:
        - Semantic similarity (find similar content/entities)
        - Clustering (group by semantic similarity)
        - Search and retrieval (find relevant information)
        - Topic modeling and concept analysis
        
        Consider:
        1. What is the primary analytical goal?
        2. What type of insights are needed?
        3. What analysis method would best answer this question?
        4. Should multiple modes be used in sequence?
        
        Respond with recommended mode(s) and reasoning.
        """
        
        llm_recommendation = await self.llm.analyze(mode_selection_prompt)
        
        return self._parse_analysis_strategy(llm_recommendation)
        
    def _parse_analysis_strategy(self, llm_response: str) -> AnalysisStrategy:
        """Parse LLM response into structured analysis strategy."""
        
        return AnalysisStrategy(
            primary_mode=self._extract_primary_mode(llm_response),
            secondary_modes=self._extract_secondary_modes(llm_response),
            reasoning=self._extract_reasoning(llm_response),
            workflow_steps=self._extract_workflow(llm_response),
            expected_outputs=self._extract_expected_outputs(llm_response)
        )
```

**Example LLM Mode Selection**:

Research Question: *"How do media outlets influence political discourse on climate change?"*

LLM Analysis:
1. **Primary Mode**: Graph - Network analysis to map outlet→politician→topic connections
2. **Secondary Mode**: Table - Statistical analysis of coverage patterns by outlet type  
3. **Tertiary Mode**: Vector - Semantic similarity of climate discourse across outlets
4. **Workflow**: Start with Graph (identify influence networks) → Table (quantify patterns) → Vector (analyze discourse similarity)

This intelligent mode selection ensures researchers get optimal analytical approaches without needing deep knowledge of different data representation advantages.

### Source Traceability
- **Complete provenance**: All results traceable to original document sources
- **Transformation history**: Track all format conversions and processing steps
- **W3C PROV compliance**: Standard provenance tracking across all operations
- **Citation support**: Automatic generation of academic citations and references

KGAS enables researchers to leverage the strengths of different data representations:

### Data Representation Layers

```
┌─────────────────────────────────────────────────────────────┐
│                 Cross-Modal Analysis Layer                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │Graph Queries│ │Table Queries │ │Vector Queries     │  │
│  │(Cypher)     │ │(SQL/Pandas)  │ │(Similarity)       │  │
│  └──────┬──────┘ └──────┬───────┘ └────────┬──────────┘  │
│         │                │                   │              │
│         └────────────────┴───────────────────┘              │
│                          │                                  │
│                 ┌────────┴────────┐                        │
│                 │ Result Linker   │                        │
│                 └────────┬────────┘                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
                   ┌──────┴──────┐
                   │Source Tracer │
                   └─────────────┘
```

### Cross-Modal Workflows

The system supports fluid movement between representations:

1. **Graph → Table**: Export subgraphs or query results to relational tables for statistical analysis
2. **Table → Graph**: Build graphs from relational data or analysis results
3. **Graph → Vector**: Generate embeddings from graph structures for similarity analysis
4. **Vector → Graph**: Create similarity graphs from vector distances
5. **Any → Source**: Trace any result back to original document chunks

## Data Representation Modes

### Graph Analysis Mode
**Optimal for**: Relationship exploration, network analysis, influence tracking
```python
# Graph representation focuses on relationships and structure
class GraphRepresentation:
    nodes: List[Entity]  # Entities as graph nodes
    edges: List[Relationship]  # Relationships as graph edges
    metadata: GraphMetadata  # Centrality, communities, paths
    
    # Analysis capabilities
    def find_influential_entities(self) -> List[Entity]
    def detect_communities(self) -> List[Community]
    def analyze_paths(self, source: Entity, target: Entity) -> List[Path]
    def calculate_centrality(self) -> Dict[Entity, float]
```

### Table Analysis Mode
**Optimal for**: Statistical analysis, aggregation, correlation discovery
```python
# Table representation focuses on attributes and statistics
class TableRepresentation:
    entities: DataFrame  # Entities with attributes as columns
    relationships: DataFrame  # Relationships as relational table
    metadata: TableMetadata  # Statistics, distributions, correlations
    
    # Analysis capabilities
    def statistical_analysis(self) -> StatisticalSummary
    def correlation_analysis(self) -> CorrelationMatrix
    def aggregate_by_attributes(self, grouping: List[str]) -> DataFrame
    def trend_analysis(self) -> TrendAnalysis
```

### Vector Analysis Mode
**Optimal for**: Similarity search, clustering, semantic analysis
```python
# Vector representation focuses on semantic similarity
class VectorRepresentation:
    entity_embeddings: Dict[Entity, Vector]  # Entity semantic vectors
    relationship_embeddings: Dict[Relationship, Vector]  # Relationship vectors
    metadata: VectorMetadata  # Clusters, similarity scores, semantic spaces
    
    # Analysis capabilities
    def find_similar_entities(self, query: Entity, k: int) -> List[Entity]
    def cluster_entities(self) -> List[Cluster]
    def semantic_search(self, query: str) -> List[Entity]
    def dimensionality_reduction(self) -> ReducedSpace
```

## Cross-Modal Integration Architecture

### Format Conversion Layer
```python
class CrossModalConverter:
    """Intelligent conversion between all data representation modes."""
    
    async def graph_to_table(self, graph: GraphRepresentation, conversion_strategy: str) -> TableRepresentation:
        """Convert graph to table with preservation of source links."""
        
        if conversion_strategy == "entity_attributes":
            # Convert nodes to rows, attributes to columns
            entities_df = self._nodes_to_dataframe(graph.nodes)
            relationships_df = self._edges_to_dataframe(graph.edges)
            
        elif conversion_strategy == "adjacency_matrix":
            # Convert graph structure to adjacency representation
            entities_df = self._create_adjacency_matrix(graph)
            relationships_df = self._create_relationship_summary(graph.edges)
            
        elif conversion_strategy == "path_statistics":
            # Convert path analysis to statistical table
            entities_df = self._path_statistics_to_table(graph)
            relationships_df = self._relationship_statistics(graph.edges)
        
        return TableRepresentation(
            entities=entities_df,
            relationships=relationships_df,
            source_graph=graph,
            conversion_metadata=ConversionMetadata(
                strategy=conversion_strategy,
                conversion_time=datetime.now(),
                source_provenance=graph.metadata.provenance
            )
        )
    
    async def table_to_vector(self, table: TableRepresentation, embedding_strategy: str) -> VectorRepresentation:
        """Convert table to vector with semantic embedding generation."""
        
        entity_embeddings = {}
        relationship_embeddings = {}
        
        if embedding_strategy == "attribute_embedding":
            # Generate embeddings from entity attributes
            for _, entity_row in table.entities.iterrows():
                embedding = await self._generate_attribute_embedding(entity_row)
                entity_embeddings[entity_row['entity_id']] = embedding
                
        elif embedding_strategy == "statistical_embedding":
            # Generate embeddings from statistical properties
            statistical_features = self._extract_statistical_features(table)
            entity_embeddings = await self._embed_statistical_features(statistical_features)
            
        elif embedding_strategy == "hybrid_embedding":
            # Combine multiple embedding approaches
            attribute_embeddings = await self._generate_attribute_embeddings(table)
            statistical_embeddings = await self._generate_statistical_embeddings(table)
            entity_embeddings = self._combine_embeddings(attribute_embeddings, statistical_embeddings)
        
        return VectorRepresentation(
            entity_embeddings=entity_embeddings,
            relationship_embeddings=relationship_embeddings,
            source_table=table,
            conversion_metadata=ConversionMetadata(
                strategy=embedding_strategy,
                conversion_time=datetime.now(),
                source_provenance=table.metadata.provenance
            )
        )
```

### Provenance Integration
```python
class ProvenanceTracker:
    """Track provenance across all cross-modal transformations."""
    
    def track_conversion(self, source_representation: Any, target_representation: Any, conversion_metadata: ConversionMetadata) -> ProvenanceRecord:
        """Create provenance record for cross-modal conversion."""
        
        return ProvenanceRecord(
            activity_type="cross_modal_conversion",
            source_format=type(source_representation).__name__,
            target_format=type(target_representation).__name__,
            conversion_strategy=conversion_metadata.strategy,
            timestamp=conversion_metadata.conversion_time,
            source_provenance=conversion_metadata.source_provenance,
            transformation_parameters=conversion_metadata.parameters,
            quality_metrics=self._calculate_conversion_quality(source_representation, target_representation)
        )
    
    def trace_to_source(self, analysis_result: Any) -> List[SourceReference]:
        """Trace any analysis result back to original source documents."""
        
        # Walk through provenance chain
        provenance_chain = self._build_provenance_chain(analysis_result)
        
        # Extract source references
        source_references = []
        for provenance_record in provenance_chain:
            if provenance_record.activity_type == "document_processing":
                source_refs = self._extract_source_references(provenance_record)
                source_references.extend(source_refs)
        
        return self._deduplicate_sources(source_references)

## Cross-Modal Semantic Preservation

### Technical Requirements
- **Entity Identity Consistency**: Unified entity IDs maintained across all representations
- **Semantic Preservation**: Complete meaning preservation during cross-modal transformations
- **Encoding Method**: Non-lossy encoding that enables full bidirectional capability
- **Quality Metrics**: Measurable preservation metrics to validate transformation integrity

### Tool Categories Supporting Cross-Modal Analysis

#### Graph Analysis Tools (T1-T30)
- **Centrality Analysis**: PageRank, betweenness, closeness centrality
- **Community Detection**: Louvain, modularity-based clustering
- **Path Analysis**: Shortest paths, path enumeration, connectivity
- **Structure Analysis**: Density, clustering coefficient, motifs

#### Table Analysis Tools (T31-T60)
- **Statistical Analysis**: Descriptive statistics, hypothesis testing
- **Correlation Analysis**: Pearson, Spearman, partial correlations
- **Aggregation Tools**: Group-by operations, pivot tables, summaries
- **Trend Analysis**: Time series, regression, forecasting

#### Vector Analysis Tools (T61-T90)
- **Similarity Search**: Cosine similarity, nearest neighbors, ranking
- **Clustering**: K-means, hierarchical, density-based clustering
- **Dimensionality Reduction**: PCA, t-SNE, UMAP
- **Semantic Analysis**: Concept mapping, topic modeling

#### Cross-Modal Integration Tools (T91-T121)
- **Format Converters**: Intelligent conversion between all modalities
- **Provenance Trackers**: Complete source linking and transformation history
- **Quality Assessors**: Conversion quality and information preservation metrics
- **Result Integrators**: Combine results from multiple analysis modes

### Example Research Workflow

```python
# 1. Find influential entities using graph analysis
high_centrality_nodes = graph_analysis.pagerank(top_k=100)

# 2. Convert to table for statistical analysis
entity_table = cross_modal.graph_to_table(high_centrality_nodes)

# 3. Perform statistical analysis
correlation_matrix = table_analysis.correlate(entity_table)

# 4. Find similar entities using embeddings
similar_entities = vector_analysis.find_similar(entity_table.ids)

# 5. Trace everything back to sources
source_references = source_tracer.trace(similar_entities)
``` 
```


### File: src/core/tool_registry.py

```
"""
Tool Registry for KGAS

This module provides the authoritative registry of all tools, including
current versions, archived versions, and conflict resolutions.

Following fail-fast principles:
- All tools listed here must pass functional validation
- Version conflicts must be explicitly resolved
- Archive decisions must be documented with rationale
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class ToolStatus(Enum):
    """Tool status based on validation evidence."""
    FUNCTIONAL = "functional"
    BROKEN = "broken"
    MISSING = "missing"
    NEEDS_VALIDATION = "needs_validation"
    ARCHIVED = "archived"

class ToolRegistry:
    """Central registry for all KGAS tools with version management."""
    
    def __init__(self):
        """Initialize tool registry with current validation data."""
        
        # Based on validation results from 2025-07-19T08:22:37.564654
        self.validation_date = "2025-07-19T08:22:37.564654"
        self.current_tools = self._initialize_current_tools()
        self.archived_tools = self._initialize_archived_tools()
        self.version_conflicts = self._initialize_version_conflicts()
        self.missing_tools = self._initialize_missing_tools()
    
    def _initialize_current_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize current tool registry based on validation evidence."""
        
        return {
            "T01": {
                "path": "src/tools/phase1/t01_pdf_loader.py",
                "class": "PDFLoader",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "PDF document loader with provenance tracking",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T15a": {
                "path": "src/tools/phase1/t15a_text_chunker.py", 
                "class": "TextChunker",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Text chunking with configurable size and overlap",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T15b": {
                "path": "src/tools/phase1/t15b_vector_embedder.py",
                "class": "VectorEmbedder", 
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["Import error: attempted relative import with no known parent package"],
                "description": "Vector embedding generation with metadata"
            },
            "T23a": {
                "path": "src/tools/phase1/t23a_spacy_ner.py",
                "class": "SpacyNER",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "SpaCy-based named entity recognition",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T27": {
                "path": "src/tools/phase1/t27_relationship_extractor.py",
                "class": "RelationshipExtractor", 
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["Tool requires parameters for execution"],
                "description": "Relationship extraction from text",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T34": {
                "path": "src/tools/phase1/t34_edge_builder.py",
                "class": "EdgeBuilder",
                "status": ToolStatus.BROKEN, 
                "validation_date": self.validation_date,
                "issues": ["Failed to instantiate tool: name 'get_config' is not defined"],
                "description": "Graph edge creation from relationships"
            },
            "T301": {
                "path": "src/tools/phase3/t301_multi_document_fusion.py",
                "class": "MultiDocumentFusion",
                "status": ToolStatus.BROKEN,
                "validation_date": self.validation_date,
                "issues": ["No tool class found in module"],
                "description": "Cross-document entity resolution and fusion"
            },
            "GraphTableExporter": {
                "path": "src/tools/cross_modal/graph_table_exporter.py",
                "class": "GraphTableExporter",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Export Neo4j subgraphs to statistical formats",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "MultiFormatExporter": {
                "path": "src/tools/cross_modal/multi_format_exporter.py",
                "class": "MultiFormatExporter", 
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Export results in academic formats (LaTeX, BibTeX)",
                "execute_signature": "(input_data: Any, context: Optional[Dict] = None) -> Dict[str, Any]"
            },
            "T68": {
                "path": "src/tools/phase1/t68_pagerank_optimized.py",
                "class": "T68PageRankOptimized",
                "status": ToolStatus.FUNCTIONAL,
                "validation_date": self.validation_date,
                "issues": [],
                "description": "Optimized PageRank graph analysis",
                "execute_signature": "(input_data: Any = None, context: Optional[Dict] = None) -> Dict[str, Any]"
            }
        }
    
    def _initialize_archived_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize archived tools registry."""
        
        # No tools archived yet - will be populated during conflict resolution
        return {}
    
    def _initialize_version_conflicts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize version conflicts that need resolution."""
        
        return {
            "t23c": {
                "description": "LLM-based entity extraction",
                "versions": [
                    {
                        "path": "src/tools/phase1/t23c_llm_entity_extractor.py",
                        "class": "LLMEntityExtractor",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic LLM entity extraction"
                    },
                    {
                        "path": "src/tools/phase2/t23c_ontology_aware_extractor.py", 
                        "class": "OntologyAwareExtractor",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Ontology-aware entity extraction (more advanced)"
                    }
                ],
                "recommended_primary": "src/tools/phase2/t23c_ontology_aware_extractor.py",
                "rationale": "Phase 2 version supports ontology-aware extraction",
                "resolution_status": "pending"
            },
            "t31": {
                "description": "Entity/graph building",
                "versions": [
                    {
                        "path": "src/tools/phase1/t31_entity_builder.py",
                        "class": "EntityBuilder", 
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic entity building"
                    },
                    {
                        "path": "src/tools/phase2/t31_ontology_graph_builder.py",
                        "class": "OntologyGraphBuilder",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Failed to instantiate tool: Neo4j connection failed"],
                        "notes": "Ontology-aware graph building"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t31_entity_builder.py",
                "rationale": "Need functional testing to determine which works better",
                "resolution_status": "pending"
            },
            "t41": {
                "description": "Text embedding generation",
                "versions": [
                    {
                        "path": "src/tools/phase1/t41_async_text_embedder.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Async text embedding (aligns with AnyIO strategy)"
                    },
                    {
                        "path": "src/tools/phase1/t41_text_embedder.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN, 
                        "issues": ["No tool class found in module"],
                        "notes": "Sync text embedding"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t41_async_text_embedder.py",
                "rationale": "Async version aligns with AnyIO structured concurrency strategy",
                "resolution_status": "pending"
            },
            "t49": {
                "description": "Multi-hop graph queries",
                "versions": [
                    {
                        "path": "src/tools/phase1/t49_enhanced_query.py",
                        "class": "Unknown",
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Enhanced query capabilities"
                    },
                    {
                        "path": "src/tools/phase1/t49_multihop_query.py", 
                        "class": "MultiHopQuery",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Multi-hop query functionality"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t49_multihop_query.py",
                "rationale": "Multi-hop is core functionality for graph analysis",
                "resolution_status": "pending"
            },
            "t68": {
                "description": "PageRank graph analysis",
                "versions": [
                    {
                        "path": "src/tools/phase1/t68_pagerank.py",
                        "class": "PageRankCalculator",
                        "status": ToolStatus.BROKEN,
                        "issues": ["Tool requires parameters: ['input_data', 'context']"],
                        "notes": "Basic PageRank implementation"
                    },
                    {
                        "path": "src/tools/phase1/t68_pagerank_optimized.py",
                        "class": "Unknown", 
                        "status": ToolStatus.BROKEN,
                        "issues": ["No tool class found in module"],
                        "notes": "Optimized PageRank implementation"
                    }
                ],
                "recommended_primary": "src/tools/phase1/t68_pagerank_optimized.py",
                "rationale": "Optimized version should provide better performance",
                "resolution_status": "pending"
            }
        }
    
    def _initialize_missing_tools(self) -> Dict[str, Dict[str, Any]]:
        """Initialize missing tools that need implementation."""
        
        # Based on latest validation, most previously "missing" tools are actually implemented
        # but have functionality issues (parameter requirements, missing classes)
        return {}
    
    def get_functional_tools(self) -> List[str]:
        """Get list of tools that are currently functional."""
        
        functional_tools = []
        for tool_id, tool_info in self.current_tools.items():
            if tool_info["status"] == ToolStatus.FUNCTIONAL:
                functional_tools.append(tool_id)
        
        return functional_tools
    
    def get_broken_tools(self) -> List[str]:
        """Get list of tools that are broken and need fixing."""
        
        broken_tools = []
        for tool_id, tool_info in self.current_tools.items():
            if tool_info["status"] == ToolStatus.BROKEN:
                broken_tools.append(tool_id)
        
        return broken_tools
    
    def get_version_conflicts(self) -> List[str]:
        """Get list of tools with unresolved version conflicts."""
        
        return [conflict_id for conflict_id, conflict_info in self.version_conflicts.items() 
                if conflict_info["resolution_status"] == "pending"]
    
    def get_missing_tools(self) -> List[str]:
        """Get list of missing tools that need implementation."""
        
        return list(self.missing_tools.keys())
    
    def get_mvrt_completion_status(self) -> Dict[str, Any]:
        """Get MVRT completion status based on current tool state."""
        
        required_mvrt_tools = [
            "T01", "T15a", "T15b", "T23a", "T23c", "T27", "T31", "T34", 
            "T49", "T301", "GraphTableExporter", "MultiFormatExporter"
        ]
        
        functional_count = 0
        total_count = len(required_mvrt_tools)
        
        # Count functional tools
        for tool_id in required_mvrt_tools:
            if tool_id in self.current_tools:
                if self.current_tools[tool_id]["status"] == ToolStatus.FUNCTIONAL:
                    functional_count += 1
            elif tool_id in self.missing_tools:
                # Missing tools are not functional
                pass
        
        completion_percentage = (functional_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            "total_required": total_count,
            "functional": functional_count,
            "completion_percentage": completion_percentage,
            "missing_tools": len(self.missing_tools),
            "version_conflicts": len(self.get_version_conflicts()),
            "broken_tools": len(self.get_broken_tools())
        }
    
    def resolve_version_conflict(self, conflict_id: str, chosen_version_path: str, archive_reason: str) -> None:
        """Resolve a version conflict by choosing primary version and archiving others."""
        
        if conflict_id not in self.version_conflicts:
            raise ValueError(f"No version conflict found for {conflict_id}")
        
        conflict = self.version_conflicts[conflict_id]
        chosen_version = None
        archive_versions = []
        
        # Find chosen version and identify others for archiving
        for version in conflict["versions"]:
            if version["path"] == chosen_version_path:
                chosen_version = version
            else:
                archive_versions.append(version)
        
        if chosen_version is None:
            raise ValueError(f"Chosen version path {chosen_version_path} not found in conflict {conflict_id}")
        
        # Update current tools registry with chosen version
        tool_id = conflict_id.upper()
        self.current_tools[tool_id] = {
            "path": chosen_version["path"],
            "class": chosen_version["class"],
            "status": chosen_version["status"],
            "validation_date": self.validation_date,
            "issues": chosen_version.get("issues", []),
            "description": conflict["description"],
            "resolution_date": datetime.now().isoformat(),
            "resolution_reason": archive_reason
        }
        
        # Archive other versions
        for version in archive_versions:
            archive_key = f"{conflict_id}_{version['path'].split('/')[-1]}"
            self.archived_tools[archive_key] = {
                "original_path": version["path"],
                "archived_path": f"archived/tools/{version['path']}",
                "class": version["class"], 
                "archive_date": datetime.now().isoformat(),
                "archive_reason": archive_reason,
                "replaced_by": chosen_version["path"]
            }
        
        # Mark conflict as resolved
        self.version_conflicts[conflict_id]["resolution_status"] = "resolved"
        self.version_conflicts[conflict_id]["chosen_version"] = chosen_version_path
        self.version_conflicts[conflict_id]["resolution_date"] = datetime.now().isoformat()
    
    def add_tool(self, tool_id: str, tool_info: Dict[str, Any]) -> None:
        """Add a new functional tool to the registry."""
        
        # Validate required fields
        required_fields = ["path", "class", "status", "description"]
        for field in required_fields:
            if field not in tool_info:
                raise ValueError(f"Tool info missing required field: {field}")
        
        # Add validation date
        tool_info["validation_date"] = datetime.now().isoformat()
        
        self.current_tools[tool_id] = tool_info
    
    def mark_tool_functional(self, tool_id: str, validation_evidence: Dict[str, Any]) -> None:
        """Mark a tool as functional with validation evidence."""
        
        if tool_id not in self.current_tools:
            raise ValueError(f"Tool {tool_id} not found in registry")
        
        self.current_tools[tool_id]["status"] = ToolStatus.FUNCTIONAL
        self.current_tools[tool_id]["validation_date"] = datetime.now().isoformat()
        self.current_tools[tool_id]["validation_evidence"] = validation_evidence
        
        # Clear any previous issues
        if "issues" in self.current_tools[tool_id]:
            self.current_tools[tool_id]["issues"] = []
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of tool registry state."""
        
        mvrt_status = self.get_mvrt_completion_status()
        
        return {
            "registry_metadata": {
                "last_validation": self.validation_date,
                "total_current_tools": len(self.current_tools),
                "total_archived_tools": len(self.archived_tools),
                "total_version_conflicts": len(self.version_conflicts),
                "total_missing_tools": len(self.missing_tools)
            },
            "mvrt_status": mvrt_status,
            "functional_tools": self.get_functional_tools(),
            "broken_tools": self.get_broken_tools(),
            "version_conflicts": self.get_version_conflicts(),
            "missing_tools": self.get_missing_tools(),
            "current_tools": self.current_tools,
            "archived_tools": self.archived_tools,
            "version_conflicts_detail": self.version_conflicts,
            "missing_tools_detail": self.missing_tools
        }

# Global registry instance
tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return tool_registry
```

