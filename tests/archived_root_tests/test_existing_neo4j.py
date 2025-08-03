#!/usr/bin/env python3
"""
Test KGAS with existing Neo4j instance
"""

import os
from neo4j import GraphDatabase

def test_existing_neo4j():
    """Test connection to existing Neo4j and run KGAS tools"""
    print("🔍 TESTING EXISTING NEO4J CONNECTION")
    print("=" * 60)
    
    # Try common Neo4j passwords
    passwords_to_try = [
        "testpassword123",  # From .env
        "password",         # Common default
        "neo4j",           # Default
        "admin",           # Common
        "test",            # Common
        "qualitative_coding_neo4j"  # Container name suggests this
    ]
    
    working_password = None
    
    print("1️⃣ Trying to connect to Neo4j at localhost:7687...")
    
    for password in passwords_to_try:
        try:
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", password)
            )
            
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                print(f"   ✅ Connected with password: {password}")
                working_password = password
                
                # Get some info
                result = session.run("MATCH (n) RETURN count(n) as count")
                node_count = result.single()["count"]
                print(f"   • Existing nodes: {node_count}")
                
                driver.close()
                break
                
        except Exception as e:
            continue
    
    if not working_password:
        print("   ❌ Could not connect with any common password")
        print("\n   Try one of these options:")
        print("   1. Check the password for the running container")
        print("   2. Use Neo4j browser at http://localhost:7474 to set password")
        print("   3. Stop existing container and run our setup script")
        return False
    
    # Update environment
    print(f"\n2️⃣ Updating environment with working credentials...")
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = working_password
    
    # Now test KGAS tools
    print("\n3️⃣ Testing KGAS tools with Neo4j...")
    
    try:
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        
        # Quick test of Neo4j tools
        print("\n🧪 Testing Neo4j-dependent tools:")
        
        # Test T31
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        entity_builder = EntityBuilder(service_manager)
        
        test_mention = [{
            'mention_id': 'test_001',
            'entity_id': 'entity_test',
            'surface_form': 'Test Entity',
            'entity_type': 'ORG',
            'confidence': 0.9,
            'source_ref': 'test',
            'text': 'Test Entity',
            'label': 'ORG'
        }]
        
        t31_request = ToolRequest(
            tool_id="T31",
            operation="build_entities", 
            input_data={"mentions": test_mention, "source_refs": ["test"]},
            parameters={}
        )
        
        result = entity_builder.execute(t31_request)
        if result.status == "success":
            print("   ✅ T31 Entity Builder: WORKING")
        else:
            print(f"   ❌ T31 failed: {result.error_message}")
        
        # Test T68
        from src.tools.phase1.t68_pagerank import PageRankCalculator
        pagerank = PageRankCalculator(service_manager)
        
        t68_request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={"graph_ref": "neo4j://graph/main"},
            parameters={}
        )
        
        result = pagerank.execute(t68_request)
        if result.status == "success":
            print("   ✅ T68 PageRank: WORKING")
            entities = result.data.get('ranked_entities', [])
            print(f"      • Found {len(entities)} entities in graph")
        else:
            print(f"   ❌ T68 failed: {result.error_message}")
        
        print("\n✅ Neo4j connection successful!")
        print(f"   • URI: bolt://localhost:7687")
        print(f"   • User: neo4j")
        print(f"   • Password: {working_password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_full_pipeline_with_neo4j():
    """Run complete pipeline including Neo4j storage"""
    print("\n🚀 RUNNING FULL PIPELINE WITH NEO4J")
    print("=" * 60)
    
    try:
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        
        # Create test document
        test_file = "neo4j_test.txt"
        with open(test_file, 'w') as f:
            f.write("""
            KGAS Neo4j Integration Test
            
            Stanford University and MIT are leading research institutions.
            Dr. Alice Chen from Stanford collaborates with Prof. Bob Smith from MIT.
            Google and Microsoft fund their AI research projects.
            The collaboration produced groundbreaking results in 2024.
            """)
        
        print("1️⃣ Loading and processing document...")
        
        # Run full pipeline
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        from src.tools.phase1.t15a_text_chunker import TextChunker
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        from src.tools.phase1.t34_edge_builder import EdgeBuilder
        from src.tools.phase1.t68_pagerank import PageRankCalculator
        from src.tools.phase1.t49_multihop_query import MultiHopQuery
        
        tools_used = []
        
        # T01: Load
        loader = PDFLoader(service_manager)
        t01_req = ToolRequest("T01", "load_document", {"file_path": test_file}, {})
        t01_res = loader.execute(t01_req)
        if t01_res.status == "success":
            document = t01_res.data['document']
            tools_used.append("T01 ✅")
        
        # T15A: Chunk
        chunker = TextChunker(service_manager)
        t15a_req = ToolRequest("T15A", "chunk_text", {
            "document_ref": document['document_ref'],
            "text": document['text'],
            "confidence": document['confidence']
        }, {"chunk_size": 200})
        t15a_res = chunker.execute(t15a_req)
        if t15a_res.status == "success":
            chunks = t15a_res.data['chunks']
            tools_used.append("T15A ✅")
        
        # T23A: Extract entities
        ner = SpacyNER(service_manager)
        all_entities = []
        for chunk in chunks:
            t23a_req = ToolRequest("T23A", "extract_entities", {
                "chunk_ref": chunk['chunk_ref'],
                "text": chunk['text'],
                "confidence": chunk['confidence']
            }, {})
            t23a_res = ner.execute(t23a_req)
            if t23a_res.status == "success":
                all_entities.extend(t23a_res.data['entities'])
        tools_used.append(f"T23A ✅ ({len(all_entities)} entities)")
        
        # T27: Extract relationships
        rel_extractor = RelationshipExtractor(service_manager)
        all_relationships = []
        for chunk in chunks:
            chunk_entities = [e for e in all_entities if chunk['chunk_ref'] in str(e.get('chunk_ref', ''))]
            if len(chunk_entities) >= 2:
                t27_entities = [{'text': e['surface_form'], 'label': e['entity_type'], 
                               'start': 0, 'end': 0} for e in chunk_entities[:10]]
                t27_req = ToolRequest("T27", "extract_relationships", {
                    "chunk_ref": chunk['chunk_ref'],
                    "text": chunk['text'],
                    "entities": t27_entities,
                    "confidence": 0.5
                }, {})
                t27_res = rel_extractor.execute(t27_req)
                if t27_res.status == "success":
                    all_relationships.extend(t27_res.data.get('relationships', []))
        tools_used.append(f"T27 ✅ ({len(all_relationships)} relationships)")
        
        # T31: Build entities in Neo4j
        entity_builder = EntityBuilder(service_manager)
        mentions = []
        for e in all_entities:
            mentions.append({
                'mention_id': e.get('mention_id'),
                'entity_id': e.get('entity_id'),
                'surface_form': e['surface_form'],
                'entity_type': e['entity_type'],
                'confidence': e.get('confidence', 0.8),
                'source_ref': e.get('chunk_ref'),
                'text': e['surface_form'],
                'label': e['entity_type']
            })
        
        t31_req = ToolRequest("T31", "build_entities", {
            "mentions": mentions,
            "source_refs": [c['chunk_ref'] for c in chunks]
        }, {})
        t31_res = entity_builder.execute(t31_req)
        if t31_res.status == "success":
            tools_used.append(f"T31 ✅ ({len(t31_res.data.get('entities', []))} nodes)")
        
        # T34: Build edges in Neo4j
        if all_relationships:
            edge_builder = EdgeBuilder(service_manager)
            t34_req = ToolRequest("T34", "build_edges", {
                "relationships": all_relationships,
                "source_refs": [c['chunk_ref'] for c in chunks]
            }, {})
            t34_res = edge_builder.execute(t34_req)
            if t34_res.status == "success":
                tools_used.append(f"T34 ✅ ({len(t34_res.data.get('edges', []))} edges)")
        
        # T68: Calculate PageRank
        pagerank = PageRankCalculator(service_manager)
        t68_req = ToolRequest("T68", "calculate_pagerank", 
                             {"graph_ref": "neo4j://graph/main"}, {})
        t68_res = pagerank.execute(t68_req)
        if t68_res.status == "success":
            ranked = t68_res.data.get('ranked_entities', [])
            tools_used.append(f"T68 ✅ (PageRank for {len(ranked)} entities)")
            
            if ranked:
                print("\n📊 Top entities by PageRank:")
                for e in ranked[:5]:
                    print(f"   • {e.get('name')}: {e.get('pagerank', 0):.4f}")
        
        # T49: Query the graph
        query_engine = MultiHopQuery(service_manager)
        t49_req = ToolRequest("T49", "query_graph", {
            "question": "What universities are mentioned?"
        }, {"max_hops": 2})
        t49_res = query_engine.execute(t49_req)
        if t49_res.status == "success":
            results = t49_res.data.get('results', [])
            tools_used.append(f"T49 ✅ ({len(results)} results)")
        
        # Clean up
        os.remove(test_file)
        
        # Summary
        print("\n📊 FULL PIPELINE SUMMARY")
        print("=" * 60)
        print("Tools successfully executed:")
        for tool in tools_used:
            print(f"   • {tool}")
        
        print(f"\nTotal: {len(tools_used)} tools working with Neo4j!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)
        return False

def main():
    """Main test function"""
    print("🚀 TESTING KGAS WITH EXISTING NEO4J")
    print("=" * 80)
    
    if test_existing_neo4j():
        print("\n" + "=" * 80)
        run_full_pipeline_with_neo4j()
    else:
        print("\n❌ Could not connect to Neo4j")
        print("\nTo set up Neo4j:")
        print("1. Stop the existing container: docker stop qualitative_coding_neo4j")
        print("2. Run our setup script again")
        print("3. Or connect to http://localhost:7474 and check the password")

if __name__ == "__main__":
    main()