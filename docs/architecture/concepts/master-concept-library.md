---
status: living
---

# Master Concept Library: Standardized Vocabulary for KGAS

## Purpose

The Master Concept Library (MCL) is a machine-readable, extensible repository of standardized concepts (entities, connections, properties, modifiers) from social, behavioral, and communication science. It ensures semantic precision and cross-theory comparability in all KGAS analyses.

## Structure

- **EntityConcept**: Actors, groups, organizations, etc.
- **ConnectionConcept**: Relationships between entities (e.g., “identifies_with”)
- **PropertyConcept**: Attributes of entities or connections (e.g., “credibility_score”)
- **ModifierConcept**: Qualifiers or contextualizers (e.g., “temporal”, “certainty”)

## Mapping Process

1. **LLM Extraction**: Indigenous terms are extracted from text.
2. **Standardization**: Terms are mapped to canonical names in the MCL.
3. **Human-in-the-Loop**: Novel terms are reviewed and added as needed.

## Schema Specification

### EntityConcept Schema
```json
{
  "type": "EntityConcept",
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:IRI",
  "subtypes": ["string"],
  "properties": ["PropertyConcept"],
  "connections": ["ConnectionConcept"],
  "bridge_links": ["external:IRI"],
  "version": "semver",
  "created_at": "timestamp",
  "validated_by": "string"
}
```

### ConnectionConcept Schema
```json
{
  "type": "ConnectionConcept", 
  "canonical_name": "string",
  "description": "string",
  "upper_parent": "dolce:Relation",
  "domain": "EntityConcept",
  "range": "EntityConcept",
  "properties": ["PropertyConcept"],
  "directional": "boolean",
  "validation_rules": ["rule"]
}
```

### PropertyConcept Schema
```json
{
  "type": "PropertyConcept",
  "canonical_name": "string", 
  "description": "string",
  "value_type": "numeric|categorical|boolean|text",
  "scale": "nominal|ordinal|interval|ratio",
  "valid_values": ["value"],
  "measurement_unit": "string",
  "uncertainty_type": "stochastic|epistemic|systematic"
}
```

## Implementation Details

### Storage and Access
- **Code Location:** `/src/ontology_library/mcl/__init__.py`
- **Schema Enforcement:** Pydantic models with JSON Schema validation
- **Database Storage:** Neo4j graph with concept relationships
- **API Endpoints:** RESTful API for concept CRUD operations
- **Integration:** Used in all theory schemas and extraction pipelines

### Validation Pipeline
```python
class MCLValidator:
    """Validates concepts against MCL standards"""
    
    def validate_concept(self, concept: ConceptDict) -> ValidationResult:
        # 1. Schema validation
        # 2. DOLCE alignment check
        # 3. Duplicate detection
        # 4. Cross-reference validation
        # 5. Semantic consistency check
```

### API Operations
```python
# Core MCL operations
mcl.add_concept(concept_data, validate=True)
mcl.get_concept(canonical_name)
mcl.search_concepts(query, filters={})
mcl.map_term_to_concept(indigenous_term)
mcl.validate_theory_schema(schema)
```

## Detailed Examples

### Production Theory Integration Example
**See**: [MCL Theory Schemas - Implementation Examples](../data/mcl-theory-schemas-examples.md) for complete production theory integrations including Cognitive Dissonance Theory, Prospect Theory, and Social Identity Theory.

### Entity Concept Example
**Indigenous term:** "grassroots organizer"
```json
{
  "type": "EntityConcept",
  "canonical_name": "CommunityOrganizer",
  "description": "Individual who mobilizes community members for collective action",
  "upper_parent": "dolce:SocialAgent",
  "subtypes": ["GrassrootsOrganizer", "PolicyOrganizer"],
  "properties": ["influence_level", "network_size", "expertise_domain"],
  "connections": ["mobilizes", "coordinates_with", "represents"],
  "indigenous_terms": ["grassroots organizer", "community leader", "activist"],
  "theory_sources": ["Social Identity Theory", "Social Cognitive Theory"],
  "validation_status": "production_ready"
}
```

### Connection Concept Example  
**Indigenous term:** "influences public opinion"
```json
{
  "type": "ConnectionConcept",
  "canonical_name": "influences_opinion",
  "description": "Causal relationship where entity affects public perception",
  "domain": "SocialAgent",
  "range": "PublicOpinion", 
  "properties": ["influence_strength", "temporal_duration"],
  "directional": true,
  "validation_rules": ["requires_evidence_source", "measurable_outcome"]
}
```

### Property Concept Example
**Indigenous term:** "credibility"
```json
{
  "type": "PropertyConcept",
  "canonical_name": "credibility_score",
  "description": "Perceived trustworthiness and reliability measure",
  "value_type": "numeric",
  "scale": "interval", 
  "valid_values": [0.0, 10.0],
  "measurement_unit": "likert_scale",
  "uncertainty_type": "stochastic"
}
```

## DOLCE Alignment Procedures

### Automated Alignment Process
```python
class DOLCEAligner:
    """Automatically aligns new concepts with DOLCE upper ontology"""
    
    def align_concept(self, concept: NewConcept) -> DOLCEAlignment:
        # 1. Semantic similarity analysis
        # 2. Definition matching against DOLCE taxonomy
        # 3. Structural constraint checking
        # 4. Expert review recommendation
        # 5. Alignment confidence score
```

### DOLCE Classification Rules
| Concept Type | DOLCE Parent | Validation Rules |
|--------------|--------------|------------------|
| **Physical Entity** | `dolce:PhysicalObject` | Must have spatial location |
| **Social Entity** | `dolce:SocialObject` | Must involve multiple agents |
| **Abstract Entity** | `dolce:AbstractObject` | Must be non-spatial |
| **Relationship** | `dolce:Relation` | Must connect two entities |
| **Property** | `dolce:Quality` | Must be measurable attribute |

### Quality Assurance Framework
```python
class ConceptQualityValidator:
    """Ensures MCL concept quality and consistency"""
    
    quality_checks = [
        "semantic_precision",      # Clear, unambiguous definition
        "dolce_consistency",       # Proper upper ontology alignment  
        "cross_reference_validity", # Valid concept connections
        "measurement_clarity",     # Clear measurement procedures
        "research_utility"         # Useful for social science research
    ]
```

## Extension Guidelines

### Adding New Concepts
1. **Research Validation**: Concept must appear in peer-reviewed literature
2. **Semantic Gap Analysis**: Must fill genuine gap in existing MCL
3. **DOLCE Alignment**: Must align with appropriate DOLCE parent class
4. **Community Review**: Subject to expert panel review process
5. **Integration Testing**: Must integrate cleanly with existing concepts

### Concept Evolution Procedures
```python
# Concept modification workflow
def evolve_concept(concept_name: str, changes: dict) -> EvolutionResult:
    # 1. Impact analysis on dependent concepts
    # 2. Backward compatibility assessment
    # 3. Migration path generation
    # 4. Validation test suite update
    # 5. Documentation synchronization
```

### Version Control and Migration
- **Semantic Versioning**: Major.Minor.Patch versioning for concept changes
- **Migration Scripts**: Automated concept evolution with data preservation
- **Rollback Procedures**: Safe rollback mechanisms for problematic changes
- **Change Documentation**: Complete audit trail for all concept modifications

## Extensibility Framework

The MCL grows systematically through:

### Research-Driven Expansion
- **Literature Integration**: New concepts from emerging research domains
- **Cross-Domain Synthesis**: Concepts spanning multiple social science fields
- **Methodological Innovation**: Concepts supporting novel analysis techniques

### Community Contribution Process
```markdown
1. **Concept Proposal**: Submit via GitHub issue with research justification
2. **Expert Review**: Panel evaluation for research merit and semantic precision
3. **Prototype Integration**: Test integration with existing concept ecosystem
4. **Community Validation**: Broader community review and feedback
5. **Production Integration**: Full integration with versioning and documentation
```

### Quality Metrics and Monitoring
- **Usage Analytics**: Track concept utilization across research projects
- **Semantic Drift Detection**: Monitor concept meaning stability over time  
- **Research Impact Assessment**: Evaluate contribution to research outcomes
- **Community Satisfaction**: Regular feedback collection from users

## Versioning Rules

| Change Type | Version Bump | Review Required | Documentation |
|-------------|--------------|-----------------|---------------|
| **Concept Addition** | Patch (x.y.z+1) | No | Update concept list |
| **Concept Modification** | Minor (x.y+1.0) | Yes | Update examples |
| **Schema Change** | Major (x+1.0.0) | Yes | Migration guide |
| **DOLCE Alignment** | Minor (x.y+1.0) | Yes | Alignment report |

### Concept Merge Policy
New concepts are merged via `scripts/mcl_merge.py` which:
- Validates against existing concepts
- Checks DOLCE alignment
- Updates cross-references
- Generates migration guide

## DOLCE and Bridge Links

### Upper Ontology Alignment
Every concept in the MCL is aligned with the DOLCE (Descriptive Ontology for Linguistic and Cognitive Engineering) upper ontology:

- **`upper_parent`**: IRI of the closest DOLCE superclass (e.g., `dolce:PhysicalObject`, `dolce:SocialObject`)
- **Semantic Precision**: Ensures ontological consistency across all concepts
- **Interoperability**: Enables integration with other DOLCE-aligned systems

### Bridge Links (Optional)
For enhanced interoperability, concepts may include:

- **`bridge_links`**: Array of IRIs linking to related concepts in external ontologies
- **Cross-Domain Mapping**: Connects social science concepts to domain-specific ontologies
- **Research Integration**: Enables collaboration with other research platforms -e 
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>
