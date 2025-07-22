# Layer-by-Layer Uncertainty Implementation Plan

**Status**: Living Document  
**Last Updated**: 2025-07-22  
**Purpose**: Concrete implementation roadmap for KGAS 4-layer uncertainty architecture

## Executive Summary

This document provides detailed implementation steps for each layer of the KGAS uncertainty architecture. The plan follows a progressive enhancement approach, starting with basic confidence scores (already implemented) and building toward full Bayesian uncertainty propagation.

## Implementation Philosophy

### Progressive Enhancement
- Each layer builds on the previous
- System remains functional at each stage
- Backward compatibility maintained
- Performance impact carefully managed

### Test-Driven Development
- Uncertainty validation tests written first
- Statistical correctness verified
- Performance benchmarks established
- Integration tests for propagation

## Layer Implementation Roadmap

### ✅ **Layer 1: Basic Confidence Scores** (COMPLETED)
**Status**: Implemented via ADR-004  
**Location**: `src/core/confidence_score.py`

#### Current Implementation
```python
class ConfidenceScore:
    """ADR-004 compliant confidence scoring"""
    value: float  # 0.0 to 1.0
    evidence_weight: int  # Number of evidence items
    propagation_method: str  # Method used
```

#### What's Working
- Basic confidence on all entities
- Simple min/max propagation
- Evidence counting
- Tool-specific confidence

#### Integration Points
- All 12 implemented tools use ConfidenceScore
- Confidence preserved in storage
- Basic propagation in tool chains

### 🚧 **Layer 2: Contextual Entity Resolution** (Phase 6-7)
**Timeline**: 4-6 weeks  
**Purpose**: Add context-aware entity disambiguation

#### Implementation Tasks

##### Week 1-2: Core Context Framework
```python
# TDD Test First
def test_contextual_resolution():
    """Test context improves entity resolution"""
    # Given: Ambiguous mention "Apple" 
    mention1 = Mention("Apple", context="technology giant iPhone")
    mention2 = Mention("Apple", context="fruit nutrition healthy")
    
    # When: Contextual resolution applied
    entity1 = contextual_resolver.resolve(mention1)
    entity2 = contextual_resolver.resolve(mention2)
    
    # Then: Different entities resolved
    assert entity1.canonical_name == "Apple Inc."
    assert entity2.canonical_name == "Apple (fruit)"
    assert entity1.confidence > 0.9  # High confidence with context
```

```python
# Implementation
class ContextualEntityResolver:
    """Layer 2: Context-aware entity resolution"""
    
    def __init__(self):
        self.context_embedder = load_context_model()
        self.entity_knowledge_base = load_entity_kb()
    
    def resolve_with_context(self, mention: Mention) -> Entity:
        # Extract context features
        context_embedding = self.context_embedder.encode(mention.context)
        
        # Compare with known entities
        candidates = self.entity_knowledge_base.search_similar(
            text=mention.surface_text,
            context=context_embedding
        )
        
        # Score candidates with context
        scored_candidates = []
        for candidate in candidates:
            score = self.calculate_contextual_score(
                mention, candidate, context_embedding
            )
            scored_candidates.append((candidate, score))
        
        # Select best with confidence
        best_entity, confidence = self.select_best_entity(scored_candidates)
        
        return Entity(
            canonical_name=best_entity.name,
            confidence=ContextualConfidence(
                base_confidence=confidence,
                context_weight=len(mention.context.split()),
                disambiguation_score=scored_candidates[0][1] - scored_candidates[1][1]
            )
        )
```

##### Week 3-4: Integration with Identity Service
```python
# Enhance T107 Identity Service
class EnhancedIdentityService(T107_IdentityService):
    """Identity service with contextual resolution"""
    
    def __init__(self):
        super().__init__()
        self.contextual_resolver = ContextualEntityResolver()
    
    def resolve_mention(self, mention: Mention) -> Entity:
        # Try contextual resolution first
        if mention.has_context():
            entity = self.contextual_resolver.resolve_with_context(mention)
            if entity.confidence.value > 0.8:
                return entity
        
        # Fallback to basic resolution
        return super().resolve_mention(mention)
```

##### Week 5-6: Testing and Optimization
- Performance benchmarks for context processing
- A/B testing contextual vs non-contextual
- Integration tests with existing tools
- Documentation and examples

#### Success Metrics

##### Performance Metrics
| Metric | Target | Acceptable | Critical | Measurement |
|--------|--------|------------|----------|-------------|
| Disambiguation Accuracy | > 90% | > 85% | < 80% | F1 score on test set |
| Context Processing Time | < 50ms | < 100ms | > 200ms | p95 latency |
| Memory Overhead | < 10% | < 20% | > 30% | Peak memory increase |
| Throughput | > 1000/sec | > 500/sec | < 250/sec | Mentions per second |

##### Quality Metrics
| Metric | Target | Measurement | Validation |
|--------|--------|-------------|------------|
| False Positive Rate | < 5% | Wrong entity selected | Manual review |
| Context Utilization | > 80% | Context features used | Feature importance |
| Confidence Calibration | ±0.05 | Predicted vs actual | Calibration plot |
| Cross-domain Performance | > 85% | Accuracy across domains | Domain-specific tests |

### 📅 **Layer 3: Temporal Knowledge Graph** (Phase 7-8)
**Timeline**: 6-8 weeks  
**Purpose**: Add time-aware confidence bounds

#### Implementation Tasks

##### Week 1-2: Temporal Data Model
```python
# TDD Test First
def test_temporal_confidence_decay():
    """Test confidence decreases over time"""
    # Given: Entity with timestamp
    entity = Entity(
        name="COVID-19 Statistics",
        confidence=0.95,
        timestamp=datetime(2020, 3, 1)
    )
    
    # When: Accessed at different times
    conf_2020 = temporal_confidence(entity, datetime(2020, 6, 1))
    conf_2023 = temporal_confidence(entity, datetime(2023, 6, 1))
    
    # Then: Confidence decays appropriately
    assert conf_2020 > conf_2023
    assert conf_2023 < 0.5  # Old COVID data less reliable
```

```python
# Implementation
class TemporalConfidence:
    """Layer 3: Time-aware confidence"""
    
    def __init__(self, base_confidence: ConfidenceScore):
        self.base = base_confidence
        self.created_at = datetime.utcnow()
        self.validity_period = self.estimate_validity_period()
    
    def get_confidence_at(self, query_time: datetime) -> float:
        """Calculate confidence at specific time"""
        age = (query_time - self.created_at).total_seconds()
        
        if age < 0:  # Future query
            return 0.0
        
        # Decay function based on domain
        if self.domain == "news":
            half_life = 7 * 24 * 3600  # 1 week
        elif self.domain == "scientific":
            half_life = 365 * 24 * 3600  # 1 year
        else:
            half_life = 90 * 24 * 3600  # 3 months default
        
        decay_factor = 0.5 ** (age / half_life)
        return self.base.value * decay_factor
```

##### Week 3-4: Temporal Graph Operations
```python
class TemporalKnowledgeGraph:
    """Knowledge graph with temporal awareness"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def add_temporal_entity(self, entity: Entity, timestamp: datetime):
        """Add entity with temporal validity"""
        query = """
        CREATE (e:Entity {
            id: $id,
            name: $name,
            valid_from: $timestamp,
            valid_to: $valid_to,
            confidence_decay_rate: $decay_rate
        })
        """
        # Implementation details...
    
    def query_at_time(self, query: str, timestamp: datetime):
        """Query graph state at specific time"""
        # Filter entities valid at timestamp
        # Apply temporal confidence adjustments
        # Return time-adjusted results
```

##### Week 5-6: Temporal Reasoning
```python
class TemporalReasoner:
    """Reasoning over temporal changes"""
    
    def track_entity_evolution(self, entity_name: str) -> EvolutionTimeline:
        """Track how entity properties change over time"""
        versions = self.get_entity_versions(entity_name)
        timeline = EvolutionTimeline()
        
        for v1, v2 in pairwise(versions):
            changes = self.detect_changes(v1, v2)
            timeline.add_transition(
                from_time=v1.timestamp,
                to_time=v2.timestamp,
                changes=changes,
                confidence=self.calculate_transition_confidence(v1, v2)
            )
        
        return timeline
```

##### Week 7-8: Integration and Testing
- Temporal query optimization
- Historical analysis capabilities
- Time-travel debugging
- Performance impact assessment

#### Success Metrics

##### Performance Metrics
| Metric | Target | Acceptable | Critical | Measurement |
|--------|--------|------------|----------|-------------|
| Temporal Query Overhead | < 1.5x | < 2x | > 3x | vs non-temporal |
| Time-travel Query Speed | < 500ms | < 1s | > 2s | Historical queries |
| Storage Overhead | < 20% | < 30% | > 50% | Database size increase |
| Decay Calculation Time | < 10ms | < 20ms | > 50ms | Per entity |

##### Accuracy Metrics
| Metric | Target | Measurement | Validation |
|--------|--------|-------------|------------|
| Decay Function Accuracy | > 90% | Expert agreement | Domain expert review |
| Temporal Consistency | 100% | No anachronisms | Automated checks |
| Version Tracking | 100% | All changes tracked | Audit trail |
| Time Resolution | ±1 hour | Timestamp precision | Clock synchronization |

##### Functional Metrics
| Metric | Target | Test Method |
|--------|--------|-------------|
| Historical Queries | All time ranges | Query any past state |
| Evolution Tracking | Complete lineage | Entity history retrieval |
| Temporal Joins | Functional | Cross-time relationships |
| Validity Periods | Enforced | Constraint validation |

### 🔬 **Layer 4: Full Bayesian Pipeline** (Phase 8-9)
**Timeline**: 8-10 weeks  
**Purpose**: Complete uncertainty propagation

#### Implementation Tasks

##### Week 1-3: Bayesian Framework
```python
# TDD Test First
def test_bayesian_propagation():
    """Test uncertainty propagates correctly"""
    # Given: Uncertain inputs
    entity1 = Entity("A", confidence=Normal(0.8, 0.1))
    entity2 = Entity("B", confidence=Normal(0.7, 0.15))
    
    # When: Combined in relationship
    relationship = create_relationship(entity1, entity2)
    
    # Then: Uncertainty propagates correctly
    assert isinstance(relationship.confidence, Distribution)
    assert 0.5 < relationship.confidence.mean() < 0.8
    assert relationship.confidence.std() > max(0.1, 0.15)
```

```python
# Implementation
from typing import Union
from scipy import stats

class BayesianConfidence:
    """Full probability distribution for confidence"""
    
    def __init__(self, distribution: Union[stats.rv_continuous, float]):
        if isinstance(distribution, float):
            # Convert point estimate to distribution
            self.dist = stats.norm(distribution, 0.05)
        else:
            self.dist = distribution
    
    def propagate_through(self, operation: str, *other_confidences):
        """Propagate uncertainty through operation"""
        if operation == "AND":
            # Multiplication of probabilities
            return self._propagate_multiplication(other_confidences)
        elif operation == "OR":
            # Maximum of probabilities
            return self._propagate_maximum(other_confidences)
        elif operation == "WEIGHTED":
            # Weighted combination
            return self._propagate_weighted(other_confidences)
```

##### Week 4-5: Monte Carlo Integration
```python
class MonteCarloUncertaintyEngine:
    """Monte Carlo methods for complex propagation"""
    
    def propagate_through_network(self, 
                                  source_nodes: List[Entity],
                                  computation_graph: Graph,
                                  n_samples: int = 10000):
        """Propagate uncertainty through arbitrary computation"""
        samples = []
        
        for _ in range(n_samples):
            # Sample from input distributions
            sample_values = {
                node.id: node.confidence.sample()
                for node in source_nodes
            }
            
            # Propagate through graph
            result = self.evaluate_graph(computation_graph, sample_values)
            samples.append(result)
        
        # Fit output distribution
        return self.fit_distribution(samples)
```

##### Week 6-7: Belief Networks
```python
class BeliefNetwork:
    """Bayesian belief network for complex dependencies"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.conditional_tables = {}
    
    def add_evidence(self, node_id: str, evidence: Distribution):
        """Add evidence to belief network"""
        self.nodes[node_id].add_evidence(evidence)
        self.propagate_beliefs()
    
    def query_posterior(self, target_node: str) -> Distribution:
        """Get posterior distribution for node"""
        return self.nodes[target_node].posterior
```

##### Week 8-10: Integration and Optimization
- GPU acceleration for Monte Carlo
- Approximate inference methods
- Visualization of uncertainty
- Performance optimization

#### Success Metrics

##### Accuracy Metrics
| Metric | Target | Acceptable | Critical | Measurement |
|--------|--------|------------|----------|-------------|
| Propagation Accuracy | < 2% error | < 5% error | > 10% error | vs analytical solution |
| Distribution Fit | > 95% | > 90% | < 85% | Kolmogorov-Smirnov test |
| Convergence Rate | < 1000 samples | < 5000 | > 10000 | Monte Carlo convergence |
| Belief Network Accuracy | > 90% | > 85% | < 80% | Posterior validation |

##### Performance Metrics
| Metric | Target | Acceptable | Critical | Measurement |
|--------|--------|------------|----------|-------------|
| Propagation Overhead | < 3x | < 5x | > 10x | vs point estimates |
| Monte Carlo Speed | > 10k/sec | > 5k/sec | < 1k/sec | Samples per second |
| Memory Usage | < 1.5x | < 2x | > 3x | Peak memory |
| GPU Utilization | > 80% | > 60% | < 40% | When available |

##### Usability Metrics
| Metric | Target | Measurement | Validation |
|--------|--------|-------------|------------|
| Visualization Clarity | > 90% understood | User study | Comprehension test |
| API Simplicity | < 5 min learning | Developer onboarding | Time to first use |
| Default Behavior | Sensible 95% | Default usage | User feedback |
| Error Messages | Clear 100% | Error scenarios | Message review |

##### Integration Metrics
| Metric | Target | Test Method |
|--------|--------|-------------|
| Tool Compatibility | 100% | All tools work with distributions |
| Backward Compatibility | 100% | Existing code continues working |
| Serialization | Lossless | Save/load distributions |
| Visualization Tools | 5+ types | Different uncertainty views |

## Integration Plan

### Tool Migration Schedule
1. **Phase 1**: Add contextual resolution to T107 (Identity Service)
2. **Phase 2**: Enhance T111 (Quality Service) with temporal awareness
3. **Phase 3**: Upgrade T120 (Uncertainty Service) to Bayesian
4. **Phase 4**: Migrate all analysis tools to uncertainty-aware versions

### Backward Compatibility
```python
class UnifiedConfidence:
    """Wrapper supporting all confidence levels"""
    
    def __init__(self, confidence):
        if isinstance(confidence, float):
            self.layer = 1
            self.value = ConfidenceScore(confidence)
        elif isinstance(confidence, ContextualConfidence):
            self.layer = 2
            self.value = confidence
        elif isinstance(confidence, TemporalConfidence):
            self.layer = 3
            self.value = confidence
        elif isinstance(confidence, BayesianConfidence):
            self.layer = 4
            self.value = confidence
    
    def as_float(self) -> float:
        """Convert to simple float for compatibility"""
        if self.layer == 1:
            return self.value.value
        elif self.layer == 2:
            return self.value.base_confidence
        elif self.layer == 3:
            return self.value.get_confidence_at(datetime.utcnow())
        elif self.layer == 4:
            return self.value.dist.mean()
```

## Testing Strategy

### Unit Tests per Layer
```python
# Layer 2 Tests
test_contextual_resolution_accuracy()
test_disambiguation_performance()
test_context_extraction()

# Layer 3 Tests  
test_temporal_decay_functions()
test_time_travel_queries()
test_evolution_tracking()

# Layer 4 Tests
test_distribution_propagation()
test_monte_carlo_convergence()
test_belief_network_inference()
```

### Integration Tests
```python
def test_uncertainty_through_pipeline():
    """Test uncertainty flows through complete pipeline"""
    # Start with uncertain document
    doc = Document("paper.pdf", extraction_confidence=0.85)
    
    # Process through pipeline
    entities = extract_entities(doc)  # Layer 2: Contextual
    graph = build_graph(entities)     # Layer 3: Temporal
    analysis = analyze_graph(graph)   # Layer 4: Bayesian
    
    # Verify uncertainty preserved and propagated
    assert all(e.confidence.layer >= 2 for e in entities)
    assert graph.has_temporal_bounds()
    assert isinstance(analysis.confidence, Distribution)
```

## Risk Mitigation

### Performance Risks
- **Mitigation**: Optional uncertainty levels
- **Fallback**: Disable higher layers if too slow
- **Monitoring**: Performance benchmarks at each layer

### Complexity Risks
- **Mitigation**: Extensive documentation
- **Training**: Uncertainty interpretation guide
- **Defaults**: Sensible defaults for non-experts

### Integration Risks
- **Mitigation**: Gradual rollout
- **Testing**: Comprehensive integration tests
- **Compatibility**: Backward compatibility maintained

## Success Criteria

### Overall Implementation Success
- All 4 layers implemented and tested
- Performance within acceptable bounds
- User acceptance of uncertainty features
- Research value demonstrated
- Documentation complete

### Per-Layer Success
- **Layer 2**: >85% disambiguation accuracy
- **Layer 3**: Temporal queries functional
- **Layer 4**: Bayesian propagation accurate

## Comprehensive Success Metrics Dashboard

### Layer Progression Metrics
| Layer | Implementation Time | Complexity Increase | Value Added |
|-------|-------------------|---------------------|-------------|
| Layer 1 (Basic) | ✅ Complete | Baseline | Confidence scores |
| Layer 2 (Contextual) | 4-6 weeks | +50% | 85%→90% accuracy |
| Layer 3 (Temporal) | 6-8 weeks | +100% | Time-aware analysis |
| Layer 4 (Bayesian) | 8-10 weeks | +200% | Full uncertainty |

### End-to-End Metrics
| Metric | Current (L1) | Target (L4) | Improvement |
|--------|--------------|-------------|-------------|
| Entity Resolution Accuracy | 75% | 95% | +20% |
| Confidence Calibration | ±0.2 | ±0.02 | 10x better |
| Temporal Queries | N/A | < 1s | New capability |
| Uncertainty Communication | Basic | Rich | Distributions |
| Research Value | Medium | Very High | Publication-ready |

### Risk-Adjusted Timeline
| Phase | Best Case | Expected | Worst Case | Mitigation |
|-------|-----------|----------|------------|------------|
| Layer 2 | 4 weeks | 5 weeks | 8 weeks | Parallel development |
| Layer 3 | 6 weeks | 7 weeks | 10 weeks | Simplified decay models |
| Layer 4 | 8 weeks | 10 weeks | 14 weeks | GPU acceleration |
| Integration | 2 weeks | 3 weeks | 4 weeks | Incremental rollout |
| **Total** | **20 weeks** | **25 weeks** | **36 weeks** | Agile adjustment |

### Go/No-Go Criteria per Layer
#### Layer 2 Go Criteria
- [ ] Disambiguation accuracy > 85%
- [ ] Performance overhead < 20%
- [ ] All existing tests pass
- [ ] Documentation complete

#### Layer 3 Go Criteria
- [ ] Temporal queries functional
- [ ] Storage overhead < 30%
- [ ] Decay functions validated
- [ ] No data loss

#### Layer 4 Go Criteria
- [ ] Propagation accuracy > 95%
- [ ] Performance acceptable (< 5x)
- [ ] Visualization working
- [ ] User acceptance positive

This implementation plan ensures systematic, testable development of the complete uncertainty architecture while maintaining system usability at each stage, with clear metrics for success at every level.