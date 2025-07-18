# Master Concept Library Integration

## Overview

The Master Concept Library provides a **pre-constructed, controlled vocabulary** of social, behavioral, and discourse concepts derived from established academic theories. This library serves as the semantic backbone for the KGAS system, ensuring consistency and theoretical grounding across all 121 tools.

## Key Benefits

### 1. **Semantic Consistency**
- All tools use the same standardized entity and relationship types
- No ambiguity about what "IndividualActor" or "Influences" means
- Reduces integration complexity across the 121-tool ecosystem

### 2. **Theory-Grounded Extraction**
- Concepts derived from established theories (Ajzen, Cialdini, Tajfel & Turner, etc.)
- Each concept includes academic references
- Ensures extractions are meaningful in social science contexts

### 3. **Programmatic Validation**
- Automatic validation against the master library
- Domain/range constraints for relationships
- Type-safe property and modifier values

### 4. **Extensibility**
- New concepts can be added by editing YAML files
- Concepts can be organized hierarchically
- Theory-specific extensions supported

## Architecture

```
src/ontology_library/
├── master_concepts.py       # Pydantic models for concepts
├── ontology_service.py      # Singleton service for concept access
└── concepts/
    ├── entities.yaml        # Entity type definitions
    ├── connections.yaml     # Relationship type definitions
    ├── properties.yaml      # Property definitions
    └── modifiers.yaml       # Modifier definitions

src/core/
├── ontology_validator.py    # Validation logic using the library
└── data_models.py          # Updated with ontology fields
```

## Concept Categories

### Entities
Standardized types for actors and objects in social systems:
- **IndividualActor**: Single human or computational entity
- **SocialGroup**: Collection of individuals with shared characteristics
- **Institution**: Formal organization with defined rules
- **Message**: Unit of information transmitted
- **Belief**, **Attitude**, **Norm**, **Identity**, etc.

### Connections (Relationships)
Standardized relationship types with domain/range constraints:
- **IdentifiesWith**: IndividualActor → SocialGroup/Identity
- **BelongsTo**: Actor → Group/Institution
- **Influences**: Various → Various (flexible influence)
- **Communicates**: Source → Audience
- **HasAuthorityOver**: Institution/Actor → Actor/Group

### Properties
Measurable attributes with defined value types:
- **Numeric**: influence_strength (0-1), age, centrality
- **Categorical**: gender, power_type, norm_type
- **Boolean**: Various binary properties
- **Derived**: Computed from other properties

### Modifiers
Contextual qualifiers for any concept:
- **Temporal**: temporal_phase, duration, recency
- **Modal**: possibility, necessity, conditionality
- **Certainty**: certainty_level, evidence_strength
- **Normative**: normative_valence, social_desirability

## Usage Examples

### 1. Basic Entity Validation

```python
from src.core.ontology_validator import OntologyValidator
from src.core.data_models import Entity

validator = OntologyValidator()

# Create an entity
entity = Entity(
    canonical_name="Jane Doe",
    entity_type="IndividualActor",  # Must be valid type
    properties={
        "age": 35,
        "source_credibility": 0.8
    },
    modifiers={
        "certainty_level": "certain",
        "temporal_phase": "present"
    }
)

# Validate against master library
errors = validator.validate_entity(entity)
if errors:
    print("Validation errors:", errors)
```

### 2. Relationship Domain/Range Validation

```python
# Create entities
person = Entity(entity_type="IndividualActor", ...)
company = Entity(entity_type="Institution", ...)

# Create relationship
relationship = Relationship(
    source_id=person.id,
    target_id=company.id,
    relationship_type="BelongsTo",  # Valid: Actor → Institution
)

# Validate with domain/range checking
errors = validator.validate_relationship(relationship, person, company)
```

### 3. Tool Contract Integration

```yaml
# In tool contract (e.g., T23A_SpacyNER.yaml)
output_contract:
  produced_data_types:
    - type: Entity
      validation:
        entity_type:
          constraint: "must_exist_in_ontology"
        properties:
          constraint: "keys_must_be_valid_properties"
        modifiers:
          constraint: "keys_must_be_valid_modifiers"

ontology_integration:
  entity_type_mapping:
    PERSON: "IndividualActor"
    ORG: "Institution"
  default_properties:
    IndividualActor: ["source_credibility", "confidence_level"]
```

### 4. Entity Enrichment

```python
# Create minimal entity
entity = Entity(
    canonical_name="John Smith",
    entity_type="IndividualActor",
    # No modifiers specified
)

# Enrich with default modifiers
enriched = validator.enrich_entity(entity)
# Now has: temporal_phase, certainty_level, etc. with defaults
```

### 5. Concept Discovery

```python
from src.ontology_library.ontology_service import OntologyService

ontology = OntologyService()

# Search by indigenous terms
concepts = ontology.search_by_indigenous_term("influences")

# Get entity template
template = validator.get_entity_template("IndividualActor")
print("Applicable properties:", template["applicable_properties"])
print("Applicable modifiers:", template["applicable_modifiers"])
```

## Integration with Contract System

The master concept library integrates seamlessly with the contract validation system:

1. **Contract Validation**: Contracts can specify ontology constraints
2. **Runtime Validation**: Tools validate outputs against the library
3. **CI/CD Integration**: Automated checks ensure compliance
4. **Type Safety**: Pydantic models enforce structure

## Adding New Concepts

To add new concepts:

1. **Edit appropriate YAML file** in `src/ontology_library/concepts/`
2. **Follow the existing format**:
   ```yaml
   ConceptName:
     indigenous_term: ["term1", "term2"]
     description: "Clear description"
     subTypeOf: ["ParentConcept"]  # Optional
     references: ["Author, Year"]
     # Type-specific fields...
   ```
3. **Run validation** to ensure consistency
4. **Update tool contracts** to use new concepts

## Best Practices

1. **Always validate** entities and relationships against the library
2. **Use enrichment** to add default modifiers
3. **Check domain/range** constraints for relationships
4. **Reference academic sources** when adding concepts
5. **Keep indigenous terms** comprehensive for better search

## Theory Meta-Schema Alignment

The master concept library implements the Theory Meta-Schema's vision:
- **termDefinition** → Entity/Connection concepts
- **propertyDefinition** → Property concepts  
- **modifierDefinition** → Modifier concepts
- **Academic grounding** → References in each concept
- **Composability** → Hierarchical concept relationships

This creates a **living ontology** that grows with the system while maintaining theoretical rigor and practical utility.