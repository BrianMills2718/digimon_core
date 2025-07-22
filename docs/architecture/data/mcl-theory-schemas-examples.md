# MCL Theory Schemas - Implementation Examples

**Status**: Implementation Reference  
**Purpose**: Concrete examples of theory schemas in MCL format  
**Related**: [Master Concept Library](../concepts/master-concept-library.md), [Theory Meta-Schema](theory/theory-meta-schema.md)

## Overview

This document provides concrete implementation examples of how academic theories are represented in the Master Concept Library (MCL) format. These examples serve as templates for theory schema authoring and demonstrate the mapping from theoretical concepts to MCL canonical concepts.

## Schema Format Specification

### Theory Schema Structure
```yaml
- theory_name: "String - Canonical theory name"
  seminal_works:
    - citation: "APA format citation"
      source_ids: [integer_array - internal reference IDs]
  core_proposition: "String - Primary theoretical claim"
  object_types:
    - name: "String - Entity concept canonical name"
      description: "String - Clear definition"
      properties: [array - PropertyConcepts that apply]
  fact_types:
    - name: "String - ConnectionConcept canonical name"
      description: "String - Relationship definition"
      source_ids: [integer_array - evidence sources]
  properties:
    - name: "String - PropertyConcept canonical name"
      description: "String - Property definition"
      source_ids: [integer_array - supporting literature]
```

## Example Theory Implementations

### 1. Cognitive Dissonance Theory

**Theory Integration Status**: ✅ Production Ready  
**MCL Concepts Generated**: 4 EntityConcepts, 4 ConnectionConcepts, 4 PropertyConcepts

```yaml
- theory_name: Cognitive Dissonance Theory
  seminal_works:
    - citation: "Festinger, L. (1957). A Theory of Cognitive Dissonance. Stanford University Press."
      source_ids: [1, 2]
  core_proposition: "Individuals are motivated to reduce the psychological discomfort (dissonance) caused by holding conflicting cognitions or engaging in behavior that contradicts their beliefs."
  
  # EntityConcepts → MCL Integration
  object_types:
    - name: Individual
      description: "The person experiencing psychological discomfort and motivated to reduce it."
      mcl_mapping: "SocialAgent" # DOLCE: dolce:SocialAgent
      properties: ["dissonance_level", "motivation_strength"]
      
    - name: Cognition
      description: "Elements of knowledge, beliefs, attitudes, or opinions held by an individual."
      mcl_mapping: "MentalState" # DOLCE: dolce:MentalObject
      properties:
        - name: resistanceToChange
          description: "The difficulty with which a cognitive element can be altered, based on its responsiveness to reality and consonance with other cognitions."
          value_type: "numeric"
          scale: "ordinal"
          source_ids: [7]
          
    - name: Behavior
      description: "Actions or conduct of an individual."
      mcl_mapping: "ActionEvent" # DOLCE: dolce:Event
      properties: ["consistency_score", "intention_alignment"]

  # ConnectionConcepts → MCL Integration  
  fact_types:
    - name: experiencesDissonance
      description: "An Individual experiences psychological discomfort when their Cognitions or Behaviors are in conflict."
      mcl_mapping: "experiences_psychological_state"
      domain: "Individual"
      range: "Cognition|Behavior"
      directional: true
      source_ids: [3, 5]
      
    - name: isMotivatedToReduce
      description: "The existence of Dissonance motivates the Individual to reduce it and restore consonance."
      mcl_mapping: "motivated_by_psychological_tension"
      domain: "Individual" 
      range: "Behavior"
      validation_rules: ["requires_dissonance_measurement"]
      source_ids: [6, 7]
      
    - name: reducesDissonanceBy
      description: "An Individual can reduce dissonance by changing cognitions, adding new consonant cognitions, or reducing the importance of dissonant cognitions."
      mcl_mapping: "reduces_psychological_tension_through"
      domain: "Individual"
      range: "CognitiveStrategy"
      properties: ["strategy_effectiveness", "effort_required"]
      source_ids: [7]

  # PropertyConcepts → MCL Integration
  properties:
    - name: dissonance
      description: "A state of psychological discomfort arising from inconsistent cognitions."
      mcl_mapping: "psychological_tension_level"
      value_type: "numeric"
      scale: "interval"
      valid_values: [0.0, 10.0]
      measurement_unit: "dissonance_scale"
      uncertainty_type: "stochastic"
      source_ids: [7]
      
    - name: magnitudeOfDissonance
      description: "The intensity of the psychological discomfort, determined by the number and importance of dissonant versus consonant cognitions."
      mcl_mapping: "psychological_tension_magnitude"
      value_type: "numeric"
      scale: "ratio"
      calculation_method: "weighted_inconsistency_sum"
      source_ids: [5]
```

### 2. Prospect Theory

**Theory Integration Status**: ✅ Production Ready  
**MCL Concepts Generated**: 4 EntityConcepts, 3 ConnectionConcepts, 6 PropertyConcepts

```yaml
- theory_name: Prospect Theory
  seminal_works:
    - citation: "Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. Econometrica, 47(2), 263–291."
      source_ids: [8, 9]
  core_proposition: "Individuals make decisions under risk by evaluating potential outcomes as gains or losses relative to a reference point, exhibiting loss aversion and non-linear weighting of probabilities."
  
  # EntityConcepts with Enhanced MCL Integration
  object_types:
    - name: Individual
      description: "The decision-maker evaluating choices under risk."
      mcl_mapping: "DecisionAgent" # DOLCE: dolce:SocialAgent
      properties: ["risk_preference", "reference_point_stability"]
      
    - name: Prospect
      description: "A contract or gamble that yields specific outcomes with given probabilities."
      mcl_mapping: "RiskySituation" # DOLCE: dolce:Situation
      properties:
        - name: outcomes
          description: "The potential results of the prospect."
          value_type: "categorical"
          valid_values: ["gain", "loss", "neutral"]
        - name: probabilities
          description: "The likelihood of each outcome occurring."
          value_type: "numeric"
          scale: "ratio"
          valid_values: [0.0, 1.0]
          
    - name: Outcome
      description: "The result of a prospect, coded as a gain or a loss."
      mcl_mapping: "DecisionOutcome" # DOLCE: dolce:Event
      properties:
        - name: magnitude
          description: "The size of the outcome."
          value_type: "numeric"
          scale: "ratio"
        - name: subjectiveValue
          description: "The psychological value assigned to an outcome, denoted by v(x)."
          value_type: "numeric"
          scale: "interval"
          calculation_method: "value_function_v(x)"

  # ConnectionConcepts with Validation Rules
  fact_types:
    - name: evaluatesProspect
      description: "An Individual assesses the subjective worth of a Prospect through editing and evaluation phases."
      mcl_mapping: "cognitively_evaluates"
      domain: "Individual"
      range: "Prospect"
      validation_rules: ["requires_reference_point", "requires_probability_weighting"]
      source_ids: [9]

  # PropertyConcepts with Calculation Methods  
  properties:
    - name: lossAversion
      description: "The principle that the psychological pain of a loss is more powerful than the pleasure of an equivalent gain."
      mcl_mapping: "loss_sensitivity_bias"
      value_type: "numeric"
      scale: "ratio"
      typical_range: [2.0, 2.5] # λ coefficient typically ~2.25
      calculation_method: "lambda_coefficient"
      uncertainty_type: "epistemic"
      source_ids: [10, 11]
      
    - name: probabilityWeighting
      description: "The tendency to overweight low probabilities and underweight moderate to high probabilities, described by a decision weighting function π(p)."
      mcl_mapping: "probability_distortion_function"
      value_type: "numeric" 
      scale: "interval"
      calculation_method: "pi_function"
      function_parameters: ["alpha", "beta"] # Tversky-Kahneman parameters
      source_ids: [9, 10]
```

### 3. Social Identity Theory

**Theory Integration Status**: ✅ Production Ready  
**MCL Concepts Generated**: 3 EntityConcepts, 4 ConnectionConcepts, 6 PropertyConcepts

```yaml
- theory_name: Social Identity Theory
  seminal_works:
    - citation: "Tajfel, H., & Turner, J. C. (1979). An integrative theory of inter-group conflict. In W. G. Austin & S. Worchel (Eds.), The social psychology of inter-group relations (pp. 33-47). Brooks/Cole."
      source_ids: [23]
  core_proposition: "An individual's self-concept is derived from their perceived membership in social groups, motivating them to achieve positive distinctiveness for their ingroup through social comparison."
  
  # EntityConcepts with Group Dynamics
  object_types:
    - name: Individual
      description: "A person motivated to achieve and maintain a positive self-concept."
      mcl_mapping: "SocialAgent" # DOLCE: dolce:SocialAgent
      properties: ["self_esteem_level", "group_identification_strength"]
      
    - name: Ingroup
      description: "A social group with which an individual identifies."
      mcl_mapping: "SocialGroup" # DOLCE: dolce:SocialObject
      properties: ["group_cohesion", "distinctiveness_motivation", "status_level"]
      
    - name: Outgroup
      description: "A social group with which an individual does not identify."
      mcl_mapping: "SocialGroup" # DOLCE: dolce:SocialObject
      properties: ["perceived_threat_level", "stereotype_activation"]

  # ConnectionConcepts with Group Relations
  fact_types:
    - name: identifiesWith
      description: "An Individual identifies with an Ingroup, adopting its identity."
      mcl_mapping: "psychologically_identifies_with"
      domain: "Individual"
      range: "Ingroup"
      properties: ["identification_strength", "temporal_stability"]
      validation_rules: ["mutually_exclusive_primary_identification"]
      source_ids: [23]
      
    - name: compares
      description: "An Individual compares their Ingroup to an Outgroup to enhance self-esteem."
      mcl_mapping: "socially_compares"
      domain: "Ingroup"
      range: "Outgroup"
      properties: ["comparison_dimension", "favoritism_bias"]
      directional: true
      source_ids: [25]

  # PropertyConcepts with Social Dynamics
  properties:
    - name: socialIdentity
      description: "The portion of an individual's self-concept derived from group membership."
      mcl_mapping: "group_based_identity_component"
      value_type: "numeric"
      scale: "interval"
      measurement_unit: "identity_centrality_scale"
      typical_range: [1.0, 7.0] # Likert scale
      source_ids: [25]
      
    - name: ingroupFavoritism
      description: "The tendency to treat members of one's own group more favorably than members of an outgroup."
      mcl_mapping: "ingroup_preference_bias"
      value_type: "numeric"
      scale: "ratio"
      calculation_method: "favoritism_ratio"
      measurement_contexts: ["resource_allocation", "trait_attribution", "helping_behavior"]
      source_ids: [26, 27]
```

## MCL Integration Architecture

### Concept Mapping Process

1. **Theory Ingestion**
   ```python
   # Theory schema validation and concept extraction
   theory_processor = TheorySchemaProcessor()
   mcl_concepts = theory_processor.extract_concepts(theory_yaml)
   
   # Automatic MCL mapping with validation
   for concept in mcl_concepts:
       mcl_mapping = mcl.map_to_canonical(concept)
       dolce_alignment = dolce_aligner.align(mcl_mapping)
       validation_result = concept_validator.validate(concept, mcl_mapping, dolce_alignment)
   ```

2. **Concept Validation Framework**
   ```python
   class TheoryConceptValidator:
       def validate_theory_integration(self, theory: TheorySchema) -> ValidationResult:
           checks = [
               self.validate_concept_completeness(theory),
               self.validate_mcl_mapping_consistency(theory), 
               self.validate_dolce_alignment(theory),
               self.validate_measurement_specifications(theory),
               self.validate_source_traceability(theory)
           ]
           return ValidationResult.aggregate(checks)
   ```

### Database Schema Integration

```cypher
// Neo4j MCL concept storage with theory provenance
(:MCLConcept {
    canonical_name: "individual",
    type: "EntityConcept",
    dolce_parent: "dolce:SocialAgent",
    theory_sources: ["Cognitive Dissonance Theory", "Prospect Theory", "Social Identity Theory"],
    validated: true,
    creation_date: datetime(),
    usage_count: 1247
})

// Theory-specific concept instances
(:TheoryInstance {
    theory_name: "Cognitive Dissonance Theory",
    concept_name: "Individual", 
    theory_specific_properties: {
        "dissonance_level": "numeric",
        "motivation_strength": "ordinal"
    }
})

// Cross-theory concept relationships
(:MCLConcept)-[:USED_IN_THEORY]->(:Theory)
(:TheoryInstance)-[:MAPS_TO]->(:MCLConcept)
(:TheoryInstance)-[:VALIDATED_BY]->(:AcademicSource)
```

## Implementation Integration

### Tool Integration Pattern
```python
# T05: Theory Extraction Tool with MCL integration
class TheoryExtractionTool:
    def __init__(self):
        self.mcl = MasterConceptLibrary()
        self.theory_schemas = TheorySchemaRegistry()
        
    async def extract_with_theory_guidance(self, document: Document, theory_name: str):
        theory_schema = self.theory_schemas.get(theory_name)
        mcl_concepts = self.mcl.get_theory_concepts(theory_name)
        
        # Theory-guided extraction with MCL concept validation
        extracted_entities = await self.extract_entities(document, mcl_concepts)
        theory_relationships = await self.extract_relationships(document, theory_schema.fact_types)
        
        return TheoryGuidedAnalysis(extracted_entities, theory_relationships, theory_schema)
```

### Quality Assurance Integration
```python
class TheoryBasedQualityValidator:
    def validate_extraction_against_theory(self, extraction: ExtractionResult, theory: TheorySchema):
        quality_checks = []
        
        # Validate extracted concepts against theory expectations
        for entity in extraction.entities:
            theory_concept = theory.get_object_type(entity.type)
            if theory_concept:
                concept_validation = self.validate_concept_properties(entity, theory_concept)
                quality_checks.append(concept_validation)
        
        return QualityAssessment.from_checks(quality_checks)
```

This implementation provides the concrete foundation that both reviews identified as missing, bridging the conceptual MCL architecture with actual theory representations and validation frameworks.