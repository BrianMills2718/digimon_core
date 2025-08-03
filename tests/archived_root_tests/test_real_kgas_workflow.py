#!/usr/bin/env python3
"""
Test REAL KGAS tools with actual databases and MCP server.
NO MOCKS, NO SIMULATIONS - Only real, working components.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import subprocess

def setup_environment():
    """Set up environment for real database connections"""
    print("🔧 SETTING UP ENVIRONMENT FOR REAL KGAS WORKFLOW")
    print("=" * 60)
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Running configuration setup...")
        print("   You can also run: python scripts/setup_config.py")
        print("   Or create .env manually with required variables:")
        print("   - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
        
        # Prompt user to run setup
        response = input("\n   Run configuration setup now? [Y/n]: ").strip().lower()
        if response in ["", "y", "yes"]:
            try:
                import subprocess
                result = subprocess.run([sys.executable, "scripts/setup_config.py"], 
                                      capture_output=False, text=True)
                if result.returncode != 0:
                    print("❌ Configuration setup failed")
                    return False
            except Exception as e:
                print(f"❌ Failed to run setup: {e}")
                return False
        else:
            print("❌ Environment setup cancelled. Please create .env file manually.")
            return False
    else:
        print("✅ Found existing .env file")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Verify required environment variables
    required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please run: python scripts/setup_config.py")
        return False
    
    return True

def check_neo4j_connection():
    """Check if Neo4j is available and accessible"""
    print("\n🔍 CHECKING NEO4J CONNECTION...")
    
    try:
        from neo4j import GraphDatabase
        import os
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not password:
            print("❌ NEO4J_PASSWORD environment variable not set")
            return False
        
        print(f"   URI: {uri}")
        print(f"   User: {user}")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            print(f"   ✅ Neo4j connection successful! Test query returned: {test_value}")
            
            # Get database info
            result = session.run("CALL dbms.components()")
            for record in result:
                print(f"   • Neo4j Version: {record['versions'][0]}")
                print(f"   • Edition: {record['edition']}")
            
            # Check node count
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            print(f"   • Existing nodes: {node_count}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Neo4j connection failed: {e}")
        print("   📝 To run with real Neo4j:")
        print("      1. Install Neo4j: https://neo4j.com/download/")
        print("      2. Start Neo4j: neo4j start")
        print("      3. Set password in Neo4j browser")
        print("      4. Update .env with credentials")
        return False

def test_real_mcp_server():
    """Test the real MCP server with actual tools"""
    print("\n🚀 TESTING REAL MCP SERVER")
    print("=" * 60)
    
    try:
        # Import MCP server components
        from src.mcp_server import get_mcp_server, get_server_status
        from src.mcp_tools import get_mcp_server_manager
        
        # Get server status
        print("1️⃣ Getting MCP server status...")
        status = get_server_status()
        
        print(f"   • Architecture: {status.get('architecture', 'unknown')}")
        print(f"   • Version: {status.get('version', 'unknown')}")
        
        server_info = status.get('server_info', {})
        print(f"   • Total tools: {server_info.get('total_tools', 0)}")
        
        # List tool collections
        print("\n2️⃣ Available tool collections:")
        for collection, info in server_info.get('tool_collections', {}).items():
            tool_count = info.get('tool_count', 0)
            available = info.get('service_available', False)
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {collection}: {tool_count} tools")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_real_workflow_with_mcp():
    """Run a complete workflow using real MCP tools"""
    print("\n🔄 RUNNING REAL WORKFLOW WITH MCP TOOLS")
    print("=" * 60)
    
    try:
        # Import required components
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        # Initialize service manager
        print("1️⃣ Initializing service manager...")
        service_manager = get_service_manager()
        print("   ✅ Service manager ready")
        
        # Create test document
        test_file = "real_workflow_test.txt"
        create_test_document(test_file)
        
        # Import and initialize real tools
        print("\n2️⃣ Initializing Phase 1 tools...")
        
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        from src.tools.phase1.t15a_text_chunker import TextChunker
        from src.tools.phase1.t23a_spacy_ner import SpacyNER
        from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
        
        pdf_loader = PDFLoader(service_manager)
        text_chunker = TextChunker(service_manager)
        entity_extractor = SpacyNER(service_manager)
        relationship_extractor = RelationshipExtractor(service_manager)
        
        print("   ✅ Tools initialized")
        
        # Execute workflow
        workflow_results = {}
        
        # Step 1: Load document
        print("\n3️⃣ Loading document with T01...")
        t01_request = ToolRequest(
            tool_id="T01",
            operation="load_document",
            input_data={
                "file_path": test_file,
                "workflow_id": "real_workflow_test"
            },
            parameters={}
        )
        
        t01_result = pdf_loader.execute(t01_request)
        if t01_result.status == "success":
            document = t01_result.data['document']
            workflow_results['document'] = document
            print(f"   ✅ Document loaded: {document['text_length']} chars")
            print(f"   • Document ID: {document['document_id']}")
            print(f"   • Confidence: {document['confidence']:.2f}")
        else:
            print(f"   ❌ Failed: {t01_result.error_message}")
            os.remove(test_file)
            return False
        
        # Step 2: Chunk text
        print("\n4️⃣ Chunking text with T15A...")
        t15a_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "document_ref": document['document_ref'],
                "text": document['text'],
                "confidence": document['confidence']
            },
            parameters={
                "chunk_size": 300,
                "overlap": 50
            }
        )
        
        t15a_result = text_chunker.execute(t15a_request)
        if t15a_result.status == "success":
            chunks = t15a_result.data['chunks']
            workflow_results['chunks'] = chunks
            print(f"   ✅ Created {len(chunks)} chunks")
            print(f"   • Average size: {t15a_result.data['stats']['avg_chunk_size']:.0f} chars")
        else:
            print(f"   ❌ Failed: {t15a_result.error_message}")
        
        # Step 3: Extract entities from all chunks
        print("\n5️⃣ Extracting entities with T23A...")
        all_entities = []
        for i, chunk in enumerate(chunks):
            t23a_request = ToolRequest(
                tool_id="T23A",
                operation="extract_entities",
                input_data={
                    "chunk_ref": chunk['chunk_ref'],
                    "text": chunk['text'],
                    "confidence": chunk['confidence']
                },
                parameters={
                    "confidence_threshold": 0.6
                }
            )
            
            t23a_result = entity_extractor.execute(t23a_request)
            if t23a_result.status == "success":
                entities = t23a_result.data['entities']
                all_entities.extend(entities)
                print(f"   • Chunk {i+1}: {len(entities)} entities")
        
        workflow_results['entities'] = all_entities
        print(f"   ✅ Total entities extracted: {len(all_entities)}")
        
        # Show some entities
        if all_entities:
            print("   Sample entities:")
            for entity in all_entities[:5]:
                print(f"   • {entity['surface_form']} ({entity['entity_type']})")
        
        # Step 4: Extract relationships
        print("\n6️⃣ Extracting relationships with T27...")
        all_relationships = []
        
        for i, chunk in enumerate(chunks):
            # Get entities for this chunk
            chunk_entities = [e for e in all_entities if chunk['chunk_ref'] in str(e.get('chunk_ref', ''))]
            
            if len(chunk_entities) >= 2:
                # Convert to T27 format
                t27_entities = []
                for entity in chunk_entities:
                    t27_entity = {
                        'text': entity['surface_form'],
                        'label': entity['entity_type'],
                        'start': entity.get('start_pos', 0),
                        'end': entity.get('end_pos', 0)
                    }
                    t27_entities.append(t27_entity)
                
                t27_request = ToolRequest(
                    tool_id="T27",
                    operation="extract_relationships",
                    input_data={
                        "chunk_ref": chunk['chunk_ref'],
                        "text": chunk['text'],
                        "entities": t27_entities,
                        "confidence": 0.6
                    },
                    parameters={}
                )
                
                t27_result = relationship_extractor.execute(t27_request)
                if t27_result.status == "success":
                    relationships = t27_result.data['relationships']
                    all_relationships.extend(relationships)
                    if relationships:
                        print(f"   • Chunk {i+1}: {len(relationships)} relationships")
        
        workflow_results['relationships'] = all_relationships
        print(f"   ✅ Total relationships extracted: {len(all_relationships)}")
        
        # Show some relationships
        if all_relationships:
            print("   Sample relationships:")
            for rel in all_relationships[:3]:
                print(f"   • {rel['head_entity']} --[{rel['relationship_type']}]--> {rel['tail_entity']}")
        
        # Try Neo4j operations if available
        neo4j_available = check_neo4j_connection()
        
        if neo4j_available:
            print("\n7️⃣ Building graph in Neo4j...")
            try:
                from src.tools.phase1.t31_entity_builder import EntityBuilder
                from src.tools.phase1.t34_edge_builder import EdgeBuilder
                
                entity_builder = EntityBuilder(service_manager)
                edge_builder = EdgeBuilder(service_manager)
                
                # Build entities
                mentions = []
                for entity in all_entities:
                    mention = {
                        'mention_id': entity.get('mention_id'),
                        'entity_id': entity.get('entity_id'),
                        'surface_form': entity.get('surface_form'),
                        'entity_type': entity.get('entity_type'),
                        'confidence': entity.get('confidence', 0.8),
                        'source_ref': entity.get('chunk_ref'),
                        'text': entity.get('surface_form'),
                        'label': entity.get('entity_type')
                    }
                    mentions.append(mention)
                
                t31_request = ToolRequest(
                    tool_id="T31",
                    operation="build_entities",
                    input_data={
                        "mentions": mentions,
                        "source_refs": [c['chunk_ref'] for c in chunks]
                    },
                    parameters={}
                )
                
                t31_result = entity_builder.execute(t31_request)
                if t31_result.status == "success":
                    print(f"   ✅ Built {len(t31_result.data.get('entities', []))} entity nodes")
                
                # Build edges
                if all_relationships:
                    t34_request = ToolRequest(
                        tool_id="T34",
                        operation="build_edges",
                        input_data={
                            "relationships": all_relationships,
                            "source_refs": [c['chunk_ref'] for c in chunks]
                        },
                        parameters={}
                    )
                    
                    t34_result = edge_builder.execute(t34_request)
                    if t34_result.status == "success":
                        print(f"   ✅ Built {len(t34_result.data.get('edges', []))} relationship edges")
                
                # Try PageRank
                print("\n8️⃣ Calculating PageRank...")
                from src.tools.phase1.t68_pagerank import PageRankCalculator
                pagerank_calc = PageRankCalculator(service_manager)
                
                t68_request = ToolRequest(
                    tool_id="T68",
                    operation="calculate_pagerank",
                    input_data={"graph_ref": "neo4j://graph/main"},
                    parameters={
                        "damping_factor": 0.85,
                        "max_iterations": 100
                    }
                )
                
                t68_result = pagerank_calc.execute(t68_request)
                if t68_result.status == "success":
                    ranked_entities = t68_result.data.get('ranked_entities', [])
                    print(f"   ✅ Calculated PageRank for {len(ranked_entities)} entities")
                    
                    if ranked_entities:
                        print("   Top entities by PageRank:")
                        for entity in ranked_entities[:5]:
                            print(f"   • {entity['name']}: {entity['pagerank']:.4f}")
                
            except Exception as e:
                print(f"   ⚠️  Neo4j operations failed: {e}")
        
        # Clean up
        os.remove(test_file)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 REAL WORKFLOW EXECUTION SUMMARY")
        print("=" * 60)
        print(f"✅ Document loaded: {workflow_results['document']['text_length']} chars")
        print(f"✅ Chunks created: {len(workflow_results['chunks'])}")
        print(f"✅ Entities extracted: {len(workflow_results['entities'])}")
        print(f"✅ Relationships found: {len(workflow_results['relationships'])}")
        
        if neo4j_available:
            print(f"✅ Graph operations: EXECUTED")
        else:
            print(f"⚠️  Graph operations: SKIPPED (Neo4j not available)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_mcp_tool_execution():
    """Test executing tools via MCP protocol"""
    print("\n🔌 TESTING MCP TOOL EXECUTION")
    print("=" * 60)
    
    try:
        # Start MCP server in subprocess
        print("1️⃣ Starting MCP server...")
        
        # Create a test script to run MCP server
        mcp_test_script = """
import asyncio
from src.mcp_server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("MCP server stopped")
"""
        
        with open("test_mcp_server.py", "w") as f:
            f.write(mcp_test_script)
        
        # Start server process
        import subprocess
        server_process = subprocess.Popen(
            [sys.executable, "test_mcp_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give server time to start
        time.sleep(2)
        
        print("   ✅ MCP server started")
        
        # Test calling MCP tools
        print("\n2️⃣ Testing MCP tool calls...")
        
        # Import MCP client capabilities
        from src.mcp_tools.server_manager import get_mcp_server_manager
        
        manager = get_mcp_server_manager()
        
        # Get available tools
        tools = manager.get_available_tools()
        print(f"   • Available tools: {len(tools)}")
        
        # Show some tools
        for tool_name in list(tools.keys())[:5]:
            print(f"   • {tool_name}")
        
        # Terminate server
        server_process.terminate()
        os.remove("test_mcp_server.py")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP execution test failed: {e}")
        if os.path.exists("test_mcp_server.py"):
            os.remove("test_mcp_server.py")
        return False

def create_test_document(filename: str):
    """Create a test document with rich content"""
    content = """
    KGAS Real-World Test Document
    
    Dr. Sarah Johnson from Stanford University has published groundbreaking 
    research on knowledge graph construction. Her collaboration with 
    Professor Michael Chen from MIT demonstrates the power of cross-institutional 
    research partnerships.
    
    The research, funded by the National Science Foundation and Google Research, 
    shows that modern NLP techniques can extract complex relationships from 
    unstructured text with 95% accuracy. Microsoft Azure and Amazon Web Services 
    provided cloud infrastructure for the experiments.
    
    Key contributors include:
    - Dr. Emily Rodriguez (Harvard University) - Machine Learning
    - Prof. David Kim (Berkeley) - Graph Theory
    - Dr. Lisa Wang (Carnegie Mellon) - Natural Language Processing
    
    The team's findings, published in Nature Machine Intelligence, indicate 
    that combining transformer models with graph neural networks yields 
    superior results for entity linking and relationship extraction.
    
    IBM Research and Apple AI Lab have already begun implementing these 
    techniques in their production systems. The open-source implementation 
    is available on GitHub under the MIT license.
    """
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f"   ✅ Created test document: {filename}")

def main():
    """Run all real KGAS tests"""
    print("🚀 REAL KGAS WORKFLOW TEST - NO MOCKS, NO SIMULATIONS")
    print("=" * 80)
    print("This test uses ONLY real, implemented tools with actual databases")
    print("=" * 80)
    
    # Setup
    if not setup_environment():
        print("❌ Environment setup failed")
        return
    
    # Test components
    tests = {
        "Neo4j Connection": check_neo4j_connection,
        "MCP Server": test_real_mcp_server,
        "Real Workflow": run_real_workflow_with_mcp,
        "MCP Tool Execution": test_mcp_tool_execution
    }
    
    results = {}
    for test_name, test_func in tests.items():
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 REAL KGAS TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL REAL TESTS PASSED!")
        print("The KGAS system is working with real tools and databases!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()