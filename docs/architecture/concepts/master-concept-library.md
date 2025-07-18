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

## Implementation

- **Code Location:** `/src/ontology_library/mcl/__init__.py`
- **Schema Enforcement:** Pydantic models
- **Integration:** Used in all theory schemas and extraction pipelines

## Example

- “grassroots organizer” → `SocialGroup` (`CommunityOrganizer` subtype)
- “credibility” → `PropertyConcept` with value type “numeric”

## Extensibility

The MCL grows as new concepts are encountered and validated, ensuring KGAS remains adaptable to emerging research and domains.

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
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
