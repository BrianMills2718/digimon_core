"""
Test Fixtures for Service Testing

Provides standardized test fixtures and data generators for comprehensive
testing of all service types and integration scenarios.
"""

import logging
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import random

from ..core.interfaces.service_interfaces import ServiceResponse
from .mock_factory import MockServiceFactory, MockServiceConfig, MockBehavior
from .config import get_testing_config

logger = logging.getLogger(__name__)


@dataclass
class FixtureDocument:
    """Test document fixture"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    document_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if 'created_at' not in self.metadata:
            self.metadata['created_at'] = datetime.now().isoformat()


@dataclass
class FixtureEntity:
    """Test entity fixture"""
    entity_id: str
    canonical_name: str
    entity_type: str = "UNKNOWN"
    confidence: float = 0.8
    properties: Dict[str, Any] = field(default_factory=dict)
    mentions: List[str] = field(default_factory=list)


@dataclass
class TestMention:
    """Test mention fixture"""
    mention_id: str
    surface_form: str
    start_pos: int
    end_pos: int
    source_ref: str
    entity_type: Optional[str] = None
    confidence: float = 0.8
    context: str = ""


@dataclass
class TestRelationship:
    """Test relationship fixture"""
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: str
    confidence: float = 0.8
    properties: Dict[str, Any] = field(default_factory=dict)


class ServiceFixtures:
    """Factory for creating standardized test fixtures"""
    
    def __init__(self) -> None:
        self.created_fixtures: Dict[str, List[Any]] = {
            'documents': [],
            'entities': [], 
            'mentions': [],
            'relationships': []
        }
    
    def create_test_document(self, content: Optional[str] = None, **metadata: Any) -> FixtureDocument:
        """Create a test document with realistic content"""
        if content is None:
            content = self._generate_sample_content()
        
        doc = FixtureDocument(
            content=content,
            metadata={
                'source': 'test_fixture',
                'language': 'en',
                'word_count': len(content.split()),
                **metadata
            }
        )
        
        self.created_fixtures['documents'].append(doc)
        logger.debug(f"Created test document {doc.document_id} with {len(content)} characters")
        return doc
    
    def create_test_entity(self, canonical_name: Optional[str] = None, 
                          entity_type: str = "PERSON") -> FixtureEntity:
        """Create a test entity with realistic properties"""
        if canonical_name is None:
            canonical_name = self._generate_entity_name(entity_type)
        
        entity = FixtureEntity(
            entity_id=f"entity_{uuid.uuid4().hex[:8]}",
            canonical_name=canonical_name,
            entity_type=entity_type,
            confidence=random.uniform(0.7, 0.95),
            properties={
                'created_at': datetime.now().isoformat(),
                'source': 'test_fixture',
                'verified': random.choice([True, False])
            }
        )
        
        self.created_fixtures['entities'].append(entity)
        logger.debug(f"Created test entity {entity.entity_id}: {canonical_name}")
        return entity
    
    def create_test_mention(self, surface_form: Optional[str] = None, 
                           source_ref: str = "test_doc") -> TestMention:
        """Create a test mention with realistic positioning"""
        if surface_form is None:
            surface_form = random.choice([
                "John Smith", "Microsoft", "New York", "artificial intelligence",
                "United Nations", "climate change", "quantum computing"
            ])
        
        start_pos = random.randint(0, 100)
        end_pos = start_pos + len(surface_form)
        
        mention = TestMention(
            mention_id=f"mention_{uuid.uuid4().hex[:8]}",
            surface_form=surface_form,
            start_pos=start_pos,
            end_pos=end_pos,
            source_ref=source_ref,
            confidence=random.uniform(0.6, 0.9),
            context=f"This is a test context containing {surface_form} as an example."
        )
        
        self.created_fixtures['mentions'].append(mention)
        logger.debug(f"Created test mention {mention.mention_id}: {surface_form}")
        return mention
    
    def create_test_relationship(self, source_id: Optional[str] = None, target_id: Optional[str] = None,
                               relationship_type: str = "RELATED_TO") -> TestRelationship:
        """Create a test relationship between entities"""
        if source_id is None:
            source_id = f"entity_{uuid.uuid4().hex[:8]}"
        if target_id is None:
            target_id = f"entity_{uuid.uuid4().hex[:8]}"
        
        relationship = TestRelationship(
            relationship_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            confidence=random.uniform(0.5, 0.85),
            properties={
                'created_at': datetime.now().isoformat(),
                'strength': random.uniform(0.1, 1.0),
                'source': 'test_fixture'
            }
        )
        
        self.created_fixtures['relationships'].append(relationship)
        logger.debug(f"Created test relationship {relationship.relationship_id}: "
                    f"{source_id} -> {target_id}")
        return relationship
    
    def create_entity_mention_pair(self, surface_form: Optional[str] = None) -> tuple[FixtureEntity, TestMention]:
        """Create a linked entity-mention pair"""
        entity = self.create_test_entity(surface_form)
        mention = self.create_test_mention(entity.canonical_name)
        
        # Link them
        entity.mentions.append(mention.mention_id)
        mention.entity_type = entity.entity_type
        
        return entity, mention
    
    def create_connected_graph(self, num_entities: int = 5, 
                             num_relationships: int = 7) -> Dict[str, List]:
        """Create a connected graph of entities and relationships"""
        entities = []
        relationships = []
        
        # Create entities
        for i in range(num_entities):
            entity_type = random.choice(["PERSON", "ORGANIZATION", "LOCATION", "CONCEPT"])
            entity = self.create_test_entity(entity_type=entity_type)
            entities.append(entity)
        
        # Create relationships
        for i in range(num_relationships):
            source = random.choice(entities)
            target = random.choice([e for e in entities if e != source])
            rel_type = random.choice(["WORKS_FOR", "LOCATED_IN", "RELATES_TO", "INFLUENCED_BY"])
            
            relationship = self.create_test_relationship(
                source.entity_id, target.entity_id, rel_type
            )
            relationships.append(relationship)
        
        return {
            'entities': entities,
            'relationships': relationships
        }
    
    def create_service_response_fixture(self, success: bool = True, 
                                      data: Optional[Any] = None,
                                      error: Optional[str] = None) -> ServiceResponse:
        """Create a standardized service response fixture"""
        if data is None and success:
            data = {"fixture_result": "test_data", "timestamp": datetime.now().isoformat()}
        
        return ServiceResponse(
            success=success,
            data=data,
            error=error or "",
            metadata={
                "fixture": True,
                "created_at": datetime.now().isoformat()
            }
        )
    
    def create_performance_test_data(self, size: str = "small") -> Dict[str, Any]:
        """Create test data for performance testing"""
        config = get_testing_config()
        sizes = {
            "small": config.test_data.small_dataset_size,
            "medium": config.test_data.medium_dataset_size,
            "large": config.test_data.large_dataset_size
        }
        
        dataset_config = sizes.get(size, sizes["small"])
        
        documents = [self.create_test_document() for _ in range(dataset_config["docs"])]
        entities = [self.create_test_entity() for _ in range(dataset_config["entities"])]
        mentions = [self.create_test_mention() for _ in range(dataset_config["mentions"])]
        relationships = [self.create_test_relationship() for _ in range(dataset_config["relationships"])]
        
        return {
            "documents": documents,
            "entities": entities,
            "mentions": mentions,
            "relationships": relationships,
            "size": size,
            "total_items": sum(dataset_config.values())
        }
    
    def create_integration_test_scenario(self, scenario: str = "basic") -> Dict[str, Any]:
        """Create complete test scenarios for integration testing"""
        scenarios = {
            "basic": self._create_basic_scenario,
            "complex": self._create_complex_scenario,
            "error": self._create_error_scenario,
            "performance": self._create_performance_scenario
        }
        
        scenario_func = scenarios.get(scenario, scenarios["basic"])
        return scenario_func()
    
    def _create_basic_scenario(self) -> Dict[str, Any]:
        """Create basic integration test scenario"""
        doc = self.create_test_document("John Smith works at Microsoft in Seattle.")
        entity1 = self.create_test_entity("John Smith", "PERSON")
        entity2 = self.create_test_entity("Microsoft", "ORGANIZATION") 
        entity3 = self.create_test_entity("Seattle", "LOCATION")
        
        mention1 = self.create_test_mention("John Smith", doc.document_id)
        mention2 = self.create_test_mention("Microsoft", doc.document_id)
        mention3 = self.create_test_mention("Seattle", doc.document_id)
        
        rel1 = self.create_test_relationship(entity1.entity_id, entity2.entity_id, "WORKS_FOR")
        rel2 = self.create_test_relationship(entity2.entity_id, entity3.entity_id, "LOCATED_IN")
        
        return {
            "scenario": "basic",
            "documents": [doc],
            "entities": [entity1, entity2, entity3],
            "mentions": [mention1, mention2, mention3],
            "relationships": [rel1, rel2],
            "expected_outcomes": {
                "entities_created": 3,
                "mentions_created": 3,
                "relationships_created": 2
            }
        }
    
    def _create_complex_scenario(self) -> Dict[str, Any]:
        """Create complex integration test scenario"""
        return self.create_connected_graph(10, 15)
    
    def _create_error_scenario(self) -> Dict[str, Any]:
        """Create error-inducing test scenario"""
        return {
            "scenario": "error",
            "invalid_data": {
                "empty_surface_form": "",
                "negative_positions": {"start": -1, "end": -5},
                "invalid_entity_type": "INVALID_TYPE",
                "malformed_ids": ["", None, "invalid/id"]
            },
            "expected_errors": [
                "Invalid surface form",
                "Invalid position",
                "Unknown entity type",
                "Invalid ID format"
            ]
        }
    
    def _create_performance_scenario(self) -> Dict[str, Any]:
        """Create performance testing scenario"""
        return self.create_performance_test_data("large")
    
    def _generate_sample_content(self) -> str:
        """Generate realistic sample document content"""
        templates = [
            "Dr. {person} from {organization} published research on {topic}. "
            "The study, conducted in {location}, revealed significant findings about {concept}.",
            
            "{organization} announced a new partnership with {other_org}. "
            "CEO {person} stated that this collaboration will advance {topic} research.",
            
            "The {event} conference in {location} featured presentations by {person1} and {person2}. "
            "Key topics included {topic1}, {topic2}, and {topic3}.",
            
            "{organization} has been working on {topic} since {year}. "
            "Lead researcher {person} believes this technology could revolutionize {field}."
        ]
        
        template = random.choice(templates)
        
        return template.format(
            person=random.choice(["Alice Johnson", "Dr. Robert Chen", "Prof. Maria Garcia"]),
            person1=random.choice(["John Williams", "Sarah Davis", "Michael Brown"]),
            person2=random.choice(["Lisa Wilson", "David Miller", "Jennifer Taylor"]),
            organization=random.choice(["MIT", "Stanford University", "Google Research", "Microsoft"]),
            other_org=random.choice(["IBM", "OpenAI", "DeepMind", "Meta"]),
            location=random.choice(["Boston", "San Francisco", "New York", "London"]),
            topic=random.choice(["artificial intelligence", "quantum computing", "climate change"]),
            topic1=random.choice(["machine learning", "data science", "robotics"]),
            topic2=random.choice(["neural networks", "computer vision", "NLP"]),
            topic3=random.choice(["ethics in AI", "sustainability", "privacy"]),
            concept=random.choice(["neural networks", "quantum entanglement", "carbon capture"]),
            event=random.choice(["ICML", "NeurIPS", "ACL", "ICLR"]),
            year=random.choice(["2020", "2021", "2022", "2023"]),
            field=random.choice(["healthcare", "education", "transportation", "finance"])
        )
    
    def _generate_entity_name(self, entity_type: str) -> str:
        """Generate realistic entity names by type"""
        names = {
            "PERSON": ["John Smith", "Maria Garcia", "Dr. Alice Johnson", "Prof. Robert Chen"],
            "ORGANIZATION": ["Microsoft", "MIT", "Google Research", "United Nations"],
            "LOCATION": ["New York", "San Francisco", "Boston", "London"],
            "CONCEPT": ["artificial intelligence", "quantum computing", "climate change"],
            "EVENT": ["ICML Conference", "World Summit", "Research Symposium"]
        }
        
        return random.choice(names.get(entity_type, ["Test Entity"]))
    
    def get_fixture_summary(self) -> Dict[str, Any]:
        """Get summary of all created fixtures"""
        return {
            "documents": len(self.created_fixtures['documents']),
            "entities": len(self.created_fixtures['entities']),
            "mentions": len(self.created_fixtures['mentions']),
            "relationships": len(self.created_fixtures['relationships']),
            "total_fixtures": sum(len(fixtures) for fixtures in self.created_fixtures.values())
        }
    
    def clear_fixtures(self) -> None:
        """Clear all created fixtures"""
        for fixture_list in self.created_fixtures.values():
            fixture_list.clear()
        logger.debug("All fixtures cleared")


# Convenient fixture generators
def generate_test_documents(count: int = 5) -> List[FixtureDocument]:
    """Generate multiple test documents"""
    fixtures = ServiceFixtures()
    return [fixtures.create_test_document() for _ in range(count)]


def generate_test_entities(count: int = 10) -> List[FixtureEntity]:
    """Generate multiple test entities"""
    fixtures = ServiceFixtures()
    return [fixtures.create_test_entity() for _ in range(count)]


def generate_complete_test_scenario() -> Dict[str, Any]:
    """Generate a complete test scenario with all data types"""
    fixtures = ServiceFixtures()
    return fixtures.create_integration_test_scenario("complex")