# Six-Level Theory Automation Architecture

**Date**: 2025-07-27  
**Status**: Architecture Defined, Level 1 Implemented  
**Type**: Target Architecture Design  
**Related**: [Theory-to-Code Workflow](THEORY_TO_CODE_WORKFLOW.md), [ADR-022](adrs/ADR-022-Theory-Selection-Architecture.md)

## Overview

This document defines the **target architecture** for automating social science theories through a six-level categorization system. Each level requires different computational approaches to handle the diversity of theoretical content beyond simple mathematical formulas.

## Architectural Vision

### Core Problem
Social science theories contain diverse operational components that cannot be handled by a single computational approach:
- **Mathematical formulas** require function execution
- **Logical rules** require reasoning engines  
- **Sequential processes** require state machines
- **Classification schemes** require decision trees
- **Decision procedures** require workflow systems
- **Computational algorithms** require iterative processing

### Solution: Six-Level Architecture
The system categorizes theoretical components into six distinct levels, each with specialized implementation patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Theory Input (V13 Schema)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Component Detection & Routing                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │  FORMULAS   │ ALGORITHMS  │ PROCEDURES  │    RULES    │  │
│  │     +       │     +       │     +       │     +       │  │
│  │ SEQUENCES   │ FRAMEWORKS  │             │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Specialized Implementation Engines             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Python    │  Algorithm  │   State     │  OWL2 DL    │  │
│  │ Functions   │   Classes   │  Machines   │ Reasoning   │  │
│  │     +       │     +       │     +       │     +       │  │
│  │ Transitions │ Classifiers │             │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Unified Results                          │
└─────────────────────────────────────────────────────────────┘
```

## Level Definitions

### Level 1: FORMULAS
**Purpose**: Mathematical functions with specific equations  
**Input**: Mathematical expressions from theory  
**Output**: Python executable functions  
**Implementation**: Dynamic function generation with parameter mapping  
**Status**: **FULLY IMPLEMENTED**

**Example**:
```python
# From: v(x) = x^α for gains (x ≥ 0)
def prospect_value_function(x, alpha=0.88):
    if x >= 0:
        return x ** alpha
    else:
        return -lambda_param * ((-x) ** beta)
```

### Level 2: ALGORITHMS  
**Purpose**: Computational methods and iterative calculations  
**Input**: Algorithmic descriptions from theory  
**Output**: Python algorithmic classes with iteration logic  
**Implementation**: Algorithm class generation with convergence criteria  
**Status**: **ARCHITECTURE DEFINED, IMPLEMENTATION PENDING**

**Target Example**:
```python
# From: PageRank-style influence calculation
class SocialInfluenceCalculator:
    def __init__(self, damping=0.85, tolerance=1e-6):
        self.damping = damping
        self.tolerance = tolerance
    
    def calculate_influence(self, social_graph):
        # Iterative calculation with convergence
        pass
```

### Level 3: PROCEDURES
**Purpose**: Step-by-step workflows and decision processes  
**Input**: Sequential procedures from theory  
**Output**: Workflow classes with state management  
**Implementation**: State machine generation with conditional logic  
**Status**: **ARCHITECTURE DEFINED, IMPLEMENTATION PENDING**

**Target Example**:
```python
# From: Rational choice decision procedure
class RationalChoiceDecisionProcedure:
    def execute(self, context):
        alternatives = self.identify_alternatives(context)
        outcomes = self.evaluate_outcomes(alternatives)
        utilities = self.calculate_utilities(outcomes)
        return self.select_optimal(utilities)
```

### Level 4: RULES
**Purpose**: Logical rules and conditional reasoning  
**Input**: If-then statements and logical conditions  
**Output**: OWL2 DL ontologies with SWRL rules  
**Implementation**: Ontology generation with automated reasoning  
**Status**: **ARCHITECTURE DEFINED, PENDING OWLREADY2**

**Target Example**:
```python
# From: "If same group, then positive bias"
with onto:
    class SocialActor(Thing): pass
    class Group(Thing): pass
    
    # SWRL rule
    imp = Imp()
    imp.set_as_rule([
        "SocialActor(?x), SocialActor(?y), belongsToGroup(?x, ?g), "
        "belongsToGroup(?y, ?g) -> exhibitsBias(?x, ?y, 'positive')"
    ])
```

### Level 5: SEQUENCES
**Purpose**: Temporal sequences and stage progressions  
**Input**: Sequential stages from theory  
**Output**: State transition systems  
**Implementation**: Finite state machine generation with transition logic  
**Status**: **ARCHITECTURE DEFINED, IMPLEMENTATION PENDING**

**Target Example**:
```python
# From: Persuasion stages
class PersuasionSequence:
    stages = ["exposure", "attention", "comprehension", 
              "yielding", "retention", "behavior"]
    
    def advance_stage(self, current_stage, conditions):
        # Conditional progression logic
        pass
```

### Level 6: FRAMEWORKS
**Purpose**: Classification systems and taxonomies  
**Input**: Typologies and classification schemes  
**Output**: Decision trees and classification systems  
**Implementation**: Classifier generation with feature extraction  
**Status**: **ARCHITECTURE DEFINED, IMPLEMENTATION PENDING**

**Target Example**:
```python
# From: Innovation type classification
class InnovationTypeClassifier:
    def classify(self, innovation):
        features = self.extract_features(innovation)
        return self.decision_tree.predict(features)
```

## Implementation Architecture

### Component Detection System
```python
def detect_operational_components(v13_theory):
    """Route theory components to appropriate implementation engines"""
    components = {
        "formulas": [],      # → Python function generator
        "algorithms": [],    # → Algorithm class generator  
        "procedures": [],    # → State machine generator
        "rules": [],         # → OWL2 ontology generator
        "sequences": [],     # → Transition system generator
        "frameworks": []     # → Classifier generator
    }
    
    # Extract from V13 algorithms section
    if "algorithms" in v13_theory:
        if "mathematical" in v13_theory["algorithms"]:
            components["formulas"].extend(
                v13_theory["algorithms"]["mathematical"]
            )
        if "logical" in v13_theory["algorithms"]:
            components["rules"].extend(
                v12_theory["algorithms"]["logical"]
            )
        if "procedural" in v12_theory["algorithms"]:
            components["procedures"].extend(
                v12_theory["algorithms"]["procedural"]
            )
    
    return components
```

### Implementation Strategy Mapping
```python
IMPLEMENTATION_STRATEGIES = {
    "FORMULAS": {
        "generator": LLMFunctionGenerator,
        "validator": MathematicalValidator,
        "executor": PythonFunctionExecutor,
        "format": "python_function"
    },
    "ALGORITHMS": {
        "generator": AlgorithmClassGenerator,
        "validator": ConvergenceValidator,
        "executor": AlgorithmExecutor,
        "format": "python_class"
    },
    "PROCEDURES": {
        "generator": StateMachineGenerator,
        "validator": WorkflowValidator,
        "executor": ProcedureExecutor,
        "format": "state_machine"
    },
    "RULES": {
        "generator": OWL2OntologyGenerator,
        "validator": DLReasonerValidator,
        "executor": OntologyExecutor,
        "format": "owlready2_ontology"
    },
    "SEQUENCES": {
        "generator": TransitionSystemGenerator,
        "validator": SequenceValidator,
        "executor": SequenceExecutor,
        "format": "transition_system"
    },
    "FRAMEWORKS": {
        "generator": ClassifierGenerator,
        "validator": ClassificationValidator,
        "executor": ClassifierExecutor,
        "format": "sklearn_classifier"
    }
}
```

## Integration Architecture

### Unified Execution Interface
```python
class TheoryComponentExecutor:
    """Unified interface for executing all theory component types"""
    
    def __init__(self):
        self.executors = {
            "formulas": PythonFunctionExecutor(),
            "algorithms": AlgorithmExecutor(),
            "procedures": ProcedureExecutor(),
            "rules": OntologyExecutor(),
            "sequences": SequenceExecutor(),
            "frameworks": ClassifierExecutor()
        }
    
    def execute_component(self, component_type, component, inputs):
        executor = self.executors[component_type]
        return executor.execute(component, inputs)
```

### Component Validation Framework
```python
class ComponentValidator:
    """Ensures generated components meet quality standards"""
    
    def validate_formula(self, function_code, test_cases):
        """Validate mathematical function accuracy"""
        pass
    
    def validate_algorithm(self, algorithm_class, convergence_tests):
        """Validate algorithm convergence and correctness"""
        pass
    
    def validate_procedure(self, state_machine, workflow_tests):
        """Validate workflow execution and state transitions"""
        pass
    
    def validate_rules(self, ontology, reasoning_tests):
        """Validate logical reasoning and inference"""
        pass
    
    def validate_sequence(self, transition_system, sequence_tests):
        """Validate temporal progression logic"""
        pass
    
    def validate_framework(self, classifier, classification_tests):
        """Validate classification accuracy and consistency"""
        pass
```

## Technical Requirements

### Core Dependencies
- **Python 3.8+**: Foundation for all implementations
- **litellm**: LLM integration for code generation
- **owlready2**: OWL2 DL reasoning (for Level 4)
- **scikit-learn**: Classification frameworks (for Level 6)
- **networkx**: Algorithm implementations (for Level 2)

### Level-Specific Requirements
```python
LEVEL_REQUIREMENTS = {
    "FORMULAS": ["ast", "exec", "numpy"],
    "ALGORITHMS": ["networkx", "scipy", "convergence_metrics"],
    "PROCEDURES": ["statemachine", "workflow_engine"],
    "RULES": ["owlready2", "pellet_reasoner", "rdflib"],
    "SEQUENCES": ["transitions", "temporal_logic"],
    "FRAMEWORKS": ["scikit-learn", "decision_trees", "feature_extraction"]
}
```

## Implementation Phases

### Phase 1: Foundation (COMPLETE)
- Level 1 (FORMULAS) fully implemented
- Component detection architecture
- V12 meta-schema integration
- LLM code generation pipeline

### Phase 2: Core Expansion (NEXT)
**Priority Order**:
1. **Level 2 (ALGORITHMS)** - Most similar to existing implementation
2. **Level 3 (PROCEDURES)** - Builds on state management concepts
3. **Level 6 (FRAMEWORKS)** - Leverages existing ML infrastructure

### Phase 3: Advanced Systems
4. **Level 5 (SEQUENCES)** - Requires temporal logic framework
5. **Level 4 (RULES)** - Requires owlready2 installation and ontology expertise

## Quality Assurance

### Testing Strategy
Each level requires specialized testing approaches:

```python
TESTING_STRATEGIES = {
    "FORMULAS": "mathematical_accuracy_tests",
    "ALGORITHMS": "convergence_and_performance_tests", 
    "PROCEDURES": "workflow_execution_tests",
    "RULES": "logical_reasoning_tests",
    "SEQUENCES": "temporal_progression_tests",
    "FRAMEWORKS": "classification_accuracy_tests"
}
```

### Validation Criteria
- **Correctness**: All implementations must produce theoretically valid results
- **Performance**: Execution within reasonable time bounds for academic use
- **Robustness**: Graceful handling of edge cases and invalid inputs
- **Consistency**: Results must be reproducible across multiple runs

## Future Extensions

### Multi-Theory Integration
- **Theory Composition**: Combine multiple theories in single analysis
- **Cross-Theory Validation**: Identify theoretical conflicts and contradictions
- **Theory Libraries**: Pre-compiled theory components for rapid deployment

### Advanced Automation
- **Auto-Categorization**: Automatic detection of component types from natural language
- **Optimization**: Performance optimization for computationally intensive theories
- **Visualization**: Visual representation of theory execution flows

## Success Metrics

### Implementation Metrics
- **Coverage**: Percentage of social science theories automatable (target: 80%+)
- **Accuracy**: Correctness of theoretical implementations (target: 95%+)
- **Performance**: Execution time for typical analyses (target: <10 minutes)

### Research Impact Metrics  
- **Adoption**: Number of researchers using automated theories
- **Publications**: Academic papers enabled by automation
- **Reproducibility**: Percentage of results independently verified

---

**Status Summary**: The six-level architecture provides a comprehensive framework for automating diverse social science theories. Level 1 is fully operational, demonstrating the viability of the approach. Levels 2-6 have complete architectural designs ready for implementation.

**Next Steps**: Implement Level 2 (ALGORITHMS) as the next priority, leveraging existing infrastructure and building toward comprehensive theory automation capability.