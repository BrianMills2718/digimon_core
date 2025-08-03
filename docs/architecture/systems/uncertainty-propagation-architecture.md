# KGAS Uncertainty Propagation Architecture

**Document Status**: ACTIVE - Consolidated Framework  
**Created**: 2025-07-25  
**Updated**: 2025-01-29 (Consolidated per architecture review)
**Author**: Architecture Analysis  
**Related**: [ADR-029](../adrs/ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md) (current architectural decision), [IC-Informed Framework Implementation](../adrs/ADR-029-IC-Informed-Uncertainty-Framework/kgas_uncertainty_framework_comprehensive7.md) (detailed implementation)

## 🎯 Executive Summary

KGAS processes knowledge through a **5-stage pipeline** from abstract theories to concrete research findings. Each stage introduces distinct uncertainty sources that compound through the system. This document defines the complete uncertainty propagation architecture, providing a framework for measuring, tracking, and managing uncertainty at each stage of the research process.

**Key Insight**: Theory selection is just one component of a complex uncertainty propagation system. The primary risks are LLM hallucination/omission (Stage 3), tool chain degradation (Stage 4), and research applicability assessment (Stage 5). Cross-modal integration uncertainty has been **removed** as adding complexity without research value.

**Note**: For superseded approaches including 6-stage models and agent coordination, see [archived uncertainty evolution documents](../archive/uncertainty-evolution/).

## 📊 The 5-Stage Uncertainty Propagation Pipeline

### Stage 1: Meta-Schema → Theory Schema Instantiation

**Process**: Transform abstract theory meta-schema into executable theory schema
```
Theory Meta-Schema v11 → Social Identity Theory Schema v2.1
```

**Uncertainty Sources**:
- **Schema Completeness**: Did we capture all essential aspects of the original theory?
- **Version Fidelity**: Does our executable schema accurately represent the canonical theory formulation?
- **Operationalization Validity**: Can abstract theoretical concepts be meaningfully converted to measurable constructs?
- **Author Interpretation Bias**: Did we misunderstand or misrepresent the original theoretical intent?
- **Theory Evolution**: Theories evolve over time - which version are we implementing?

**Measurement Framework**:
```yaml
stage_1_uncertainty_metrics:
  schema_coverage_score:
    calculation: "captured_theory_elements / total_theory_elements"
    range: [0.0, 1.0]
    threshold: 0.85
    measurement: "expert review against canonical sources"
    
  operationalization_validity:
    calculation: "executable_concepts / abstract_concepts"
    range: [0.0, 1.0] 
    threshold: 0.80
    measurement: "concept mapping validation"
    
  expert_validation_score:
    calculation: "expert_agreement_on_schema_accuracy"
    range: [0.0, 1.0]
    threshold: 0.75
    measurement: "domain expert review process"
    
  version_consistency:
    calculation: "alignment_with_canonical_formulations"
    range: [0.0, 1.0]
    threshold: 0.80
    measurement: "citation verification and version tracking"
    
  temporal_stability:
    calculation: "schema_consistency_across_theory_evolution"
    range: [0.0, 1.0]
    measurement: "version compatibility assessment"
```

**Critical Dependencies**:
- Theory Meta-Schema v11 completeness and accuracy
- Domain expert availability for validation
- Access to canonical theoretical sources
- Version control for theoretical evolution

---

### Stage 2: Theory Schema → Discourse Schema Mapping

**Process**: Adapt general theory schema to specific discourse context
```
Social Identity Theory Schema + Carter Speech Context → Carter-SIT Discourse Schema
```

**Uncertainty Sources**:
- **Context Appropriateness**: Does this theory actually apply to this specific discourse?
- **Concept Mapping Validity**: Do discourse elements meaningfully correspond to theoretical constructs?
- **Domain Transfer Validity**: Theory developed in Laboratory Context X, applied to Real-World Context Y
- **Contextual Specification Errors**: Misunderstanding the strategic, temporal, or cultural context
- **Scope Boundary Violations**: Applying theory beyond its intended domain

**Measurement Framework**:
```yaml
stage_2_uncertainty_metrics:
  theory_discourse_fit:
    calculation: "theory_domain_overlap_with_discourse_context"
    range: [0.0, 1.0]
    threshold: 0.70
    measurement: "domain boundary analysis"
    
  concept_mapping_confidence:
    calculation: "discourse_element_theory_construct_alignment"
    range: [0.0, 1.0]
    threshold: 0.75
    measurement: "mapping validation against theory requirements"
    
  context_transfer_validity:
    calculation: "theory_validity_preservation_across_contexts"
    range: [0.0, 1.0]
    threshold: 0.65
    measurement: "contextual boundary condition assessment"
    
  mapping_completeness:
    calculation: "mapped_discourse_elements / total_relevant_elements"
    range: [0.0, 1.0]
    threshold: 0.80
    measurement: "discourse coverage analysis"
    
  scope_boundary_compliance:
    calculation: "discourse_within_theory_stated_domain"
    output: "boolean_with_confidence"
    threshold: 0.90
    measurement: "boundary condition validation"
```

**Context Integration Requirements**:
```yaml
discourse_context_modeling:
  strategic_intent_detection:
    purpose: "understand speaker/author goals and intentions"
    methods: ["rhetorical_analysis", "audience_analysis", "strategic_communication_theory"]
    
  temporal_context_integration:
    purpose: "account for historical moment and timing"
    methods: ["historical_contextualization", "temporal_discourse_analysis"]
    
  audience_analysis:
    purpose: "model multiple target audiences and messaging layers"
    methods: ["stakeholder_analysis", "message_stratification"]
    
  institutional_context_modeling:
    purpose: "understand organizational and cultural constraints"
    methods: ["institutional_analysis", "cultural_context_assessment"]
```

---

### Stage 3: LLM-Driven Concept Operationalization

**Process**: Use LLM to extract theoretical constructs from discourse
```
Carter-SIT Discourse Schema → LLM Extraction → Operationalized Measurements
```

**Uncertainty Sources**:
- **LLM Hallucination**: Generated evidence that doesn't exist in source material
- **LLM Omission**: Missed relevant evidence that does exist in the discourse
- **Interpretation Inconsistency**: Same text analyzed differently across multiple runs
- **Prompt Specification Errors**: Inadequately specified extraction instructions
- **Context Window Limitations**: Missing broader discourse context due to length constraints
- **Model Bias**: Systematic biases in LLM training affecting interpretation
- **Temporal Drift**: LLM performance degradation over time

**Measurement Framework**:
```yaml
stage_3_uncertainty_metrics:
  hallucination_detection:
    calculation: "generated_evidence_not_in_source / total_generated_evidence"
    range: [0.0, 1.0]
    threshold: 0.05  # Very low tolerance
    measurement: "source verification against original text"
    
  omission_likelihood:
    calculation: "missed_relevant_content_probability"
    range: [0.0, 1.0]
    threshold: 0.15
    measurement: "human expert review of missed content"
    
  consistency_across_runs:
    calculation: "identical_extractions / total_runs"
    range: [0.0, 1.0]
    threshold: 0.85
    measurement: "multiple run consistency testing"
    
  prompt_specification_quality:
    calculation: "prompt_captures_theory_requirements"
    range: [0.0, 1.0]
    threshold: 0.80
    measurement: "prompt validation against theory schema"
    
  context_completeness:
    calculation: "available_context / required_context_for_theory"
    range: [0.0, 1.0]
    threshold: 0.75
    measurement: "context adequacy assessment"
    
  model_confidence_calibration:
    calculation: "predicted_confidence_vs_actual_accuracy"
    measurement: "brier_score_decomposition"
    target: "<0.1"  # Lower is better
    
  bias_detection:
    calculation: "systematic_bias_in_extractions"
    measurement: "bias_audit_across_diverse_examples"
    threshold: "case_by_case_assessment"
```

**LLM Quality Assurance Strategies**:
```yaml
llm_quality_assurance:
  multi_model_validation:
    strategy: "use multiple LLM providers for same extraction"
    agreement_threshold: 0.75
    
  human_expert_validation:
    strategy: "expert review of LLM extractions"
    sample_percentage: 0.20
    focus: "high_uncertainty_cases"
    
  source_grounding_verification:
    strategy: "verify all extractions trace back to source text"
    coverage: "100% of generated evidence"
    
  consistency_monitoring:
    strategy: "track extraction consistency over time"
    recalibration_trigger: "consistency_drop > 0.10"
```

---

### Stage 4: Tool Chain Execution Uncertainty

**Process**: Execute analysis tool chains to process operationalized measurements
```
Operationalized Measurements → Tool Chain (T01→T15A→T23A→T31→T34) → Analysis Results
```

**Uncertainty Sources**:
- **Chain Length Degradation**: Uncertainty grows exponentially with chain length
- **Tool-Specific Errors**: Each tool introduces noise, bias, or processing errors
- **Composition Errors**: Tools may not integrate properly or make incompatible assumptions
- **Parameter Propagation**: Upstream errors amplified and distorted downstream
- **Tool Selection Appropriateness**: Wrong tool chosen for specific analysis step
- **Resource Constraints**: Memory, time, or computational limitations affecting tool performance
- **Version Compatibility**: Tool version mismatches creating inconsistent results

**Measurement Framework**:
```yaml
stage_4_uncertainty_metrics:
  chain_length_penalty:
    calculation: "base_uncertainty * (1 + chain_length_factor)^chain_length"
    parameters:
      base_uncertainty: 0.05
      chain_length_factor: 0.15
    measurement: "uncertainty compounds with each tool"
    
  tool_error_accumulation:
    calculation: "sqrt(sum(tool_error_variance_i))"  # Assuming independence
    range: [0.0, 1.0]
    measurement: "error propagation through chain"
    
  composition_validity:
    calculation: "tool_compatibility_score"
    range: [0.0, 1.0]
    threshold: 0.80
    measurement: "tool interface and assumption compatibility"
    
  parameter_sensitivity:
    calculation: "output_change / input_parameter_change"
    measurement: "sensitivity analysis across tool chain"
    threshold: "context_dependent"
    
  tool_selection_appropriateness:
    calculation: "optimal_tool_for_task_match"
    range: [0.0, 1.0]
    threshold: 0.75
    measurement: "tool capability vs task requirements"
    
  resource_constraint_impact:
    calculation: "performance_degradation_due_to_constraints"
    range: [0.0, 1.0]
    measurement: "resource utilization vs optimal performance"
```

**Tool Chain Quality Strategies**:
```yaml
tool_chain_optimization:
  chain_length_minimization:
    strategy: "shortest_path_to_analysis_goal"
    max_recommended_length: 5
    
  parallel_validation:
    strategy: "run alternative tool chains for same analysis"
    agreement_threshold: 0.70
    
  checkpoint_validation:
    strategy: "validate outputs at each major chain step"
    human_review_triggers: ["high_uncertainty", "critical_analysis_points"]
    
  tool_performance_monitoring:
    strategy: "track individual tool performance over time"
    recalibration_triggers: ["accuracy_drop", "consistency_issues"]
```

---

### Stage 5: Research Question Applicability Assessment

**Process**: Validate that tool chain results appropriately address the original research question
```
Tool Chain Results + Research Question → Answer Validity Assessment
```

**Note**: Cross-modal integration uncertainty (former Stage 5) has been **removed** as it added complexity without research value. Mode selection should occur before analysis rather than attempting to integrate conflicting results post-hoc.

**Uncertainty Sources**:
- **Question-Theory Mismatch**: Selected theory doesn't actually address the research question
- **Scope Boundary Violations**: Results exceed theory's validated domain of application
- **Inference Leap Errors**: Conclusions go beyond what the evidence can support
- **Generalizability Limitations**: Findings may be limited to specific contexts or conditions
- **Causal vs Correlational Confusion**: Inappropriate causal claims from correlational evidence
- **Statistical vs Practical Significance**: Statistically significant but meaningless findings

**Measurement Framework**:
```yaml
stage_5_uncertainty_metrics:
  question_theory_alignment:
    calculation: "research_question_theoretical_framework_match"
    range: [0.0, 1.0]
    threshold: 0.80
    measurement: "alignment assessment against research objectives"
    
  scope_boundary_compliance:
    calculation: "results_within_theory_validated_domain"
    output: "boolean_with_confidence_bounds"
    threshold: 0.90
    measurement: "boundary condition validation"
    
  inference_validity:
    calculation: "logical_connection_evidence_to_conclusions"
    range: [0.0, 1.0]
    threshold: 0.75
    measurement: "logical inference chain validation"
    
  generalizability_bounds:
    calculation: "scope_of_valid_application"
    output: "contextual_boundary_specification"
    measurement: "generalizability assessment"
    
  causal_claim_validity:
    calculation: "appropriateness_of_causal_vs_correlational_claims"
    range: [0.0, 1.0]
    threshold: 0.85
    measurement: "causal inference validation"
    
  practical_significance:
    calculation: "real_world_meaningfulness_of_findings"
    range: [0.0, 1.0]
    threshold: 0.60
    measurement: "practical impact assessment"
```

---

## 🔄 Uncertainty Propagation & Accumulation Models

### Compound Uncertainty Calculation

**Independent Error Model** (Conservative):
```python
def calculate_independent_uncertainty(stage_uncertainties):
    """Assume all stages contribute independent error"""
    return math.sqrt(sum(u**2 for u in stage_uncertainties))
```

**Dependent Error Model** (Realistic):
```python
def calculate_dependent_uncertainty(stage_uncertainties, dependency_matrix):
    """Account for dependencies between stages"""
    
    # Model dependencies between stages
    dependency_adjustments = model_stage_dependencies(dependency_matrix)
    
    # Apply correlation corrections
    adjusted_uncertainties = apply_correlation_corrections(
        stage_uncertainties, 
        dependency_adjustments
    )
    
    return combine_correlated_uncertainties(adjusted_uncertainties)
```

**Dependency Matrix**:
```yaml
stage_dependencies:
  # Stage dependencies (how errors in one stage affect others)
  stage_1_to_2: 0.60  # Theory schema errors strongly affect discourse mapping
  stage_2_to_3: 0.75  # Discourse mapping errors strongly affect LLM extraction
  stage_3_to_4: 0.40  # LLM extraction errors moderately affect tool chains
  stage_4_to_5: 0.25  # Tool chain errors moderately affect applicability assessment
  
  # Cross-stage dependencies
  stage_1_to_5: 0.80  # Theory schema errors directly affect final applicability
  stage_2_to_5: 0.70  # Context mapping errors directly affect applicability
```

### Critical Decision Gates

```yaml
uncertainty_decision_gates:
  stage_1_gate:
    name: "Theory Schema Validation Gate"
    threshold: 0.85
    action_if_failed: "return_to_theory_selection_or_schema_refinement"
    rationale: "Must be confident in theoretical foundation"
    
  stage_2_gate:
    name: "Context Appropriateness Gate" 
    threshold: 0.70
    action_if_failed: "reconsider_theory_applicability_or_context_specification"
    rationale: "Theory must be appropriate for discourse context"
    
  stage_3_gate:
    name: "LLM Reliability Gate"
    threshold: 0.75
    action_if_failed: "human_validation_required_or_alternative_extraction"
    rationale: "Must trust LLM operationalization for downstream analysis"
    
  stage_4_gate:
    name: "Tool Chain Reliability Gate"
    threshold: 0.65
    action_if_failed: "simplify_chain_or_manual_review_or_alternative_tools"
    rationale: "Tool chain must produce reliable results"
    
  final_gate:
    name: "Research Publication Gate"
    compound_threshold: 0.50
    action_if_failed: "do_not_publish_findings_or_additional_validation_required"
    rationale: "Overall confidence must support research claims"
```

## 📊 Implementation Framework

### Uncertainty Tracking Architecture

```python
class UncertaintyTracker:
    """Track uncertainty propagation through all stages"""
    
    def __init__(self):
        self.stage_uncertainties = {}
        self.dependency_model = DependencyModel()
        self.decision_gates = DecisionGateConfig()
    
    def track_stage_uncertainty(self, stage: int, metrics: Dict) -> StageUncertainty:
        """Calculate and store uncertainty for specific stage"""
        uncertainty = self.calculate_stage_uncertainty(stage, metrics)
        self.stage_uncertainties[stage] = uncertainty
        return uncertainty
    
    def evaluate_decision_gate(self, stage: int) -> GateDecision:
        """Evaluate whether to proceed past decision gate"""
        uncertainty = self.stage_uncertainties[stage]
        threshold = self.decision_gates.get_threshold(stage)
        
        if uncertainty.overall_score >= threshold:
            return GateDecision(proceed=True, confidence=uncertainty.overall_score)
        else:
            return GateDecision(
                proceed=False, 
                confidence=uncertainty.overall_score,
                required_actions=self.decision_gates.get_required_actions(stage)
            )
    
    def calculate_compound_uncertainty(self) -> CompoundUncertainty:
        """Calculate overall uncertainty across all stages"""
        return self.dependency_model.combine_uncertainties(
            self.stage_uncertainties
        )
```

### Configuration Framework

```yaml
uncertainty_configuration:
  # Environment-specific thresholds
  development:
    gate_thresholds: "relaxed"  # Lower thresholds for exploration
    validation_requirements: "reduced"
    
  production:
    gate_thresholds: "strict"   # Higher thresholds for publication
    validation_requirements: "complete"
    
  # Domain-specific adaptations
  political_science:
    stage_2_context_weight: 0.8  # Context very important
    
  psychology:
    stage_1_theory_precision_weight: 0.9  # Theory precision critical
    stage_3_llm_consistency_weight: 0.8
    
  # Research phase adaptations
  exploratory_phase:
    overall_uncertainty_tolerance: 0.4  # Higher uncertainty acceptable
    gate_bypass_enabled: ["stage_4"]
    
  confirmatory_phase:
    overall_uncertainty_tolerance: 0.6  # Lower uncertainty required
    gate_bypass_enabled: []
    validation_requirements: "maximum"
```

## 🎯 Research Impact & Value Assessment

### High-Value Components

1. **Stage 3 LLM Reliability (Critical)**
   - **Research Impact**: 9/10 - LLM hallucination can invalidate entire analysis
   - **Unique to KGAS**: Advanced LLM-driven theory operationalization
   - **Implementation Priority**: Immediate

2. **Stage 2 Context Appropriateness (Essential)**
   - **Research Impact**: 8/10 - Prevents inappropriate theory application
   - **Research Value**: Addresses common methodological errors
   - **Implementation Priority**: Phase 1

### Medium-Value Components

3. **Stage 4 Tool Chain Reliability (Important)**
   - **Research Impact**: 6/10 - Important but not unique to KGAS
   - **Implementation Priority**: Phase 2

4. **Stage 5 Applicability Assessment (Quality)**
   - **Research Impact**: 6/10 - Helps ensure research quality
   - **Implementation Priority**: Phase 2

### Lower-Priority Components

5. **Stage 1 Theory Schema Validation (Foundational)**
   - **Research Impact**: 5/10 - Important but not dynamic
   - **Implementation Priority**: Phase 3 (one-time setup per theory)

## 🔮 Future Extensions & Research Opportunities

### Advanced Uncertainty Modeling

```yaml
future_enhancements:
  dynamic_uncertainty_learning:
    description: "Learn uncertainty patterns from research outcomes"
    approach: "bayesian_updating_of_uncertainty_models"
    
  cross_domain_uncertainty_transfer:
    description: "Transfer uncertainty knowledge across research domains"
    approach: "domain_adaptation_techniques"
    
  uncertainty_visualization:
    description: "Interactive uncertainty exploration for researchers"
    approach: "uncertainty_aware_research_interfaces"
    
  collaborative_uncertainty_assessment:
    description: "Multiple researcher uncertainty consensus"
    approach: "expert_disagreement_modeling"
```

### Integration with External Systems

```yaml
external_integrations:
  peer_review_systems:
    purpose: "integrate uncertainty assessment with journal peer review"
    
  replication_databases:
    purpose: "track uncertainty vs replication success rates"
    
  meta_analysis_platforms:
    purpose: "uncertainty-aware meta-analysis across studies"
```

## 📚 Related Documentation

- **[ADR-007: Uncertainty Metrics](../adrs/ADR-007-uncertainty-metrics.md)** - Superseded uncertainty metrics framework
- **[ADR-029: IC-Informed Uncertainty Framework](../adrs/ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md)** - Current uncertainty approach
- **[Theory Meta-Schema v13](../../config/schemas/theory_meta_schema_v13.json)** - Executable theory specifications
- **[Uncertainty Framework Selection](uncertainty-framework-selection-integration.md)** - Theory selection challenges
- **[KGAS Architecture Overview](ARCHITECTURE_OVERVIEW.md)** - Complete system architecture

---

**Document Maintenance**: This framework should be updated as we gain experience with uncertainty patterns in real research workflows. Each stage's measurement framework should be refined based on empirical validation against research outcomes.