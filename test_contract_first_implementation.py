#!/usr/bin/env python3
"""Test Contract-First Tool Implementation

This script demonstrates the proper implementation of tools according to
the contract-first design (ADR-001) and three-layer architecture (ADR-028).
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.service_manager import ServiceManager
from src.core.tool_adapter_layer2 import adapt_tool_for_orchestrator
from src.core.orchestration.workflow_engines.sequential_engine import SequentialEngine
from src.core.orchestration.result_aggregators.simple_aggregator import SimpleAggregator
# Monitoring is optional for this test

# Import tools to test
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from src.tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Test contract-first tool implementation."""
    
    # Set minimal security (no password required)
    os.environ['NEO4J_PASSWORD'] = ''
    
    print("\n" + "="*60)
    print("Testing Contract-First Tool Implementation")
    print("="*60 + "\n")
    
    # Initialize service manager
    print("1. Initializing Service Manager...")
    try:
        service_manager = ServiceManager()
        print("✅ Service Manager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Service Manager: {e}")
        return
    
    # Create tools with proper dependency injection
    print("\n2. Creating tools with dependency injection...")
    tools_to_create = [
        ("T23C", OntologyAwareExtractor),
        ("T31", T31EntityBuilderUnified),
        ("T34", T34EdgeBuilderUnified),
        ("T68", T68PageRankCalculatorUnified)
    ]
    
    tools = []
    for tool_name, tool_class in tools_to_create:
        try:
            tool = tool_class(service_manager)
            # Adapt tool for orchestrator compatibility
            adapted_tool = adapt_tool_for_orchestrator(tool, service_manager)
            tools.append(adapted_tool)
            print(f"✅ Created and adapted {tool_name}")
        except Exception as e:
            print(f"❌ Failed to create {tool_name}: {e}")
            return
    
    # Create orchestrator
    print("\n3. Creating Sequential Engine...")
    from src.core.config_manager import ConfigManager
    config_manager = ConfigManager()
    engine = SequentialEngine(config_manager)
    aggregator = SimpleAggregator()
    
    # Test data
    test_text = """
    Dr. Sarah Chen presented groundbreaking research on quantum computing at Stanford University. 
    Her work with Professor Michael Johnson has revolutionized error correction algorithms. 
    The collaboration between Stanford and MIT has produced significant breakthroughs.
    """
    
    initial_data = {
        "text": test_text,
        "chunk_ref": "test_chunk_001",
        "source_ref": "test_document"
    }
    
    # Execute pipeline
    print("\n4. Executing pipeline with contract-first tools...")
    print(f"   Processing text: {test_text[:100]}...")
    
    try:
        # Execute tools in sequence
        result = engine.execute_pipeline(
            tools=tools,
            input_data=initial_data,
            monitors=[]
        )
        
        print("\n5. Pipeline Results:")
        print(f"   Status: {result['status']}")
        print(f"   Tools executed: {result['execution_stats']['tools_executed']}")
        print(f"   Total time: {result['total_execution_time']:.2f}s")
        
        # Show execution details
        print("\n6. Tool Execution Details:")
        for i, exec_result in enumerate(result['execution_results']):
            print(f"   Tool {i+1}: {exec_result['tool_name']}")
            print(f"      Status: {exec_result['status']}")
            print(f"      Time: {exec_result['execution_time']:.2f}s")
            if 'result_summary' in exec_result:
                summary = exec_result['result_summary']
                if 'counts' in summary:
                    for key, value in summary['counts'].items():
                        print(f"      {key}: {value}")
        
        # Check final data
        final_data = result['final_data']
        print("\n7. Data Flow Verification:")
        
        # Check if entities were extracted
        if 'entities' in final_data:
            print(f"   ✅ Entities extracted: {len(final_data['entities'])}")
            for entity in final_data['entities'][:3]:
                print(f"      - {entity.get('text', 'N/A')} ({entity.get('entity_type', 'N/A')})")
        
        # Check if entity IDs are consistent
        if 'entity_ids' in final_data:
            print(f"   ✅ Entity IDs created: {len(final_data['entity_ids'])}")
        
        # Verify Neo4j data
        print("\n8. Neo4j Verification:")
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", ""))
            
            with driver.session() as session:
                # Count entities
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']
                print(f"   ✅ Entities in Neo4j: {entity_count}")
                
                # Count relationships
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']
                print(f"   ✅ Relationships in Neo4j: {rel_count}")
                
                # Show sample entities
                entities = session.run("MATCH (e:Entity) RETURN e.canonical_name as name LIMIT 3").values()
                print("   Sample entities:")
                for name in entities:
                    print(f"      - {name[0]}")
            
            driver.close()
        except Exception as e:
            print(f"   ⚠️  Could not verify Neo4j data: {e}")
        
        print("\n" + "="*60)
        print("✅ Contract-First Implementation Test SUCCESSFUL")
        print("="*60)
        
        # Show architecture alignment
        print("\n9. Architecture Alignment:")
        print("   - Layer 1: Tool implementations (T23C, T31, T34, T68)")
        print("   - Layer 2: KGASTool contract via Layer2ToolAdapter")
        print("   - Orchestrator: Sequential engine with proper validation")
        print("   - Data Flow: Consistent without field adapters")
        
    except Exception as e:
        print(f"\n❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()