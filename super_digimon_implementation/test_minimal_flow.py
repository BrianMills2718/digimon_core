#!/usr/bin/env python
"""Minimal test to verify the complete flow works."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.utils.database import DatabaseManager
from src.tools.phase1.t01_pdf_loader import PDFDocumentLoader
from src.tools.phase2.t13_text_chunker import TextChunker
from src.tools.phase2.t23a_entity_extractor import EntityExtractorSpacy
from src.tools.phase3.t41_embedding_generator import EmbeddingGenerator
from src.tools.phase7.t94_natural_language_query import NaturalLanguageQuery


def main():
    """Run minimal flow test."""
    print("=== Minimal Flow Test ===\n")
    
    # Initialize database
    print("1. Initializing database...")
    db = DatabaseManager()
    db.faiss.dimension = 384
    db.initialize()
    
    # Clear Neo4j
    with db.neo4j.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    
    try:
        # Create a minimal test PDF
        from reportlab.pdfgen import canvas
        test_pdf = Path("minimal_test.pdf")
        c = canvas.Canvas(str(test_pdf))
        c.drawString(100, 750, "OpenAI created GPT-4. Anthropic built Claude.")
        c.save()
        print("✓ Created test PDF")
        
        # Step 1: Load PDF
        print("\n2. Loading PDF...")
        loader = PDFDocumentLoader(db)
        pdf_result = loader.load_pdf(test_pdf)
        doc_ref = pdf_result['document_ref']
        print(f"✓ Document: {doc_ref}")
        
        # Step 2: Create ONE chunk
        print("\n3. Creating chunk...")
        chunker = TextChunker(db)
        chunk_result = chunker.chunk_document(doc_ref, chunk_size=1000)  # One big chunk
        chunk_ref = chunk_result['chunk_refs'][0]
        print(f"✓ Chunk: {chunk_ref}")
        
        # Step 3: Extract entities
        print("\n4. Extracting entities...")
        extractor = EntityExtractorSpacy(db)
        entity_result = extractor.extract_entities(chunk_ref)
        print(f"✓ Found {entity_result['entity_count']} entities")
        for ref in entity_result['entity_refs'][:3]:
            print(f"  - {ref}")
        
        # Step 4: Generate embeddings
        print("\n5. Generating embeddings...")
        embedder = EmbeddingGenerator(db)
        if entity_result['entity_refs']:
            embed_result = embedder.generate_embeddings(
                object_refs=entity_result['entity_refs'][:5]  # Just first 5
            )
            print(f"✓ Created {embed_result['embeddings_created']} embeddings")
            print(f"  FAISS total: {db.faiss.index.ntotal}")
        
        # Step 5: Test query
        print("\n6. Testing query...")
        query_tool = NaturalLanguageQuery(db)
        result = query_tool.query("What company created GPT-4?")
        print(f"✓ Results: {len(result['results'])}")
        print(f"Answer preview: {result['answer'][:200]}...")
        
        # Check if LLM was used
        if "Based on the available information:" in result['answer']:
            print("⚠ Template answer detected")
        else:
            print("✓ LLM answer detected")
        
        # Verify data flow
        print("\n7. Verifying data flow...")
        
        # Check SQLite
        docs = db.sqlite.get_all_documents()
        print(f"Documents: {len(docs)}")
        
        # Check Neo4j
        with db.neo4j.driver.session() as session:
            r = session.run("MATCH (n:Entity) RETURN count(n) as count")
            print(f"Entities: {r.single()['count']}")
        
        # Check FAISS
        print(f"Vectors: {db.faiss.index.ntotal}")
        
        print("\n✅ Minimal flow test completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'test_pdf' in locals() and test_pdf.exists():
            test_pdf.unlink()
        with db.neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        db.close()


if __name__ == "__main__":
    main()