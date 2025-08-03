# Theory Extraction Implementation Architecture

**Status**: Living Document  
**Version**: 1.0  
**Last Updated**: 2025-01-29  
**Related**: [ADR-022](../adrs/ADR-022-Theory-Selection-Architecture.md), [V13 Meta-Schema](../data/theory-meta-schema.md)

## Overview

This document describes the implementation architecture for Layer 1 of KGAS's two-layer theory architecture: Theory Structure Extraction. The system extracts computable theoretical components from academic texts using the V13 meta-schema, categorizing them into six implementation levels for automated execution.

## Architecture Context

Within the two-layer architecture:
- **Layer 1**: Theory Structure Extraction (this document)
- **Layer 2**: Question-Driven Analysis (see [analytics-service.md](analytics-service.md))

Layer 1 transforms unstructured theoretical knowledge into structured, computable components.

## Six-Level Component Categorization

Theory components are categorized into six implementation levels based on their computational requirements:

### Level 1: FORMULAS
**Description**: Mathematical functions with specific equations  
**V13 Mapping**: `algorithms.mathematical`  
**Implementation**: Python function generation  
**Status**: Fully Implemented  

**Example**:
```python
# From Prospect Theory: v(x) = x^α for gains
def prospect_value_function(x, alpha=0.88):
    if x >= 0:
        return x ** alpha
    else:
        return -lambda_param * ((-x) ** beta)
```

### Level 2: ALGORITHMS
**Description**: Computational methods requiring iteration or complex logic  
**V13 Mapping**: `algorithms.procedural` (computational subtype)  
**Implementation**: Algorithm classes with convergence criteria  
**Status**: 🏗️ Architecture Defined  

**Target Structure**:
```python
class InfluenceAlgorithm:
    def __init__(self, damping=0.85, tolerance=1e-6):
        self.damping = damping
        self.tolerance = tolerance
    
    def calculate(self, network_graph):
        # Iterative calculation with convergence
        pass
```

### Level 3: PROCEDURES
**Description**: Step-by-step workflows and decision processes  
**V13 Mapping**: `algorithms.procedural` (workflow subtype)  
**Implementation**: State machine with conditional logic  
**Status**: 🏗️ Architecture Defined  

**Target Structure**:
```python
class DecisionProcedure:
    def execute(self, context):
        alternatives = self.identify_alternatives(context)
        outcomes = self.evaluate_outcomes(alternatives)
        utilities = self.calculate_utilities(outcomes)
        return self.select_optimal(utilities)
```

### Level 4: RULES
**Description**: Logical rules and conditional reasoning  
**V13 Mapping**: `algorithms.logical`  
**Implementation**: OWL2 DL ontologies with SWRL rules  
**Status**: 🏗️ Architecture Defined  

**Target Structure**:
```python
# OWL2 ontology with reasoning
with onto:
    class SocialActor(Thing): pass
    class Group(Thing): pass
    
    # SWRL rule for in-group bias
    rule = Imp()
    rule.set_as_rule(
        "SocialActor(?x), belongsToGroup(?x, ?g), "
        "SocialActor(?y), belongsToGroup(?y, ?g) "
        "-> exhibitsBias(?x, ?y, 'positive')"
    )
```

### Level 5: SEQUENCES
**Description**: Temporal progressions and stage models  
**V13 Mapping**: Relations with temporal constraints  
**Implementation**: Finite state machines  
**Status**: 🏗️ Architecture Defined  

**Target Structure**:
```python
class StageSequence:
    stages = ["awareness", "interest", "evaluation", "trial", "adoption"]
    
    def can_advance(self, current_stage, conditions):
        # Validate progression conditions
        pass
    
    def advance(self, current_stage, conditions):
        # Execute stage transition
        pass
```

### Level 6: FRAMEWORKS
**Description**: Classification systems and taxonomies  
**V13 Mapping**: Entities with hierarchical relations  
**Implementation**: Decision trees or classifiers  
**Status**: 🏗️ Architecture Defined  

**Target Structure**:
```python
class FrameworkClassifier:
    def __init__(self, classification_rules):
        self.rules = classification_rules
        self.build_decision_tree()
    
    def classify(self, instance):
        features = self.extract_features(instance)
        return self.decision_tree.predict(features)
```

## Component Detection System

The system automatically identifies and routes theory components to appropriate implementation engines:

### Detection Pipeline
```python
def detect_operational_components(v13_theory):
    """Extract and categorize operational components from V13 theory"""
    components = {
        "formulas": [],      # Level 1
        "algorithms": [],    # Level 2
        "procedures": [],    # Level 3
        "rules": [],         # Level 4
        "sequences": [],     # Level 5
        "frameworks": []     # Level 6
    }
    
    # Extract from V13 algorithms section
    if "algorithms" in v13_theory:
        # Mathematical formulas
        if "mathematical" in v13_theory["algorithms"]:
            components["formulas"].extend(
                v13_theory["algorithms"]["mathematical"]
            )
        
        # Logical rules
        if "logical" in v13_theory["algorithms"]:
            components["rules"].extend(
                v13_theory["algorithms"]["logical"]
            )
        
        # Procedural components (split by type)
        if "procedural" in v13_theory["algorithms"]:
            for proc in v13_theory["algorithms"]["procedural"]:
                if proc.get("type") == "computational":
                    components["algorithms"].append(proc)
                elif proc.get("type") == "workflow":
                    components["procedures"].append(proc)
    
    # Detect sequences from temporal relations
    temporal_relations = [
        r for r in v13_theory.get("relations", [])
        if "temporal" in r.get("properties", {})
    ]
    if temporal_relations:
        components["sequences"].append(
            build_sequence_from_relations(temporal_relations)
        )
    
    # Detect frameworks from hierarchical entities
    hierarchical_entities = detect_hierarchical_structures(
        v13_theory.get("entities", [])
    )
    if hierarchical_entities:
        components["frameworks"].extend(hierarchical_entities)
    
    return components
```

### Implementation Strategy Mapping
```python
IMPLEMENTATION_STRATEGIES = {
    "FORMULAS": {
        "generator": LLMFunctionGenerator,
        "validator": MathematicalValidator,
        "executor": PythonFunctionExecutor,
        "requirements": ["numpy", "scipy"]
    },
    "ALGORITHMS": {
        "generator": AlgorithmClassGenerator,
        "validator": ConvergenceValidator,
        "executor": AlgorithmExecutor,
        "requirements": ["networkx", "convergence_metrics"]
    },
    "PROCEDURES": {
        "generator": StateMachineGenerator,
        "validator": WorkflowValidator,
        "executor": ProcedureExecutor,
        "requirements": ["transitions", "workflow_engine"]
    },
    "RULES": {
        "generator": OWL2OntologyGenerator,
        "validator": DLReasonerValidator,
        "executor": OntologyExecutor,
        "requirements": ["owlready2", "rdflib"]
    },
    "SEQUENCES": {
        "generator": TransitionSystemGenerator,
        "validator": SequenceValidator,
        "executor": SequenceExecutor,
        "requirements": ["statemachine", "temporal_logic"]
    },
    "FRAMEWORKS": {
        "generator": ClassifierGenerator,
        "validator": ClassificationValidator,
        "executor": ClassifierExecutor,
        "requirements": ["scikit-learn", "pandas"]
    }
}
```

## Integration Architecture

### Unified Execution Interface
```python
class TheoryComponentExecutor:
    """Unified interface for executing all theory component types"""
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.executors = self._initialize_executors()
    
    def _initialize_executors(self):
        return {
            "formulas": PythonFunctionExecutor(),
            "algorithms": AlgorithmExecutor(),
            "procedures": ProcedureExecutor(),
            "rules": OntologyExecutor(),
            "sequences": SequenceExecutor(),
            "frameworks": ClassifierExecutor()
        }
    
    def execute_component(self, component_type, component, inputs):
        """Execute a theory component with appropriate engine"""
        if component_type not in self.executors:
            raise ValueError(f"Unknown component type: {component_type}")
        
        executor = self.executors[component_type]
        
        # Track provenance
        with self.service_manager.provenance.track_operation(
            f"execute_{component_type}", 
            inputs
        ):
            result = executor.execute(component, inputs)
        
        return result
    
    def validate_component(self, component_type, component):
        """Validate component before execution"""
        strategy = IMPLEMENTATION_STRATEGIES[component_type.upper()]
        validator = strategy["validator"]()
        return validator.validate(component)
```

### Component Registry
```python
class TheoryComponentRegistry:
    """Registry for discovered and implemented theory components"""
    
    def __init__(self):
        self.components = {}
        self.metadata = {}
    
    def register_component(self, theory_id, component_type, component):
        """Register an extracted component"""
        key = f"{theory_id}:{component_type}:{component['name']}"
        
        self.components[key] = component
        self.metadata[key] = {
            "extraction_time": datetime.now(),
            "confidence": component.get("confidence", 0.8),
            "implementation_status": self._get_status(component_type)
        }
    
    def get_components_by_theory(self, theory_id):
        """Get all components for a theory"""
        return {
            k: v for k, v in self.components.items()
            if k.startswith(f"{theory_id}:")
        }
    
    def _get_status(self, component_type):
        """Get implementation status for component type"""
        status_map = {
            "formulas": "implemented",
            "algorithms": "architecture_defined",
            "procedures": "architecture_defined",
            "rules": "architecture_defined",
            "sequences": "architecture_defined",
            "frameworks": "architecture_defined"
        }
        return status_map.get(component_type, "unknown")
```

## Quality Assurance

### Component Validation Framework
```python
class ComponentValidator:
    """Base validator for all component types"""
    
    def validate(self, component):
        """Validate component structure and content"""
        # Check required fields
        self._validate_structure(component)
        
        # Type-specific validation
        self._validate_content(component)
        
        # Test execution capability
        self._validate_execution(component)
        
        return ValidationResult(
            is_valid=True,
            confidence=self._calculate_confidence(component),
            warnings=self._collect_warnings(component)
        )
```

### Testing Strategy
Each component level requires specialized testing:

| Level | Test Focus | Validation Criteria |
|-------|------------|-------------------|
| FORMULAS | Mathematical accuracy | Output matches expected values within tolerance |
| ALGORITHMS | Convergence & correctness | Reaches stable state, produces valid results |
| PROCEDURES | State transitions | All paths reachable, conditions valid |
| RULES | Logical consistency | No contradictions, valid inferences |
| SEQUENCES | Temporal validity | Proper ordering, transition conditions |
| FRAMEWORKS | Classification accuracy | Consistent categorization, complete coverage |

## Implementation Roadmap

### Phase 1: Foundation (Complete)
- V13 meta-schema integration
- Component detection architecture
- Level 1 (FORMULAS) implementation
- LLM code generation pipeline

### Phase 2: Core Expansion (🚧 Current)
Priority implementation order based on complexity and utility:

1. **Level 2 (ALGORITHMS)** - Q1 2025
   - Leverage existing mathematical infrastructure
   - Add iteration and convergence handling
   
2. **Level 3 (PROCEDURES)** - Q1 2025
   - Build on state management patterns
   - Integrate workflow engine
   
3. **Level 6 (FRAMEWORKS)** - Q2 2025
   - Utilize ML classification infrastructure
   - Connect to existing entity systems

### Phase 3: Advanced Systems (🔮 Future)
4. **Level 5 (SEQUENCES)** - Q2 2025
   - Implement temporal logic framework
   - Connect to event systems
   
5. **Level 4 (RULES)** - Q3 2025
   - Deploy OWL2 reasoning infrastructure
   - Integrate with knowledge base

## Performance Considerations

### Optimization Strategies
- **Caching**: Pre-computed components stored in registry
- **Lazy Loading**: Components loaded only when needed
- **Parallel Execution**: Independent components run concurrently
- **Resource Limits**: Timeout and memory constraints per component

### Scalability Targets
- Component extraction: <30 seconds per theory
- Component execution: <5 seconds per invocation
- Registry lookup: <10ms
- Validation: <1 second per component

## Future Enhancements

### Multi-Theory Composition
- Combine components from multiple theories
- Resolve conflicts between theoretical predictions
- Create hybrid analytical approaches

### Advanced Code Generation
- Optimize generated code for performance
- Add automatic parallelization
- Include uncertainty propagation

### Visual Theory Exploration
- Interactive component visualization
- Execution flow diagrams
- Real-time debugging interfaces

## Related Documentation

- [Two-Layer Theory Architecture](../adrs/ADR-022-Theory-Selection-Architecture.md)
- [V13 Meta-Schema](../data/theory-meta-schema.md)
- [Analytics Service](analytics-service.md)
- [Theory Repository](theory-repository.md)

---

**Status Summary**: The six-level implementation architecture provides a comprehensive framework for extracting and executing diverse theoretical components. Level 1 (FORMULAS) is fully operational, demonstrating viability. Levels 2-6 have complete architectural designs ready for phased implementation.