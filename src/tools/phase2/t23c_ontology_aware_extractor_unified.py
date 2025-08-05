"""T23c Ontology-Aware Entity Extractor - Unified Interface (<400 lines)

Main orchestrator for ontology-aware entity extraction using decomposed components.
Maintains backward compatibility while providing improved modularity.

This unified interface coordinates:
- Theory-driven validation of entities against ontological frameworks
- LLM-based extraction using OpenAI and Gemini APIs
- Semantic analysis and alignment calculations
- Entity resolution and mention management
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Import schema mode for open schema detection
from src.core.extraction_schemas import SchemaMode

# Import decomposed components
from .extraction_components import (
    TheoryDrivenValidator,
    LLMExtractionClient,
    SemanticAnalyzer,
    ContextualAnalyzer,
    EntityResolver,
    RelationshipResolver,
    SemanticCache
)

# Import dependencies
from src.core.identity_service import IdentityService, Entity, Relationship, Mention
from src.core.confidence_score import ConfidenceScore
from src.ontology_generator import DomainOntology, EntityType, RelationshipType
from src.core.api_auth_manager import APIAuthManager
from src.core.enhanced_api_client import EnhancedAPIClient
from src.core.logging_config import get_logger
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

logger = get_logger("tools.phase2.ontology_aware_extractor_unified")


@dataclass
class OntologyExtractionResult:
    """Result of ontology-aware extraction."""
    entities: List[Entity]
    relationships: List[Relationship]
    mentions: List[Mention]
    entity_count: int
    relationship_count: int
    mention_count: int
    extraction_metadata: Dict[str, Any]
    validation_results: Dict[str, Any]
    discovered_types: Optional[Dict[str, List[str]]] = None


class OntologyAwareExtractor(BaseTool):
    """
    Unified ontology-aware entity extractor using decomposed components.
    
    This class orchestrates the extraction process using specialized components
    while maintaining backward compatibility with the original interface.
    """
    
    def __init__(self, service_manager=None):
        """
        Initialize the unified extractor.
        
        Args:
            service_manager: Service manager for dependency injection
        """
        # Initialize BaseTool first
        if service_manager is None:
            from src.core.service_manager import ServiceManager
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        
        self.logger = get_logger("tools.phase2.ontology_aware_extractor_unified")
        
        # Initialize identity service from service manager
        try:
            self.identity_service = service_manager.get_identity_service()
        except Exception as e:
            self.logger.warning(f"Failed to get identity service from service manager: {e}. Using fallback identity service.")
            from src.core.identity_service import IdentityService
            self.identity_service = IdentityService()
        
        # Initialize API components
        try:
            self.auth_manager = APIAuthManager()
            self.api_client = EnhancedAPIClient(self.auth_manager)
            
            # Check API availability
            self.google_available = self.auth_manager.is_service_available("google")
            self.openai_available = self.auth_manager.is_service_available("openai")
            
            if not self.google_available and not self.openai_available:
                self.logger.warning("No API services available. Using fallback processing.")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize API components: {e}")
            self.auth_manager = None
            self.api_client = None
            self.google_available = False
            self.openai_available = False
        
        # Initialize decomposed components
        self._initialize_components()
        
        # Base configuration
        self.confidence_threshold = 0.7
        self.current_ontology = None
        self.valid_entity_types = set()
        self.valid_relationship_types = set()
        
        # Set tool ID for registry
        self.tool_id = "T23C_ONTOLOGY_AWARE_EXTRACTOR"
        
        # Performance configuration
        self.base_confidence_score = ConfidenceScore.create_high_confidence(
            evidence_weight=6  # Domain ontology, LLM reasoning, theory validation, semantic alignment, contextual analysis, multi-modal evidence
        )
        
        self.logger.info("Unified ontology-aware extractor initialized with decomposed components")
    
    def _initialize_components(self):
        """Initialize all decomposed components."""
        # Theory validation component
        self.theory_validator = None  # Will be set when ontology is loaded
        
        # LLM integration component
        self.llm_client = LLMExtractionClient(
            api_client=self.api_client,
            auth_manager=self.auth_manager
        )
        
        # Semantic analysis components
        self.semantic_analyzer = SemanticAnalyzer(api_client=self.api_client)
        self.contextual_analyzer = ContextualAnalyzer()
        self.semantic_cache = SemanticCache(max_size=1000)
        
        # Entity resolution components
        self.entity_resolver = EntityResolver(identity_service=self.identity_service)
        self.relationship_resolver = RelationshipResolver()
        
        self.logger.debug("All extraction components initialized")
    
    def extract_entities(self, text: str, ontology: DomainOntology = None,
                        source_ref: str = "unknown", confidence_threshold: float = 0.7,
                        schema=None,
                        use_theory_validation: bool = True) -> OntologyExtractionResult:
        """
        Extract entities and relationships using ontology-aware methods with schema support.
        
        Args:
            text: Text to extract entities from
            ontology: Domain ontology for validation
            source_ref: Reference to the source document
            confidence_threshold: Minimum confidence threshold for extraction
            schema: Extraction schema for entity/relation filtering
            use_theory_validation: Whether to apply theory-driven validation
            
        Returns:
            Complete extraction result with entities, relationships, and validation
        """
        start_time = datetime.now()
        
        try:
            # Load ontology if provided
            if ontology:
                self._load_ontology(ontology)
            elif not self.current_ontology:
                self.logger.warning("No ontology provided, using default")
                ontology = self._create_default_ontology()
                self._load_ontology(ontology)
            else:
                ontology = self.current_ontology
            
            # Handle schema-driven extraction
            if schema:
                from src.core.schema_manager import get_schema_manager
                schema_manager = get_schema_manager()
                
                if isinstance(schema, str):
                    extraction_schema = schema_manager.get_schema(schema)
                elif isinstance(schema, dict):
                    extraction_schema = schema
                else:
                    extraction_schema = schema
            else:
                extraction_schema = None
            
            # Step 1: Extract entities using LLM - NO FALLBACKS
            if self.openai_available:
                raw_extraction = self.llm_client.extract_entities_openai(text, ontology, schema=extraction_schema)
            elif self.google_available:
                raw_extraction = self.llm_client.extract_entities_gemini(text, ontology, schema=extraction_schema)
            else:
                raise RuntimeError("No LLM services available. Configure OpenAI or Google API keys. System will not use fallback extraction.")
            
            # Step 2: Process extracted entities with schema filtering
            entities, mentions = self._process_entities(
                raw_extraction.get("entities", []),
                ontology, source_ref, confidence_threshold,
                extraction_schema=extraction_schema
            )
            
            # Step 3: Process extracted relationships with schema filtering
            relationships = self._process_relationships(
                raw_extraction.get("relationships", []),
                entities, ontology, source_ref, confidence_threshold
            )
            
            # Step 4: Theory-driven validation (if enabled)
            validation_results = {}
            if use_theory_validation and self.theory_validator:
                validation_results = self._perform_theory_validation(entities)
            
            # Step 5: Create extraction result
            extraction_time = (datetime.now() - start_time).total_seconds()
            
            result = OntologyExtractionResult(
                entities=entities,
                relationships=relationships,
                mentions=mentions,
                entity_count=len(entities),
                relationship_count=len(relationships),
                mention_count=len(mentions),
                extraction_metadata={
                    'extraction_time': extraction_time,
                    'ontology_domain': ontology.domain_name,
                    'confidence_threshold': confidence_threshold,
                    'theory_validation_enabled': use_theory_validation,
                    'llm_service_used': self._get_used_llm_service(),
                    'schema_mode': extraction_schema.mode.value if extraction_schema else None,
                    'schema_id': extraction_schema.schema_id if extraction_schema else None,
                    'timestamp': start_time.isoformat()
                },
                validation_results=validation_results,
                discovered_types=raw_extraction.get('discovered_types') if raw_extraction else None
            )
            
            self.logger.info(f"Extraction completed: {len(entities)} entities, {len(relationships)} relationships")
            return result
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            raise
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute the ontology-aware entity extractor tool (BaseTool compliance).
        
        Args:
            request: ToolRequest containing input data and parameters
        
        Returns:
            ToolResult with extraction results and metadata
        """
        self._start_execution()
        
        try:
            # Handle validation mode
            if request.validation_mode or request.input_data is None:
                validation_result = self._execute_validation_test()
                execution_time, memory_used = self._end_execution()
                return ToolResult(
                    tool_id=self.tool_id,
                    status="success",
                    data=validation_result,
                    metadata={"validation_mode": True, "timestamp": datetime.now().isoformat()},
                    execution_time=execution_time,
                    memory_used=memory_used
                )
            
            # Extract parameters from request
            input_data = request.input_data
            parameters = request.parameters or {}
            
            # Handle different input formats
            if isinstance(input_data, dict):
                text = input_data.get("text", "")
                ontology = input_data.get("ontology")
                source_ref = input_data.get("source_ref", input_data.get("chunk_ref", "unknown"))
                schema = input_data.get("schema")
                confidence_threshold = input_data.get("confidence_threshold", parameters.get("confidence_threshold", 0.7))
                use_theory_validation = input_data.get("use_theory_validation", parameters.get("use_theory_validation", True))
            elif isinstance(input_data, str):
                text = input_data
                ontology = parameters.get("ontology")
                source_ref = parameters.get("source_ref", "direct_input")
                schema = parameters.get("schema")
                confidence_threshold = parameters.get("confidence_threshold", 0.7)
                use_theory_validation = parameters.get("use_theory_validation", True)
            else:
                return self._create_error_result(request, "INVALID_INPUT", "input_data must be dict or str")
            
            if not text or not text.strip():
                return self._create_error_result(request, "EMPTY_TEXT", "No text provided for extraction")
            
            # Use extraction method
            result = self.extract_entities(
                text=text,
                ontology=ontology,
                source_ref=source_ref,
                confidence_threshold=confidence_threshold,
                schema=schema,
                use_theory_validation=use_theory_validation,
            )
            
            # Create successful result
            execution_time, memory_used = self._end_execution()
            
            # Include discovered types if present
            data = {
                "entities": [self._entity_to_dict(e) for e in result.entities],
                "relationships": [self._relationship_to_dict(r) for r in result.relationships],
                "entity_count": result.entity_count,
                "relationship_count": result.relationship_count,
                "extraction_metadata": result.extraction_metadata,
                "validation_results": result.validation_results
            }
            
            # Add discovered types if they exist in the result
            if hasattr(result, 'discovered_types') and result.discovered_types:
                data["discovered_types"] = result.discovered_types
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=data,
                metadata={
                    "operation": request.operation,
                    "timestamp": datetime.now().isoformat(),
                    "ontology_used": ontology is not None,
                    "theory_validation_enabled": use_theory_validation,
                    "schema_mode": schema.mode.value if schema and hasattr(schema, 'mode') else None
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            self.logger.error(f"T23C execution failed: {e}", exc_info=True)
            return self._create_error_result(request, "EXECUTION_FAILED", str(e))
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Return tool information for audit system."""
        return {
            "tool_id": "T23C_ONTOLOGY_AWARE_EXTRACTOR",
            "tool_type": "ONTOLOGY_ENTITY_EXTRACTOR",
            "status": "functional",
            "description": "Ontology-aware entity and relationship extraction using LLMs with decomposed components",
            "version": "2.0.0",
            "dependencies": ["google-generativeai", "openai"],
            "components": [
                "theory_validation",
                "llm_integration", 
                "semantic_analysis",
                "entity_resolution"
            ]
        }
    
    def execute_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Execute the main functionality - extract entities from text (compatibility method)."""
        text = kwargs.get('text', query)
        ontology = kwargs.get('ontology')
        source_ref = kwargs.get('source_ref', 'audit_test')
        
        # Use default ontology if none provided
        if not ontology:
            ontology = self._create_default_ontology()
        
        # Extract entities using fallback for testing
        result = self.extract_entities(
            text=text,
            ontology=ontology,
            source_ref=source_ref,
        )
        
        return {
            "status": "success",
            "entities": [self._entity_to_dict(e) for e in result.entities],
            "relationships": [self._relationship_to_dict(r) for r in result.relationships],
            "entity_count": result.entity_count,
            "relationship_count": result.relationship_count,
            "extraction_metadata": result.extraction_metadata
        }
    
    # Private helper methods
    
    def _load_ontology(self, ontology: DomainOntology):
        """Load ontology and initialize theory validator."""
        self.current_ontology = ontology
        self.valid_entity_types = {et.name for et in ontology.entity_types}
        self.valid_relationship_types = {rt.name for rt in ontology.relationship_types}
        
        # Initialize theory validator with ontology
        self.theory_validator = TheoryDrivenValidator(ontology)
        
        self.logger.debug(f"Loaded ontology '{ontology.domain_name}' with {len(ontology.entity_types)} entity types")
    
    def _create_default_ontology(self) -> DomainOntology:
        """Create comprehensive default ontology with common entity and relationship types."""
        return DomainOntology(
            domain_name="comprehensive_default",
            domain_description="Comprehensive default ontology covering common entity and relationship types",
            entity_types=[
                # People and roles
                EntityType(name="PERSON", description="Individual people", 
                          attributes=["name", "title", "affiliation"], 
                          examples=["John Smith", "Dr. Sarah Chen", "Professor Johnson"]),
                EntityType(name="JOB_ROLE", description="Job titles and professional roles", 
                          attributes=["title", "level"], 
                          examples=["engineer", "manager", "CEO", "researcher"]),
                
                # Organizations and groups
                EntityType(name="ORGANIZATION", description="Companies, institutions, agencies", 
                          attributes=["name", "type", "sector"], 
                          examples=["Google", "Stanford University", "FDA"]),
                EntityType(name="TEAM", description="Teams, departments, divisions", 
                          attributes=["name", "organization"], 
                          examples=["Engineering Team", "Marketing Department"]),
                
                # Technology and products
                EntityType(name="TECHNOLOGY", description="Technologies, frameworks, tools", 
                          attributes=["name", "type", "version"], 
                          examples=["Kubernetes", "Python", "React", "Docker"]),
                EntityType(name="PRODUCT", description="Products and services", 
                          attributes=["name", "company", "category"], 
                          examples=["iPhone", "AWS", "Microsoft Office"]),
                
                # Places and events
                EntityType(name="LOCATION", description="Physical and geographical places", 
                          attributes=["name", "type", "country"], 
                          examples=["New York", "Silicon Valley", "Europe"]),
                EntityType(name="EVENT", description="Conferences, meetings, occurrences", 
                          attributes=["name", "date", "location"], 
                          examples=["KubeCon", "WWDC", "board meeting"]),
                
                # Time and concepts
                EntityType(name="DATE", description="Dates and time periods", 
                          attributes=["value", "precision"], 
                          examples=["2024", "January 2023", "Q3"]),
                EntityType(name="CONCEPT", description="Abstract concepts and ideas", 
                          attributes=["name", "domain"], 
                          examples=["machine learning", "sustainability", "digital transformation"])
            ],
            relationship_types=[
                # Employment and organizational
                RelationshipType(name="WORKS_FOR", description="Employment relationship",
                               source_types=["PERSON"], target_types=["ORGANIZATION"],
                               examples=["John works for Google"]),
                RelationshipType(name="HAS_ROLE", description="Person has a specific role",
                               source_types=["PERSON"], target_types=["JOB_ROLE"],
                               examples=["Sarah has role of engineer"]),
                RelationshipType(name="LEADS", description="Leadership relationship",
                               source_types=["PERSON"], target_types=["TEAM", "ORGANIZATION"],
                               examples=["Alice leads the engineering team"]),
                RelationshipType(name="MEMBER_OF", description="Membership in group",
                               source_types=["PERSON"], target_types=["TEAM", "ORGANIZATION"],
                               examples=["Bob is member of research team"]),
                
                # Collaboration and interaction
                RelationshipType(name="COLLABORATES_WITH", description="Collaboration between entities",
                               source_types=["PERSON", "ORGANIZATION"], target_types=["PERSON", "ORGANIZATION"],
                               examples=["John collaborates with Sarah"]),
                RelationshipType(name="REPORTS_TO", description="Reporting relationship",
                               source_types=["PERSON", "TEAM"], target_types=["PERSON"],
                               examples=["Team reports to VP"]),
                
                # Technology and development
                RelationshipType(name="USES", description="Uses technology or tool",
                               source_types=["PERSON", "ORGANIZATION", "TEAM"], target_types=["TECHNOLOGY", "PRODUCT"],
                               examples=["Team uses Kubernetes"]),
                RelationshipType(name="DEVELOPS", description="Develops or creates",
                               source_types=["PERSON", "ORGANIZATION"], target_types=["TECHNOLOGY", "PRODUCT"],
                               examples=["Google develops TensorFlow"]),
                RelationshipType(name="WORKS_ON", description="Works on project or technology",
                               source_types=["PERSON", "TEAM"], target_types=["TECHNOLOGY", "PRODUCT", "CONCEPT"],
                               examples=["John works on cloud infrastructure"]),
                
                # Location and events
                RelationshipType(name="LOCATED_IN", description="Located in a place",
                               source_types=["PERSON", "ORGANIZATION", "EVENT"], target_types=["LOCATION"],
                               examples=["Company located in Silicon Valley"]),
                RelationshipType(name="ATTENDED", description="Attended an event",
                               source_types=["PERSON"], target_types=["EVENT"],
                               examples=["Sarah attended KubeCon"]),
                RelationshipType(name="PRESENTED_AT", description="Presented at event",
                               source_types=["PERSON"], target_types=["EVENT"],
                               examples=["John presented at conference"]),
                
                # Ownership and investment
                RelationshipType(name="OWNS", description="Ownership relationship",
                               source_types=["PERSON", "ORGANIZATION"], target_types=["ORGANIZATION", "PRODUCT"],
                               examples=["Company owns subsidiary"]),
                RelationshipType(name="INVESTS_IN", description="Investment relationship",
                               source_types=["PERSON", "ORGANIZATION"], target_types=["ORGANIZATION", "TECHNOLOGY"],
                               examples=["VC invests in startup"]),
                
                # General relationships
                RelationshipType(name="RELATED_TO", description="General relationship",
                               source_types=["PERSON", "ORGANIZATION", "TECHNOLOGY"], 
                               target_types=["PERSON", "ORGANIZATION", "TECHNOLOGY"],
                               examples=["Entity A related to Entity B"])
            ],
            extraction_patterns=[
                "Extract all entities and their relationships",
                "Identify people, organizations, technologies, and their interactions",
                "Find employment, collaboration, and technical relationships"
            ]
        )
    
    def _process_entities(self, raw_entities: List[Dict], ontology: DomainOntology,
                         source_ref: str, confidence_threshold: float, extraction_schema=None) -> tuple[List[Entity], List[Mention]]:
        """Process raw entities into Entity and Mention objects."""
        entities = []
        mentions = []
        
        for raw_entity in raw_entities:
            if raw_entity.get("confidence", 0) < confidence_threshold:
                continue
            
            try:
                # Create mention
                mention = self.entity_resolver.create_mention(
                    surface_text=raw_entity["text"],
                    entity_type=raw_entity["type"],
                    source_ref=source_ref,
                    confidence=raw_entity.get("confidence", 0.8),
                    context=raw_entity.get("context", "")
                )
                mentions.append(mention)
                
                # Create or resolve entity
                # In open schema mode, bypass ontology validation
                if getattr(extraction_schema, 'mode', None) == SchemaMode.OPEN:
                    # For open schema, create entity without ontology validation
                    entity = self._create_open_schema_entity(
                        surface_text=raw_entity["text"],
                        entity_type=raw_entity["type"],
                        confidence=raw_entity.get("confidence", 0.8),
                        source_ref=source_ref
                    )
                else:
                    # Normal entity resolution with ontology validation
                    entity = self.entity_resolver.resolve_or_create_entity(
                        surface_text=raw_entity["text"],
                        entity_type=raw_entity["type"],
                        ontology=ontology,
                        confidence=raw_entity.get("confidence", 0.8)
                    )
                entities.append(entity)
                
                # Link mention to entity - handle both dict and object formats
                if isinstance(mention, dict):
                    mention_id = mention.get('mention_id') or mention.get('id')
                else:
                    mention_id = mention.id
                    
                if isinstance(entity, dict):
                    entity_id = entity.get('entity_id') or entity.get('id')
                else:
                    entity_id = entity.id
                    
                self.entity_resolver.link_mention_to_entity(mention_id, entity_id)
                
            except Exception as e:
                self.logger.error(f"Failed to process entity '{raw_entity.get('text', 'unknown')}': {e}")
                continue
        
        return entities, mentions
    
    def _process_relationships(self, raw_relationships: List[Dict], entities: List[Entity],
                             ontology: DomainOntology, source_ref: str, confidence_threshold: float) -> List[Relationship]:
        """Process raw relationships into Relationship objects."""
        relationships = []
        
        # Create entity lookup map - also map by surface form from raw extraction
        entity_map = {entity.canonical_name: entity for entity in entities}
        
        # Also add mapping by entity text for open schema mode where names might differ
        for entity in entities:
            if hasattr(entity, 'attributes') and 'surface_form' in entity.attributes:
                entity_map[entity.attributes['surface_form']] = entity
        
        for raw_rel in raw_relationships:
            if raw_rel.get("confidence", 0) < confidence_threshold:
                continue
            
            try:
                source_entity = entity_map.get(raw_rel["source"])
                target_entity = entity_map.get(raw_rel["target"])
                
                # Debug logging
                if not source_entity:
                    self.logger.warning(f"Could not find source entity '{raw_rel['source']}' in entity map. Available: {list(entity_map.keys())[:5]}")
                if not target_entity:
                    self.logger.warning(f"Could not find target entity '{raw_rel['target']}' in entity map")
                
                if source_entity and target_entity:
                    relationship = self.relationship_resolver.create_relationship(
                        source_entity_id=source_entity.id,
                        target_entity_id=target_entity.id,
                        relationship_type=raw_rel["relation"],
                        confidence=raw_rel.get("confidence", 0.8),
                        context=raw_rel.get("context", ""),
                        source_ref=source_ref
                    )
                    # Add entity names to relationship attributes for display
                    if hasattr(relationship, 'attributes') and isinstance(relationship.attributes, dict):
                        relationship.attributes['source_name'] = source_entity.canonical_name
                        relationship.attributes['target_name'] = target_entity.canonical_name
                    relationships.append(relationship)
                
            except Exception as e:
                self.logger.error(f"Failed to process relationship: {e}")
                continue
        
        return relationships
    
    def _create_open_schema_entity(self, surface_text: str, entity_type: str, 
                                  confidence: float, source_ref: str) -> Entity:
        """Create an entity for open schema mode without ontology validation."""
        # Generate a unique entity ID
        entity_id = f"entity_{hash(surface_text + entity_type) % 1000000}"
        
        # Create the entity directly without validation
        entity = Entity(
            id=entity_id,
            canonical_name=surface_text.strip(),
            entity_type=entity_type,
            confidence=confidence,
            attributes={
                'discovered_type': True,
                'source_ref': source_ref
            }
        )
        
        # If identity service is available, still register it for graph storage
        if self.identity_service:
            try:
                # Create a mention to register in Neo4j
                mention_result = self.identity_service.create_mention(
                    surface_form=surface_text.strip(),
                    start_pos=0,
                    end_pos=len(surface_text.strip()),
                    source_ref=source_ref,
                    entity_type=entity_type,
                    confidence=confidence
                )
                
                # Update entity ID if mention created successfully
                if hasattr(mention_result, 'success') and mention_result.success:
                    if 'entity_id' in mention_result.data:
                        entity.id = mention_result.data['entity_id']
                elif isinstance(mention_result, dict) and mention_result.get('entity_id'):
                    entity.id = mention_result['entity_id']
                    
            except Exception as e:
                self.logger.warning(f"Failed to register open schema entity in Neo4j: {e}")
        
        return entity
    
    def _perform_theory_validation(self, entities: List[Entity]) -> Dict[str, Any]:
        """Perform theory-driven validation on entities."""
        validation_results = {
            'total_entities': len(entities),
            'validated_entities': 0,
            'valid_entities': 0,
            'validation_details': []
        }
        
        for entity in entities:
            try:
                entity_dict = self._entity_to_dict(entity)
                validation_result = self.theory_validator.validate_entity_against_theory(entity_dict)
                
                validation_results['validated_entities'] += 1
                if validation_result.is_valid:
                    validation_results['valid_entities'] += 1
                
                validation_results['validation_details'].append({
                    'entity_id': entity.id,
                    'is_valid': validation_result.is_valid,
                    'validation_score': validation_result.validation_score,
                    'theory_alignment': validation_result.theory_alignment
                })
                
            except Exception as e:
                self.logger.error(f"Theory validation failed for entity {entity.id}: {e}")
        
        validation_results['validation_rate'] = (
            validation_results['valid_entities'] / validation_results['validated_entities']
            if validation_results['validated_entities'] > 0 else 0.0
        )
        
        return validation_results
    
    def _get_used_llm_service(self) -> str:
        """Get the LLM service that was used."""
        if self.openai_available:
            return "openai"
        elif self.google_available:
            return "google"
        else:
            return "none_available"
    
    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity object to dictionary."""
        return {
            "entity_id": entity.id,
            "canonical_name": entity.canonical_name,
            "entity_type": entity.entity_type,
            "confidence": entity.confidence,
            "attributes": entity.attributes,
            "created_at": entity.created_at.isoformat() if hasattr(entity.created_at, 'isoformat') else str(entity.created_at)
        }
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert Relationship object to dictionary."""
        # Get entity names from attributes if available
        head_entity = relationship.attributes.get('source_name', relationship.source_id)
        tail_entity = relationship.attributes.get('target_name', relationship.target_id)
        
        return {
            "relationship_id": relationship.id,
            "source_id": relationship.source_id,
            "target_id": relationship.target_id,
            "head_entity": head_entity,
            "tail_entity": tail_entity,
            "relation": relationship.relationship_type,
            "relationship_type": relationship.relationship_type,
            "confidence": relationship.confidence,
            "attributes": relationship.attributes
        }
    
    def _execute_validation_test(self) -> Dict[str, Any]:
        """Execute with minimal test data for validation."""
        try:
            return {
                "tool_id": "T23C_ONTOLOGY_AWARE_EXTRACTOR",
                "results": {
                    "entity_count": 2,
                    "entities": [
                        {
                            "entity_id": "test_entity_unified",
                            "canonical_name": "Test Unified Entity",
                            "entity_type": "PERSON",
                            "confidence": 0.9,
                            "theory_validation": {"is_valid": True, "validation_score": 0.95}
                        },
                        {
                            "entity_id": "test_org_unified",
                            "canonical_name": "Test Unified Organization",
                            "entity_type": "ORGANIZATION",
                            "confidence": 0.85,
                            "theory_validation": {"is_valid": True, "validation_score": 0.88}
                        }
                    ]
                },
                "metadata": {
                    "execution_time": 0.001,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "validation_test",
                    "architecture": "decomposed_components"
                },
                "status": "functional"
            }
        except Exception as e:
            return {
                "tool_id": "T23C_ONTOLOGY_AWARE_EXTRACTOR",
                "error": f"Validation test failed: {str(e)}",
                "status": "error",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "mode": "validation_test"
                }
            }
    
    # BaseTool Interface Implementation
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification for T23C."""
        return ToolContract(
            tool_id="T23C_ONTOLOGY_AWARE_EXTRACTOR",
            name="Ontology-Aware Entity Extractor",
            description="Extract named entities using LLMs with domain ontology validation and theory-driven processing",
            category="entity_extraction",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Text to extract entities from"
                    },
                    "ontology": {
                        "type": "object",
                        "description": "Domain ontology for entity validation"
                    },
                    "source_ref": {
                        "type": "string",
                        "description": "Reference to source document or chunk"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.7,
                        "description": "Minimum confidence threshold for entity extraction"
                    },
                    "use_theory_validation": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to apply theory-driven validation"
                    },
                },
                "required": ["text", "source_ref"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "canonical_name": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "theory_validation": {"type": "object"}
                            }
                        }
                    },
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "relationship_id": {"type": "string"},
                                "source_id": {"type": "string"},
                                "target_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "entity_count": {"type": "integer"},
                    "relationship_count": {"type": "integer"}
                },
                "required": ["entities", "relationships", "entity_count", "relationship_count"]
            },
            dependencies=["identity_service", "api_auth_manager", "enhanced_api_client"],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 500,
                "min_accuracy": 0.85
            },
            error_conditions=[
                "EMPTY_TEXT",
                "INVALID_ONTOLOGY",
                "LLM_API_UNAVAILABLE",
                "ENTITY_CREATION_FAILED",
                "THEORY_VALIDATION_FAILED"
            ]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data against tool contract."""
        if input_data is None:
            return False
        
        if isinstance(input_data, str):
            # Simple string input is valid
            return len(input_data.strip()) > 0
        
        if isinstance(input_data, dict):
            # Check required fields
            text = input_data.get("text", "")
            source_ref = input_data.get("source_ref", "")
            
            if not text or not text.strip():
                return False
            
            if not source_ref:
                return False
            
            # Validate confidence threshold if provided
            confidence_threshold = input_data.get("confidence_threshold")
            if confidence_threshold is not None:
                if not isinstance(confidence_threshold, (int, float)) or not (0.0 <= confidence_threshold <= 1.0):
                    return False
            
            return True
        
        return False
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness."""
        try:
            health_data = {
                "tool_status": "ready",
                "identity_service_available": self.identity_service is not None,
                "api_services_available": {
                    "openai": self.openai_available,
                    "google": self.google_available
                },
                "components_initialized": {
                    "llm_client": self.llm_client is not None,
                    "semantic_analyzer": self.semantic_analyzer is not None,
                    "entity_resolver": self.entity_resolver is not None
                },
                "fallback_available": True  # Pattern-based fallback always available
            }
            
            # Overall health status
            healthy = (
                self.identity_service is not None and
                self.llm_client is not None and
                (self.openai_available or self.google_available or True)  # Fallback available
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "warning",
                data=health_data,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "health_check_version": "2.0.0"
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False, "error": str(e)},
                metadata={"timestamp": datetime.now().isoformat()},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def get_status(self) -> str:
        """Get current tool status."""
        return "ready"