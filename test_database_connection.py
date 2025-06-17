#!/usr/bin/env python3
"""Test database connections and diagnose issues"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_neo4j_connection():
    """Test Neo4j connection"""
    print("🔍 Testing Neo4j Connection...")
    
    try:
        from neo4j import GraphDatabase
        
        # Test basic connection
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "password")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j Connected!' as message")
            record = result.single()
            print(f"✅ {record['message']}")
            
            # Test write operation
            session.run("CREATE (test:TestNode {name: 'connection_test', timestamp: datetime()})")
            print("✅ Write operation successful")
            
            # Test read operation
            result = session.run("MATCH (test:TestNode {name: 'connection_test'}) RETURN test.name as name")
            record = result.single()
            if record:
                print(f"✅ Read operation successful: {record['name']}")
            
            # Clean up
            session.run("MATCH (test:TestNode {name: 'connection_test'}) DELETE test")
            print("✅ Cleanup successful")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_core_services():
    """Test core services initialization"""
    print("\n🔍 Testing Core Services...")
    
    try:
        from core.identity_service import IdentityService
        identity = IdentityService()
        print("✅ Identity Service initialized")
        
        from core.provenance_service import ProvenanceService  
        provenance = ProvenanceService()
        print("✅ Provenance Service initialized")
        
        from core.quality_service import QualityService
        quality = QualityService()
        print("✅ Quality Service initialized")
        
        from core.workflow_state_service import WorkflowStateService
        workflow = WorkflowStateService("./data/test_workflows")
        print("✅ Workflow Service initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Core services failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_phase1_tools():
    """Test Phase 1 tools"""
    print("\n🔍 Testing Phase 1 Tools...")
    
    try:
        # Test individual tools
        from tools.phase1.t01_pdf_loader import PDFLoader
        print("✅ T01 PDF Loader imports")
        
        from tools.phase1.t15a_text_chunker import TextChunker
        print("✅ T15a Text Chunker imports")
        
        from tools.phase1.t23a_spacy_ner import SpacyNER
        print("✅ T23a spaCy NER imports")
        
        from tools.phase1.t27_relationship_extractor import RelationshipExtractor
        print("✅ T27 Relationship Extractor imports")
        
        from tools.phase1.t31_entity_builder import EntityBuilder
        print("✅ T31 Entity Builder imports")
        
        from tools.phase1.t34_edge_builder import EdgeBuilder
        print("✅ T34 Edge Builder imports")
        
        from tools.phase1.t68_pagerank import PageRankCalculator
        print("✅ T68 PageRank imports")
        
        from tools.phase1.t49_multihop_query import MultiHopQuery
        print("✅ T49 Multi-hop Query imports")
        
        # Test workflow
        from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
        print("✅ Vertical Slice Workflow imports")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 1 tools failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spacy_model():
    """Test spaCy model availability"""
    print("\n🔍 Testing spaCy Model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        # Test processing
        doc = nlp("Apple Inc. was founded by Steve Jobs.")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        print(f"✅ spaCy model loaded successfully")
        print(f"✅ Test entities: {entities}")
        
        return True
        
    except Exception as e:
        print(f"❌ spaCy model failed: {e}")
        print("💡 Try running: python -m spacy download en_core_web_sm")
        return False

def run_minimal_workflow():
    """Run a minimal workflow to test integration"""
    print("\n🔍 Testing Minimal Workflow...")
    
    try:
        # Create test content
        test_content = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
        
        # Test text chunker
        from core.identity_service import IdentityService
        from core.provenance_service import ProvenanceService
        from core.quality_service import QualityService
        from tools.phase1.t15a_text_chunker import TextChunker
        
        identity = IdentityService()
        provenance = ProvenanceService()
        quality = QualityService()
        
        chunker = TextChunker(identity, provenance, quality)
        
        result = chunker.chunk_text(
            document_ref="storage://document/test",
            text=test_content,
            document_confidence=0.9
        )
        
        print(f"✅ Text chunking: {result['status']}")
        print(f"   Chunks created: {result['total_chunks']}")
        
        # Test entity extraction
        from tools.phase1.t23a_spacy_ner import SpacyNER
        
        ner = SpacyNER(identity, provenance, quality)
        
        if result['chunks']:
            chunk = result['chunks'][0]
            entity_result = ner.extract_entities(
                chunk_ref=chunk['chunk_ref'],
                text=chunk['text'],
                chunk_confidence=chunk['confidence']
            )
            
            print(f"✅ Entity extraction: {entity_result['status']}")
            print(f"   Entities found: {entity_result['total_entities']}")
            
            if entity_result['entities']:
                print(f"   Sample entity: {entity_result['entities'][0]['surface_form']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🔬 SUPER-DIGIMON DATABASE DIAGNOSTICS")
    print("=" * 50)
    
    results = []
    
    # Test each component
    results.append(("Neo4j Connection", test_neo4j_connection()))
    results.append(("Core Services", test_core_services()))
    results.append(("Phase 1 Tools", test_phase1_tools()))
    results.append(("spaCy Model", test_spacy_model()))
    results.append(("Minimal Workflow", run_minimal_workflow()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All systems operational!")
        print("💡 Try running: python quick_test.py")
    else:
        print("🔧 Some systems need attention")
        print("💡 Check the error messages above for details")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)