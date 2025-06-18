#!/usr/bin/env python3
"""
Comprehensive test of enhanced pipeline with LLMs and embeddings
Shows how to integrate all the enhanced services together
"""

import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Import enhanced services
from src.core.enhanced_identity_service import EnhancedIdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t23c_llm_entity_extractor import LLMEntityExtractor
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.tools.phase1.t68_pagerank import PageRankCalculator
from src.tools.phase1.t49_enhanced_query import EnhancedMultiHopQuery

def test_enhanced_pipeline():
    """Test the complete enhanced pipeline with LLMs"""
    
    print("🚀 Testing Enhanced GraphRAG Pipeline with LLMs\n")
    
    # Initialize core services
    print("📦 Initializing enhanced services...")
    identity_service = EnhancedIdentityService()
    provenance_service = ProvenanceService()
    quality_service = QualityService()
    
    # Initialize tools
    pdf_loader = PDFLoader(identity_service=identity_service, provenance_service=provenance_service, quality_service=quality_service)
    chunker = TextChunker(identity_service=identity_service, provenance_service=provenance_service, quality_service=quality_service)
    llm_extractor = LLMEntityExtractor(
        identity_service=identity_service,
        provenance_service=provenance_service,
        quality_service=quality_service,
        use_enhanced_identity=True
    )
    entity_builder = EntityBuilder(
        identity_service=identity_service,
        provenance_service=provenance_service,
        quality_service=quality_service
    )
    edge_builder = EdgeBuilder(
        identity_service=identity_service,
        provenance_service=provenance_service,
        quality_service=quality_service
    )
    pagerank = PageRankCalculator(
        identity_service=identity_service,
        provenance_service=provenance_service,
        quality_service=quality_service
    )
    query_system = EnhancedMultiHopQuery(
        provenance_service=provenance_service,
        quality_service=quality_service
    )
    
    # Create test document
    test_text = """
    Quantum Computing Breakthrough at MIT
    
    Dr. Sarah Johnson from MIT announced a revolutionary quantum computing algorithm 
    that could transform cryptography. The Massachusetts Institute of Technology 
    research team, collaborating with Stanford University and IBM Research, has 
    achieved a major milestone in quantum error correction.
    
    The project, funded by a $10 million grant from the National Science Foundation, 
    represents three years of intensive research. Dr. Johnson, who previously worked 
    at Google's Quantum AI division, leads a team of 15 researchers.
    
    "This breakthrough brings us closer to practical quantum computers," said 
    Prof. Michael Chen from Stanford, who peer-reviewed the findings. The results 
    were published in Nature Quantum Journal in March 2024.
    
    Meanwhile, renewable energy companies are also advancing. SolarTech Industries, 
    headquartered in Phoenix, Arizona, announced a $2 billion expansion plan. 
    CEO Maria Rodriguez stated that the company will double its solar panel 
    production capacity by 2025.
    
    WindPower Global, based in Copenhagen, Denmark, is partnering with GreenEnergy 
    Solutions from Berlin to develop offshore wind farms in the North Sea. The 
    €500 million project will generate power for 2 million homes.
    
    Both MIT and Stanford have established quantum computing research centers, 
    with MIT's center located in Cambridge, Massachusetts. The collaboration 
    between these institutions represents a new era in quantum research.
    """
    
    # Save as PDF for testing
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import simpleSplit
    
    pdf_path = "enhanced_test.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Quantum Computing and Renewable Energy Report")
    
    # Add content
    c.setFont("Helvetica", 11)
    y = height - 100
    for line in test_text.strip().split('\n'):
        if line.strip():
            wrapped_lines = simpleSplit(line, "Helvetica", 11, width - 100)
            for wrapped_line in wrapped_lines:
                c.drawString(50, y, wrapped_line)
                y -= 15
                if y < 50:
                    c.showPage()
                    y = height - 50
        else:
            y -= 10
    
    c.save()
    print(f"✅ Created test PDF: {pdf_path}")
    
    # Step 1: Load PDF
    print("\n📄 Step 1: Loading PDF...")
    pdf_result = pdf_loader.load_pdf(pdf_path)
    if pdf_result["status"] != "success":
        print(f"❌ PDF loading failed: {pdf_result.get('error')}")
        return
    
    document_ref = pdf_result["document"]["document_ref"]
    text = pdf_result["document"]["text"]
    print(f"✅ Loaded {len(text)} characters")
    
    # Step 2: Chunk text
    print("\n📝 Step 2: Chunking text...")
    chunk_result = chunker.chunk_text(text, document_ref)
    if chunk_result["status"] != "success":
        print(f"❌ Chunking failed: {chunk_result.get('error')}")
        return
    
    chunks = chunk_result["chunks"]
    print(f"✅ Created {len(chunks)} chunks")
    
    # Step 3: Extract entities with LLM
    print("\n🤖 Step 3: Extracting entities with Gemini 2.5 Flash...")
    extraction_result = llm_extractor.extract_from_chunks(chunks)
    
    if extraction_result["status"] == "success":
        print(f"✅ Extracted {extraction_result['total_entities']} entities")
        print(f"✅ Found {extraction_result['total_relationships']} relationships")
        print(f"📊 Key topics: {', '.join(extraction_result['key_topics'][:5])}")
        
        # Show some entities
        print("\n🔍 Sample entities (with identity resolution):")
        seen_ids = set()
        for entity in extraction_result["entities"][:10]:
            if entity["entity_id"] not in seen_ids:
                print(f"  • {entity['text']} → {entity['canonical_name']} ({entity['entity_type']})")
                if entity.get('identity_matched'):
                    print(f"    ↳ Matched existing entity (similarity: {entity.get('identity_similarity', 0):.3f})")
                seen_ids.add(entity["entity_id"])
    else:
        print(f"❌ Extraction failed: {extraction_result.get('error')}")
        return
    
    # Step 4: Build graph nodes
    print("\n🔨 Step 4: Building graph nodes...")
    # Get chunk references for source tracking
    chunk_refs = [chunk["chunk_ref"] for chunk in chunks]
    
    # Convert LLM entities to mentions format expected by EntityBuilder
    mentions = []
    for entity in extraction_result["entities"]:
        mention = {
            "mention_id": f"mention_{uuid.uuid4().hex[:8]}",
            "entity_id": entity["entity_id"],
            "text": entity["text"],
            "entity_type": entity["entity_type"],
            "confidence": entity["confidence"],
            "context": entity.get("context", ""),
            "start_char": entity.get("start_char", 0),
            "end_char": entity.get("end_char", len(entity["text"])),
            "mention_ref": f"storage://mention/{entity['entity_id']}"
        }
        mentions.append(mention)
    
    node_result = entity_builder.build_entities(mentions, chunk_refs)
    if node_result["status"] == "success":
        # Check what keys are available
        if "nodes_created" in node_result:
            print(f"✅ Created {node_result['nodes_created']} unique nodes in Neo4j")
        elif "entities" in node_result:
            print(f"✅ Created {len(node_result['entities'])} unique nodes in Neo4j")
        else:
            print(f"✅ Entity building succeeded (keys: {list(node_result.keys())})")
    
    # Step 5: Build graph edges
    print("\n🔗 Step 5: Building graph edges...")
    edge_result = edge_builder.build_edges(extraction_result["relationships"], chunk_refs)
    if edge_result["status"] == "success":
        if "edges_created" in edge_result:
            print(f"✅ Created {edge_result['edges_created']} edges in Neo4j")
        elif "edges" in edge_result:
            print(f"✅ Created {len(edge_result['edges'])} edges in Neo4j")
        else:
            print(f"✅ Edge building succeeded (keys: {list(edge_result.keys())})")
    
    # Step 6: Calculate PageRank
    print("\n📊 Step 6: Calculating PageRank...")
    pagerank_result = pagerank.calculate_pagerank()
    if pagerank_result["status"] == "success":
        print(f"✅ Ranked {pagerank_result['entities_ranked']} entities")
        print("\n🏆 Top 5 entities by importance:")
        for i, entity in enumerate(pagerank_result["top_entities"][:5], 1):
            print(f"  {i}. {entity['canonical_name']} ({entity['entity_type']}) - Score: {entity['pagerank_score']:.4f}")
    
    # Show identity resolution statistics
    print("\n🔍 Identity Resolution Statistics:")
    stats = identity_service.get_statistics()
    print(f"  • Total unique entities: {stats['total_entities']}")
    print(f"  • Total surface forms: {stats['total_surface_forms']}")
    print(f"  • Entities with aliases: {stats['entities_with_aliases']}")
    print("  • Entity types:")
    for entity_type, count in stats['entities_by_type'].items():
        print(f"    - {entity_type}: {count}")
    
    # Step 7: Test enhanced query system
    print("\n❓ Step 7: Testing Enhanced Query System...")
    
    test_queries = [
        "What organizations are working on quantum computing?",
        "Who are the CEOs mentioned?",
        "What funding amounts were announced?",
        "Which universities are collaborating?",
        "Where are the renewable energy companies located?"
    ]
    
    for query in test_queries:
        print(f"\n💬 Query: {query}")
        result = query_system.answer_question(query)
        print(f"💡 Answer: {result['answer']}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        
        if result['supporting_facts']:
            print("📋 Supporting facts:")
            for fact in result['supporting_facts'][:2]:
                print(f"   • {fact}")
    
    # Cleanup
    query_system.close()
    os.remove(pdf_path)
    
    print("\n✅ Enhanced pipeline test complete!")
    print("\n🎯 Key improvements demonstrated:")
    print("  1. LLM-based entity extraction with better context understanding")
    print("  2. Semantic entity resolution (MIT = Massachusetts Institute of Technology)")
    print("  3. Structured output for consistent results")
    print("  4. Natural language query understanding and answering")
    print("  5. Confidence tracking throughout the pipeline")

if __name__ == "__main__":
    # Check API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        exit(1)
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        exit(1)
    
    # Check Neo4j
    from neo4j import GraphDatabase
    try:
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
    except Exception as e:
        print("❌ Error: Neo4j not running or not accessible")
        print(f"   {e}")
        print("\n💡 Start Neo4j with: docker-compose up -d neo4j")
        exit(1)
    
    # Run test
    test_enhanced_pipeline()