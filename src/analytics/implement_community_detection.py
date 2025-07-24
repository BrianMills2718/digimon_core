#!/usr/bin/env python3
"""
Implementation script for Community Detection

This script demonstrates the usage of CommunityDetector
and validates its functionality.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.neo4j_manager import Neo4jDockerManager
from src.core.distributed_transaction_manager import DistributedTransactionManager
from src.analytics.community_detector import CommunityDetector


async def main():
    """Demonstrate community detection implementation"""
    print("Community Detection Implementation Demo")
    print("=" * 50)
    
    # Initialize infrastructure
    neo4j_manager = Neo4jDockerManager()
    await neo4j_manager.ensure_started()
    
    dtm = DistributedTransactionManager(neo4j_manager)
    detector = CommunityDetector(neo4j_manager, dtm)
    
    try:
        # Create sample collaborative network
        print("\nCreating sample research collaboration network...")
        await create_research_network(neo4j_manager)
        
        # Test different algorithms
        algorithms = ['louvain', 'label_propagation', 'greedy_modularity']
        
        for algorithm in algorithms:
            print(f"\n{algorithm.upper()} Algorithm:")
            print("-" * 30)
            
            result = await detector.detect_research_communities(
                algorithm=algorithm,
                min_community_size=2,
                resolution=1.0
            )
            
            print(f"Communities found: {result['metadata']['total_communities']}")
            print(f"Modularity score: {result['analysis']['modularity']:.3f}")
            print(f"Clustering coefficient: {result['analysis']['clustering']:.3f}")
            print(f"Execution time: {result['metadata']['execution_time']:.3f}s")
            
            # Show community details
            for i, community in enumerate(result['communities'][:3], 1):
                print(f"\nCommunity {i}:")
                print(f"  - Size: {community['size']} members")
                print(f"  - Density: {community['density']:.3f}")
                print(f"  - Dominant labels: {community['dominant_labels']}")
                
                # Show top members
                print("  - Members:")
                for member in community['members'][:5]:
                    print(f"    • {member['name']} ({', '.join(member['labels'])})")
        
        # Analyze cross-community connections
        print("\n\nCross-Community Analysis:")
        print("-" * 30)
        
        analysis = result['analysis']
        connections = analysis['cross_community_connections']
        
        if connections.get('strongest_connections'):
            print("Strongest inter-community connections:")
            for conn in connections['strongest_connections'][:3]:
                print(f"  - Community {conn['community_1']} ↔ Community {conn['community_2']}: "
                      f"strength {conn['connection_strength']:.2f}")
        
        print("\n✓ Community detection implementation successful!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        await cleanup_sample_data(neo4j_manager)
        await neo4j_manager.cleanup()


async def create_research_network(neo4j_manager):
    """Create sample research collaboration network"""
    # Clear existing demo data
    await neo4j_manager.execute_write_query(
        "MATCH (n:CommunityDemo) DETACH DELETE n"
    )
    
    # Create a network with clear community structure
    create_query = """
    // Community 1: Machine Learning researchers
    CREATE (ml1:CommunityDemo:Author {name: 'ML Researcher 1'})
    CREATE (ml2:CommunityDemo:Author {name: 'ML Researcher 2'})
    CREATE (ml3:CommunityDemo:Author {name: 'ML Researcher 3'})
    CREATE (mlp1:CommunityDemo:Paper {name: 'Advances in ML'})
    CREATE (mlp2:CommunityDemo:Paper {name: 'Deep Learning Methods'})
    
    // Community 2: Physics researchers
    CREATE (ph1:CommunityDemo:Author {name: 'Physics Researcher 1'})
    CREATE (ph2:CommunityDemo:Author {name: 'Physics Researcher 2'})
    CREATE (ph3:CommunityDemo:Author {name: 'Physics Researcher 3'})
    CREATE (php1:CommunityDemo:Paper {name: 'Quantum Mechanics'})
    CREATE (php2:CommunityDemo:Paper {name: 'Particle Physics'})
    
    // Community 3: Interdisciplinary researchers
    CREATE (id1:CommunityDemo:Author {name: 'Interdisciplinary Researcher 1'})
    CREATE (id2:CommunityDemo:Author {name: 'Interdisciplinary Researcher 2'})
    CREATE (idp1:CommunityDemo:Paper {name: 'ML in Physics'})
    
    // Intra-community connections (strong)
    CREATE (ml1)-[:COLLABORATES {weight: 0.9}]->(ml2)
    CREATE (ml2)-[:COLLABORATES {weight: 0.9}]->(ml3)
    CREATE (ml1)-[:COLLABORATES {weight: 0.8}]->(ml3)
    CREATE (ml1)-[:AUTHORED]->(mlp1)
    CREATE (ml2)-[:AUTHORED]->(mlp1)
    CREATE (ml2)-[:AUTHORED]->(mlp2)
    CREATE (ml3)-[:AUTHORED]->(mlp2)
    
    CREATE (ph1)-[:COLLABORATES {weight: 0.9}]->(ph2)
    CREATE (ph2)-[:COLLABORATES {weight: 0.9}]->(ph3)
    CREATE (ph1)-[:COLLABORATES {weight: 0.8}]->(ph3)
    CREATE (ph1)-[:AUTHORED]->(php1)
    CREATE (ph2)-[:AUTHORED]->(php1)
    CREATE (ph2)-[:AUTHORED]->(php2)
    CREATE (ph3)-[:AUTHORED]->(php2)
    
    // Inter-community connections (weak)
    CREATE (id1)-[:COLLABORATES {weight: 0.5}]->(ml1)
    CREATE (id1)-[:COLLABORATES {weight: 0.5}]->(ph1)
    CREATE (id2)-[:COLLABORATES {weight: 0.4}]->(ml3)
    CREATE (id2)-[:COLLABORATES {weight: 0.4}]->(ph3)
    CREATE (id1)-[:AUTHORED]->(idp1)
    CREATE (id2)-[:AUTHORED]->(idp1)
    
    // Citation network
    CREATE (mlp1)-[:CITES]->(mlp2)
    CREATE (php1)-[:CITES]->(php2)
    CREATE (idp1)-[:CITES]->(mlp1)
    CREATE (idp1)-[:CITES]->(php1)
    """
    
    await neo4j_manager.execute_write_query(create_query)
    print("✓ Research collaboration network created successfully")


async def cleanup_sample_data(neo4j_manager):
    """Clean up demo data"""
    await neo4j_manager.execute_write_query(
        "MATCH (n:CommunityDemo) DETACH DELETE n"
    )


if __name__ == "__main__":
    asyncio.run(main())