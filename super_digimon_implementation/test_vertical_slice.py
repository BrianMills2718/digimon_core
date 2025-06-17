#!/usr/bin/env python
"""Test the complete vertical slice: PDF → PageRank → Answer."""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.database import DatabaseManager

# Import all tools for vertical slice
from src.tools.phase1 import PDFDocumentLoader
from src.tools.phase2 import TextChunker, EntityExtractorSpacy
from src.tools.phase3 import EmbeddingGenerator
from src.tools.phase5 import PageRankAnalyzer
from src.tools.phase7 import NaturalLanguageQuery


def create_test_pdf(file_path: Path) -> None:
    """Create a test PDF file."""
    import fitz  # PyMuPDF
    
    # Create a new PDF
    doc = fitz.open()
    
    # Add a page with content
    page = doc.new_page()
    
    # Sample content about companies and technology
    content = """
    Technology Industry Report
    
    Apple Inc. is a leading technology company headquartered in Cupertino, California.
    The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    Apple is known for its innovative products including the iPhone, iPad, and Mac computers.
    
    Microsoft Corporation, founded by Bill Gates and Paul Allen, is another major player
    in the technology industry. Based in Redmond, Washington, Microsoft develops the
    Windows operating system and Office productivity suite.
    
    Google, now part of Alphabet Inc., was founded by Larry Page and Sergey Brin while
    they were PhD students at Stanford University. The company revolutionized internet
    search and now offers a wide range of products and services.
    
    Amazon.com, founded by Jeff Bezos in 1994, started as an online bookstore but has
    grown into one of the world's largest e-commerce and cloud computing companies.
    Amazon Web Services (AWS) is a leader in cloud infrastructure.
    
    These companies, often referred to as "Big Tech," have significantly influenced
    the global technology landscape and continue to drive innovation in areas such as
    artificial intelligence, cloud computing, and consumer electronics.
    """
    
    # Insert text
    text_rect = fitz.Rect(50, 50, 550, 750)
    page.insert_textbox(
        text_rect,
        content,
        fontsize=12,
        fontname="helv"
    )
    
    # Save PDF
    doc.save(str(file_path))
    doc.close()
    print(f"✓ Created test PDF: {file_path}")


def test_vertical_slice():
    """Test the complete vertical slice workflow."""
    print("🚀 Testing Vertical Slice: PDF → PageRank → Answer")
    print("=" * 60)
    
    # Setup
    config = Config()
    config.sqlite_db_path = Path("./data/test_vertical_slice.db")
    config.faiss_index_path = Path("./data/test_vertical_faiss")
    config.checkpoint_dir = Path("./data/test_vertical_checkpoints")
    config.ensure_directories()
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    
    # Create test PDF
    test_pdf = Path("./data/test_document.pdf")
    test_pdf.parent.mkdir(parents=True, exist_ok=True)
    create_test_pdf(test_pdf)
    
    # Initialize tools
    pdf_loader = PDFDocumentLoader(db_manager)
    text_chunker = TextChunker(db_manager)
    entity_extractor = EntityExtractorSpacy(db_manager)
    embedding_generator = EmbeddingGenerator(db_manager)
    pagerank_analyzer = PageRankAnalyzer(db_manager)
    query_tool = NaturalLanguageQuery(db_manager)
    
    try:
        # Step 1: Load PDF
        print("\n📄 Step 1: Loading PDF document...")
        pdf_result = pdf_loader.load_pdf(
            str(test_pdf),
            metadata={"source": "test", "type": "industry_report"}
        )
        print(f"✓ Loaded document: {pdf_result['document_ref']}")
        print(f"  - Pages: {pdf_result['page_count']}")
        print(f"  - Confidence: {pdf_result['confidence']:.2f}")
        
        # Step 2: Chunk document
        print("\n✂️ Step 2: Chunking document...")
        chunk_result = text_chunker.chunk_document(
            pdf_result['document_ref'],
            chunk_size=500,
            overlap=100,
            text_content=pdf_result['text']
        )
        print(f"✓ Created {chunk_result['chunk_count']} chunks")
        print(f"  - Confidence: {chunk_result['confidence']:.2f}")
        
        # Step 3: Extract entities from chunks
        print("\n🔍 Step 3: Extracting entities...")
        all_entity_refs = []
        all_chunk_refs = []
        
        for chunk_ref in chunk_result['chunk_refs']:
            try:
                entity_result = entity_extractor.extract_entities(chunk_ref)
                all_entity_refs.extend(entity_result['entity_refs'])
                all_chunk_refs.append(chunk_ref)
                print(f"  - Found {entity_result['entity_count']} entities in chunk")
            except Exception as e:
                print(f"  ⚠️ Failed to extract from chunk: {e}")
        
        unique_entities = len(set(all_entity_refs))
        print(f"✓ Extracted {unique_entities} unique entities total")
        
        # Step 4: Generate embeddings
        print("\n🧮 Step 4: Generating embeddings...")
        
        # Embed entities
        if all_entity_refs:
            entity_embedding_result = embedding_generator.generate_embeddings(
                list(set(all_entity_refs))  # Unique entities only
            )
            print(f"✓ Generated {entity_embedding_result['embedding_count']} entity embeddings")
        
        # Embed chunks
        chunk_embedding_result = embedding_generator.generate_embeddings(
            all_chunk_refs
        )
        print(f"✓ Generated {chunk_embedding_result['embedding_count']} chunk embeddings")
        
        # Step 5: Calculate PageRank
        print("\n📊 Step 5: Computing PageRank...")
        pagerank_result = pagerank_analyzer.compute_pagerank(
            damping_factor=0.85,
            max_iterations=20
        )
        print(f"✓ Computed PageRank for {len(pagerank_result['scores'])} entities")
        
        # Show top entities
        print("\n🏆 Top Entities by PageRank:")
        for i, entity in enumerate(pagerank_result['top_entities'][:5], 1):
            print(f"  {i}. {entity['name']} ({entity['type']}) - Score: {entity['score']:.4f}")
        
        # Step 6: Test natural language query
        print("\n💬 Step 6: Testing natural language queries...")
        
        test_queries = [
            "What technology companies are mentioned?",
            "Who founded Apple?",
            "Tell me about cloud computing",
            "Which companies are considered Big Tech?"
        ]
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            
            query_result = query_tool.query(
                query,
                top_k=3
            )
            
            print(f"✓ Found {len(query_result['results'])} results")
            print(f"  - Confidence: {query_result['confidence']:.2f}")
            
            # Show top result
            if query_result['results']:
                top = query_result['results'][0]
                print(f"  - Top match: {top['content'][:100]}...")
                print(f"    Score: {top['combined_score']:.3f}")
            
            # Show answer
            print(f"\n📝 Answer:")
            print(query_result['answer'][:500] + "..." if len(query_result['answer']) > 500 else query_result['answer'])
        
        # Step 7: Verify provenance chain
        print("\n🔗 Step 7: Verifying provenance chain...")
        
        # Get provenance records
        provenance_records = db_manager.sqlite.get_provenance_records()
        print(f"✓ Total operations tracked: {len(provenance_records)}")
        
        # Count by tool
        tool_counts = {}
        for record in provenance_records:
            tool_counts[record.tool_id] = tool_counts.get(record.tool_id, 0) + 1
        
        print("\n📊 Operations by tool:")
        for tool_id, count in sorted(tool_counts.items()):
            print(f"  - {tool_id}: {count} operations")
        
        # Step 8: Check workflow state
        print("\n💾 Step 8: Checking workflow state...")
        
        checkpoints = db_manager.sqlite.list_checkpoints()
        if checkpoints:
            print(f"✓ Found {len(checkpoints)} workflow checkpoints")
            latest = checkpoints[0]
            print(f"  - Latest: {latest.workflow_type} at step {latest.step_number}/{latest.total_steps}")
        else:
            print("  - No checkpoints created (workflow completed without interruption)")
        
        print("\n✅ Vertical slice test completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during vertical slice test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        
        # Clean Neo4j
        with db_manager.neo4j.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        db_manager.close()
        
        # Clean files
        if test_pdf.exists():
            test_pdf.unlink()
        if config.sqlite_db_path.exists():
            config.sqlite_db_path.unlink()
        if config.faiss_index_path.exists():
            config.faiss_index_path.unlink()
        
        print("✓ Cleanup complete")


if __name__ == "__main__":
    # Wait for services
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    # Run test
    test_vertical_slice()