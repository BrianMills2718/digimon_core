# KGAS Component Architecture - Detailed Design

**Version**: 1.0
**Status**: Target Architecture
**Last Updated**: 2025-07-22

## Overview

This document provides detailed architectural specifications for all KGAS components, including interfaces, algorithms, data structures, and interaction patterns.

## Core Services Layer

### 1. Pipeline Orchestrator

The PipelineOrchestrator coordinates all document processing workflows, managing state, handling errors, and ensuring reproducibility.

#### Interface Specification

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    tool_id: str
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
@dataclass
class WorkflowDefinition:
    """Complete workflow specification"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    dependencies: Dict[str, List[str]]  # step_id -> [dependency_ids]
    metadata: Dict[str, Any]

class IPipelineOrchestrator(ABC):
    """Interface for pipeline orchestration"""
    
    @abstractmethod
    async def create_workflow(self, definition: WorkflowDefinition) -> str:
        """Create new workflow instance"""
        pass
    
    @abstractmethod
    async def execute_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """Execute workflow, yielding progress updates"""
        pass
    
    @abstractmethod
    async def pause_workflow(self, workflow_id: str) -> None:
        """Pause running workflow"""
        pass
    
    @abstractmethod
    async def resume_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """Resume paused workflow"""
        pass
    
    @abstractmethod
    async def get_workflow_state(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow state"""
        pass
```

#### Core Algorithm

```python
class PipelineOrchestrator(IPipelineOrchestrator):
    """Concrete implementation of pipeline orchestration"""
    
    def __init__(self, service_manager: ServiceManager):
        self.workflows = {}  # In-memory for now
        self.tool_registry = service_manager.get_service("tool_registry")
        self.state_service = service_manager.get_service("workflow_state")
        self.provenance = service_manager.get_service("provenance")
        
    async def execute_workflow(self, workflow_id: str) -> AsyncIterator[WorkflowStep]:
        """
        Execute workflow using topological sort for dependency resolution
        
        Algorithm:
        1. Build dependency graph
        2. Topological sort to find execution order
        3. Execute steps in parallel where possible
        4. Handle errors with retry logic
        5. Checkpoint state after each step
        """
        workflow = self.workflows[workflow_id]
        
        # Build execution graph
        graph = self._build_dependency_graph(workflow)
        execution_order = self._topological_sort(graph)
        
        # Group steps that can run in parallel
        parallel_groups = self._identify_parallel_groups(execution_order, graph)
        
        for group in parallel_groups:
            # Execute steps in parallel
            tasks = []
            for step_id in group:
                step = workflow.get_step(step_id)
                task = self._execute_step(step)
                tasks.append(task)
            
            # Wait for all parallel steps to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle errors
            for step_id, result in zip(group, results):
                step = workflow.get_step(step_id)
                
                if isinstance(result, Exception):
                    step.status = WorkflowStatus.FAILED
                    step.error = str(result)
                    
                    # Retry logic
                    if self._should_retry(step, result):
                        await asyncio.sleep(self._get_backoff_time(step))
                        retry_result = await self._execute_step(step)
                        if not isinstance(retry_result, Exception):
                            result = retry_result
                        else:
                            # Propagate failure
                            raise WorkflowExecutionError(
                                f"Step {step_id} failed after retries: {result}"
                            )
                else:
                    step.outputs = result
                    step.status = WorkflowStatus.COMPLETED
                
                # Checkpoint state
                await self._checkpoint_state(workflow_id, step)
                
                # Yield progress
                yield step
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Kahn's algorithm for topological sorting
        
        Time complexity: O(V + E)
        Space complexity: O(V)
        """
        # Count in-degrees
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                in_degree[neighbor] += 1
        
        # Find nodes with no dependencies
        queue = [node for node in graph if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree for neighbors
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(graph):
            raise ValueError("Circular dependency detected in workflow")
        
        return result
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute single workflow step with monitoring"""
        # Get tool from registry
        tool = self.tool_registry.get_tool(step.tool_id)
        
        # Create execution context
        context = ExecutionContext(
            workflow_id=step.workflow_id,
            step_id=step.step_id,
            provenance=self.provenance
        )
        
        # Execute with monitoring
        start_time = time.time()
        try:
            # Prepare request
            request = ToolRequest(
                input_data=step.inputs,
                options=step.options,
                context=context
            )
            
            # Execute tool
            result = await tool.execute(request)
            
            # Record provenance
            await self.provenance.record(
                operation=f"execute_{step.tool_id}",
                inputs=step.inputs,
                outputs=result.data,
                duration=time.time() - start_time,
                metadata={
                    "workflow_id": step.workflow_id,
                    "step_id": step.step_id,
                    "confidence": result.confidence.value
                }
            )
            
            return result.data
            
        except Exception as e:
            # Record failure
            await self.provenance.record(
                operation=f"execute_{step.tool_id}_failed",
                inputs=step.inputs,
                error=str(e),
                duration=time.time() - start_time
            )
            raise
```

### 2. Analytics Service

The AnalyticsService orchestrates cross-modal analysis operations, selecting optimal representations and coordinating conversions.

#### Interface Specification

```python
@dataclass
class AnalysisRequest:
    """Request for cross-modal analysis"""
    query: str
    data_source: Any  # Graph, Table, or Vector data
    preferred_mode: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class AnalysisResult:
    """Result of cross-modal analysis"""
    data: Any
    mode: str  # "graph", "table", "vector"
    confidence: AdvancedConfidenceScore
    provenance: List[str]  # Source references
    conversions: List[str]  # Modal conversions applied

class IAnalyticsService(ABC):
    """Interface for cross-modal analytics"""
    
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform cross-modal analysis"""
        pass
    
    @abstractmethod
    async def convert(self, data: Any, from_mode: str, to_mode: str) -> Any:
        """Convert data between modes"""
        pass
    
    @abstractmethod
    async def suggest_mode(self, query: str, data_stats: Dict) -> str:
        """Suggest optimal mode for analysis"""
        pass
```

#### Mode Selection Algorithm

```python
class AnalyticsService(IAnalyticsService):
    """Orchestrates cross-modal analysis"""
    
    def __init__(self, service_manager: ServiceManager):
        self.mode_bridges = {
            ("graph", "table"): GraphToTableBridge(),
            ("table", "vector"): TableToVectorBridge(),
            ("vector", "graph"): VectorToGraphBridge(),
            # ... other combinations
        }
        self.mode_analyzers = {
            "graph": GraphAnalyzer(),
            "table": TableAnalyzer(), 
            "vector": VectorAnalyzer()
        }
        
    async def suggest_mode(self, query: str, data_stats: Dict) -> str:
        """
        LLM-driven mode selection based on query intent
        
        Algorithm:
        1. Extract query features
        2. Match to mode capabilities
        3. Consider data characteristics
        4. Return optimal mode
        """
        # Extract query intent features
        features = self._extract_query_features(query)
        
        # Score each mode
        mode_scores = {}
        
        # Graph mode scoring
        graph_score = 0.0
        if any(term in features for term in [
            "relationship", "connection", "network", "path",
            "centrality", "community", "influence"
        ]):
            graph_score += 0.8
        
        if data_stats.get("node_count", 0) > 10:
            graph_score += 0.2
            
        mode_scores["graph"] = graph_score
        
        # Table mode scoring  
        table_score = 0.0
        if any(term in features for term in [
            "aggregate", "sum", "average", "count", "group",
            "correlation", "regression", "statistical"
        ]):
            table_score += 0.8
            
        if data_stats.get("has_numeric_features", False):
            table_score += 0.2
            
        mode_scores["table"] = table_score
        
        # Vector mode scoring
        vector_score = 0.0
        if any(term in features for term in [
            "similar", "cluster", "embed", "nearest",
            "semantic", "distance", "group"
        ]):
            vector_score += 0.8
            
        if data_stats.get("has_embeddings", False):
            vector_score += 0.2
            
        mode_scores["vector"] = vector_score
        
        # Return highest scoring mode
        return max(mode_scores.items(), key=lambda x: x[1])[0]
    
    async def convert(self, data: Any, from_mode: str, to_mode: str) -> Any:
        """
        Convert data between modes with enrichment
        
        Principle: Add information during conversion, don't lose it
        """
        bridge_key = (from_mode, to_mode)
        
        if bridge_key not in self.mode_bridges:
            # Try indirect path
            path = self._find_conversion_path(from_mode, to_mode)
            if not path:
                raise ValueError(f"No conversion path from {from_mode} to {to_mode}")
            
            # Multi-hop conversion
            result = data
            for i in range(len(path) - 1):
                bridge = self.mode_bridges[(path[i], path[i+1])]
                result = await bridge.convert(result)
            
            return result
        
        # Direct conversion
        bridge = self.mode_bridges[bridge_key]
        return await bridge.convert(data)
```

### 3. Identity Service

The IdentityService manages entity resolution and maintains consistent identity across documents.

#### Interface and Algorithm

```python
class IIdentityService(ABC):
    """Interface for entity identity management"""
    
    @abstractmethod
    async def resolve_entity(self, mention: Mention, context: str) -> Entity:
        """Resolve mention to canonical entity"""
        pass
    
    @abstractmethod
    async def merge_entities(self, entity_ids: List[str]) -> str:
        """Merge multiple entities into one"""
        pass
    
    @abstractmethod
    async def split_entity(self, entity_id: str, criteria: Dict) -> List[str]:
        """Split entity into multiple entities"""
        pass

class IdentityService(IIdentityService):
    """Advanced entity resolution with context awareness"""
    
    def __init__(self, service_manager: ServiceManager):
        self.entity_store = service_manager.get_service("entity_store")
        self.embedder = service_manager.get_service("embedder")
        self.uncertainty = service_manager.get_service("uncertainty")
        
    async def resolve_entity(self, mention: Mention, context: str) -> Entity:
        """
        Context-aware entity resolution algorithm
        
        Steps:
        1. Generate contextual embedding
        2. Search for candidate entities
        3. Score candidates with context
        4. Apply uncertainty quantification
        5. Return best match or create new
        """
        # Step 1: Contextual embedding
        mention_embedding = await self.embedder.embed_with_context(
            text=mention.surface_form,
            context=context,
            window_size=500  # tokens
        )
        
        # Step 2: Find candidates
        candidates = await self._find_candidates(mention, mention_embedding)
        
        if not candidates:
            # Create new entity
            return await self._create_entity(mention, mention_embedding)
        
        # Step 3: Context-aware scoring
        scores = []
        for candidate in candidates:
            score = await self._score_candidate(
                mention=mention,
                mention_embedding=mention_embedding,
                candidate=candidate,
                context=context
            )
            scores.append(score)
        
        # Step 4: Apply uncertainty
        best_idx = np.argmax([s.value for s in scores])
        best_score = scores[best_idx]
        best_candidate = candidates[best_idx]
        
        # Step 5: Decision with threshold
        if best_score.value > self.resolution_threshold:
            # Update entity with new mention
            await self._add_mention_to_entity(
                entity=best_candidate,
                mention=mention,
                confidence=best_score
            )
            return best_candidate
        else:
            # Uncertainty too high - create new entity
            return await self._create_entity(
                mention, 
                mention_embedding,
                similar_to=[best_candidate.entity_id]
            )
    
    async def _score_candidate(self, 
                              mention: Mention,
                              mention_embedding: np.ndarray,
                              candidate: Entity,
                              context: str) -> AdvancedConfidenceScore:
        """
        Multi-factor scoring for entity resolution
        
        Factors:
        1. Embedding similarity
        2. String similarity
        3. Type compatibility
        4. Context compatibility
        5. Temporal consistency
        """
        scores = {}
        
        # 1. Embedding similarity (cosine)
        embedding_sim = self._cosine_similarity(
            mention_embedding, 
            candidate.embedding
        )
        scores["embedding"] = embedding_sim
        
        # 2. String similarity (multiple metrics)
        string_scores = [
            self._levenshtein_similarity(
                mention.surface_form, 
                candidate.canonical_name
            ),
            self._jaro_winkler_similarity(
                mention.surface_form,
                candidate.canonical_name  
            ),
            self._token_overlap(
                mention.surface_form,
                candidate.canonical_name
            )
        ]
        scores["string"] = max(string_scores)
        
        # 3. Type compatibility
        if mention.entity_type == candidate.entity_type:
            scores["type"] = 1.0
        elif self._types_compatible(mention.entity_type, candidate.entity_type):
            scores["type"] = 0.7
        else:
            scores["type"] = 0.0
        
        # 4. Context compatibility using LLM
        context_score = await self._evaluate_context_compatibility(
            mention_context=context,
            entity_contexts=candidate.contexts[-5:],  # Last 5 contexts
            mention_text=mention.surface_form,
            entity_name=candidate.canonical_name
        )
        scores["context"] = context_score
        
        # 5. Temporal consistency
        if self._temporally_consistent(mention.timestamp, candidate.temporal_bounds):
            scores["temporal"] = 1.0
        else:
            scores["temporal"] = 0.3
        
        # Weighted combination
        weights = {
            "embedding": 0.3,
            "string": 0.2,
            "type": 0.2,
            "context": 0.2,
            "temporal": 0.1
        }
        
        final_score = sum(
            scores[factor] * weight 
            for factor, weight in weights.items()
        )
        
        # Build confidence score with CERQual
        return AdvancedConfidenceScore(
            value=final_score,
            methodological_quality=0.9,  # Well-established algorithm
            relevance_to_context=scores["context"],
            coherence_score=scores["type"] * scores["temporal"],
            data_adequacy=len(candidate.mentions) / 100,  # More mentions = better
            evidence_weight=len(candidate.mentions),
            depends_on=[mention.extraction_confidence]
        )
```

### 4. Theory Repository

The TheoryRepository manages theory schemas and provides theory-aware processing capabilities.

#### Theory Management System

```python
@dataclass
class TheorySchema:
    """Complete theory specification"""
    schema_id: str
    name: str
    domain: str
    version: str
    
    # Core components
    constructs: List[Construct]
    relationships: List[TheoryRelationship]
    measurement_models: List[MeasurementModel]
    
    # Ontological grounding
    ontology_mappings: Dict[str, str]  # construct_id -> ontology_uri
    dolce_alignment: Dict[str, str]   # construct_id -> DOLCE category
    
    # Validation rules
    constraints: List[Constraint]
    incompatibilities: List[str]  # Incompatible theory IDs
    
    # Metadata
    authors: List[str]
    citations: List[str]
    evidence_base: Dict[str, float]  # construct -> evidence strength

class ITheoryRepository(ABC):
    """Interface for theory management"""
    
    @abstractmethod
    async def register_theory(self, schema: TheorySchema) -> str:
        """Register new theory schema"""
        pass
    
    @abstractmethod
    async def get_theory(self, schema_id: str) -> TheorySchema:
        """Retrieve theory schema"""
        pass
    
    @abstractmethod
    async def validate_extraction(self, 
                                 extraction: Dict,
                                 theory_id: str) -> ValidationResult:
        """Validate extraction against theory"""
        pass
    
    @abstractmethod
    async def suggest_theories(self, 
                             domain: str,
                             text_sample: str) -> List[TheorySchema]:
        """Suggest applicable theories"""
        pass

class TheoryRepository(ITheoryRepository):
    """Advanced theory management with validation"""
    
    def __init__(self, service_manager: ServiceManager):
        self.theories: Dict[str, TheorySchema] = {}
        self.mcl = service_manager.get_service("master_concept_library")
        self.validator = TheoryValidator()
        
    async def validate_extraction(self,
                                 extraction: Dict,
                                 theory_id: str) -> ValidationResult:
        """
        Validate extraction against theory constraints
        
        Algorithm:
        1. Check construct presence
        2. Validate measurement models
        3. Check relationship consistency
        4. Apply theory constraints
        5. Calculate confidence
        """
        theory = self.theories[theory_id]
        violations = []
        warnings = []
        
        # 1. Check required constructs
        extracted_constructs = set(extraction.get("constructs", {}).keys())
        required_constructs = {
            c.id for c in theory.constructs 
            if c.required
        }
        
        missing = required_constructs - extracted_constructs
        if missing:
            violations.append(
                f"Missing required constructs: {missing}"
            )
        
        # 2. Validate measurements
        for construct_id, measurements in extraction.get("measurements", {}).items():
            construct = self._get_construct(theory, construct_id)
            if not construct:
                continue
                
            model = self._get_measurement_model(theory, construct_id)
            if model:
                valid, issues = self._validate_measurement(
                    measurements, 
                    model
                )
                if not valid:
                    violations.extend(issues)
        
        # 3. Check relationships
        for rel in extraction.get("relationships", []):
            if not self._relationship_valid(rel, theory):
                violations.append(
                    f"Invalid relationship: {rel['type']} between "
                    f"{rel['source']} and {rel['target']}"
                )
        
        # 4. Apply constraints
        for constraint in theory.constraints:
            if not self._evaluate_constraint(constraint, extraction):
                violations.append(
                    f"Constraint violation: {constraint.description}"
                )
        
        # 5. Calculate confidence
        if violations:
            confidence = 0.3  # Low confidence with violations
        elif warnings:
            confidence = 0.7  # Medium confidence with warnings
        else:
            confidence = 0.9  # High confidence when fully valid
        
        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            confidence=confidence,
            suggestions=self._generate_suggestions(violations, theory)
        )
    
    async def suggest_theories(self,
                             domain: str,
                             text_sample: str) -> List[TheorySchema]:
        """
        Smart theory suggestion using domain and content analysis
        
        Algorithm:
        1. Filter by domain
        2. Extract key concepts from text
        3. Match concepts to theory constructs
        4. Rank by relevance
        5. Check compatibility
        """
        # 1. Domain filtering
        candidate_theories = [
            t for t in self.theories.values()
            if t.domain == domain or domain in t.related_domains
        ]
        
        # 2. Extract concepts using NER + domain terminology
        concepts = await self._extract_key_concepts(text_sample, domain)
        
        # 3. Score theories by concept overlap
        theory_scores = []
        for theory in candidate_theories:
            score = self._calculate_theory_relevance(
                theory=theory,
                concepts=concepts,
                text_sample=text_sample
            )
            theory_scores.append((theory, score))
        
        # 4. Rank and filter
        theory_scores.sort(key=lambda x: x[1], reverse=True)
        top_theories = [t for t, s in theory_scores[:5] if s > 0.3]
        
        # 5. Check compatibility if multiple theories
        if len(top_theories) > 1:
            compatible_sets = self._find_compatible_theory_sets(top_theories)
            # Return largest compatible set
            if compatible_sets:
                top_theories = max(compatible_sets, key=len)
        
        return top_theories
```

### 5. Provenance Service

Complete lineage tracking for reproducibility.

#### Provenance Implementation

```python
@dataclass
class ProvenanceRecord:
    """Complete provenance for an operation"""
    record_id: str
    timestamp: datetime
    operation: str
    tool_id: str
    tool_version: str
    
    # Inputs and outputs
    inputs: List[ProvenanceReference]
    outputs: List[ProvenanceReference]
    parameters: Dict[str, Any]
    
    # Execution context
    workflow_id: Optional[str]
    step_id: Optional[str]
    user_id: Optional[str]
    
    # Performance metrics
    duration_ms: float
    memory_usage_mb: float
    
    # Quality metrics
    confidence: Optional[float]
    warnings: List[str]
    
    # Lineage
    depends_on: List[str]  # Previous record IDs
    
@dataclass
class ProvenanceReference:
    """Reference to data with provenance"""
    ref_type: str  # "entity", "document", "chunk", etc.
    ref_id: str
    ref_hash: str  # Content hash for verification
    confidence: float

class ProvenanceService:
    """Comprehensive provenance tracking"""
    
    def __init__(self, storage: ProvenanceStorage):
        self.storage = storage
        self.hasher = ContentHasher()
        
    async def record_operation(self,
                             operation: str,
                             tool: Tool,
                             inputs: Dict[str, Any],
                             outputs: Dict[str, Any],
                             context: ExecutionContext) -> ProvenanceRecord:
        """
        Record complete operation provenance
        
        Features:
        1. Content hashing for verification
        2. Automatic lineage tracking
        3. Performance metrics capture
        4. Confidence propagation
        """
        # Create input references with hashing
        input_refs = []
        for key, value in inputs.items():
            ref = ProvenanceReference(
                ref_type=self._determine_type(value),
                ref_id=self._extract_id(value),
                ref_hash=self.hasher.hash(value),
                confidence=self._extract_confidence(value)
            )
            input_refs.append(ref)
        
        # Create output references
        output_refs = []
        for key, value in outputs.items():
            ref = ProvenanceReference(
                ref_type=self._determine_type(value),
                ref_id=self._extract_id(value), 
                ref_hash=self.hasher.hash(value),
                confidence=self._extract_confidence(value)
            )
            output_refs.append(ref)
        
        # Find dependencies from inputs
        depends_on = await self._find_dependencies(input_refs)
        
        # Create record
        record = ProvenanceRecord(
            record_id=self._generate_id(),
            timestamp=datetime.utcnow(),
            operation=operation,
            tool_id=tool.tool_id,
            tool_version=tool.version,
            inputs=input_refs,
            outputs=output_refs,
            parameters=tool.get_parameters(),
            workflow_id=context.workflow_id,
            step_id=context.step_id,
            user_id=context.user_id,
            duration_ms=context.duration_ms,
            memory_usage_mb=context.memory_usage_mb,
            confidence=outputs.get("confidence"),
            warnings=context.warnings,
            depends_on=depends_on
        )
        
        # Store record
        await self.storage.store(record)
        
        # Update indexes for fast queries
        await self._update_indexes(record)
        
        return record
    
    async def trace_lineage(self, 
                          artifact_id: str,
                          direction: str = "backward") -> LineageGraph:
        """
        Trace complete lineage of an artifact
        
        Algorithm:
        1. Start from artifact
        2. Follow provenance links
        3. Build DAG of operations
        4. Include confidence decay
        """
        if direction == "backward":
            return await self._trace_backward(artifact_id)
        else:
            return await self._trace_forward(artifact_id)
    
    async def _trace_backward(self, artifact_id: str) -> LineageGraph:
        """Trace how artifact was created"""
        graph = LineageGraph()
        visited = set()
        queue = [(artifact_id, 0)]  # (id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Find records that output this artifact
            records = await self.storage.find_by_output(current_id)
            
            for record in records:
                # Add node to graph
                graph.add_node(
                    node_id=record.record_id,
                    node_type="operation",
                    operation=record.operation,
                    tool=record.tool_id,
                    timestamp=record.timestamp,
                    confidence=record.confidence,
                    depth=depth
                )
                
                # Add edge from inputs to this operation
                for input_ref in record.inputs:
                    graph.add_edge(
                        source=input_ref.ref_id,
                        target=record.record_id,
                        edge_type="input_to",
                        confidence_impact=input_ref.confidence
                    )
                    
                    # Queue input for processing
                    if input_ref.ref_id not in visited:
                        queue.append((input_ref.ref_id, depth + 1))
                
                # Add edge from operation to output
                graph.add_edge(
                    source=record.record_id,
                    target=current_id,
                    edge_type="output_from",
                    confidence_impact=record.confidence
                )
        
        return graph
    
    async def verify_reproducibility(self,
                                   workflow_id: str,
                                   target_outputs: List[str]) -> ReproducibilityReport:
        """
        Verify workflow can be reproduced
        
        Checks:
        1. All inputs available
        2. All tools available with correct versions
        3. Parameters recorded
        4. No missing dependencies
        """
        records = await self.storage.find_by_workflow(workflow_id)
        
        issues = []
        missing_inputs = []
        version_conflicts = []
        
        for record in records:
            # Check input availability
            for input_ref in record.inputs:
                if not await self._artifact_exists(input_ref):
                    missing_inputs.append(input_ref)
            
            # Check tool availability
            tool = self.tool_registry.get_tool(
                record.tool_id, 
                version=record.tool_version
            )
            if not tool:
                issues.append(
                    f"Tool {record.tool_id} v{record.tool_version} not available"
                )
            elif tool.version != record.tool_version:
                version_conflicts.append(
                    f"Tool {record.tool_id}: recorded v{record.tool_version}, "
                    f"available v{tool.version}"
                )
        
        # Calculate reproducibility score
        score = 1.0
        if missing_inputs:
            score *= 0.5
        if version_conflicts:
            score *= 0.8
        if issues:
            score *= 0.3
        
        return ReproducibilityReport(
            reproducible=score > 0.7,
            score=score,
            missing_inputs=missing_inputs,
            version_conflicts=version_conflicts,
            issues=issues,
            recommendations=self._generate_recommendations(
                missing_inputs,
                version_conflicts,
                issues
            )
        )
```

## Cross-Modal Bridge Components

### Graph to Table Bridge

```python
class GraphToTableBridge:
    """Convert graph data to tabular format with enrichment"""
    
    async def convert(self, graph: Neo4jGraph) -> pd.DataFrame:
        """
        Convert graph to table with computed features
        
        Enrichment approach:
        1. Node properties → columns
        2. Add computed graph metrics
        3. Aggregate relationship data
        4. Preserve graph structure info
        """
        # Extract nodes with properties
        nodes_data = []
        
        async for node in graph.get_nodes():
            row = {
                "node_id": node.id,
                "type": node.labels[0],
                **node.properties
            }
            
            # Add graph metrics
            metrics = await self._compute_node_metrics(node, graph)
            row.update({
                "degree": metrics.degree,
                "in_degree": metrics.in_degree,
                "out_degree": metrics.out_degree,
                "pagerank": metrics.pagerank,
                "betweenness": metrics.betweenness,
                "clustering_coeff": metrics.clustering_coefficient,
                "community_id": metrics.community_id
            })
            
            # Aggregate relationship info
            rel_summary = await self._summarize_relationships(node, graph)
            row.update({
                "rel_types": rel_summary.types,
                "rel_count": rel_summary.count,
                "avg_rel_weight": rel_summary.avg_weight,
                "strongest_connection": rel_summary.strongest
            })
            
            nodes_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(nodes_data)
        
        # Add metadata
        df.attrs["source_type"] = "graph"
        df.attrs["conversion_time"] = datetime.utcnow()
        df.attrs["node_count"] = len(nodes_data)
        df.attrs["enrichments"] = [
            "degree_metrics",
            "centrality_scores", 
            "community_detection",
            "relationship_aggregation"
        ]
        
        return df
```

### Table to Vector Bridge

```python
class TableToVectorBridge:
    """Convert tabular data to vector representations"""
    
    async def convert(self, df: pd.DataFrame) -> VectorStore:
        """
        Convert table to vectors with multiple strategies
        
        Strategies:
        1. Row embeddings (each row → vector)
        2. Column embeddings (each column → vector)
        3. Cell embeddings (each cell → vector)
        4. Aggregate embeddings (groups → vectors)
        """
        vector_store = VectorStore()
        
        # Strategy 1: Row embeddings
        if self._should_embed_rows(df):
            row_vectors = await self._embed_rows(df)
            vector_store.add_vectors(
                vectors=row_vectors,
                metadata={"type": "row", "source": "table"}
            )
        
        # Strategy 2: Column embeddings for text columns
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if self._should_embed_column(df[col]):
                col_vectors = await self._embed_column(df[col])
                vector_store.add_vectors(
                    vectors=col_vectors,
                    metadata={"type": "column", "column_name": col}
                )
        
        # Strategy 3: Smart aggregations
        if "group_by" in df.attrs:
            group_col = df.attrs["group_by"]
            for group_val in df[group_col].unique():
                group_data = df[df[group_col] == group_val]
                group_vector = await self._embed_group(group_data)
                vector_store.add_vector(
                    vector=group_vector,
                    metadata={
                        "type": "group",
                        "group": f"{group_col}={group_val}",
                        "size": len(group_data)
                    }
                )
        
        return vector_store
    
    async def _embed_rows(self, df: pd.DataFrame) -> List[np.ndarray]:
        """Embed each row as a vector"""
        embeddings = []
        
        for _, row in df.iterrows():
            # Combine all row data into text
            text_parts = []
            for col, val in row.items():
                if pd.notna(val):
                    text_parts.append(f"{col}: {val}")
            
            row_text = "; ".join(text_parts)
            embedding = await self.embedder.embed(row_text)
            embeddings.append(embedding)
        
        return embeddings
```

## Tool Contract Implementation

### Example Tool: Advanced Entity Extractor

```python
class AdvancedEntityExtractor(KGASTool):
    """
    Theory-aware entity extraction with uncertainty
    
    Demonstrates:
    1. Contract compliance
    2. Theory integration
    3. Uncertainty quantification
    4. Error handling
    """
    
    def __init__(self):
        self.ner_model = self._load_model()
        self.theory_matcher = TheoryAwareMatcher()
        self.uncertainty_engine = UncertaintyEngine()
        
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "context": {"type": "string"},
                "theory_schemas": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {"type": "string"},
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "theory_grounding": {"type": "object"}
                        }
                    }
                }
            }
        }
    
    async def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute entity extraction with full contract compliance
        """
        try:
            # Validate input
            text = request.input_data["text"]
            context = request.input_data.get("context", "")
            theory_ids = request.input_data.get("theory_schemas", [])
            
            # Load theories if specified
            theories = []
            if theory_ids:
                for theory_id in theory_ids:
                    theory = await self.theory_repo.get_theory(theory_id)
                    theories.append(theory)
            
            # Step 1: Base NER
            base_entities = await self._extract_base_entities(text)
            
            # Step 2: Theory-aware enhancement
            if theories:
                enhanced_entities = await self._enhance_with_theory(
                    base_entities, 
                    text,
                    theories
                )
            else:
                enhanced_entities = base_entities
            
            # Step 3: Context-aware resolution
            resolved_entities = await self._resolve_with_context(
                enhanced_entities,
                context
            )
            
            # Step 4: Uncertainty quantification
            final_entities = []
            for entity in resolved_entities:
                confidence = await self.uncertainty_engine.assess_uncertainty(
                    claim=entity,
                    context=UncertaintyContext(
                        domain=self._detect_domain(text),
                        has_theory=len(theories) > 0,
                        context_strength=len(context) / len(text)
                    )
                )
                
                entity["confidence"] = confidence.value
                entity["uncertainty_details"] = confidence.to_dict()
                final_entities.append(entity)
            
            # Build result
            return ToolResult(
                status="success",
                data={"entities": final_entities},
                confidence=self._aggregate_confidence(final_entities),
                metadata={
                    "model_version": self.ner_model.version,
                    "theories_applied": theory_ids,
                    "entity_count": len(final_entities)
                },
                provenance=ProvenanceRecord(
                    operation="entity_extraction",
                    tool_id=self.tool_id,
                    inputs={"text": text[:100] + "..."},
                    outputs={"entity_count": len(final_entities)}
                )
            )
            
        except Exception as e:
            return ToolResult(
                status="error",
                data={},
                confidence=AdvancedConfidenceScore(value=0.0),
                metadata={"error": str(e)},
                provenance=ProvenanceRecord(
                    operation="entity_extraction_failed",
                    tool_id=self.tool_id,
                    error=str(e)
                )
            )
    
    async def _enhance_with_theory(self,
                                  entities: List[Dict],
                                  text: str,
                                  theories: List[TheorySchema]) -> List[Dict]:
        """
        Enhance entities with theory grounding
        
        Example:
        Base entity: {"text": "social capital", "type": "CONCEPT"}
        Enhanced: {
            "text": "social capital",
            "type": "THEORETICAL_CONSTRUCT",
            "theory_grounding": {
                "theory": "putnam_social_capital",
                "construct_id": "social_capital",
                "dimensions": ["bonding", "bridging"],
                "measurement_hints": ["trust", "reciprocity", "networks"]
            }
        }
        """
        enhanced = []
        
        for entity in entities:
            # Try to ground in each theory
            groundings = []
            for theory in theories:
                grounding = await self.theory_matcher.ground_entity(
                    entity_text=entity["text"],
                    entity_context=text[
                        max(0, entity["start"]-100):
                        min(len(text), entity["end"]+100)
                    ],
                    theory=theory
                )
                if grounding.confidence > 0.5:
                    groundings.append(grounding)
            
            if groundings:
                # Use best grounding
                best_grounding = max(groundings, key=lambda g: g.confidence)
                entity["theory_grounding"] = best_grounding.to_dict()
                entity["type"] = f"THEORETICAL_{entity['type']}"
            
            enhanced.append(entity)
        
        return enhanced
```

## Performance Optimization Patterns

### Async Processing Pattern

```python
class AsyncBatchProcessor:
    """Efficient batch processing with concurrency control"""
    
    def __init__(self, max_concurrency: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.results_queue = asyncio.Queue()
        
    async def process_batch(self, 
                          items: List[Any],
                          processor: Callable,
                          batch_size: int = 100) -> List[Any]:
        """
        Process items in batches with controlled concurrency
        
        Features:
        1. Automatic batching
        2. Concurrency limiting
        3. Progress tracking
        4. Error isolation
        """
        batches = [
            items[i:i + batch_size] 
            for i in range(0, len(items), batch_size)
        ]
        
        tasks = []
        for batch_idx, batch in enumerate(batches):
            task = self._process_batch_with_progress(
                batch, 
                processor,
                batch_idx,
                len(batches)
            )
            tasks.append(task)
        
        # Process all batches
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        errors = []
        
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                errors.append(batch_result)
            else:
                all_results.extend(batch_result)
        
        if errors:
            # Log errors but don't fail entire batch
            for error in errors:
                logger.error(f"Batch processing error: {error}")
        
        return all_results
    
    async def _process_batch_with_progress(self,
                                         batch: List[Any],
                                         processor: Callable,
                                         batch_idx: int,
                                         total_batches: int) -> List[Any]:
        """Process single batch with semaphore control"""
        async with self.semaphore:
            results = []
            
            for idx, item in enumerate(batch):
                try:
                    result = await processor(item)
                    results.append(result)
                    
                    # Report progress
                    progress = (batch_idx * len(batch) + idx + 1) / (total_batches * len(batch))
                    await self.results_queue.put({
                        "type": "progress",
                        "value": progress
                    })
                    
                except Exception as e:
                    # Isolated error handling
                    results.append(ProcessingError(item=item, error=e))
                    await self.results_queue.put({
                        "type": "error",
                        "item": item,
                        "error": str(e)
                    })
            
            return results
```

### Caching Strategy

```python
class IntelligentCache:
    """Multi-level caching with TTL and LRU eviction"""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 disk_cache_size: int = 10000):
        self.memory_cache = LRUCache(maxsize=memory_cache_size)
        self.disk_cache = DiskCache(max_size=disk_cache_size)
        self.stats = CacheStats()
        
    async def get_or_compute(self,
                           key: str,
                           compute_func: Callable,
                           ttl: int = 3600) -> Any:
        """
        Get from cache or compute with fallback
        
        Cache hierarchy:
        1. Memory cache (fastest)
        2. Disk cache (fast)
        3. Compute (slow)
        """
        # Check memory cache
        result = self.memory_cache.get(key)
        if result is not None:
            self.stats.memory_hits += 1
            return result
        
        # Check disk cache
        result = await self.disk_cache.get(key)
        if result is not None:
            self.stats.disk_hits += 1
            # Promote to memory cache
            self.memory_cache.put(key, result, ttl)
            return result
        
        # Compute and cache
        self.stats.misses += 1
        result = await compute_func()
        
        # Store in both caches
        self.memory_cache.put(key, result, ttl)
        await self.disk_cache.put(key, result, ttl * 10)  # Longer TTL for disk
        
        return result
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        # Memory cache invalidation
        keys_to_remove = [
            k for k in self.memory_cache.keys()
            if fnmatch(k, pattern)
        ]
        for key in keys_to_remove:
            self.memory_cache.invalidate(key)
        
        # Disk cache invalidation
        self.disk_cache.invalidate_pattern(pattern)
```

## Summary

This detailed component architecture provides:

1. **Complete interface specifications** for all major components
2. **Detailed algorithms** with complexity analysis
3. **Concrete pseudo-code** examples
4. **Data structure definitions**
5. **Error handling patterns**
6. **Performance optimization strategies**

Each component is designed to:
- Support the cross-modal analysis vision
- Integrate with theory frameworks
- Propagate uncertainty properly
- Maintain complete provenance
- Scale within single-node constraints

The architecture enables the ambitious KGAS vision while maintaining practical implementability through clear specifications and modular design.