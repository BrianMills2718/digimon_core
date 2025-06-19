"""Performance Profiling Test

Identifies bottlenecks in the workflow.
"""

import time
import os
import sys
from contextlib import contextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from src.tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow


@contextmanager
def timer(name):
    """Context manager for timing code blocks."""
    start = time.time()
    yield
    end = time.time()
    print(f"{name}: {end - start:.2f}s")


def profile_workflow():
    """Profile each step of the workflow."""
    pdf_path = "./examples/pdfs/wiki1.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found: {pdf_path}")
        return
    
    print("="*60)
    print("WORKFLOW PERFORMANCE PROFILING")
    print("="*60)
    print()
    
    workflow = VerticalSliceWorkflow()
    
    # Profile each tool separately
    print("Step-by-step profiling:")
    
    with timer("1. PDF Loading"):
        pdf_result = workflow.pdf_loader.load_pdf(pdf_path)
    
    if pdf_result["status"] == "success":
        doc = pdf_result["document"]
        
        with timer("2. Text Chunking"):
            chunk_result = workflow.text_chunker.chunk_text(
                document_ref=doc["document_ref"],
                text=doc["text"],
                document_confidence=doc["confidence"]
            )
        
        if chunk_result["status"] == "success":
            chunks = chunk_result["chunks"]
            
            all_entities = []
            with timer("3. Entity Extraction (all chunks)"):
                for chunk in chunks:
                    entity_result = workflow.entity_extractor.extract_entities(
                        chunk_ref=chunk["chunk_ref"],
                        text=chunk["text"],
                        chunk_confidence=chunk["confidence"]
                    )
                    if entity_result["status"] == "success":
                        all_entities.extend(entity_result["entities"])
            
            all_relationships = []
            with timer("4. Relationship Extraction (all chunks)"):
                for chunk in chunks:
                    chunk_entities = [e for e in all_entities if e["source_chunk"] == chunk["chunk_ref"]]
                    if len(chunk_entities) >= 2:
                        rel_result = workflow.relationship_extractor.extract_relationships(
                            chunk_ref=chunk["chunk_ref"],
                            text=chunk["text"],
                            entities=chunk_entities,
                            chunk_confidence=chunk["confidence"]
                        )
                        if rel_result["status"] == "success":
                            all_relationships.extend(rel_result["relationships"])
            
            with timer("5. Entity Building (Neo4j)"):
                entity_build_result = workflow.entity_builder.build_entities(
                    mentions=all_entities,
                    source_refs=[doc["document_ref"]]
                )
            
            with timer("6. Edge Building (Neo4j)"):
                edge_build_result = workflow.edge_builder.build_edges(
                    relationships=all_relationships,
                    source_refs=[doc["document_ref"]]
                )
            
            with timer("7. PageRank Calculation"):
                pagerank_result = workflow.pagerank_calculator.calculate_pagerank()
            
            with timer("8. Query Execution"):
                query_result = workflow.query_engine.query_graph(
                    query_text="What are the main entities?",
                    max_hops=2,
                    result_limit=10
                )
    
    workflow.close()
    
    print("\n" + "="*60)
    print("BOTTLENECK ANALYSIS")
    print("="*60)
    print("\nLikely bottlenecks:")
    print("1. Entity Extraction - Using spaCy NER on all chunks")
    print("2. Neo4j Operations - Multiple round trips to database")
    print("3. PageRank - Full graph computation")
    print("\nOptimization opportunities:")
    print("1. Batch Neo4j operations")
    print("2. Cache spaCy model loading")
    print("3. Parallel chunk processing")


if __name__ == "__main__":
    profile_workflow()