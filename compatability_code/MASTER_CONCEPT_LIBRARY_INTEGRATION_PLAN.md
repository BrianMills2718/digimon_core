# Master Concept Library Full Integration Plan

## MISSION: Complete Integration of Master Concept Library into Main GraphRAG System

**Status**: Master Concept Library ✅ CREATED | Main System Integration ❌ MISSING | Runtime Validation ❌ NOT ENFORCED  
**Analysis**: Master concept library exists in isolation within compatability_code but is not integrated into the main workflow  
**Next Phase**: Integrate ontology validation into all tools and enforce semantic correctness

---

## 🚨 CRITICAL INTEGRATION GAPS

### **Gap 1: Directory Structure Mismatch**
- Master concept library created in `compatability_code/src/`
- Main system expects modules in `/home/brian/Digimons/src/`
- Import paths incompatible between directories

### **Gap 2: Tool Integration Missing**
- Only 2 example tool contracts created (T23A_SpacyNER, T27_RelationshipExtractor)
- Main workflow tools don't use OntologyValidator
- No runtime enforcement of semantic validation

### **Gap 3: Data Model Integration Incomplete**
- Entity/Relationship models have placeholder validators
- Actual validation not called during tool execution
- Properties/modifiers fields unused by existing tools

---

## 🎯 COMPLETE INTEGRATION PLAN

### **PHASE 1: Merge Master Concept Library into Main System (Day 1)**

**Goal**: Move master concept library from compatability_code to main src directory

#### **M1: Relocate Ontology Library**
**Task**: Move ontology library to main system location

**Implementation**:

1. **Copy ontology library to main src**:
```bash
# From /home/brian/Digimons directory
cp -r compatability_code/src/ontology_library src/
cp compatability_code/src/core/ontology_validator.py src/core/
```

2. **Update imports in moved files**:
```python
# src/core/ontology_validator.py
# BEFORE:
from ..ontology_library.ontology_service import OntologyService

# AFTER:
from src.ontology_library.ontology_service import OntologyService
```

3. **Verify imports work**:
```python
# Test script
from src.ontology_library.ontology_service import OntologyService
from src.core.ontology_validator import OntologyValidator

ontology = OntologyService()
print(f"✅ Loaded {ontology.get_statistics()['total_concepts']} concepts")
```

#### **M2: Update Main Data Models**
**Task**: Integrate ontology fields into main data models

**Implementation**:

1. **Update src/core/data_models.py**:
```python
# Add imports
from .ontology_validator import OntologyValidator

# Update Entity class
class Entity(BaseObject):
    # ... existing fields ...
    
    # Ontology validation fields
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Properties from master concept library"
    )
    modifiers: Dict[str, str] = Field(
        default_factory=dict,
        description="Modifiers from master concept library"
    )
    
    @model_validator(mode='after')
    def validate_against_ontology(self):
        """Validate entity type and properties against master concept library"""
        validator = OntologyValidator()
        errors = validator.validate_entity(self)
        if errors:
            # Log warnings but don't fail (for backward compatibility)
            import logging
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.warning(f"Ontology validation: {error}")
        return self
```

2. **Update Relationship class similarly**:
```python
class Relationship(BaseObject):
    # ... existing fields ...
    
    properties: Dict[str, Any] = Field(default_factory=dict)
    modifiers: Dict[str, str] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_against_ontology(self):
        """Validate relationship type against master concept library"""
        validator = OntologyValidator()
        errors = validator.validate_relationship(self)
        if errors:
            import logging
            logger = logging.getLogger(__name__)
            for error in errors:
                logger.warning(f"Ontology validation: {error}")
        return self
```

---

### **PHASE 2: Integrate Validation into Tools (Day 2-3)**

**Goal**: Update all entity/relationship extraction tools to use master concepts

#### **T1: Update SpacyNER Tool**
**File**: `src/tools/phase1/t23a_spacy_ner.py`

**Implementation**:

```python
from src.ontology_library.ontology_service import OntologyService
from src.core.ontology_validator import OntologyValidator

class SpacyNER:
    def __init__(self):
        self.ontology = OntologyService()
        self.validator = OntologyValidator()
        
        # Entity type mapping from SpaCy to master concepts
        self.entity_type_mapping = {
            "PERSON": "IndividualActor",
            "ORG": "Institution", 
            "GPE": "SocialGroup",
            "LOC": "Location",  # Note: Need to add Location to master concepts
            "DATE": "temporal_phase",
            "EVENT": "Event"
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities with ontology validation."""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            # Map SpaCy type to master concept type
            entity_type = self.entity_type_mapping.get(ent.label_, "Entity")
            
            # Create entity with ontology fields
            entity = Entity(
                canonical_name=ent.text,
                entity_type=entity_type,
                confidence=0.85,
                quality_tier="medium",
                created_by="t23a_spacy_ner",
                workflow_id=self.workflow_id,
                # Add default properties based on entity type
                properties=self._get_default_properties(entity_type),
                modifiers=self._get_default_modifiers()
            )
            
            # Enrich with ontology defaults
            entity = self.validator.enrich_entity(entity)
            
            entities.append(entity)
        
        return entities
    
    def _get_default_properties(self, entity_type: str) -> Dict[str, Any]:
        """Get default properties for entity type."""
        defaults = {
            "IndividualActor": {
                "source_credibility": 0.7,
                "confidence_level": 0.8
            },
            "Institution": {
                "legitimacy": 0.8,
                "centrality": 0.5
            },
            "SocialGroup": {
                "group_cohesion": 0.6,
                "network_density": 0.4
            }
        }
        return defaults.get(entity_type, {})
    
    def _get_default_modifiers(self) -> Dict[str, str]:
        """Get default modifiers for all entities."""
        return {
            "certainty_level": "somewhat_certain",
            "temporal_phase": "present",
            "source_attribution": "text"
        }
```

#### **T2: Update Relationship Extractor**
**File**: `src/tools/phase1/t27_relationship_extractor.py`

**Implementation**:

```python
class RelationshipExtractor:
    def __init__(self):
        self.ontology = OntologyService()
        self.validator = OntologyValidator()
        
        # Pattern to relationship type mapping
        self.relationship_patterns = {
            r"founded|established|created": "Causes",
            r"leads|manages|heads": "HasAuthorityOver",
            r"works for|employed by": "BelongsTo",
            r"located in|based in": "BelongsTo",
            r"influences|affects": "Influences",
            r"communicates with|talks to": "Communicates",
            r"competes with|rivals": "CompetesWith"
        }
    
    def extract_relationships(self, entities: List[Entity], text: str) -> List[Relationship]:
        """Extract relationships with ontology validation."""
        relationships = []
        
        for pattern, rel_type in self.relationship_patterns.items():
            # Find matches in text
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Extract source and target entities (simplified)
                source, target = self._find_entities_around_match(match, entities, text)
                
                if source and target:
                    # Check domain/range constraints
                    if self.ontology.validate_connection_domain_range(
                        rel_type, source.entity_type, target.entity_type
                    ):
                        relationship = Relationship(
                            source_id=source.id,
                            target_id=target.id,
                            relationship_type=rel_type,
                            confidence=0.75,
                            quality_tier="medium",
                            created_by="t27_relationship_extractor",
                            workflow_id=self.workflow_id,
                            properties=self._get_relationship_properties(rel_type),
                            modifiers=self._get_default_modifiers()
                        )
                        
                        # Enrich with defaults
                        relationship = self.validator.enrich_relationship(relationship)
                        relationships.append(relationship)
        
        return relationships
```

#### **T3: Create Tool Adapter for Backward Compatibility**
**File**: `src/core/ontology_tool_adapter.py`

**Implementation**:

```python
"""Adapter to add ontology validation to existing tools."""

from typing import List, Dict, Any
from src.core.data_models import Entity, Relationship
from src.core.ontology_validator import OntologyValidator

class OntologyToolAdapter:
    """Wraps existing tools to add ontology validation."""
    
    def __init__(self, tool):
        self.tool = tool
        self.validator = OntologyValidator()
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute tool and add ontology validation to results."""
        # Execute original tool
        result = self.tool.execute(*args, **kwargs)
        
        # Add ontology validation to entities
        if "entities" in result and isinstance(result["entities"], list):
            validated_entities = []
            for entity_data in result["entities"]:
                if isinstance(entity_data, dict):
                    # Convert to Entity object if needed
                    entity = Entity(**entity_data) if not isinstance(entity_data, Entity) else entity_data
                    
                    # Enrich with ontology defaults
                    entity = self.validator.enrich_entity(entity)
                    validated_entities.append(entity)
                
            result["entities"] = validated_entities
        
        # Add ontology validation to relationships
        if "relationships" in result and isinstance(result["relationships"], list):
            validated_relationships = []
            for rel_data in result["relationships"]:
                if isinstance(rel_data, dict):
                    relationship = Relationship(**rel_data) if not isinstance(rel_data, Relationship) else rel_data
                    
                    # Enrich with defaults
                    relationship = self.validator.enrich_relationship(relationship)
                    validated_relationships.append(relationship)
            
            result["relationships"] = validated_relationships
        
        return result
```

---

### **PHASE 3: Update Pipeline and Workflows (Day 4)**

**Goal**: Integrate ontology validation into pipeline orchestrator

#### **P1: Update PipelineOrchestrator**
**File**: `src/core/pipeline_orchestrator.py`

**Implementation**:

```python
from src.core.ontology_tool_adapter import OntologyToolAdapter

class PipelineOrchestrator:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = get_logger("core.pipeline_orchestrator")
        self.tools = self._initialize_tools()
        
        # Add ontology validation flag
        self.enable_ontology_validation = config.enable_ontology_validation
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools with optional ontology validation."""
        tools = []
        
        for tool_config in self.config.tools:
            tool = self._create_tool(tool_config)
            
            # Wrap with ontology validation if enabled
            if self.enable_ontology_validation and tool_config.produces_entities_or_relationships:
                tool = OntologyToolAdapter(tool)
            
            tools.append(tool)
        
        return tools
```

#### **P2: Update Workflow Configurations**
**File**: `src/core/tool_factory.py`

**Implementation**:

```python
def create_unified_workflow_config(
    phase: Phase,
    optimization_level: OptimizationLevel,
    workflow_storage_dir: str = "./data/workflows",
    enable_ontology_validation: bool = True  # New parameter
) -> PipelineConfig:
    """Create unified workflow configuration with ontology support."""
    
    config = PipelineConfig(
        phase=phase,
        optimization_level=optimization_level,
        workflow_storage_dir=workflow_storage_dir,
        enable_ontology_validation=enable_ontology_validation,
        # ... other config
    )
    
    return config
```

---

### **PHASE 4: Testing and Validation (Day 5)**

**Goal**: Ensure ontology validation works end-to-end

#### **Test Script**: `tests/integration/test_ontology_integration_e2e.py`

```python
import pytest
from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
from src.ontology_library.ontology_service import OntologyService

class TestOntologyIntegrationE2E:
    def test_workflow_with_ontology_validation(self):
        """Test complete workflow with ontology validation enabled."""
        # Create workflow with ontology validation
        workflow = VerticalSliceWorkflow(enable_ontology_validation=True)
        
        # Test document
        test_content = "Elon Musk founded Tesla Inc. in California."
        
        # Execute workflow
        result = workflow.execute_pdf_workflow(
            document_paths=["test.txt"],
            queries=["Who founded Tesla?"]
        )
        
        # Verify entities have ontology fields
        entities = result.get("entities", [])
        assert len(entities) > 0
        
        for entity in entities:
            assert "properties" in entity
            assert "modifiers" in entity
            assert entity.get("entity_type") in ["IndividualActor", "Institution", "Location"]
        
        # Verify relationships use master concepts
        relationships = result.get("relationships", [])
        for rel in relationships:
            assert rel.get("relationship_type") in ["Causes", "BelongsTo", "HasAuthorityOver"]
            assert "properties" in rel
            assert "modifiers" in rel
    
    def test_ontology_statistics(self):
        """Verify ontology is loaded and accessible."""
        ontology = OntologyService()
        stats = ontology.get_statistics()
        
        assert stats["total_concepts"] >= 88
        assert stats["entities"] >= 16
        assert stats["connections"] >= 23
```

---

## 🎯 SUCCESS CRITERIA

### **Phase 1 Success**:
- [ ] Ontology library copied to main src directory
- [ ] All imports updated and working
- [ ] Data models include ontology fields with validation

### **Phase 2 Success**:
- [ ] SpacyNER uses master concept entity types
- [ ] RelationshipExtractor uses master concept relationships
- [ ] Tool adapter provides backward compatibility

### **Phase 3 Success**:
- [ ] PipelineOrchestrator supports ontology validation flag
- [ ] Workflows can enable/disable ontology validation
- [ ] All tools wrapped when validation enabled

### **Phase 4 Success**:
- [ ] End-to-end test passes with ontology validation
- [ ] Entities have proper types from master concepts
- [ ] Relationships respect domain/range constraints

### **Verification Commands**:
```bash
# Test ontology import
python -c "from src.ontology_library.ontology_service import OntologyService; print('✅')"

# Test entity validation
python -c "from src.core.data_models import Entity; e = Entity(entity_type='IndividualActor', canonical_name='Test'); print('✅')"

# Run integration test
pytest tests/integration/test_ontology_integration_e2e.py -v

# Check concept usage
grep -r "IndividualActor\|Institution\|BelongsTo\|Influences" src/tools/
```

This plan provides complete integration of the master concept library into the main GraphRAG system with validation at every level.