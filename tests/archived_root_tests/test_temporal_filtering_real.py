#!/usr/bin/env python3
"""
Test temporal filtering implementation in T23A_SPACY_NER
"""
import asyncio
import logging
from pathlib import Path

# Configure logging to see filtering
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Show temporal filtering debug messages
logging.getLogger('src.tools.phase1.t23a_spacy_ner_unified').setLevel(logging.DEBUG)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)

async def test_temporal_filtering():
    """Test that temporal filtering actually filters entities"""
    
    print("\n" + "="*80)
    print("TESTING TEMPORAL FILTERING IMPLEMENTATION")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create test document with temporal data
    doc_path = Path("test_temporal.txt")
    doc_path.write_text("""
    In 2022, Microsoft acquired Activision for $69 billion.
    In 2023, Google launched Bard AI to compete with ChatGPT.
    In 2024, Apple released the Vision Pro headset.
    
    Microsoft reported $198 billion revenue in 2022.
    Google's 2023 revenue was $282 billion.
    Apple expects $400 billion revenue in 2024.
    """)
    
    interface.current_document_path = str(doc_path)
    
    # Test 1: Filter for 2023 only
    print("\n" + "="*70)
    print("TEST 1: Asking about 2023 - should only return 2023 entities")
    print("="*70)
    
    question = "What happened with tech companies in 2023?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    # Check entities
    if hasattr(result, 'entities'):
        print(f"\nEntities found: {len(result.entities)}")
        for entity in result.entities[:10]:  # Show first 10
            print(f"  - {entity.get('surface_form')} ({entity.get('entity_type')})")
        
        # Check if filtering worked
        entities_2023 = [e for e in result.entities if '2023' in str(e.get('surface_form', ''))]
        entities_other = [e for e in result.entities if '2022' in str(e.get('surface_form', '')) or '2024' in str(e.get('surface_form', ''))]
        
        print(f"\n2023 entities: {len(entities_2023)}")
        print(f"Other year entities: {len(entities_other)}")
        
        if entities_other:
            print("\n⚠️ WARNING: Found entities from other years!")
            for e in entities_other[:5]:
                print(f"  - {e.get('surface_form')}")
    
    # Test 2: No temporal filter
    print("\n" + "="*70)
    print("TEST 2: General question - should return all entities")
    print("="*70)
    
    question = "What tech companies are mentioned?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    if hasattr(result, 'entities'):
        print(f"\nEntities found: {len(result.entities)}")
        years_found = set()
        for entity in result.entities:
            if entity.get('entity_type') == 'DATE':
                years_found.add(entity.get('surface_form'))
        print(f"Years found: {sorted(years_found)}")
    
    # Cleanup
    doc_path.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("TEMPORAL FILTERING TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_temporal_filtering())