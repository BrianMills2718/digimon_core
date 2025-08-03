---
status: living
---

# Provenance & Lineage in KGAS

## Overview
Provenance (lineage) tracking is implemented throughout KGAS to ensure every node and edge in the knowledge graph can be traced back to its generating activity, supporting full auditability and reproducibility. This includes comprehensive uncertainty calculation provenance to enable transparent research quality assessment.

## Provenance Object
Each theory instance and graph element includes a `provenance` object:
```json
{
  "source_chunk_id": "str",
  "prompt_hash": "str",
  "model_id": "str",
  "timestamp": "datetime",
  "uncertainty_provenance": {
    "calculation_method": "root_sum_squares|ic_analysis|expert_assessment|weighted_average",
    "input_confidences": [0.85, 0.72, 0.90],
    "calculation_parameters": {
      "independence_assumption": true,
      "correlation_factors": {"stage_1_to_2": 0.6},
      "weighting_scheme": "theory_informed"
    },
    "ic_analysis_details": {
      "competing_hypotheses": ["hypothesis_1", "hypothesis_2"],
      "evidence_quality_score": 0.78,
      "bias_mitigation_applied": ["devils_advocacy", "alternative_futures"],
      "assumptions_validated": 3,
      "critical_gaps_identified": ["temporal_context", "audience_analysis"]
    },
    "decision_trace": "extraction:0.85 → context:0.72 → integration:0.90 → final:0.78",
    "confidence_bounds": {"lower": 0.74, "upper": 0.82}
  },
  "transformation_lineage": {
    "from_format": "graph|table|vector|text",
    "to_format": "graph|table|vector|text",
    "transformation_confidence": 0.90,
    "information_preserved": 0.95,
    "conversion_method": "graph_to_table_bridge|llm_extraction|statistical_conversion"
  }
}
```

### Core Provenance Fields
- **source_chunk_id**: Unique ID of the input chunk or document
- **prompt_hash**: SHA-256 hash of the prompt or input
- **model_id**: Identifier for the LLM or tool used
- **timestamp**: ISO 8601 UTC timestamp of generation

### Uncertainty Provenance Fields
- **calculation_method**: How the confidence value was computed
- **input_confidences**: All confidence values that contributed to the final score
- **calculation_parameters**: Mathematical parameters and assumptions used
- **ic_analysis_details**: Intelligence Community analysis methodology details (when applicable)
- **decision_trace**: Step-by-step confidence calculation path
- **confidence_bounds**: Uncertainty in the uncertainty assessment itself

### Transformation Lineage Fields
- **from_format/to_format**: Data representation transformations
- **transformation_confidence**: Confidence in the transformation process
- **information_preserved**: Estimate of information retention during transformation
- **conversion_method**: Specific tool or algorithm used for transformation

## Hashing Rule
- All prompts/inputs are hashed using SHA-256.
- Hashes are stored alongside provenance metadata in the database.

## Storage
- Provenance objects are stored as part of each node/edge in the graph database.
- The `generated_by_activity_id` field links to the activity/process that created the element.

## CI Validation
- CI checks ensure every node/edge contract includes `generated_by_activity_id`.
- Provenance fields are validated for presence and correct format.
- See `scripts/verify_all_documentation_claims.sh` for automated checks.

## Uncertainty Audit Trail Requirements

### Research Reproducibility
All uncertainty calculations must be fully reproducible through provenance records:

```python
class UncertaintyAuditTrail:
    def record_confidence_calculation(self, 
                                   stage: str,
                                   input_data: Dict,
                                   confidence_value: float,
                                   calculation_method: str,
                                   parameters: Dict,
                                   justification: str):
        """Every confidence value must have traceable justification"""
        
    def record_ic_analysis(self,
                          research_question: str,
                          evidence: List[Dict],
                          competing_hypotheses: List[str],
                          bias_mitigation: List[str],
                          final_assessment: Dict):
        """Record Intelligence Community analysis details"""
        
    def record_propagation_step(self,
                              input_confidences: List[float],
                              propagation_method: str,
                              output_confidence: float,
                              assumptions: List[str]):
        """Every propagation step must be reproducible"""
```

### Uncertainty Lineage Queries
The system must support queries like:
- "How was the final confidence of 0.78 calculated?"
- "What assumptions went into the uncertainty assessment?"
- "Which evidence contributed most to the confidence score?"
- "How would the confidence change if assumption X was violated?"

### Quality Gates Integration
Uncertainty provenance must integrate with quality assessment:

```python
def validate_uncertainty_provenance(provenance_record: Dict) -> ValidationResult:
    """
    Validate that uncertainty calculations are:
    1. Mathematically coherent
    2. Based on traceable evidence  
    3. Use appropriate IC methodologies
    4. Include proper confidence bounds
    """
```

## Implementation Requirements

### Database Schema Extensions
- Add `uncertainty_provenance` and `transformation_lineage` fields to all entity records
- Create indexes for uncertainty calculation method and confidence value queries
- Support temporal queries for uncertainty evolution over time

### Tool Integration
- All KGAS tools must record uncertainty provenance in their output
- ProvenanceService must validate uncertainty calculation completeness
- Uncertainty calculations must be verified against recorded parameters

### Validation Requirements
- CI checks must verify uncertainty provenance completeness
- All confidence values must have corresponding calculation records
- Missing uncertainty provenance should trigger validation failures

## W3C PROV Compliance
- KGAS uses the W3C PROV model: `(Entity)-[GENERATED_BY]->(Activity)`.
- Uncertainty provenance extends this with `(ConfidenceValue)-[CALCULATED_BY]->(UncertaintyActivity)`
- Enables full lineage queries and audit trails including uncertainty calculations.

---
For more, see `ARCHITECTURE.md`, `CONTRACT_SYSTEM.md`, and [ADR-029](../adrs/ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md). 