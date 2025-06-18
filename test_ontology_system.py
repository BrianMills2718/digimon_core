#!/usr/bin/env python3
"""
Test the complete ontology generation and extraction system.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ontology_generator import DomainOntology, EntityType, RelationshipType
from src.ontology.gemini_ontology_generator import GeminiOntologyGenerator
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.core.enhanced_identity_service import EnhancedIdentityService
from src.core.ontology_storage_service import OntologyStorageService, OntologySession


def test_ontology_generation():
    """Test ontology generation with Gemini."""
    print("=== Testing Ontology Generation ===")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set. Using mock ontology.")
        return create_mock_climate_ontology()
    
    try:
        generator = GeminiOntologyGenerator()
        
        # Simulate conversation
        messages = [
            {"role": "user", "content": "I'm analyzing climate change research papers"},
            {"role": "assistant", "content": "I can help you create an ontology for climate change research. What specific aspects are you interested in?"},
            {"role": "user", "content": "I want to track climate policies, renewable energy technologies, environmental impacts, and key organizations working on climate solutions."}
        ]
        
        # Generate ontology
        print("Generating ontology from conversation...")
        ontology = generator.generate_from_conversation(
            messages=messages,
            temperature=0.7,
            constraints={"max_entities": 8, "max_relations": 6}
        )
        
        print(f"✓ Generated ontology: {ontology.domain_name}")
        print(f"  - Entity types: {len(ontology.entity_types)}")
        print(f"  - Relationship types: {len(ontology.relationship_types)}")
        
        return ontology
        
    except Exception as e:
        print(f"❌ Ontology generation failed: {e}")
        print("Using mock ontology instead...")
        return create_mock_climate_ontology()


def create_mock_climate_ontology():
    """Create a mock climate ontology for testing."""
    return DomainOntology(
        domain_name="Climate Research",
        domain_description="Ontology for analyzing climate change research, policies, and technologies",
        entity_types=[
            EntityType(
                name="CLIMATE_POLICY",
                description="Government or international climate policies and agreements",
                examples=["Paris Agreement", "Green New Deal", "Carbon Tax"],
                attributes=["scope", "target_year", "emission_goals"]
            ),
            EntityType(
                name="RENEWABLE_TECH",
                description="Renewable energy technologies and solutions",
                examples=["Solar Panels", "Wind Turbines", "Battery Storage"],
                attributes=["efficiency", "capacity", "cost"]
            ),
            EntityType(
                name="CLIMATE_ORG",
                description="Organizations working on climate solutions",
                examples=["IPCC", "Climate Action Network", "350.org"],
                attributes=["type", "focus_area", "geographic_scope"]
            ),
            EntityType(
                name="ENVIRONMENTAL_IMPACT",
                description="Environmental effects and climate impacts",
                examples=["Sea Level Rise", "Deforestation", "Ocean Acidification"],
                attributes=["severity", "affected_regions", "timeframe"]
            )
        ],
        relationship_types=[
            RelationshipType(
                name="IMPLEMENTS",
                description="Organization implements or promotes a policy",
                source_types=["CLIMATE_ORG"],
                target_types=["CLIMATE_POLICY"],
                examples=["EU implements Carbon Tax"]
            ),
            RelationshipType(
                name="ADDRESSES",
                description="Technology or policy addresses an environmental impact",
                source_types=["RENEWABLE_TECH", "CLIMATE_POLICY"],
                target_types=["ENVIRONMENTAL_IMPACT"],
                examples=["Solar Power addresses Carbon Emissions"]
            ),
            RelationshipType(
                name="DEVELOPS",
                description="Organization develops or researches technology",
                source_types=["CLIMATE_ORG"],
                target_types=["RENEWABLE_TECH"],
                examples=["Tesla develops Battery Storage"]
            )
        ],
        extraction_patterns=[
            "Look for policy names, especially those with 'Act', 'Agreement', 'Protocol'",
            "Identify renewable technologies by keywords like 'solar', 'wind', 'renewable'",
            "Organizations often have acronyms or end with 'Institute', 'Foundation'",
            "Environmental impacts often include measurements or geographic references"
        ],
        created_by_conversation="Mock conversation for testing"
    )


def test_extraction(ontology: DomainOntology):
    """Test entity extraction with the ontology."""
    print("\n=== Testing Entity Extraction ===")
    
    # Sample text
    sample_text = """
    The Paris Agreement, adopted by 196 parties in 2015, aims to limit global warming to 1.5°C above 
    pre-industrial levels. The European Union has implemented a comprehensive Carbon Tax system to 
    reduce emissions. Meanwhile, organizations like the IPCC continue to study sea level rise and 
    its impacts on coastal communities.
    
    In response to these challenges, companies like Tesla are developing advanced battery storage 
    technologies to support renewable energy adoption. Solar panel efficiency has improved dramatically, 
    making it a viable solution to address carbon emissions. The Climate Action Network coordinates 
    global efforts to implement these climate policies effectively.
    """
    
    # Initialize services
    identity_service = EnhancedIdentityService()
    extractor = OntologyAwareExtractor(identity_service)
    
    try:
        # Extract entities
        print("Extracting entities from sample text...")
        result = extractor.extract_entities(
            text=sample_text,
            ontology=ontology,
            source_ref="test_document_001",
            confidence_threshold=0.7
        )
        
        print(f"✓ Extraction complete!")
        print(f"  - Entities found: {len(result.entities)}")
        print(f"  - Relationships found: {len(result.relationships)}")
        print(f"  - Mentions created: {len(result.mentions)}")
        
        # Show some results
        print("\nSample entities:")
        for entity in result.entities[:5]:
            print(f"  - {entity.canonical_name} ({entity.entity_type}) - confidence: {entity.confidence:.2f}")
        
        print("\nSample relationships:")
        for rel in result.relationships[:3]:
            source = next(e for e in result.entities if e.id == rel.source_id)
            target = next(e for e in result.entities if e.id == rel.target_id)
            print(f"  - {source.canonical_name} --{rel.relationship_type}--> {target.canonical_name}")
        
        return result
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None


def test_storage(ontology: DomainOntology):
    """Test ontology storage for TORC compliance."""
    print("\n=== Testing Ontology Storage ===")
    
    storage = OntologyStorageService()
    
    # Create session
    session = OntologySession(
        session_id=f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        created_at=datetime.now(),
        conversation_history=[
            {"role": "user", "content": "I'm analyzing climate change research"},
            {"role": "assistant", "content": "What aspects interest you?"},
            {"role": "user", "content": "Climate policies and renewable technologies"}
        ],
        initial_ontology=ontology,
        refinements=[],
        final_ontology=ontology,
        generation_parameters={
            "model": "gemini-2.0-flash-exp",
            "temperature": 0.7,
            "constraints": {"max_entities": 8}
        }
    )
    
    # Save session
    print("Saving ontology session...")
    session_id = storage.save_session(session)
    print(f"✓ Session saved: {session_id}")
    
    # Load and verify
    print("Loading session...")
    loaded = storage.load_session(session_id)
    if loaded:
        print(f"✓ Session loaded successfully")
        print(f"  - Domain: {loaded.final_ontology.domain_name}")
        print(f"  - Created: {loaded.created_at}")
    
    # Record usage
    storage.record_usage(
        session_id=session_id,
        usage_type="extraction",
        context={"document": "test_document_001", "text_length": 500},
        results_summary={"entities": 10, "relationships": 5}
    )
    print("✓ Usage recorded")
    
    # Export session
    export_path = f"./data/exports/ontology_{session_id}.json"
    storage.export_session(session_id, export_path)
    print(f"✓ Session exported to: {export_path}")
    
    # Verify integrity
    integrity = storage.verify_integrity()
    print(f"✓ Integrity check: {integrity['valid_sessions']}/{integrity['total_sessions']} sessions valid")


def main():
    """Run all tests."""
    print("🚀 Testing Super-Digimon Ontology System\n")
    
    # Test 1: Generate ontology
    ontology = test_ontology_generation()
    
    if not ontology:
        print("❌ Failed to generate ontology. Exiting.")
        return
    
    # Test 2: Extract entities
    extraction_result = test_extraction(ontology)
    
    # Test 3: Storage and TORC compliance
    test_storage(ontology)
    
    print("\n✅ All tests completed!")
    print("\nTo use the UI, run: streamlit run streamlit_app.py")


if __name__ == "__main__":
    main()