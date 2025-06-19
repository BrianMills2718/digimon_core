#!/usr/bin/env python3
"""Query entities by type"""

import sys
from neo4j import GraphDatabase

def query_by_type(entity_type=None, query_text=None):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    
    with driver.session() as session:
        if entity_type:
            # Query by entity type
            print(f"\n🔍 Finding all {entity_type} entities:\n")
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.entity_type = $type
                RETURN e.canonical_name as name, e.pagerank_score as score
                ORDER BY coalesce(e.pagerank_score, 0) DESC
            """, type=entity_type.upper())
        else:
            # Free text search
            print(f"\n🔍 Searching for: '{query_text}'\n")
            result = session.run("""
                MATCH (e:Entity)
                WHERE toLower(e.canonical_name) CONTAINS toLower($query)
                RETURN e.canonical_name as name, e.entity_type as type, e.pagerank_score as score
                ORDER BY coalesce(e.pagerank_score, 0) DESC
                LIMIT 20
            """, query=query_text)
        
        results = list(result)
        if results:
            for i, record in enumerate(results, 1):
                if entity_type:
                    print(f"{i}. {record['name']} (PageRank: {record['score'] or 0:.4f})")
                else:
                    print(f"{i}. {record['name']} ({record['type']}) - PageRank: {record['score'] or 0:.4f}")
        else:
            print("No results found.")
    
    driver.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ['org', 'person', 'gpe', 'date', 'money', 'event']:
            query_by_type(entity_type=sys.argv[1])
        else:
            query_by_type(query_text=' '.join(sys.argv[1:]))
    else:
        print("\n📊 Available entity types:")
        print("  • org - Organizations/Companies")
        print("  • person - People")
        print("  • gpe - Locations (Geopolitical Entities)")
        print("  • date - Dates")
        print("  • money - Monetary values")
        print("  • event - Events")
        print("\nUsage:")
        print("  python query_by_type.py org")
        print("  python query_by_type.py person")
        print("  python query_by_type.py 'search term'")