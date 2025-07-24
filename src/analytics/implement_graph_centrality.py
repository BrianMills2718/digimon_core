#!/usr/bin/env python3
"""
Implementation script for Graph Centrality Analytics

This script demonstrates the usage of GraphCentralityAnalyzer
and validates its functionality.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.neo4j_manager import Neo4jDockerManager
from src.core.distributed_transaction_manager import DistributedTransactionManager
from src.analytics.graph_centrality_analyzer import GraphCentralityAnalyzer


async def main():
    """Demonstrate graph centrality implementation"""
    print("Graph Centrality Analytics Implementation Demo")
    print("=" * 50)
    
    # Initialize infrastructure
    neo4j_manager = Neo4jDockerManager()
    await neo4j_manager.ensure_started()
    
    dtm = DistributedTransactionManager(neo4j_manager)
    analyzer = GraphCentralityAnalyzer(neo4j_manager, dtm)
    
    try:
        # Create sample data
        print("\nCreating sample graph data...")
        await create_sample_graph(neo4j_manager)
        
        # 1. PageRank Centrality
        print("\n1. Calculating PageRank Centrality...")
        pagerank_result = await analyzer.calculate_pagerank_centrality(
            entity_type='Paper',
            damping_factor=0.85
        )
        
        print(f"   - Total nodes: {pagerank_result['metadata']['total_nodes']}")
        print(f"   - Method used: {pagerank_result['metadata']['method']}")
        print(f"   - Execution time: {pagerank_result['metadata']['execution_time']:.3f}s")
        
        if pagerank_result['scores']:
            print("   - Top 5 entities by PageRank:")
            for i, entity in enumerate(pagerank_result['scores'][:5], 1):
                print(f"     {i}. {entity['entity_name']} (score: {entity['pagerank_score']:.4f})")
        
        # 2. Betweenness Centrality
        print("\n2. Calculating Betweenness Centrality...")
        betweenness_result = await analyzer.calculate_betweenness_centrality(
            entity_type='Author'
        )
        
        print(f"   - Total nodes: {betweenness_result['metadata']['total_nodes']}")
        print(f"   - Method used: {betweenness_result['metadata']['method']}")
        print(f"   - Execution time: {betweenness_result['metadata']['execution_time']:.3f}s")
        
        # 3. Closeness Centrality
        print("\n3. Calculating Closeness Centrality...")
        closeness_result = await analyzer.calculate_closeness_centrality()
        
        print(f"   - Total nodes: {closeness_result['metadata']['total_nodes']}")
        print(f"   - Execution time: {closeness_result['metadata']['execution_time']:.3f}s")
        
        print("\n✓ Graph centrality analytics implementation successful!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        await cleanup_sample_data(neo4j_manager)
        await neo4j_manager.cleanup()


async def create_sample_graph(neo4j_manager):
    """Create sample graph for demonstration"""
    # Clear existing demo data
    await neo4j_manager.execute_write_query(
        "MATCH (n:DemoNode) DETACH DELETE n"
    )
    
    # Create nodes and relationships
    create_query = """
    // Create papers
    CREATE (p1:DemoNode:Paper {name: 'Foundations of ML', citations: 100})
    CREATE (p2:DemoNode:Paper {name: 'Deep Learning', citations: 80})
    CREATE (p3:DemoNode:Paper {name: 'Neural Networks', citations: 60})
    CREATE (p4:DemoNode:Paper {name: 'Computer Vision', citations: 40})
    
    // Create authors
    CREATE (a1:DemoNode:Author {name: 'Alice Johnson'})
    CREATE (a2:DemoNode:Author {name: 'Bob Smith'})
    CREATE (a3:DemoNode:Author {name: 'Carol Davis'})
    
    // Create citations
    CREATE (p2)-[:CITES {weight: 1.0}]->(p1)
    CREATE (p3)-[:CITES {weight: 0.8}]->(p1)
    CREATE (p3)-[:CITES {weight: 0.9}]->(p2)
    CREATE (p4)-[:CITES {weight: 0.7}]->(p2)
    CREATE (p4)-[:CITES {weight: 0.6}]->(p3)
    
    // Create authorships
    CREATE (a1)-[:AUTHORED]->(p1)
    CREATE (a1)-[:AUTHORED]->(p2)
    CREATE (a2)-[:AUTHORED]->(p2)
    CREATE (a2)-[:AUTHORED]->(p3)
    CREATE (a3)-[:AUTHORED]->(p3)
    CREATE (a3)-[:AUTHORED]->(p4)
    
    // Create collaborations
    CREATE (a1)-[:COLLABORATES]->(a2)
    CREATE (a2)-[:COLLABORATES]->(a3)
    """
    
    await neo4j_manager.execute_write_query(create_query)
    print("✓ Sample graph created successfully")


async def cleanup_sample_data(neo4j_manager):
    """Clean up demo data"""
    await neo4j_manager.execute_write_query(
        "MATCH (n:DemoNode) DETACH DELETE n"
    )


if __name__ == "__main__":
    asyncio.run(main())