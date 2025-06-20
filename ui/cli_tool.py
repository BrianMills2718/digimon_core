#!/usr/bin/env python3
"""Command-line tool for Super-Digimon GraphRAG System"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
from neo4j import GraphDatabase
import json


def check_neo4j():
    """Check Neo4j connection."""
    try:
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True, "Connected"
    except Exception as e:
        return False, str(e)


def process_documents(document_paths: list, query: str, output_format: str = "text"):
    """Process documents and answer a query."""
    print(f"\n📄 Processing: {', '.join(document_paths)}")
    print(f"❓ Query: {query}")
    print("-" * 60)
    
    # Check if files exist
    for doc_path in document_paths:
        if not os.path.exists(doc_path):
            print(f"❌ Error: File not found: {doc_path}")
            return
    
    # Initialize workflow
    print("🔧 Initializing workflow...")
    workflow = VerticalSliceWorkflow(workflow_storage_dir="./data/cli_workflows")
    
    # Execute workflow
    print("⚙️  Processing (this may take 1-3 minutes)...")
    result = workflow.execute_workflow(
        document_paths=document_paths,
        queries=[query],
        workflow_name=f"CLI_{Path(document_paths[0]).stem}"
    )
    
    # Display results
    if result["status"] == "success":
        print("\n✅ Processing complete!")
        
        # Summary
        if "workflow_summary" in result:
            summary = result["workflow_summary"]
            print(f"\n📊 Summary:")
            print(f"  • Chunks created: {summary.get('chunks_created', 0)}")
            print(f"  • Entities extracted: {summary.get('entities_extracted', 0)}")
            print(f"  • Relationships found: {summary.get('relationships_found', 0)}")
            print(f"  • Graph entities: {summary.get('graph_entities', 0)}")
            print(f"  • Graph edges: {summary.get('graph_edges', 0)}")
        
        # Query results
        if "query_result" in result:
            query_result = result["query_result"]
            
            print(f"\n🎯 Query Results:")
            if query_result.get("results"):
                for i, answer in enumerate(query_result["results"][:5], 1):
                    print(f"\n{i}. {answer.get('answer_entity', 'N/A')}")
                    print(f"   Confidence: {answer.get('confidence', 0):.2f}")
                    if "evidence" in answer:
                        print(f"   Evidence: {answer['evidence'][:100]}...")
            else:
                print("   No direct answers found.")
            
            # Top entities
            if query_result.get("top_entities"):
                print(f"\n🏆 Top Entities by PageRank:")
                for entity in query_result["top_entities"][:10]:
                    print(f"  • {entity.get('name', 'N/A')} ({entity.get('type', 'UNK')}) - Score: {entity.get('pagerank_score', 0):.4f}")
        
        # Save results if requested
        if output_format == "json":
            output_file = f"{Path(document_paths[0]).stem}_results.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
    
    else:
        print(f"\n❌ Processing failed: {result.get('error', 'Unknown error')}")
        if "traceback" in result:
            print("\nTraceback:")
            print(result["traceback"])


def show_graph_stats():
    """Show statistics about the graph database."""
    neo4j_ok, status = check_neo4j()
    if not neo4j_ok:
        print(f"❌ Neo4j not connected: {status}")
        return
    
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    
    with driver.session() as session:
        # Count entities
        entity_result = session.run("MATCH (e:Entity) RETURN count(e) as count, collect(DISTINCT e.entity_type) as types")
        entity_record = entity_result.single()
        
        # Count relationships
        rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count, collect(DISTINCT type(r)) as types")
        rel_record = rel_result.single()
        
        # Top entities by PageRank
        top_result = session.run("""
            MATCH (e:Entity)
            RETURN e.canonical_name as name, e.entity_type as type, e.pagerank_score as score
            ORDER BY e.pagerank_score DESC
            LIMIT 10
        """)
        
        print("\n📊 Graph Database Statistics")
        print("=" * 40)
        print(f"Total Entities: {entity_record['count']}")
        print(f"Entity Types: {', '.join(entity_record['types'])}")
        print(f"\nTotal Relationships: {rel_record['count']}")
        print(f"Relationship Types: {', '.join(rel_record['types'])}")
        
        print("\n🏆 Top 10 Entities by PageRank:")
        for record in top_result:
            score = record['score'] if record['score'] is not None else 0.0
            print(f"  • {record['name']} ({record['type']}) - Score: {score:.4f}")
    
    driver.close()


def main():
    parser = argparse.ArgumentParser(description="Super-Digimon GraphRAG CLI Tool")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process documents and answer a query')
    process_parser.add_argument('document_paths', nargs='+', help='Path(s) to the document file(s)')
    process_parser.add_argument('query', help='Question to answer about the documents')
    process_parser.add_argument('--json', action='store_true', help='Save results as JSON')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show graph database statistics')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check system status')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        process_documents(args.document_paths, args.query, 'json' if args.json else 'text')
    
    elif args.command == 'stats':
        show_graph_stats()
    
    elif args.command == 'check':
        print("🔍 System Status Check")
        print("=" * 40)
        
        # Check Neo4j
        neo4j_ok, status = check_neo4j()
        if neo4j_ok:
            print("✅ Neo4j: Connected")
        else:
            print(f"❌ Neo4j: {status}")
        
        # Check imports
        try:
            from tools.phase1.vertical_slice_workflow import VerticalSliceWorkflow
            print("✅ Workflow: Available")
        except Exception as e:
            print(f"❌ Workflow: {e}")
        
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy: Model loaded")
        except Exception as e:
            print(f"❌ spaCy: {e}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()