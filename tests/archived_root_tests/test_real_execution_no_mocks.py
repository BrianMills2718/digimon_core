#!/usr/bin/env python3
"""
REAL Execution Test - No Mocks, Real Tools, Real Databases, Real API Calls
This will either work with realistic timing or fail loudly
"""

import sys
sys.path.append('src')

import asyncio
import time
import os
from datetime import datetime
import traceback

# Real imports - these will fail if not properly configured
from src.core.service_manager import ServiceManager
from src.core.enhanced_api_client import EnhancedAPIClient
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.core.neo4j_manager import Neo4jManager
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()

async def test_real_execution():
    """Test real execution with actual tools, databases, and API calls"""
    
    print("🎯 REAL EXECUTION TEST - NO MOCKS")
    print("=" * 80)
    print("This will use:")
    print("  - Real Neo4j database connections")
    print("  - Real SQLite database operations")
    print("  - Real LLM API calls (OpenAI/Anthropic)")
    print("  - Real spaCy NLP processing")
    print("  - Real file I/O operations")
    print("=" * 80)
    
    start_time = time.time()
    
    # Check API keys
    print("\n📋 Checking API Keys...")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("❌ No API keys found! Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        print("   Real LLM calls will fail!")
    else:
        print(f"✅ API keys found: OpenAI={bool(openai_key)}, Anthropic={bool(anthropic_key)}")
    
    # Initialize real service manager
    print("\n📋 Initializing Service Manager...")
    try:
        service_manager = ServiceManager()
        print("✅ Service Manager initialized")
    except Exception as e:
        print(f"❌ Service Manager failed: {e}")
        traceback.print_exc()
        return
    
    # Test Neo4j connection
    print("\n📋 Testing Neo4j Connection...")
    try:
        neo4j_manager = Neo4jManager()
        # This will fail if Neo4j is not running
        with neo4j_manager.driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_val = result.single()["test"]
            print(f"✅ Neo4j connected and responding: {test_val}")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("   Make sure Neo4j is running on bolt://localhost:7687")
        # Continue anyway to show other failures
    
    # Test SQLite operations
    print("\n📋 Testing SQLite Operations...")
    try:
        # Real identity service operations
        mention_result = service_manager.identity_service.create_mention(
            surface_form="Test Entity",
            start_pos=0,
            end_pos=11,
            source_ref="test_doc",
            entity_type="TEST",
            confidence=0.9
        )
        if mention_result.success:
            print(f"✅ SQLite operations working: {mention_result.data}")
        else:
            print(f"❌ SQLite operation failed: {mention_result.error}")
    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        traceback.print_exc()
    
    # Create test document
    test_text = """
    Stanford University announced a breakthrough in quantum computing research.
    Dr. Sarah Chen, lead researcher at Stanford's Quantum Lab, demonstrated
    a new quantum algorithm that achieves 100x speedup over classical methods.
    The research was funded by Google, Microsoft, and the NSF with a $50M grant.
    MIT researchers confirmed the results in independent testing.
    """
    
    print("\n🔧 EXECUTING REAL TOOL CHAIN")
    print("=" * 60)
    
    tool_results = []
    
    # Tool 1: Real text chunking
    print("\n1️⃣ Text Chunking (T15A)...")
    chunk_start = time.time()
    try:
        chunker = T15ATextChunkerUnified(service_manager)
        from src.tools.base_tool import ToolRequest
        
        chunk_request = ToolRequest(
            tool_id="T15A",
            operation="chunk_text",
            input_data={
                "text": test_text,
                "document_ref": "quantum_research",
                "document_confidence": 0.95
            },
            parameters={"chunk_size": 100, "overlap": 20}
        )
        
        chunk_result = chunker.execute(chunk_request)
        chunk_time = time.time() - chunk_start
        
        if chunk_result.status == "success":
            print(f"✅ Chunking completed in {chunk_time:.3f}s")
            print(f"   Created {len(chunk_result.data['chunks'])} chunks")
            tool_results.append(("chunking", chunk_time, "success"))
        else:
            print(f"❌ Chunking failed: {chunk_result.error_message}")
            tool_results.append(("chunking", chunk_time, "failed"))
            
    except Exception as e:
        print(f"❌ Chunking error: {e}")
        traceback.print_exc()
        tool_results.append(("chunking", time.time() - chunk_start, "error"))
    
    # Tool 2: Real spaCy NER extraction
    print("\n2️⃣ spaCy Entity Extraction (T23A)...")
    ner_start = time.time()
    try:
        # This will use real spaCy model loading and processing
        ner_extractor = T23ASpacyNERUnified(service_manager)
        
        ner_request = ToolRequest(
            tool_id="T23A",
            operation="extract_entities",
            input_data={
                "text": chunk_result.data['chunks'][0]['text'] if 'chunk_result' in locals() else test_text,
                "chunk_ref": "chunk_0"
            },
            parameters={}
        )
        
        ner_result = ner_extractor.execute(ner_request)
        ner_time = time.time() - ner_start
        
        if ner_result.status == "success":
            print(f"✅ NER extraction completed in {ner_time:.3f}s")
            print(f"   Found {len(ner_result.data['entities'])} entities")
            tool_results.append(("spacy_ner", ner_time, "success"))
        else:
            print(f"❌ NER extraction failed: {ner_result.error_message}")
            tool_results.append(("spacy_ner", ner_time, "failed"))
            
    except Exception as e:
        print(f"❌ NER extraction error: {e}")
        traceback.print_exc()
        tool_results.append(("spacy_ner", time.time() - ner_start, "error"))
    
    # Tool 3: Real LLM API call for ontology-aware extraction
    print("\n3️⃣ LLM Entity Extraction (T23C)...")
    llm_start = time.time()
    try:
        # This will make REAL API calls to OpenAI/Anthropic
        ontology_extractor = OntologyAwareExtractor(
            identity_service=service_manager.identity_service
        )
        
        # Create a simple ontology for testing
        from src.ontology_generator import DomainOntology
        test_ontology = DomainOntology(
            domain="quantum_computing",
            entity_types=["PERSON", "ORGANIZATION", "TECHNOLOGY", "FUNDING"],
            relationships=["WORKS_AT", "FUNDED_BY", "RESEARCHES"],
            constraints={}
        )
        
        extraction_result = ontology_extractor.extract_entities(
            text_content=test_text,
            ontology=test_ontology,
            source_ref="quantum_doc",
            confidence_threshold=0.7
        )
        
        llm_time = time.time() - llm_start
        
        if extraction_result:
            print(f"✅ LLM extraction completed in {llm_time:.3f}s")
            print(f"   Found {extraction_result.total_entities} entities")
            print(f"   API call took realistic time: {llm_time:.1f}s")
            tool_results.append(("llm_extraction", llm_time, "success"))
        else:
            print(f"❌ LLM extraction failed")
            tool_results.append(("llm_extraction", llm_time, "failed"))
            
    except Exception as e:
        print(f"❌ LLM extraction error: {e}")
        print("   This is likely due to missing API keys or API errors")
        traceback.print_exc()
        tool_results.append(("llm_extraction", time.time() - llm_start, "error"))
    
    # Tool 4: Real Neo4j graph building
    print("\n4️⃣ Neo4j Graph Building (T31)...")
    graph_start = time.time()
    try:
        from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
        
        entity_builder = T31EntityBuilderUnified(service_manager)
        
        # Prepare entities for graph building
        entities_to_build = []
        if 'ner_result' in locals() and ner_result.status == "success":
            entities_to_build = ner_result.data['entities']
        elif 'extraction_result' in locals() and extraction_result:
            entities_to_build = extraction_result.entities
        
        if entities_to_build:
            build_request = ToolRequest(
                tool_id="T31",
                operation="build_entities",
                input_data={
                    "entities": entities_to_build,
                    "source_refs": ["quantum_research"]
                },
                parameters={}
            )
            
            build_result = entity_builder.execute(build_request)
            graph_time = time.time() - graph_start
            
            if build_result.status == "success":
                print(f"✅ Graph building completed in {graph_time:.3f}s")
                print(f"   Created {build_result.data.get('nodes_created', 0)} nodes")
                tool_results.append(("graph_building", graph_time, "success"))
            else:
                print(f"❌ Graph building failed: {build_result.error_message}")
                tool_results.append(("graph_building", graph_time, "failed"))
        else:
            print("❌ No entities to build into graph")
            tool_results.append(("graph_building", time.time() - graph_start, "no_data"))
            
    except Exception as e:
        print(f"❌ Graph building error: {e}")
        traceback.print_exc()
        tool_results.append(("graph_building", time.time() - graph_start, "error"))
    
    # Tool 5: Real PageRank calculation on Neo4j
    print("\n5️⃣ PageRank Calculation (T68)...")
    pagerank_start = time.time()
    try:
        from src.tools.phase1.t68_pagerank_calculator_unified import T68PageRankCalculatorUnified
        
        pagerank_calc = T68PageRankCalculatorUnified(service_manager)
        
        pagerank_request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={},
            parameters={"damping_factor": 0.85, "iterations": 20}
        )
        
        pagerank_result = pagerank_calc.execute(pagerank_request)
        pagerank_time = time.time() - pagerank_start
        
        if pagerank_result.status == "success":
            print(f"✅ PageRank completed in {pagerank_time:.3f}s")
            print(f"   Calculated scores for {len(pagerank_result.data.get('scores', {}))} nodes")
            tool_results.append(("pagerank", pagerank_time, "success"))
        else:
            print(f"❌ PageRank failed: {pagerank_result.error_message}")
            tool_results.append(("pagerank", pagerank_time, "failed"))
            
    except Exception as e:
        print(f"❌ PageRank error: {e}")
        traceback.print_exc()
        tool_results.append(("pagerank", time.time() - pagerank_start, "error"))
    
    # Continue with more tools...
    # Tool 6: Multi-hop query
    print("\n6️⃣ Multi-hop Query (T49)...")
    query_start = time.time()
    try:
        from src.tools.phase1.t49_multihop_query_unified import T49MultiHopQueryUnified
        
        query_tool = T49MultiHopQueryUnified(service_manager)
        
        query_request = ToolRequest(
            tool_id="T49",
            operation="query_graph",
            input_data={
                "query": "Stanford quantum research",
                "start_entities": ["Stanford University"] if entities_to_build else []
            },
            parameters={"max_hops": 2}
        )
        
        query_result = query_tool.execute(query_request)
        query_time = time.time() - query_start
        
        if query_result.status == "success":
            print(f"✅ Query completed in {query_time:.3f}s")
            print(f"   Found {len(query_result.data.get('paths', []))} paths")
            tool_results.append(("multihop_query", query_time, "success"))
        else:
            print(f"❌ Query failed: {query_result.error_message}")
            tool_results.append(("multihop_query", query_time, "failed"))
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        traceback.print_exc()
        tool_results.append(("multihop_query", time.time() - query_start, "error"))
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📊 REAL EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total execution time: {total_time:.2f}s")
    print(f"Tools executed: {len(tool_results)}")
    
    print("\n📋 Tool Results:")
    successful = 0
    for tool_name, exec_time, status in tool_results:
        emoji = "✅" if status == "success" else "❌"
        print(f"  {emoji} {tool_name}: {exec_time:.3f}s ({status})")
        if status == "success":
            successful += 1
    
    print(f"\nSuccess rate: {successful}/{len(tool_results)} ({successful/len(tool_results)*100:.0f}%)")
    
    print("\n💡 Key Observations:")
    print("  - Real execution times (not mocked)")
    print("  - LLM API calls take several seconds")
    print("  - Database operations have real latency")
    print("  - Failures are loud and clear")
    
    # Test pipeline orchestrator for full workflow
    print("\n" + "=" * 80)
    print("🔗 TESTING FULL PIPELINE ORCHESTRATOR")
    print("=" * 80)
    
    pipeline_start = time.time()
    try:
        orchestrator = PipelineOrchestrator(service_manager)
        
        # Create a test PDF path (would need real PDF)
        test_pdf = "test_data/sample.pdf"
        
        print(f"Attempting to process: {test_pdf}")
        if not os.path.exists(test_pdf):
            print(f"❌ Test PDF not found at {test_pdf}")
            print("   Would fail with FileNotFoundError in real execution")
        else:
            # This would process a real PDF through the entire pipeline
            result = await orchestrator.process_documents_async(
                document_paths=[test_pdf],
                queries=["What are the main findings?"],
                confidence_threshold=0.7
            )
            
            pipeline_time = time.time() - pipeline_start
            print(f"✅ Pipeline completed in {pipeline_time:.2f}s")
            
    except Exception as e:
        pipeline_time = time.time() - pipeline_start
        print(f"❌ Pipeline failed after {pipeline_time:.2f}s: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting real execution test...")
    print("⚠️  This will make real API calls and database connections")
    print("⚠️  Ensure you have:")
    print("    - Neo4j running on localhost:7687")
    print("    - API keys set (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    print("    - Network connectivity")
    print()
    
    asyncio.run(test_real_execution())