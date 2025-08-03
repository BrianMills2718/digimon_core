# KGAS Schema Management Architecture

**Version**: 1.0  
**Status**: Target Architecture  
**Last Updated**: 2025-07-23  

## Overview

KGAS uses a **three-schema architecture** to separate concerns between storage, runtime validation, and theoretical execution. This document clarifies the purpose, relationships, and management of these schemas.

## Three-Schema Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Schema Management Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │   Pydantic      │  │   Database      │  │   Theory Meta       │  │
│  │   Schemas       │◄─┤   Schemas       │  │   Schema            │  │
│  │  (Runtime API)  │  │  (Storage)      │  │  (Execution)        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Storage Layer                                  │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐  │
│  │       Neo4j Graph           │    │       SQLite Metadata      │  │
│  │   (Entities, Relations)     │    │   (Provenance, Config)     │  │
│  └─────────────────────────────┘    └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Comprehensive Modeling Paradigm Schema Ecosystem

**Status**: **VALIDATED** - 5 Complete Schema Implementations  
**Validation**: 100% success across all Carter speech analysis tests  
**Coverage**: Object-oriented, semantic web, fact-based, enhanced ER, and n-ary approaches

KGAS implements a comprehensive ecosystem of 5 major schema modeling paradigms, each optimized for different aspects of political analysis and research:

### Schema Paradigm Capability Matrix

| **Capability** | **UML** | **RDF/OWL** | **ORM** | **TypeDB** | **N-ary** |
|----------------|---------|-------------|---------|------------|-----------|
| **Fact-based modeling** | | | | ⚠️ | ⚠️ |
| **Formal semantics** | | | | ⚠️ | |
| **Automated reasoning** | | | | | ⚠️ |
| **Rich constraints** | ⚠️ | | | | ⚠️ |
| **Natural verbalization** | | ⚠️ | | ⚠️ | ⚠️ |
| **N-ary relationships** | | | | | |
| **Industry adoption** | | ⚠️ | | | |
| **Visual modeling** | | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

**Capability Scores** (out of 38 total capabilities):
1. **RDF/OWL**: 29 points (76.3%) - Highest semantic precision
2. **ORM**: 20 points (52.6%) - Most business-friendly  
3. **TypeDB**: 19 points (50.0%) - Best for complex relationship databases
4. **UML**: 17 points (44.7%) - Industry standard with excellent tooling
5. **N-ary**: 13 points (34.2%) - Specialized for complex multi-party relationships

### 1. UML Class Diagram Schemas (`src/core/uml_class_schemas.py`)

**Paradigm**: Object-Oriented Attribute-Based  
**Foundation**: Object-oriented programming concepts  
**Strength**: Industry standard with excellent tool support

**Key Features**:
- Object-oriented class hierarchies with inheritance
- Associations, aggregations, and compositions
- PlantUML code generation for visual diagrams
- Method and attribute modeling

**Political Analysis Example**:
```python
# Carter speech as UML objects
carter = PoliticalLeader(firstName='Jimmy', lastName='Carter')
negotiation = Negotiation(topic='détente', outcome='ongoing')
negotiation.addParticipant(carter)
negotiation.addParticipant(brezhnev)
```

**Best for**: Software system design, object-relational mapping, team communication with developers  
**Avoid for**: Pure conceptual domain modeling, semantic web applications, automated reasoning

### 2. RDF/OWL Ontology Schemas (`src/core/rdf_owl_schemas.py`)

**Paradigm**: Triple-Based Semantic Web  
**Foundation**: Description Logic and First-Order Logic  
**Strength**: Most semantically precise with formal logical foundation

**Key Features**:
- RDF triple representation (subject-predicate-object)
- OWL class hierarchies and property definitions
- SWRL rules for automated reasoning
- Turtle serialization and SPARQL queries

**Political Analysis Example**:
```turtle
<pol:DetenteNegotiation1977> rdf:type pol:Negotiation .
<pol:DetenteNegotiation1977> pol:hasInitiator pol:JimmyCarter .
<pol:DetenteNegotiation1977> pol:hasResponder pol:LeonidBrezhnev .
<pol:DetenteNegotiation1977> pol:concerns pol:DetenteInstance .
```

**Best for**: Semantic web applications, knowledge graphs, automated reasoning, cross-domain integration  
**Avoid for**: Simple business applications, performance-critical systems, rapid prototyping

### 3. ORM Fact-Based Schemas (`src/core/orm_schemas.py`)

**Paradigm**: Fact-Based Relationship-Centered  
**Foundation**: Conceptual modeling theory  
**Strength**: Most natural and precise conceptual modeling

**Key Features**:
- Elementary facts with role constraints
- Natural language verbalization
- Rich constraint vocabulary (uniqueness, subset, frequency)
- Business-user friendly representations

**Political Analysis Example**:
```python
# Natural language facts
"Person <Jimmy Carter> initiates Negotiation <détente_talks>"
"Negotiation <détente_talks> involves Person <Leonid Brezhnev>"
"Negotiation <détente_talks> concerns Concept <world_peace>"
```

**Best for**: Conceptual domain modeling, business rule validation, requirements analysis  
**Avoid for**: Direct software implementation, visual modeling requirements, automated reasoning

### 4. TypeDB Enhanced ER Schemas (`src/core/typedb_style_schemas.py`)

**Paradigm**: Enhanced Entity-Relation-Attribute  
**Foundation**: Extended ER model with type system  
**Strength**: Native n-ary relationships with database backing

**Key Features**:
- Native n-ary relationships without reification
- Type inheritance and polymorphism
- Rule-based symbolic reasoning
- Query-friendly relationship modeling

**Political Analysis Example**:
```typeql
(initiator: $carter, responder: $brezhnev, 
 underlying-principle: $detente, ultimate-goal: $peace) isa negotiation;
```

**Best for**: Complex relationship databases, knowledge base applications, symbolic reasoning  
**Avoid for**: Simple relational databases, cross-platform interoperability, standard SQL environments

### 5. N-ary Graph Schemas (`src/core/nary_graph_schemas.py`)

**Paradigm**: Reified Relationship-Based  
**Foundation**: Graph theory with relationship reification  
**Strength**: Excellent for complex multi-party relationships

**Key Features**:
- Relationships as first-class entities
- Participant role modeling
- Causal and temporal constraints
- Complex multi-party relationship analysis

**Political Analysis Example**:
```python
ReifiedRelationship {
    relation_id: 'détente_negotiation_1977',
    relation_type: NEGOTIATION,
    participants: [
        NAryParticipant('jimmy_carter', INITIATOR),
        NAryParticipant('leonid_brezhnev', RESPONDER),
        NAryParticipant('world_peace', TARGET)
    ]
}
```

**Best for**: Complex multi-party political analysis, social network analysis, process modeling  
**Avoid for**: Simple binary relationships, performance-critical applications, large-scale systems

### Schema Selection Guide

**For Academic Research**:
- **Exploratory Analysis**: Start with RDF/OWL for semantic precision
- **Business Requirements**: Use ORM for stakeholder communication
- **Implementation**: Convert to UML for software development

**For Political Analysis**:
- **Multi-party Events**: N-ary schemas for complex relationships
- **Policy Analysis**: TypeDB for rule-based reasoning
- **Cross-domain Integration**: RDF/OWL for semantic interoperability

**For Software Development**:
- **Object-oriented Systems**: UML class diagrams
- **Database Design**: Convert from conceptual (ORM) to implementation (UML)
- **API Contracts**: Pydantic schemas derived from conceptual models

### Implementation Architecture

```python
class SchemaManager:
    """Unified management of all schema paradigms"""
    
    def __init__(self):
        self.uml_manager = UMLClassDiagramManager()
        self.rdf_manager = RDFOWLOntologyManager()
        self.orm_manager = ORMFactBasedManager()
        self.typedb_manager = TypeDBStyleManager()
        self.nary_manager = NAryGraphSchemaManager()
    
    def convert_between_paradigms(self, 
                                 source_schema: Any, 
                                 source_type: str, 
                                 target_type: str) -> Any:
        """Convert same domain model between schema paradigms"""
        
        # Extract semantic content
        semantic_model = self._extract_semantics(source_schema, source_type)
        
        # Generate target paradigm representation
        return self._generate_target(semantic_model, target_type)
    
    def analyze_capabilities(self, domain_requirements: List[str]) -> Dict[str, float]:
        """Score each schema paradigm for given domain requirements"""
        
        scores = {}
        for paradigm in ['uml', 'rdf_owl', 'orm', 'typedb', 'nary']:
            scores[paradigm] = self._calculate_fit_score(
                paradigm, domain_requirements
            )
        
        return scores
```

### Testing and Validation

**Cross-Paradigm Validation**:
All schema approaches successfully model the same political fact:
*"Jimmy Carter initiates détente negotiation with Leonid Brezhnev regarding world peace"*

**Quality Metrics**:
- **Statistical Complexity**: RDF/OWL most complex (229 elements), N-ary simplest (16 elements)
- **Constraint Richness**: ORM highest (11 constraints), UML lowest (4 constraints)  
- **Semantic Precision**: RDF/OWL leads with formal logic foundation
- **Natural Language**: ORM provides best business-user comprehension

**Comprehensive Testing Suite**:
- `test_uml_class_schemas.py` - Object-oriented modeling validation
- `test_rdf_owl_schemas.py` - Semantic web standards compliance  
- `test_orm_schemas.py` - Fact-based modeling and verbalization
- `test_typedb_schemas.py` - Enhanced ER and n-ary relationships
- `test_nary_graph_schemas.py` - Reified relationship modeling
- `test_comprehensive_schema_comparison.py` - Cross-paradigm analysis

This comprehensive schema ecosystem enables KGAS to support diverse research methodologies and analytical requirements while maintaining theoretical rigor and practical applicability.

## Schema Purposes and Responsibilities

### 1. Pydantic Schemas (PYDANTIC_SCHEMAS.md)
**Purpose**: Runtime validation and API contracts

**Responsibilities**:
- Type validation for all API interactions
- Tool input/output contract enforcement
- Service interface definitions
- Cross-modal data exchange formats

**Location**: `/docs/architecture/data/PYDANTIC_SCHEMAS.md`

**Example**:
```python
# Runtime validation for entity processing
class Entity(BaseModel):
    id: str = Field(..., description="Unique entity identifier")
    canonical_name: str = Field(..., min_length=1)
    entity_type: EntityType
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_document: str
    
    class Config:
        validate_assignment = True
        use_enum_values = True
```

### 2. Database Schemas (DATABASE_SCHEMAS.md)
**Purpose**: Physical storage optimization

**Responsibilities**:
- Neo4j node and relationship definitions
- SQLite table structures and indexes
- Storage-specific optimizations
- Query performance tuning

**Location**: `/docs/architecture/data/DATABASE_SCHEMAS.md`

**Example**:
```cypher
// Neo4j storage schema - optimized for graph queries
CREATE CONSTRAINT entity_id_unique FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE INDEX entity_type_index FOR (e:Entity) ON (e.entity_type);
CREATE VECTOR INDEX entity_embedding FOR (e:Entity) ON (e.embedding);

(:Entity {
    id: string,              // Primary key
    canonical_name: string,  // Display name
    entity_type: string,     // Enum as string
    confidence: float,       // 0.0-1.0
    embedding: vector[384],  // Vector search
    metadata: map           // Additional properties
})
```

### 3. Theory Meta Schema (theory-meta-schema-v10.md)
**Purpose**: Domain theory integration and rule execution

**Responsibilities**:
- Theory-specific data transformations
- Rule execution frameworks
- Domain ontology integration
- Academic workflow configurations

**Location**: `/docs/architecture/data/theory-meta-schema-v10.md`

**Example**:
```json
{
    "theory_id": "social_network_analysis",
    "version": "v10",
    "execution": {
        "rules": [
            {
                "name": "centrality_weighting",
                "condition": "entity.type == 'PERSON'",
                "transformation": "apply_social_centrality_boost(entity, 1.2)"
            }
        ]
    }
}
```

## Schema Transformation Layer

The **SchemaManager** class provides unified transformation between schemas:

```python
from typing import Any, Dict
from pydantic import BaseModel

class SchemaManager:
    """Unified schema management and transformation"""
    
    def to_database(self, pydantic_model: BaseModel) -> Dict[str, Any]:
        """Convert Pydantic model to database storage format
        
        Transformations:
        - Flatten nested objects for storage efficiency
        - Convert enums to string values
        - Separate vector embeddings for indexing
        - Extract metadata for separate storage
        """
        data = pydantic_model.dict()
        
        # Storage optimizations
        storage_format = {
            "id": data["id"],
            "canonical_name": data["canonical_name"],
            "entity_type": data["entity_type"].value if hasattr(data["entity_type"], 'value') else data["entity_type"],
            "confidence": data["confidence"],
            "embedding": data.get("embedding", []),
            "metadata": {k: v for k, v in data.items() if k not in ["id", "canonical_name", "entity_type", "confidence", "embedding"]}
        }
        
        return storage_format
    
    def from_database(self, db_record: Dict[str, Any]) -> BaseModel:
        """Convert database record to Pydantic model
        
        Reconstructions:
        - Rebuild nested objects from flattened storage
        - Convert strings back to enum types
        - Merge metadata back into main object
        - Validate all constraints
        """
        # Reconstruct Pydantic format
        pydantic_data = {
            "id": db_record["id"],
            "canonical_name": db_record["canonical_name"],
            "entity_type": EntityType(db_record["entity_type"]),
            "confidence": db_record["confidence"],
            "embedding": db_record.get("embedding", []),
        }
        
        # Merge metadata
        if "metadata" in db_record and db_record["metadata"]:
            pydantic_data.update(db_record["metadata"])
        
        return Entity(**pydantic_data)
    
    def apply_theory_rules(self, model: BaseModel, theory_schema: Dict[str, Any]) -> BaseModel:
        """Apply theory transformations to runtime model
        
        Transformations:
        - Execute theory-specific rules
        - Apply domain ontology mappings
        - Add theory-derived attributes
        - Validate theory compliance
        """
        # Get theory rules
        rules = theory_schema.get("execution", {}).get("rules", [])
        
        # Apply each applicable rule
        model_data = model.dict()
        for rule in rules:
            if self._evaluate_condition(rule["condition"], model_data):
                model_data = self._apply_transformation(rule["transformation"], model_data)
        
        # Return updated model
        return model.__class__(**model_data)
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Safely evaluate rule conditions"""
        # Implement safe evaluation logic
        # NOTE: In production, replace eval() with proper parser
        safe_globals = {"entity": type('obj', (object,), data)()}
        try:
            return eval(condition, {"__builtins__": {}}, safe_globals)
        except:
            return False
    
    def _apply_transformation(self, transformation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply theory-specific transformations"""
        # Implement transformation logic
        # This would include domain-specific functions
        if "social_centrality_boost" in transformation:
            data["confidence"] = min(1.0, data["confidence"] * 1.2)
        
        return data
```

## Schema Evolution Strategy

### Version Management
```python
# Each schema maintains version compatibility
class SchemaVersion(Enum):
    V9 = "v9"      # Legacy (deprecated)
    V10 = "v10"    # Current production
    V11 = "v11"    # Development
```

### Migration Strategy
```python
class SchemaMigrator:
    """Handles schema version migrations"""
    
    def migrate_v9_to_v10(self, v9_data: Dict) -> Dict:
        """Migrate from v9 to v10 format"""
        # Handle field renames
        if "process" in v9_data:
            v9_data["execution"] = v9_data.pop("process")
        
        # Add new required fields
        v9_data["version"] = "v10"
        
        return v9_data
```

## Schema Consistency Rules

### 1. Field Naming Consistency
- Use `snake_case` in Pydantic schemas
- Use `camelCase` in Neo4j for JSON compatibility  
- Use `snake_case` in SQLite for SQL conventions

### 2. Type Mapping Rules
```python
# Consistent type mappings across schemas
TYPE_MAPPING = {
    "pydantic": {
        "entity_id": "str",
        "confidence": "float",
        "created_at": "datetime"
    },
    "neo4j": {
        "entity_id": "STRING",
        "confidence": "FLOAT", 
        "created_at": "DATETIME"
    },
    "sqlite": {
        "entity_id": "TEXT",
        "confidence": "REAL",
        "created_at": "TIMESTAMP"
    }
}
```

### 3. Validation Consistency
- All schemas enforce same business rules
- Confidence values: 0.0 ≤ confidence ≤ 1.0
- Entity IDs must be globally unique
- Required fields consistent across all schemas

## Schema Documentation Standards

### Each Schema File Must Include:
1. **Purpose Statement**: Clear explanation of schema role
2. **Version Information**: Current version and changelog
3. **Relationships**: How it relates to other schemas
4. **Examples**: Concrete usage examples
5. **Migration Guide**: How to upgrade from previous versions

### Cross-Schema References:
```markdown
## Schema Relationships

This schema connects to:
- **Pydantic Schema**: Provides runtime validation for [specific objects]
- **Database Schema**: Stored in [specific tables/nodes] 
- **Theory Schema**: Enhanced by [specific rules]

See SchemaManager for transformation details.
```

## Implementation Requirements

### Runtime Schema Management
```python
# All components use SchemaManager for consistency
class BaseTool:
    def __init__(self, service_manager: ServiceManager):
        self.schema_manager = service_manager.schema_manager
    
    def process_entity(self, entity_data: Dict) -> Entity:
        # Always use schema manager for transformations
        entity = self.schema_manager.from_database(entity_data)
        
        # Apply theory rules if applicable
        if self.theory_context:
            entity = self.schema_manager.apply_theory_rules(
                entity, self.theory_context
            )
        
        return entity
```

### Schema Validation Pipeline
```python
# Validation occurs at schema boundaries
def validate_cross_schema_consistency():
    """Ensure all schemas represent the same logical model"""
    
    # Test entity flows through all schemas
    test_entity = create_test_entity()
    
    # Pydantic → Database → Pydantic roundtrip
    db_format = schema_manager.to_database(test_entity)
    reconstructed = schema_manager.from_database(db_format)
    assert test_entity == reconstructed
    
    # Theory transformation consistency
    theory_enhanced = schema_manager.apply_theory_rules(
        test_entity, test_theory_schema
    )
    assert theory_enhanced.id == test_entity.id  # Identity preserved
```

## Benefits of Three-Schema Architecture

### 1. **Separation of Concerns**
- Storage optimization independent of business logic
- Runtime validation separate from persistence
- Theory integration without storage coupling

### 2. **Evolution Flexibility** 
- Database schemas can change for performance
- API contracts remain stable
- Theory schemas evolve with research needs

### 3. **Type Safety**
- Pydantic provides runtime validation
- Database constraints prevent corruption
- Theory schemas ensure domain compliance

### 4. **Performance Optimization**
- Storage schemas optimized for queries
- Runtime schemas optimized for validation
- Theory schemas optimized for execution

## Common Pitfalls to Avoid

### **Don't**: Mix schema purposes
```python
# Wrong - storage concerns in API schema
class Entity(BaseModel):
    neo4j_node_id: int  # Storage detail in API
    sqlite_row_id: int  # Storage detail in API
```

### **Do**: Keep schemas focused
```python
# Right - API schema focused on business logic
class Entity(BaseModel):
    id: str                # Business identifier
    canonical_name: str    # Business concept
    confidence: float      # Business metric
```

### **Don't**: Bypass schema manager
```python
# Wrong - direct transformation
neo4j_data = pydantic_model.dict()  # Loses transformations
```

### **Do**: Use schema manager
```python
# Right - proper transformation
neo4j_data = schema_manager.to_database(pydantic_model)
```

## Future Enhancements

### 1. **Schema Generation**
- Auto-generate database schemas from Pydantic
- Auto-generate theory schemas from domain ontologies
- Validate cross-schema consistency automatically

### 2. **Performance Monitoring**
- Track transformation performance
- Monitor schema validation overhead
- Optimize hot transformation paths

### 3. **Developer Tooling**
- Schema diff tools for version changes
- Visual schema relationship diagrams
- Automated migration generators

The three-schema architecture provides a robust foundation for KGAS data management while maintaining flexibility for evolution and optimization.