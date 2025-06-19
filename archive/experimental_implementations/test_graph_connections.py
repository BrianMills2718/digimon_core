#!/usr/bin/env python
"""Debug graph connections."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.database import DatabaseManager

db = DatabaseManager()
db.initialize()

print("=== Graph Connection Debug ===\n")

with db.neo4j.driver.session() as session:
    # Find Bill Gates and Steve Jobs
    result = session.run("""
        MATCH (gates:Entity)
        WHERE gates.name =~ '(?i).*gates.*'
        RETURN gates.id as id, gates.name as name
    """)
    gates_nodes = list(result)
    print("Bill Gates nodes:")
    for n in gates_nodes:
        print(f"  - {n['name']} (ID: {n['id'][:8]}...)")
    
    result = session.run("""
        MATCH (jobs:Entity)
        WHERE jobs.name =~ '(?i).*jobs.*'
        RETURN jobs.id as id, jobs.name as name
    """)
    jobs_nodes = list(result)
    print("\nSteve Jobs nodes:")
    for n in jobs_nodes:
        print(f"  - {n['name']} (ID: {n['id'][:8]}...)")
    
    # Check their connections
    if gates_nodes and jobs_nodes:
        gates_id = gates_nodes[0]['id']
        jobs_id = jobs_nodes[0]['id']
        
        # Direct connections
        result = session.run("""
            MATCH (g:Entity {id: $gates_id})-[r]-(j:Entity {id: $jobs_id})
            RETURN type(r) as rel_type
        """, gates_id=gates_id, jobs_id=jobs_id)
        
        direct = list(result)
        if direct:
            print(f"\nDirect connection: {direct[0]['rel_type']}")
        else:
            print("\nNo direct connection")
        
        # Find ANY path
        result = session.run("""
            MATCH (g:Entity {id: $gates_id})
            MATCH (j:Entity {id: $jobs_id})
            MATCH path = (g)-[*1..3]-(j)
            RETURN length(path) as hops, 
                   [n in nodes(path) | n.name] as path_nodes,
                   [r in relationships(path) | type(r)] as rel_types
            LIMIT 5
        """, gates_id=gates_id, jobs_id=jobs_id)
        
        paths = list(result)
        if paths:
            print(f"\nFound {len(paths)} paths:")
            for p in paths:
                print(f"  {p['hops']} hops: {' -> '.join(p['path_nodes'])}")
                print(f"    Relations: {p['rel_types']}")
        else:
            print("\nNo paths found within 3 hops")
    
    # Check overall connectivity
    print("\n\nOverall graph connectivity:")
    result = session.run("""
        MATCH (n:Entity)
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) as degree
        RETURN 
            count(n) as total_nodes,
            count(CASE WHEN degree > 0 THEN 1 END) as connected_nodes,
            count(CASE WHEN degree = 0 THEN 1 END) as isolated_nodes,
            avg(degree) as avg_degree,
            max(degree) as max_degree
    """)
    
    stats = result.single()
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  Connected nodes: {stats['connected_nodes']}")
    print(f"  Isolated nodes: {stats['isolated_nodes']}")
    print(f"  Average degree: {stats['avg_degree']:.2f}")
    print(f"  Max degree: {stats['max_degree']}")

db.close()