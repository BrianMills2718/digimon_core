# Theory Meta-Schema v10.0: Executable Implementation Framework

**Status**: Active Development  
**Purpose**: Comprehensive framework for representing executable social science theories  
**Last Updated**: 2025-07-21

## Overview

Theory Meta-Schema v10.0 represents a major evolution from v9.0, incorporating practical implementation insights to bridge the gap between abstract theory and concrete execution. This version enables direct translation from theory schemas to executable workflows.

## Key Enhancements in v10.0

### 1. Execution Framework
- **Renamed `process` to `execution`** for clarity
- **Added implementation methods**: `llm_extraction`, `predefined_tool`, `custom_script`, `hybrid`
- **Embedded LLM prompts** directly in schema
- **Tool mapping strategy** with parameter adaptation
- **Custom script specifications** with test cases

### 2. Practical Implementation Support
- **Operationalization details** for concept boundaries
- **Cross-modal mappings** for graph/table/vector representations
- **Dynamic adaptation** for theories with changing processes
- **Uncertainty handling** at step level

### 3. Validation and Testing
- **Theory validation framework** with test cases
- **Operationalization documentation** for transparency
- **Boundary case specifications** for edge handling

### 4. Configuration Management
- **Configurable tracing levels** (minimal to debug)
- **LLM model selection** per task type
- **Performance optimization** flags
- **Fallback strategies** for error handling

## Schema Structure

### Core Required Fields
```json
{
  "theory_id": "stakeholder_theory",
  "theory_name": "Stakeholder Theory", 
  "version": "1.0.0",
  "classification": {...},
  "ontology": {...},
  "execution": {...},
  "telos": {...}
}
```

### Execution Framework Detail

#### Analysis Steps with Multiple Implementation Methods

**LLM Extraction Method**:
```json
{
  "step_id": "identify_stakeholders",
  "method": "llm_extraction",
  "llm_prompts": {
    "extraction_prompt": "Identify all entities that have a stake in the organization's decisions...",
    "validation_prompt": "Does this entity have legitimate interest, power, or urgency?"
  }
}
```

**Predefined Tool Method**:
```json
{
  "step_id": "calculate_centrality",
  "method": "predefined_tool",
  "tool_mapping": {
    "preferred_tool": "graph_centrality_mcp",
    "tool_parameters": {
      "centrality_type": "pagerank",
      "normalize": true
    },
    "parameter_adaptation": {
      "method": "wrapper_script",
      "adaptation_logic": "Convert stakeholder_salience to centrality weights"
    }
  }
}
```

**Custom Script Method**:
```json
{
  "step_id": "stakeholder_salience",
  "method": "custom_script",
  "custom_script": {
    "algorithm_name": "mitchell_agle_wood_salience",
    "business_logic": "Calculate geometric mean of legitimacy, urgency, and power",
    "implementation_hint": "salience = (legitimacy * urgency * power) ^ (1/3)",
    "inputs": {
      "legitimacy": {"type": "float", "range": [0,1]},
      "urgency": {"type": "float", "range": [0,1]}, 
      "power": {"type": "float", "range": [0,1]}
    },
    "outputs": {
      "salience_score": {"type": "float", "range": [0,1]}
    },
    "test_cases": [
      {
        "inputs": {"legitimacy": 1.0, "urgency": 1.0, "power": 1.0},
        "expected_output": 1.0,
        "description": "Maximum salience case"
      }
    ],
    "tool_contracts": ["stakeholder_interface", "salience_calculator"]
  }
}
```

### Cross-Modal Mappings

Specify how theory concepts map across different analysis modes:

```json
"cross_modal_mappings": {
  "graph_representation": {
    "nodes": "stakeholder_entities",
    "edges": "influence_relationships", 
    "node_properties": ["salience_score", "legitimacy", "urgency", "power"]
  },
  "table_representation": {
    "primary_table": "stakeholders",
    "key_columns": ["entity_id", "salience_score", "influence_rank"],
    "calculated_metrics": ["centrality_scores", "cluster_membership"]
  },
  "vector_representation": {
    "embedding_features": ["behavioral_patterns", "communication_style"],
    "similarity_metrics": ["stakeholder_type_similarity"]
  }
}
```

### Dynamic Adaptation (New Feature)

For theories like Spiral of Silence that change behavior based on state:

```json
"dynamic_adaptation": {
  "adaptation_triggers": [
    {"condition": "minority_visibility < 0.3", "action": "increase_spiral_strength"}
  ],
  "state_variables": {
    "minority_visibility": {"type": "float", "initial": 0.5},
    "spiral_strength": {"type": "float", "initial": 1.0}
  },
  "adaptation_rules": [
    "spiral_strength *= 1.2 when minority_visibility decreases"
  ]
}
```

### Validation Framework

```json
"validation": {
  "operationalization_notes": [
    "Legitimacy operationalized as stakeholder claim validity (0-1 scale)",
    "Power operationalized as ability to influence organizational decisions",
    "Urgency operationalized as time-critical nature of stakeholder claim"
  ],
  "theory_tests": [
    {
      "test_name": "high_salience_stakeholder_identification",
      "input_scenario": "CEO announces layoffs affecting employees and shareholders",
      "expected_theory_application": "Both employees and shareholders identified as high-salience stakeholders",
      "validation_criteria": "Salience scores > 0.7 for both groups"
    }
  ],
  "boundary_cases": [
    {
      "case_description": "Potential future stakeholder with no current relationship",
      "theory_applicability": "Mitchell model may not apply",
      "expected_behavior": "Flag as edge case, use alternative identification method"
    }
  ]
}
```

### Configuration Options

```json
"configuration": {
  "tracing_level": "standard",
  "llm_models": {
    "extraction": "gpt-4-turbo",
    "reasoning": "claude-3-opus", 
    "validation": "gpt-3.5-turbo"
  },
  "performance_optimization": {
    "enable_caching": true,
    "batch_processing": true,
    "parallel_execution": false
  },
  "fallback_strategies": {
    "missing_tools": "llm_implementation",
    "low_confidence": "human_review",
    "edge_cases": "uncertainty_flagging"
  }
}
```

## Migration from v9.0 to v10.0

### Breaking Changes
- `process` renamed to `execution`
- `steps` array structure enhanced with implementation methods
- New required fields: `method` in each step

### Migration Strategy
1. Rename `process` to `execution`
2. Add `method` field to each step 
3. Move prompts from separate files into `llm_prompts` objects
4. Add `custom_script` specifications for algorithms
5. Include `tool_mapping` for predefined tools

### Backward Compatibility
A migration tool will convert v9.0 schemas to v10.0 format:
- Default `method` to "llm_extraction" for existing steps
- Generate placeholder prompts from step descriptions
- Create basic tool mappings based on step naming

## Implementation Requirements

### For Theory Schema Authors
1. **Specify implementation method** for each analysis step
2. **Include LLM prompts** for extraction steps
3. **Define custom algorithms** with test cases for novel procedures
4. **Document operationalization decisions** in validation section

### For System Implementation
1. **Execution engine** that can dispatch to different implementation methods
2. **Custom script compiler** using Claude Code for algorithm implementation
3. **Tool mapper** using LLM intelligence for tool selection
4. **Validation framework** that runs theory tests automatically

### For Researchers
1. **Transparent operationalization** - all theory simplifications documented
2. **Configurable complexity** - adjust tracing and validation levels
3. **Extensible framework** - can add custom theories and algorithms
4. **Cross-modal capability** - theory works across graph, table, vector modes

## Next Steps

1. **Create example theory** using v10.0 schema (stakeholder theory)
2. **Implement execution engine** that can interpret v10.0 schemas
3. **Build validation framework** for theory testing
4. **Test stress cases** with complex multi-step theories

The v10.0 schema provides the comprehensive framework needed to bridge theory and implementation while maintaining flexibility and configurability.