# Ontology Library Module - CLAUDE.md

## Overview
The `src/ontology_library/` directory contains the **Master Concept Library** that serves as the controlled vocabulary and master ontology for the entire GraphRAG system. This module provides a comprehensive ontology service with entity, connection, property, and modifier definitions.

## Ontology Library Architecture

### Master Concept Pattern
The ontology library follows a structured master concept pattern:
- **MasterConceptRegistry**: Central registry for all concept definitions
- **Concept Categories**: Entities, Connections, Properties, Modifiers
- **YAML Storage**: Concept definitions stored in YAML files
- **Singleton Service**: OntologyService provides singleton access

### Concept Hierarchy Pattern
All concepts follow a hierarchical structure:
- **ConceptDefinition**: Base class for all concepts
- **Specialized Concepts**: EntityConcept, ConnectionConcept, PropertyConcept, ModifierConcept
- **Subtype Relationships**: Concepts can be subtypes of other concepts
- **Theory References**: Concepts can reference academic theories

## Individual Component Patterns

### OntologyService (`ontology_service.py`)
**Purpose**: Singleton service for managing the Master Concept Library

**Key Patterns**:
- **Singleton Pattern**: Single instance across the system
- **YAML Loading**: Load concepts from YAML files
- **Validation**: Validate concept types and relationships
- **Hierarchy Management**: Manage concept hierarchies and subtypes

**Usage**:
```python
from src.ontology_library.ontology_service import OntologyService

# Get singleton instance
ontology_service = OntologyService()

# Validate entity types
is_valid = ontology_service.validate_entity_type("Person")

# Get entity attributes
attributes = ontology_service.get_entity_attributes("Organization")

# Validate connections
is_valid = ontology_service.validate_connection_domain_range(
    "works_for", "Person", "Organization"
)

# Get concept statistics
stats = ontology_service.get_statistics()
print(f"Entities: {stats['entities']}, Connections: {stats['connections']}")
```

**Core Components**:

#### Concept Loading
```python
def _load_all_concepts(self):
    """Load all concept definitions from YAML files"""
```

**Loading Features**:
- **YAML Parsing**: Parse YAML files for concept definitions
- **Error Handling**: Handle loading errors gracefully
- **Category Loading**: Load entities, connections, properties, modifiers
- **Statistics**: Track loading statistics

#### Concept Validation
```python
def validate_entity_type(self, entity_type: str) -> bool:
    """Check if an entity type exists in the master library"""

def validate_connection_type(self, connection_type: str) -> bool:
    """Check if a connection type exists in the master library"""

def validate_property_name(self, property_name: str) -> bool:
    """Check if a property name exists in the master library"""

def validate_modifier_name(self, modifier_name: str) -> bool:
    """Check if a modifier name exists in the master library"""
```

**Validation Features**:
- **Type Validation**: Validate concept types against registry
- **Domain/Range Validation**: Validate connection domain and range constraints
- **Property Validation**: Validate property values and types
- **Error Handling**: Handle validation errors gracefully

#### Concept Retrieval
```python
def get_concept(self, concept_name: str) -> Optional[ConceptDefinition]:
    """Get a concept by name from any category"""

def get_entity_attributes(self, entity_type: str) -> List[str]:
    """Get typical attributes for an entity type"""

def get_property_value_type(self, property_name: str) -> Optional[str]:
    """Get the value type for a property"""

def get_modifier_values(self, modifier_name: str) -> List[str]:
    """Get possible values for a modifier"""
```

**Retrieval Features**:
- **Cross-Category Search**: Search across all concept categories
- **Attribute Retrieval**: Get entity attributes and properties
- **Type Information**: Get property value types and constraints
- **Value Lists**: Get valid values for categorical properties

### Master Concepts (`master_concepts.py`)
**Purpose**: Pydantic models for generic concepts in the Master Concept Library

**Key Patterns**:
- **Pydantic Models**: Use Pydantic for data validation
- **Type Safety**: Strong typing for all concept definitions
- **Hierarchical Structure**: Support for concept hierarchies
- **Theory Integration**: Integration with academic theories

**Core Models**:

#### ConceptDefinition
```python
class ConceptDefinition(BaseModel):
    name: str = Field(description="Standardized, camelCase or snake_case name")
    indigenous_term: List[str] = Field(description="Common real-world phrasing")
    description: str = Field(description="Concise explanation of the concept")
    subTypeOf: Optional[List[str]] = Field(description="Parent concept names")
    references: Optional[List[str]] = Field(description="Academic references")
    aliases: Optional[List[str]] = Field(description="Alternative names")
```

**Base Features**:
- **Standardized Names**: Use camelCase or snake_case naming
- **Indigenous Terms**: Include real-world terminology
- **Subtype Relationships**: Support for concept hierarchies
- **Academic References**: Link to academic sources
- **Aliases**: Support for alternative names

#### EntityConcept
```python
class EntityConcept(ConceptDefinition):
    object_type: Literal["Entity"] = "Entity"
    typical_attributes: Optional[List[str]] = Field(description="Common attributes")
    examples: Optional[List[str]] = Field(description="Examples from literature")
```

**Entity Features**:
- **Entity Type**: Fixed object type for entities
- **Typical Attributes**: Common attributes for entity types
- **Examples**: Real-world examples from literature
- **Inheritance**: Inherit from base ConceptDefinition

#### ConnectionConcept
```python
class ConnectionConcept(ConceptDefinition):
    object_type: Literal["Connection"] = "Connection"
    domain: Optional[List[str]] = Field(description="Valid source entity types")
    range: Optional[List[str]] = Field(description="Valid target entity types")
    is_directed: bool = Field(description="Whether relationship is directional")
    is_symmetric: bool = Field(description="Whether relationship is symmetric")
    cardinality: Optional[str] = Field(description="Cardinality constraints")
```

**Connection Features**:
- **Domain/Range**: Define valid source and target types
- **Directionality**: Support for directed and undirected relationships
- **Symmetry**: Support for symmetric relationships
- **Cardinality**: Support for cardinality constraints

#### PropertyConcept
```python
class PropertyConcept(ConceptDefinition):
    object_type: Literal["Property"] = "Property"
    value_type: Literal["numeric", "categorical", "boolean", "string", "complex", "derived"]
    applies_to: Optional[List[str]] = Field(description="Applicable concept types")
    valid_values: Optional[List[Any]] = Field(description="Allowed values")
    value_range: Optional[Dict[str, Any]] = Field(description="Min/max values")
    computation: Optional[str] = Field(description="Computation method")
    unit: Optional[str] = Field(description="Unit of measurement")
```

**Property Features**:
- **Value Types**: Support for multiple data types
- **Applicability**: Define which concepts can have this property
- **Value Constraints**: Support for valid values and ranges
- **Computation**: Support for derived properties
- **Units**: Support for measurement units

#### ModifierConcept
```python
class ModifierConcept(ConceptDefinition):
    object_type: Literal["Modifier"] = "Modifier"
    category: Literal["temporal", "modal", "truth_value", "certainty", "normative", "other"]
    applies_to: Optional[List[str]] = Field(description="Applicable concept types")
    values: Optional[List[str]] = Field(description="Possible values")
    default_value: Optional[str] = Field(description="Default value")
```

**Modifier Features**:
- **Categories**: Support for different modifier categories
- **Applicability**: Define which concepts can be modified
- **Value Lists**: Support for predefined value lists
- **Defaults**: Support for default values

### Master Concept Registry (`master_concepts.py`)
**Purpose**: Registry to hold all loaded concepts with validation and hierarchy management

**Key Patterns**:
- **Central Registry**: Single registry for all concept types
- **Cross-Category Operations**: Operations across all concept categories
- **Hierarchy Management**: Manage concept hierarchies and relationships
- **Validation**: Validate concept relationships and constraints

**Core Methods**:

#### Concept Retrieval
```python
def get_concept(self, concept_name: str) -> Optional[ConceptDefinition]:
    """Get a concept by name from any category"""

def get_all_names(self) -> List[str]:
    """Get all concept names across all categories"""

def get_concepts_by_type(self, concept_type: Literal["Entity", "Connection", "Property", "Modifier"]) -> Dict[str, ConceptDefinition]:
    """Get all concepts of a specific type"""
```

**Retrieval Features**:
- **Cross-Category Search**: Search across all concept categories
- **Type Filtering**: Filter concepts by type
- **Name Collection**: Collect all concept names
- **Flexible Access**: Access concepts by name or type

#### Validation
```python
def validate_domain_range(self, connection_name: str, source_type: str, target_type: str) -> bool:
    """Validate if a connection's domain and range constraints are satisfied"""

def get_subtypes(self, concept_name: str) -> List[str]:
    """Get all concepts that are subtypes of the given concept"""
```

**Validation Features**:
- **Domain/Range Validation**: Validate connection constraints
- **Subtype Discovery**: Find all subtypes of a concept
- **Hierarchy Validation**: Validate concept hierarchies
- **Constraint Checking**: Check concept constraints

## YAML Concept Files

### File Structure
The `concepts/` directory contains YAML files for each concept category:
- **entities.yaml**: Entity concept definitions
- **connections.yaml**: Connection concept definitions  
- **properties.yaml**: Property concept definitions
- **modifiers.yaml**: Modifier concept definitions

### YAML Format
```yaml
# Example entity definition
Person:
  indigenous_term: ["person", "individual", "human", "actor"]
  description: "A human individual or actor in the system"
  subTypeOf: ["Entity"]
  typical_attributes: ["name", "age", "role", "location"]
  examples: ["John Smith", "Jane Doe", "researcher", "student"]
  references: ["Social Theory 101", "Actor Network Theory"]
  aliases: ["Individual", "Actor", "Human"]
```

**YAML Features**:
- **Hierarchical Structure**: Nested concept definitions
- **List Support**: Support for lists of values
- **Optional Fields**: Support for optional concept fields
- **Reference Support**: Support for academic references

## Common Commands & Workflows

### Development Commands
```bash
# Test ontology service
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(f'Loaded {len(service.registry.entities)} entities')"

# Test concept validation
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.validate_entity_type('Person'))"

# Test concept retrieval
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.get_entity_attributes('Organization'))"

# Test registry operations
python -c "from src.ontology_library.master_concepts import MasterConceptRegistry; registry = MasterConceptRegistry(); print(f'Registry has {len(registry.entities)} entities')"
```

### Testing Commands
```bash
# Test YAML loading
python -c "import yaml; from pathlib import Path; concepts_dir = Path('src/ontology_library/concepts'); entities_file = concepts_dir / 'entities.yaml'; print(yaml.safe_load(open(entities_file)))"

# Test concept hierarchy
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.get_concept_hierarchy())"

# Test domain/range validation
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.validate_connection_domain_range('works_for', 'Person', 'Organization'))"

# Test property validation
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.validate_property_value('age', 25))"
```

### Debugging Commands
```bash
# Check concept statistics
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); stats = service.get_statistics(); print(f'Entities: {stats[\"entities\"]}, Connections: {stats[\"connections\"]}, Properties: {stats[\"properties\"]}, Modifiers: {stats[\"modifiers\"]}')"

# List all concept names
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.registry.get_all_names())"

# Test concept search
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); results = service.search_by_indigenous_term('person'); print([c.name for c in results])"

# Test theory references
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.get_concepts_for_theory('Social Theory'))"
```

## Code Style & Conventions

### Service Design Patterns
- **Singleton Pattern**: Single instance across the system
- **Registry Pattern**: Central registry for all concepts
- **Validation Pattern**: Comprehensive validation for all operations
- **Hierarchy Pattern**: Support for concept hierarchies

### Naming Conventions
- **Service Names**: Use `Service` suffix for service classes
- **Concept Names**: Use camelCase or snake_case for concept names
- **Method Names**: Use descriptive names for operations
- **Constants**: Use UPPER_CASE for magic numbers and thresholds

### Error Handling Patterns
- **Graceful Degradation**: Handle errors gracefully
- **Validation Errors**: Provide clear validation error messages
- **Loading Errors**: Handle YAML loading errors
- **Registry Errors**: Handle registry operation errors

### Logging Patterns
- **Loading Logging**: Log concept loading progress
- **Validation Logging**: Log validation results
- **Error Logging**: Log errors with context
- **Statistics Logging**: Log registry statistics

## Integration Points

### Core Integration
- **Service Manager**: Integration with core service manager
- **Logging**: Integration with core logging configuration
- **Configuration**: Integration with core configuration system
- **Error Handling**: Integration with core error handling

### Tool Integration
- **Phase 1 Tools**: Integration with basic extraction tools
- **Phase 2 Tools**: Integration with ontology-aware tools
- **Phase 3 Tools**: Integration with fusion tools
- **Validation**: Integration with extraction validation

### External Dependencies
- **Pydantic**: Data validation and serialization
- **PyYAML**: YAML file parsing
- **Pathlib**: File path handling
- **Typing**: Type hints and validation

## Performance Considerations

### Loading Optimization
- **Lazy Loading**: Load concepts only when needed
- **Caching**: Cache loaded concepts in memory
- **YAML Optimization**: Optimize YAML parsing
- **Registry Optimization**: Optimize registry operations

### Memory Management
- **Concept Reuse**: Reuse concept objects when possible
- **Reference Management**: Manage theory references efficiently
- **Hierarchy Caching**: Cache hierarchy relationships
- **Cleanup**: Proper cleanup of temporary data

### Speed Optimization
- **Indexing**: Index concepts for fast lookup
- **Validation Caching**: Cache validation results
- **Hierarchy Optimization**: Optimize hierarchy traversal
- **Search Optimization**: Optimize concept search

## Testing Patterns

### Unit Testing
- **Service Testing**: Test OntologyService independently
- **Model Testing**: Test Pydantic models
- **Registry Testing**: Test MasterConceptRegistry
- **Validation Testing**: Test validation methods

### Integration Testing
- **YAML Integration**: Test YAML file loading
- **Service Integration**: Test service integration
- **Tool Integration**: Test tool integration
- **End-to-End**: Test complete ontology pipeline

### Data Testing
- **Concept Testing**: Test concept definitions
- **Hierarchy Testing**: Test concept hierarchies
- **Validation Testing**: Test concept validation
- **Constraint Testing**: Test concept constraints

## Troubleshooting

### Common Issues
1. **YAML Loading Issues**: Check YAML file format and syntax
2. **Concept Validation Issues**: Check concept definitions and constraints
3. **Hierarchy Issues**: Check subtype relationships
4. **Performance Issues**: Check registry size and operations

### Debug Commands
```bash
# Check YAML file syntax
python -c "import yaml; from pathlib import Path; yaml.safe_load(open('src/ontology_library/concepts/entities.yaml'))"

# Test concept loading
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print('Concepts loaded successfully')"

# Test registry operations
python -c "from src.ontology_library.master_concepts import MasterConceptRegistry; registry = MasterConceptRegistry(); print('Registry created successfully')"

# Test validation
python -c "from src.ontology_library.ontology_service import OntologyService; service = OntologyService(); print(service.validate_entity_type('TestEntity'))"
```

## Migration & Upgrades

### Concept Migration
- **YAML Migration**: Migrate YAML concept definitions
- **Model Migration**: Migrate Pydantic models
- **Registry Migration**: Migrate registry structure
- **Validation Migration**: Migrate validation rules

### Service Migration
- **Service Updates**: Update service implementation
- **API Changes**: Handle API changes and deprecations
- **Integration Updates**: Update tool integrations
- **Performance Updates**: Update performance optimizations

### Configuration Updates
- **YAML Configuration**: Update YAML file structure
- **Validation Configuration**: Update validation rules
- **Performance Configuration**: Update performance settings
- **Integration Configuration**: Update integration settings 