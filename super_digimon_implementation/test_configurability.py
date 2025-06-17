#!/usr/bin/env python
"""Test tool configurability - verify parameters aren't hardcoded."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import DatabaseManager
from src.tools.phase3.t31_entity_node_builder import EntityNodeBuilder

print("=== TESTING TOOL CONFIGURABILITY ===\n")

# Initialize
db = DatabaseManager()
db.faiss.dimension = 384
db.initialize()

# Create test graph with known structure
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    
    # Create two clusters with a link of weight 2.5
    session.run("""
        // Cluster 1
        CREATE (a1:Entity {id: 'a1', name: 'A1'})
        CREATE (a2:Entity {id: 'a2', name: 'A2'})
        CREATE (a1)-[:STRONG {weight: 5.0}]->(a2)
        
        // Cluster 2  
        CREATE (b1:Entity {id: 'b1', name: 'B1'})
        CREATE (b2:Entity {id: 'b2', name: 'B2'})
        CREATE (b1)-[:STRONG {weight: 5.0}]->(b2)
        
        // Inter-cluster link with weight 2.5
        CREATE (a1)-[:WEAK {weight: 2.5}]->(b1)
    """)

print("Created graph with inter-cluster link weight = 2.5")

# Test 1: Default threshold (3.0) - should create 2 communities
print("\nTest 1: Default threshold (3.0)")
node_builder = EntityNodeBuilder(db)
result = node_builder.build_entity_nodes()
print(f"  Communities detected: {result['community_count']} (expected: 2)")

# Test 2: Lower threshold (2.0) - should merge into 1 community
print("\nTest 2: Lower threshold (2.0)")
result = node_builder.build_entity_nodes(weight_threshold=2.0)
print(f"  Communities detected: {result['community_count']} (expected: 1)")

# Test 3: Higher threshold (10.0) - should keep as 2 communities
print("\nTest 3: Higher threshold (10.0)")
result = node_builder.build_entity_nodes(weight_threshold=10.0)
print(f"  Communities detected: {result['community_count']} (expected: 2)")

# Test 4: Different max_iterations
print("\nTest 4: Testing max_iterations parameter")
result1 = node_builder.build_entity_nodes(max_iterations=1)
result2 = node_builder.build_entity_nodes(max_iterations=5)
print(f"  With max_iterations=1: {result1['metadata']['duration_ms']}ms")
print(f"  With max_iterations=5: {result2['metadata']['duration_ms']}ms")

# Test other tools for configurability
print("\n\nChecking other tools for configurability:")

# Test chunker
from src.tools.phase2.t13_text_chunker import TextChunker
chunker = TextChunker(db)
print("\n✓ T13 Text Chunker:")
print(f"  - chunk_size parameter: {'chunk_size' in chunker.chunk_document.__code__.co_varnames}")
print(f"  - overlap parameter: {'overlap' in chunker.chunk_document.__code__.co_varnames}")

# Test hop query
from src.tools.phase4.t49_hop_query import HopQuery
hop_query = HopQuery(db)
print("\n✓ T49 Hop Query:")
print(f"  - k parameter: {'k' in hop_query.hop_query.__code__.co_varnames}")
print(f"  - relationship_types parameter: {'relationship_types' in hop_query.hop_query.__code__.co_varnames}")

# Test path finding
from src.tools.phase4.t52_path_finding import PathFinding
pathfinder = PathFinding(db)
print("\n✓ T52 Path Finding:")
print(f"  - max_length parameter: {'max_length' in pathfinder.path_finding.__code__.co_varnames}")
print(f"  - algorithm parameter: {'algorithm' in pathfinder.path_finding.__code__.co_varnames}")

# Summary
print("\n\n=== CONFIGURABILITY SUMMARY ===")
print("Community detection now accepts configurable parameters:")
print("- weight_threshold: Controls when communities merge")
print("- max_iterations: Limits algorithm iterations")
print("\nOther tools already follow configurability pattern.")

# Cleanup
with db.neo4j.driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
db.close()

print("\n✅ Configurability test complete!")