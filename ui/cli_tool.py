#!/usr/bin/env python3
"""Command-line tool for Super-Digimon GraphRAG System"""

import sys
import os
from pathlib import Path
import argparse
from typing import Optional

from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel
from src.core.config_manager import ConfigManager
from neo4j import GraphDatabase
import json


def check_neo4j():
    """Check Neo4j connection using ConfigManager."""
    try:
        config_manager = ConfigManager()
        neo4j_config = config_manager.get_neo4j_config()
        auth = None if neo4j_config['user'] is None else (neo4j_config['user'], neo4j_config['password'])
        driver = GraphDatabase.driver(neo4j_config['uri'], auth=auth)
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
    
    # Initialize pipeline orchestrator
    print("🔧 Initializing PipelineOrchestrator...")
    config_manager = ConfigManager()
    config = create_unified_workflow_config(
        phase=Phase.PHASE1,
        optimization_level=OptimizationLevel.STANDARD,
        workflow_storage_dir="./data/cli_workflows"
    )
    orchestrator = PipelineOrchestrator(config, config_manager)
    
    # Execute workflow
    print("⚙️  Processing (this may take 1-3 minutes)...")
    result = orchestrator.execute(
        document_paths=document_paths,
        queries=[query]
    )
    
    # Display results - Handle new PipelineOrchestrator format
    final_result = result.get("final_result", {})
    entities = final_result.get("entities", [])
    relationships = final_result.get("relationships", [])
    query_results = final_result.get("query_results", [])
    
    if entities or relationships or query_results:
        print("\n✅ Processing complete!")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  • Entities extracted: {len(entities)}")
        print(f"  • Relationships found: {len(relationships)}")
        print(f"  • Query results: {len(query_results)} result sets")
        
        # Query results
        if query_results:
            print(f"\n🎯 Query Results:")
            for query_idx, query_result in enumerate(query_results):
                print(f"\nQuery: {query_result.get('query', query)}")
                if query_result.get("results"):
                    for i, answer in enumerate(query_result["results"][:5], 1):
                        print(f"\n{i}. {answer.get('answer_entity', 'N/A')}")
                        print(f"   Confidence: {answer.get('confidence', 0):.2f}")
                        if answer.get("explanation"):
                            print(f"   Path: {answer['explanation']}")
                else:
                    print("   No direct answers found.")
        
        # Show sample entities if no query results
        if not query_results and entities:
            print(f"\n🏷️  Sample entities:")
            for i, entity in enumerate(entities[:10], 1):
                entity_name = entity.get('canonical_name') or entity.get('surface_form') or entity.get('name', 'Unknown')
                entity_type = entity.get('entity_type', 'UNKNOWN')
                print(f"  {i}. {entity_name} ({entity_type})")
        
        # Save results if requested
        if output_format == "json":
            output_file = f"{Path(document_paths[0]).stem}_results.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
    
    else:
        print(f"\n❌ Processing failed: No results found")
        print(f"Debug info: {result.keys()}")
        if result.get("error"):
            print(f"Error: {result['error']}")
        if "traceback" in result:
            print("\nTraceback:")
            print(result["traceback"])


def show_graph_stats():
    """Show statistics about the graph database."""
    neo4j_ok, status = check_neo4j()
    if not neo4j_ok:
        print(f"❌ Neo4j not connected: {status}")
        return
    
    config_manager = ConfigManager()
    neo4j_config = config_manager.get_neo4j_config()
    auth = None if neo4j_config['user'] is None else (neo4j_config['user'], neo4j_config['password'])
    driver = GraphDatabase.driver(neo4j_config['uri'], auth=auth)
    
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
            from src.core.pipeline_orchestrator import PipelineOrchestrator
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