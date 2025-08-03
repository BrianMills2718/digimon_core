# Entity Resolution Architecture - IC-Informed Framework

**Purpose**: Define the entity resolution approach for KGAS based on the Comprehensive7 IC-informed uncertainty framework, integrating Intelligence Community methodologies with modern LLM capabilities.

---

## Executive Summary

This document describes the IC-informed entity resolution architecture within KGAS that applies proven Intelligence Community standards while leveraging LLM intelligence. The approach uses ICD-203 probability bands, ICD-206 source quality assessment, and structured analytic techniques to handle entity resolution uncertainty systematically.

## Core Philosophy

**Primary Principle**: "Evidence-based entity resolution with IC methodologies, mathematical rigor, and LLM intelligence"

### Key Design Decisions

1. **IC Standards**: Apply ICD-203 probability bands and ICD-206 quality assessment
2. **Evidence-Based Resolution**: Evaluate evidence quality regardless of representation format
3. **Mathematical Propagation**: Use proper uncertainty propagation (root-sum-squares)
4. **Heuer's Paradox Awareness**: More evidence doesn't automatically mean higher confidence
5. **Single Integrated Analysis**: One comprehensive LLM call with IC methodologies

---

## Entity Resolution Challenges

### Core Challenge: Referential Uncertainty in Discourse

When analyzing discourse, we encounter various forms of ambiguous references that require systematic handling:

```
Speaker A: "We need to protect our values from their influence"
Speaker B: "They said they would help them with the investigation" 
Speaker C: "The party leadership told us to vote against it"
Speaker D: "Some coalition members remain unconvinced"
```

### Specific Challenges by Type

#### 1. Context-Dependent References
```json
{
  "text": "We strongly support this initiative",
  "speaker": "Sen_Collins",
  "previous_context": "Speaking as moderate Republicans...",
  "resolution": {
    "entity": "Moderate_Republicans",
    "confidence": 0.88,
    "method": "contextual_inference"
  }
}
```

#### 2. Strategic Ambiguity
```json
{
  "text": "Certain parties have expressed concerns",
  "speaker": "Press_Secretary",
  "context": "Formal diplomatic statement",
  "resolution": {
    "entity": null,
    "confidence": 0.45,
    "distribution": {
      "Opposition_Party": 0.35,
      "Coalition_Partners": 0.30,
      "Intentionally_Vague": 0.35
    },
    "method": "strategic_ambiguity_detected"
  }
}
```

#### 3. Pronoun Chains with Degrading Context
```json
{
  "text": "They responded to their criticism",
  "speaker": "Reporter",
  "context": "Third reference in paragraph, original entities unclear",
  "resolution": {
    "entity": null, 
    "confidence": 0.55,
    "distribution": {
      "Democrats": 0.40,
      "Republicans": 0.35,
      "UNKNOWN": 0.25
    },
    "method": "degraded_context"
  }
}
```

---

## Balanced Resolution Architecture

### Core Components

#### 1. LLM-Intelligent Entity Resolution

**Modern LLM Capabilities**: Context-aware disambiguation achieving realistic confidence ranges

```python
class IntelligentEntityResolver:
    """Leverage LLM intelligence for context-aware entity resolution"""
    
    def resolve_entity(self, 
                      text: str, 
                      context_window: str,
                      speaker_info: Dict,
                      theory_schema: TheorySchema) -> EntityResolution:
        """
        Intelligent entity resolution with realistic confidence assessment
        """
        
        # Stage 1: Quick confidence assessment
        context_strength = self._assess_context_strength(text, context_window)
        ambiguity_type = self._classify_ambiguity(text, context_window)
        
        # Stage 2: LLM-based resolution with appropriate confidence
        if context_strength >= 0.8 and ambiguity_type == "resolvable":
            # High-confidence resolution
            return self._resolve_with_high_confidence(text, context_window, speaker_info)
            
        elif ambiguity_type == "strategic":
            # Recognize intentional ambiguity
            return self._handle_strategic_ambiguity(text, context_window)
            
        elif context_strength >= 0.5:
            # Moderate confidence with uncertainty preservation
            return self._resolve_with_uncertainty(text, context_window, speaker_info)
            
        else:
            # Low confidence - preserve uncertainty
            return self._preserve_uncertainty(text, context_window, theory_schema)
    
    def _resolve_with_high_confidence(self, text: str, context: str, speaker: Dict) -> EntityResolution:
        """Handle clear references with high confidence"""
        
        # Example: "As Democrats, we believe..." 
        if self._is_explicit_self_identification(text):
            return EntityResolution(
                original_text=text,
                resolved_entity="Democrats",
                confidence=0.92,
                method="explicit_identification",
                reasoning="Direct self-identification by speaker"
            )
        
        # Example: "We" immediately after "The Republican caucus decided..."
        if self._has_clear_contextual_antecedent(text, context):
            antecedent = self._extract_antecedent(context)
            return EntityResolution(
                original_text=text,
                resolved_entity=antecedent,
                confidence=0.85,
                method="clear_contextual_reference",
                reasoning=f"Clear reference to previously mentioned {antecedent}"
            )
        
        # Should not reach here if context_strength >= 0.8
        raise ValueError("High confidence resolution failed - check context assessment")
    
    def _handle_strategic_ambiguity(self, text: str, context: str) -> EntityResolution:
        """Recognize and handle intentional ambiguity"""
        
        # Strategic ambiguity patterns: "certain parties", "some members", "various stakeholders"
        strategic_markers = self._detect_strategic_language(text, context)
        
        return EntityResolution(
            original_text=text,
            resolved_entity=None,
            confidence=0.45,  # Low confidence - intentionally ambiguous
            distribution=self._estimate_strategic_distribution(text, context),
            method="strategic_ambiguity",
            reasoning=f"Intentional ambiguity detected: {strategic_markers}",
            preserve_ambiguity=True  # Flag for downstream processing
        )
    
    def _resolve_with_uncertainty(self, text: str, context: str, speaker: Dict) -> EntityResolution:
        """Resolve with moderate confidence, preserving uncertainty"""
        
        # Use LLM intelligence to generate probability distribution
        distribution = self._generate_probability_distribution(text, context, speaker)
        
        # Most likely entity
        most_likely = max(distribution.items(), key=lambda x: x[1])
        
        return EntityResolution(
            original_text=text,
            resolved_entity=most_likely[0] if most_likely[1] > 0.6 else None,
            confidence=most_likely[1],
            distribution=distribution,
            method="uncertain_resolution",
            reasoning="Multiple plausible referents based on context"
        )
```

#### 2. Mathematically Coherent Aggregation

**Core Principle**: Separate frequency counts from confidence scores

```python
class CoherentEntityAggregation:
    """Aggregate entity instances preserving mathematical coherence"""
    
    def aggregate_entity_instances(self, 
                                 instances: List[EntityResolution],
                                 aggregation_strategy: str = "weighted") -> EntityAggregation:
        """
        Aggregate entity instances without mathematical errors
        """
        
        # Separate resolved from uncertain instances
        resolved_instances = [inst for inst in instances if inst.resolved_entity is not None]
        uncertain_instances = [inst for inst in instances if inst.resolved_entity is None]
        
        # Calculate frequency counts (how often entities are mentioned)
        entity_frequencies = defaultdict(int)
        confidence_scores = defaultdict(list)
        
        for instance in resolved_instances:
            entity = instance.resolved_entity
            entity_frequencies[entity] += 1  # Simple count - no probability addition
            confidence_scores[entity].append(instance.confidence)
        
        # Calculate average confidence per entity (NOT total probability)
        average_confidences = {
            entity: sum(scores) / len(scores) 
            for entity, scores in confidence_scores.items()
        }
        
        # Preserve uncertain instances as distributions
        uncertainty_mass = len(uncertain_instances) / len(instances)
        preserved_distributions = [inst.distribution for inst in uncertain_instances if inst.distribution]
        
        return EntityAggregation(
            entity_frequencies=dict(entity_frequencies),           # How often mentioned
            average_confidences=average_confidences,               # How confident we are
            uncertainty_mass=uncertainty_mass,                     # Fraction unresolved
            preserved_distributions=preserved_distributions,       # Raw uncertainty
            quality_metrics=self._calculate_quality_metrics(instances)
        )
    
    def _calculate_quality_metrics(self, instances: List[EntityResolution]) -> QualityMetrics:
        """Assess overall quality of entity resolution"""
        
        if not instances:
            return QualityMetrics(resolution_rate=0.0, average_confidence=0.0)
        
        resolved_instances = [inst for inst in instances if inst.resolved_entity is not None]
        resolution_rate = len(resolved_instances) / len(instances)
        
        if resolved_instances:
            average_confidence = sum(inst.confidence for inst in resolved_instances) / len(resolved_instances)
        else:
            average_confidence = 0.0
        
        return QualityMetrics(
            resolution_rate=resolution_rate,
            average_confidence=average_confidence,
            total_instances=len(instances),
            strategic_ambiguity_rate=self._calculate_strategic_rate(instances),
            quality_tier=self._determine_quality_tier(resolution_rate, average_confidence)
        )
```

#### 3. Context-Aware Processing Pipeline

```python
class ContextAwareProcessor:
    """Process documents maintaining context for entity resolution"""
    
    def process_document(self, 
                        document: Document, 
                        theory_schema: TheorySchema,
                        context_window_size: int = 500) -> ProcessedDocument:
        """
        Process document with sliding context window for entity resolution
        """
        
        # Extract natural processing units (paragraphs, speaker turns, sentences)
        processing_units = document.extract_natural_units()
        
        # Initialize sliding context
        context_manager = SlidingContextManager(window_size=context_window_size)
        
        resolved_entities = []
        
        for unit in processing_units:
            # Get current context window
            current_context = context_manager.get_context_for_unit(unit)
            
            # Extract entities from this unit
            entity_mentions = self._extract_entity_mentions(unit.text, theory_schema)
            
            # Resolve each entity mention with context
            for mention in entity_mentions:
                resolution = self.entity_resolver.resolve_entity(
                    text=mention.text,
                    context_window=current_context,
                    speaker_info=unit.speaker_info,
                    theory_schema=theory_schema
                )
                
                # Add position and context metadata
                resolution.position = mention.position
                resolution.processing_unit_id = unit.id
                resolution.context_used = current_context
                
                resolved_entities.append(resolution)
            
            # Update context window with processed unit
            context_manager.add_processed_unit(unit, resolved_entities[-len(entity_mentions):])
        
        return ProcessedDocument(
            original_document=document,
            resolved_entities=resolved_entities,
            processing_metadata=self._generate_processing_metadata(processing_units, resolved_entities)
        )
```

---

## Realistic Confidence Ranges

### Evidence-Based Calibration

Based on comprehensive stress testing and LLM capability assessment:

#### High Confidence Cases (0.85-0.95)
- **Explicit self-identification**: "As Democrats, we..."
- **Clear contextual references**: "We" immediately after entity introduction
- **Formal role references**: "The President announced...", "Senator Smith said..."

#### Moderate Confidence Cases (0.70-0.85) 
- **Contextual inference**: "We" with supporting context clues
- **Speaker-based resolution**: Known speaker affiliation informs pronoun resolution
- **Pattern-based resolution**: Consistent patterns within document

#### Uncertain Cases (0.50-0.70)
- **Ambiguous pronouns**: "They" with multiple possible referents
- **Degraded context**: References distant from original entity mention
- **Cross-speaker references**: References across different speakers

#### Low Confidence Cases (0.30-0.50)
- **Strategic ambiguity**: Intentionally vague references
- **No context**: Pronouns without sufficient contextual information
- **Contradictory clues**: Context suggests multiple incompatible referents

### Calibration Examples

```python
# High confidence example
text = "As Democrats, we strongly oppose this measure"
expected_confidence = 0.92  # Explicit self-identification

# Moderate confidence example  
text = "We cannot support this"
context = "Democratic leadership met yesterday to discuss the bill"
expected_confidence = 0.78  # Good contextual support

# Uncertain example
text = "Some of us remain concerned"
context = "Bipartisan meeting with unclear composition"
expected_confidence = 0.58  # Multiple plausible referents

# Low confidence example
text = "Certain parties have raised questions"
context = "Formal diplomatic statement"
expected_confidence = 0.42  # Strategic ambiguity detected
```

---

## Integration with KGAS Pipeline

### Stage 2: Entity Extraction Integration

```python
def integrate_with_extraction_stage(extraction_results: List[ConstructInstance],
                                  document_context: DocumentContext) -> List[ResolvedInstance]:
    """
    Integrate entity resolution with construct extraction
    """
    
    resolved_instances = []
    
    for instance in extraction_results:
        # Extract entity mentions from construct instance
        entity_mentions = extract_entity_mentions(instance.text, instance.construct_type)
        
        # Resolve each mention using balanced approach
        for mention in entity_mentions:
            resolution = entity_resolver.resolve_entity(
                text=mention.text,
                context_window=document_context.get_context_for_position(mention.position),
                speaker_info=instance.speaker_info,
                theory_schema=document_context.theory_schema
            )
            
            # Create resolved instance with uncertainty preservation
            resolved_instance = ResolvedInstance(
                construct=instance.construct_type,
                text=instance.text,
                entity_resolution=resolution,
                confidence=resolution.confidence,
                processing_metadata=instance.metadata
            )
            
            resolved_instances.append(resolved_instance)
    
    return resolved_instances
```

### Stage 3: Aggregation Integration

```python
def integrate_with_aggregation_stage(resolved_instances: List[ResolvedInstance]) -> AggregatedAnalysis:
    """
    Aggregate resolved instances preserving uncertainty
    """
    
    # Group instances by construct type
    instances_by_construct = defaultdict(list)
    for instance in resolved_instances:
        instances_by_construct[instance.construct].append(instance)
    
    aggregated_constructs = {}
    
    for construct_type, instances in instances_by_construct.items():
        # Extract entity resolutions
        entity_resolutions = [inst.entity_resolution for inst in instances]
        
        # Apply coherent aggregation
        aggregated = coherent_aggregator.aggregate_entity_instances(entity_resolutions)
        
        # Calculate construct-level quality metrics
        construct_quality = assess_construct_quality(aggregated, construct_type)
        
        aggregated_constructs[construct_type] = ConstructAggregation(
            entity_aggregation=aggregated,
            construct_type=construct_type,
            quality_assessment=construct_quality,
            instance_count=len(instances)
        )
    
    return AggregatedAnalysis(
        construct_aggregations=aggregated_constructs,
        overall_quality=calculate_overall_quality(aggregated_constructs),
        resolution_summary=generate_resolution_summary(aggregated_constructs)
    )
```

---

## Quality Assessment and Suitability

### Research Suitability Framework

```python
class ResearchSuitabilityAssessor:
    """Assess suitability of entity resolution for different research approaches"""
    
    def assess_suitability(self, aggregated_analysis: AggregatedAnalysis) -> SuitabilityAssessment:
        """
        Determine appropriate research methodologies given resolution quality
        """
        
        overall_quality = aggregated_analysis.overall_quality
        resolution_rate = overall_quality.resolution_rate
        average_confidence = overall_quality.average_confidence
        uncertainty_mass = overall_quality.uncertainty_mass
        
        # Calculate composite suitability score
        composite_score = (resolution_rate * 0.4 + average_confidence * 0.4 + 
                          (1 - uncertainty_mass) * 0.2)
        
        if composite_score >= 0.80:
            return SuitabilityAssessment(
                quantitative_analysis="HIGHLY_SUITABLE",
                network_analysis="SUITABLE",
                statistical_testing="SUITABLE", 
                causal_inference="SUITABLE_WITH_CAVEATS",
                recommendation="Entity resolution quality supports quantitative approaches",
                composite_score=composite_score,
                primary_strength="High resolution rate and confidence"
            )
        
        elif composite_score >= 0.65:
            return SuitabilityAssessment(
                quantitative_analysis="MODERATELY_SUITABLE",
                mixed_methods="RECOMMENDED",
                network_analysis="FILTER_LOW_CONFIDENCE",
                statistical_testing="USE_ROBUST_METHODS",
                recommendation="Mixed methods approach recommended given uncertainty levels",
                composite_score=composite_score,
                primary_limitation="Moderate uncertainty requires methodological adjustments"
            )
        
        else:
            return SuitabilityAssessment(
                quantitative_analysis="NOT_RECOMMENDED",
                qualitative_analysis="RECOMMENDED",
                exploratory_analysis="SUITABLE",
                pattern_identification="SUITABLE",
                recommendation="Focus on qualitative and exploratory approaches",
                composite_score=composite_score,
                primary_limitation="High uncertainty levels limit quantitative reliability"
            )
```

### Quality Metrics Dashboard

```python
def generate_quality_dashboard(suitability: SuitabilityAssessment) -> QualityDashboard:
    """Generate comprehensive quality dashboard for researchers"""
    
    return QualityDashboard(
        executive_summary=suitability.recommendation,
        composite_score=suitability.composite_score,
        method_recommendations={
            "Quantitative Analysis": suitability.quantitative_analysis,
            "Network Analysis": getattr(suitability, 'network_analysis', 'N/A'),
            "Statistical Testing": getattr(suitability, 'statistical_testing', 'N/A'),
            "Mixed Methods": getattr(suitability, 'mixed_methods', 'N/A'),
            "Qualitative Analysis": getattr(suitability, 'qualitative_analysis', 'N/A')
        },
        key_limitations=[suitability.primary_limitation] if hasattr(suitability, 'primary_limitation') else [],
        key_strengths=[suitability.primary_strength] if hasattr(suitability, 'primary_strength') else [],
        uncertainty_disclosure=generate_uncertainty_disclosure(suitability)
    )
```

---

## Implementation Examples

### Example 1: Political Coalition Analysis

```python
# Input discourse
discourse = """
Speaker_A (Sen_Collins): "Some of us believe this approach is too extreme."
Speaker_B (Sen_Warren): "We Democrats have consistently opposed such measures." 
Speaker_C (Rep_McCarthy): "They don't understand the fiscal implications."
"""

# Processing results
processing_results = {
    "Speaker_A": EntityResolution(
        original_text="Some of us",
        resolved_entity=None,  # Intentionally ambiguous
        confidence=0.45,
        distribution={
            "Moderate_Republicans": 0.40,
            "Bipartisan_Group": 0.35, 
            "Specific_Subset": 0.25
        },
        method="moderate_ambiguity"
    ),
    
    "Speaker_B": EntityResolution(
        original_text="We Democrats", 
        resolved_entity="Democrats",
        confidence=0.92,
        method="explicit_identification"
    ),
    
    "Speaker_C": EntityResolution(
        original_text="They",
        resolved_entity="Democrats",  # Context: responding to Warren
        confidence=0.82,
        method="contextual_reference"
    )
}

# Aggregation results
aggregation = CoherentEntityAggregation().aggregate_entity_instances([
    processing_results["Speaker_A"],
    processing_results["Speaker_B"], 
    processing_results["Speaker_C"]
])

# Results:
# entity_frequencies: {"Democrats": 2}  # Mentioned twice (Speaker_B, Speaker_C)
# average_confidences: {"Democrats": 0.87}  # (0.92 + 0.82) / 2
# uncertainty_mass: 0.33  # 1/3 instances unresolved
# preserved_distributions: [Speaker_A distribution]
```

### Example 2: Organizational Communication

```python
# Input: Internal organizational communication
communication = """
From: Department Head
"Our team needs to coordinate with their team on the implementation.
We've been working on this for months, but they seem to have different priorities."
"""

# Context: Email thread about cross-departmental project
context = "Previous emails identify 'their team' as Marketing Department"

# Resolution with context
resolution = IntelligentEntityResolver().resolve_entity(
    text="their team",
    context_window=context,
    speaker_info={"role": "Department_Head", "department": "Engineering"},
    theory_schema=organizational_theory_schema
)

# Expected result:
# EntityResolution(
#     resolved_entity="Marketing_Department",
#     confidence=0.84,  # High confidence due to clear context
#     method="contextual_reference",
#     reasoning="Previous email thread clearly identifies referent"
# )
```

---

## Benefits and Limitations

### Benefits of Balanced Approach

1. **Realistic Assessment**: Confidence ranges reflect actual LLM capabilities
2. **Mathematical Coherence**: No probabilistic errors in aggregation
3. **Uncertainty Preservation**: Maintains genuine uncertainty for appropriate handling
4. **Research Guidance**: Provides actionable methodology recommendations
5. **Scalable Processing**: Linear complexity suitable for large document collections
6. **Transparent Reasoning**: Clear explanation of resolution decisions

### Acknowledged Limitations

1. **Context Window Constraints**: Limited to sliding window context
2. **Single Document Scope**: No cross-document entity linking
3. **Temporal Limitations**: Basic temporal awareness only
4. **Strategic Ambiguity Challenges**: Some intentional vagueness may be mis-categorized
5. **Cultural/Linguistic Scope**: Primarily English-language optimized
6. **Speaker Consistency**: Assumes reasonable speaker consistency within document

### Comparison with Alternative Approaches

#### vs. Complex Tracking Systems
- **Advantage**: Simpler implementation, better scalability
- **Trade-off**: Less detailed coreference chains

#### vs. Over-Engineered Bayesian Networks  
- **Advantage**: Mathematical coherence, practical usability
- **Trade-off**: Less theoretical sophistication

#### vs. Simplistic Point Estimates
- **Advantage**: Uncertainty preservation, research transparency
- **Trade-off**: Requires more sophisticated downstream processing

---

## Future Enhancements

### Planned Extensions

1. **Advanced Context Management**
   - Cross-document entity linking
   - Long-range dependency tracking
   - Multi-modal context integration

2. **Enhanced Ambiguity Detection**
   - Improved strategic ambiguity recognition
   - Cultural and linguistic variation handling
   - Domain-specific ambiguity patterns

3. **Uncertainty Refinement**
   - Active learning for high-uncertainty cases
   - Human-in-the-loop validation
   - Ensemble resolution approaches

4. **Quality Improvement**
   - Calibration feedback loops
   - Domain-specific confidence adjustment
   - Resolution accuracy tracking

### Enhancement Principles

- **Maintain Balance**: Preserve simplicity-sophistication balance
- **Evidence-Based**: All enhancements validated against research scenarios
- **Mathematical Coherence**: Preserve separation of frequency/confidence
- **Research Focus**: Enhancements must improve research decision-making

---

## Conclusion

The balanced entity resolution architecture provides KGAS with sophisticated yet practical entity resolution capabilities. By leveraging modern LLM intelligence while maintaining mathematical coherence and uncertainty preservation, it enables researchers to work with realistic assessments of entity resolution quality and make informed decisions about appropriate analytical methodologies.

The framework's emphasis on research impact over technical complexity ensures that uncertainty enhances rather than hinders research quality, providing transparent, actionable guidance for academic research workflows.

---


This document describes the **target entity resolution architecture** based on the Comprehensive6 framework. For current implementation status, see **[Comprehensive6 Framework](kgas_uncertainty_framework_comprehensive6.md)** for complete framework details and **[Roadmap Overview](../roadmap/ROADMAP_OVERVIEW.md)** for development progress.

*This architecture document contains no implementation status information by design - all status tracking occurs in the roadmap documentation.*