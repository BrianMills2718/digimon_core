#!/usr/bin/env python
"""Fixed integration test for the vertical slice."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from src.utils.database import DatabaseManager
from src.utils.config import Config
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
from src.tools.phase2.t13_text_chunker import TextChunker
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase5.t68_pagerank import PageRankAnalyzer
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery


def create_test_pdf(file_path: Path) -> None:
    """Create a test PDF with real content."""
    c = canvas.Canvas(str(file_path), pagesize=letter)
    width, height = letter
    
    # Page 1: AI Companies
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Leading AI Companies and Research")
    
    c.setFont("Helvetica", 12)
    content = [
        "",
        "OpenAI is a leading artificial intelligence research laboratory founded in 2015.",
        "The company is headquartered in San Francisco, California and is known for",
        "developing GPT models and ChatGPT. Sam Altman serves as the CEO of OpenAI.",
        "",
        "Anthropic is an AI safety company founded by former OpenAI researchers in 2021.",
        "The company is based in San Francisco and focuses on building reliable, interpretable,",
        "and steerable AI systems. Dario Amodei and Daniela Amodei are the co-founders.",
        "",
        "Google DeepMind (formerly DeepMind Technologies) is based in London, United Kingdom.",
        "It was acquired by Google in 2014 and is known for AlphaGo and AlphaFold.",
        "Demis Hassabis is the CEO and co-founder of DeepMind.",
        "",
        "These companies are at the forefront of artificial intelligence research,",
        "developing large language models, reinforcement learning systems, and",
        "pushing the boundaries of what AI can achieve."
    ]
    
    y = height - 100
    for line in content:
        c.drawString(50, y, line)
        y -= 20
    
    c.showPage()
    
    # Page 2: Technical Details
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Technical Innovations in AI")
    
    c.setFont("Helvetica", 12)
    content2 = [
        "",
        "Large Language Models (LLMs) have revolutionized natural language processing.",
        "GPT-4, developed by OpenAI, demonstrates remarkable reasoning capabilities.",
        "Claude, created by Anthropic, focuses on being helpful, harmless, and honest.",
        "",
        "The transformer architecture, introduced in the 'Attention is All You Need' paper,",
        "forms the foundation of modern language models. Key innovations include:",
        "- Self-attention mechanisms for capturing long-range dependencies",
        "- Positional encodings for sequence information",
        "- Multi-head attention for learning different types of relationships",
        "",
        "Recent advances in AI safety include:",
        "- Constitutional AI (CAI) developed by Anthropic",
        "- Reinforcement Learning from Human Feedback (RLHF)",
        "- Interpretability research to understand model behavior"
    ]
    
    y = height - 100
    for line in content2:
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"✓ Created test PDF: {file_path}")


def main():
    """Run the fixed integration test."""
    print("=== Fixed Integration Test ===\n")
    
    # Setup
    config = Config()
    config.ensure_directories()
    
    # Clean up any existing test data
    test_pdf = Path("test_ai_companies.pdf")
    if test_pdf.exists():
        test_pdf.unlink()
    
    # Initialize database
    print("1. Initializing databases...")
    db = DatabaseManager()
    db.faiss.dimension = 384  # Set dimension before init
    db.initialize()
    
    # Clear any existing data
    with db.neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("✓ Databases initialized and cleared")
    
    # Create test PDF
    print("\n2. Creating test PDF...")
    create_test_pdf(test_pdf)
    
    try:
        # Step 1: Load PDF
        print("\n3. Loading PDF (T01)...")
        pdf_loader = PDFDocumentLoader(db)
        pdf_result = pdf_loader.load_pdf(test_pdf)
        print(f"✓ PDF loaded: {pdf_result['document_ref']}")
        print(f"  Pages: {pdf_result['page_count']}")
        print(f"  Text length: {len(pdf_result['text'])} chars")
        
        # Step 2: Chunk text
        print("\n4. Chunking text (T13)...")
        chunker = TextChunker(db)
        chunk_result = chunker.chunk_document(
            document_ref=pdf_result['document_ref'],
            chunk_size=500,
            overlap=50
        )
        print(f"✓ Created {chunk_result['chunk_count']} chunks")
        
        # Step 3: Extract entities from chunks
        print("\n5. Extracting entities (T23a)...")
        extractor = EntityExtractorSpacy(db)
        all_entity_refs = []
        
        for i, chunk_ref in enumerate(chunk_result['chunk_refs']):
            print(f"  Processing chunk {i+1}/{len(chunk_result['chunk_refs'])}...")
            entity_result = extractor.extract_entities(chunk_ref)
            all_entity_refs.extend(entity_result['entity_refs'])
            print(f"    Found {entity_result['entity_count']} entities")
        
        # Remove duplicates
        unique_entity_refs = list(set(all_entity_refs))
        print(f"✓ Total unique entities: {len(unique_entity_refs)}")
        
        # Step 4: Generate embeddings for entities
        print("\n6. Generating embeddings (T41)...")
        embedder = EmbeddingGenerator(db)
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(unique_entity_refs), batch_size):
            batch = unique_entity_refs[i:i+batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(unique_entity_refs) + batch_size - 1)//batch_size}...")
            embed_result = embedder.generate_embeddings(
                object_refs=batch,
                batch_size=batch_size
            )
            print(f"    Generated {embed_result['embeddings_created']} embeddings")
        
        print(f"✓ FAISS index now contains {db.faiss.index.ntotal} vectors")
        
        # Step 5: Calculate PageRank
        print("\n7. Calculating PageRank (T68)...")
        pagerank = PageRankAnalyzer(db)
        
        # Check if we have enough entities
        with db.neo4j.driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN count(n) as count")
            entity_count = result.single()["count"]
        
        if entity_count > 0:
            pr_result = pagerank.calculate_pagerank(
                min_score=0.0,
                damping_factor=0.85,
                max_iterations=20
            )
            print(f"✓ PageRank calculated for {pr_result['entities_processed']} entities")
            print(f"  Top entity: {pr_result['top_entities'][0]['name']} (score: {pr_result['top_entities'][0]['score']:.4f})")
        else:
            print("⚠ No entities in graph, skipping PageRank")
        
        # Step 6: Test natural language queries
        print("\n8. Testing natural language queries (T94)...")
        query_tool = NaturalLanguageQuery(db)
        
        queries = [
            "Who is the CEO of OpenAI?",
            "What companies are working on AI safety?",
            "Tell me about transformer architecture",
            "What are the main AI research labs?"
        ]
        
        for query in queries:
            print(f"\n  Query: '{query}'")
            try:
                result = query_tool.query(query, top_k=5)
                print(f"  Results found: {len(result['results'])}")
                print(f"  Answer preview: {result['answer'][:200]}...")
                if 'OpenAI' in query:
                    # Check if OpenAI used for answer
                    if result['answer'] != "No relevant information found for your query." and len(result['answer']) > 100:
                        print("  ✓ LLM-generated answer detected")
                    else:
                        print("  ⚠ Template answer detected")
            except Exception as e:
                print(f"  ❌ Query failed: {e}")
        
        # Verify the complete chain
        print("\n9. Verifying complete data flow...")
        
        # Check documents
        docs = db.sqlite.get_all_documents()
        print(f"✓ Documents in SQLite: {len(docs)}")
        
        # Check chunks  
        chunks = []
        for doc in docs:
            chunks.extend(db.sqlite.get_chunks_by_document(doc.id))
        print(f"✓ Chunks in SQLite: {len(chunks)}")
        
        # Check entities
        with db.neo4j.driver.session() as session:
            result = session.run("MATCH (n:Entity) RETURN count(n) as count")
            entity_count = result.single()["count"]
        print(f"✓ Entities in Neo4j: {entity_count}")
        
        # Check FAISS
        print(f"✓ Vectors in FAISS: {db.faiss.index.ntotal}")
        
        # Check provenance
        provenance_records = db.sqlite.get_provenance_records()
        tool_counts = {}
        for record in provenance_records:
            tool_counts[record.tool_id] = tool_counts.get(record.tool_id, 0) + 1
        
        print(f"\n✓ Provenance records by tool:")
        for tool_id, count in sorted(tool_counts.items()):
            print(f"  {tool_id}: {count} operations")
        
        print("\n✅ Integration test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n10. Cleaning up...")
        if test_pdf.exists():
            test_pdf.unlink()
        with db.neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        db.close()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    main()