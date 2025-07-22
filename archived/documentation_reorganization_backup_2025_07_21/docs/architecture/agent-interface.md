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